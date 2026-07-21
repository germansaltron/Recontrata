"""Webhook de WhatsApp (Meta Cloud API) para el bot de ventas.

Endpoint público (Meta no puede autenticarse con Clerk). La confianza se establece de
dos formas, ambas obligatorias:

  * `GET`  — Meta verifica la URL una sola vez con `hub.verify_token`.
  * `POST` — cada entrega viene firmada con HMAC-SHA256 en `X-Hub-Signature-256`.
             Se valida contra `META_APP_SECRET` sobre el cuerpo CRUDO.

Dos reglas no obvias, ambas aprendidas en producción con el bot de Faymex:

  1. **Siempre responder 200.** Si el endpoint devuelve 5xx, Meta lo marca como no
     saludable y reduce o desactiva la entrega. Un error nuestro no puede costarnos
     el canal, así que se loguea y se responde 200 igual.
  2. **Idempotencia por `wamid`.** Meta reintenta si no recibe el 2xx a tiempo, así que
     el mismo mensaje puede llegar dos veces. El índice unique sobre
     `bot_inbound_events.wamid` es el árbitro: si el insert choca, ya lo procesamos.

Ver docs/BOT_WHATSAPP.md.
"""

import asyncio
import hashlib
import hmac

import structlog
from anthropic import AsyncAnthropic
from fastapi import APIRouter, Depends, Request, Response, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.client import send_whatsapp_text
from app.bot.conversation import BotEngine
from app.config import settings
from app.database import async_session, get_db
from app.models.bot import BotInboundEvent

logger = structlog.get_logger()

router = APIRouter(prefix="/whatsapp", tags=["whatsapp"])

_anthropic_client: AsyncAnthropic | None = None

# El event loop solo guarda referencias DÉBILES a las tasks creadas con
# asyncio.create_task; sin retenerlas, el GC puede recolectar una task a mitad de
# ejecución y la respuesta del bot nunca se enviaría. Se guarda una referencia fuerte
# aquí y se descarta al terminar. Ver https://docs.python.org/3/library/asyncio-task.html#asyncio.create_task
_background_tasks: set[asyncio.Task] = set()


def get_anthropic_client() -> AsyncAnthropic:
    """Cliente Anthropic perezoso y reutilizado (los tests inyectan otro por el engine)."""
    global _anthropic_client
    if _anthropic_client is None:
        _anthropic_client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
    return _anthropic_client


async def _process_bot_message(phone: str, text: str) -> None:
    """Corre la conversación en segundo plano, con su PROPIA sesión de DB (la del request
    ya está cerrada), y envía la respuesta. Nunca revienta: el webhook ya respondió 200."""
    try:
        async with async_session() as db:
            engine = BotEngine(db, get_anthropic_client())
            reply = await engine.handle_message(phone, text)
        if reply:
            await send_whatsapp_text(phone, reply)
    except Exception as e:  # noqa: BLE001
        logger.warning("bot_process_failed", phone=phone, error=str(e))


def verify_signature(raw_body: bytes, header: str | None) -> bool:
    """Valida `X-Hub-Signature-256` (HMAC-SHA256 del cuerpo crudo con el app secret).

    Falla cerrado: sin `META_APP_SECRET` configurado, o sin header, nada es válido.
    La comparación es en tiempo constante para no filtrar el prefijo correcto de la
    firma vía timing.
    """
    if not settings.META_APP_SECRET or not header:
        return False
    if not header.startswith("sha256="):
        return False
    expected = hmac.new(
        settings.META_APP_SECRET.encode("utf-8"),
        raw_body,
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(expected, header[len("sha256=") :])


def is_blocked(phone: str) -> bool:
    """True si el número está bloqueado. Compara solo dígitos, así que da igual el
    formato en que Meta o la env var lo entreguen."""
    digits = "".join(c for c in phone if c.isdigit())
    return bool(digits) and digits in settings.blocked_numbers_digits


def extract_messages(payload: dict) -> list[dict]:
    """Saca los mensajes entrantes del sobre de Meta.

    El payload trae también eventos de estado (`statuses`: entregado, leído) que no son
    mensajes y hay que ignorar. La estructura es profunda y opcional en cada nivel, así
    que se navega defensivamente: un cambio de forma de Meta no debe reventar el webhook.
    """
    out: list[dict] = []
    for entry in payload.get("entry") or []:
        for change in entry.get("changes") or []:
            value = change.get("value") or {}
            for message in value.get("messages") or []:
                out.append(message)
    return out


def message_text(message: dict) -> str:
    """Texto del mensaje. Lo que no es texto se degrada a un marcador legible en vez de
    perderse: el bot necesita saber que llegó *algo* para no responder en el vacío."""
    msg_type = message.get("type")
    if msg_type == "text":
        return (message.get("text") or {}).get("body", "")
    if msg_type in ("image", "document", "audio", "video"):
        media = message.get(msg_type) or {}
        caption = media.get("caption")
        return caption if caption else f"[{msg_type}]"
    if msg_type == "interactive":
        interactive = message.get("interactive") or {}
        for key in ("button_reply", "list_reply"):
            if key in interactive:
                return (interactive[key] or {}).get("title", "")
    return f"[{msg_type or 'desconocido'}]"


@router.get("/webhook")
async def verify_webhook(request: Request) -> Response:
    """Verificación de la URL por parte de Meta (se hace una sola vez, al configurar).

    Meta manda `hub.mode=subscribe` + `hub.verify_token` + `hub.challenge`, y espera el
    challenge de vuelta en texto plano.
    """
    params = request.query_params
    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge", "")

    expected = settings.WHATSAPP_VERIFY_TOKEN
    # Falla cerrado: sin token configurado no se verifica nada.
    if not expected:
        logger.warning("whatsapp_verify_no_token_configured")
        return Response(status_code=status.HTTP_403_FORBIDDEN)

    if mode == "subscribe" and token and hmac.compare_digest(token, expected):
        logger.info("whatsapp_webhook_verified")
        return Response(content=challenge, media_type="text/plain")

    logger.warning("whatsapp_verify_failed", mode=mode)
    return Response(status_code=status.HTTP_403_FORBIDDEN)


@router.post("/webhook")
async def receive_webhook(request: Request, db: AsyncSession = Depends(get_db)) -> dict:
    """Recepción de mensajes. Devuelve 200 pase lo que pase (ver docstring del módulo).

    La firma inválida es la única excepción parcial: se responde 200 (para no darle
    señal a quien sondea) pero no se procesa nada.
    """
    raw = await request.body()

    if not verify_signature(raw, request.headers.get("X-Hub-Signature-256")):
        logger.warning("whatsapp_bad_signature")
        return {"received": True}

    try:
        payload = await request.json()
    except Exception:
        logger.warning("whatsapp_bad_json")
        return {"received": True}

    for message in extract_messages(payload):
        wamid = message.get("id")
        phone = message.get("from", "")
        if not wamid:
            continue

        if is_blocked(phone):
            logger.info("whatsapp_blocked_number", phone=phone)
            continue

        # Idempotencia: el unique sobre wamid decide. Si el insert choca, este mensaje
        # ya entró antes (reintento de Meta) y no se vuelve a procesar.
        event = BotInboundEvent(wamid=wamid, phone=phone, signature_valid=True, raw_payload=message)
        db.add(event)
        try:
            await db.commit()
        except IntegrityError:
            await db.rollback()
            logger.info("whatsapp_duplicate_wamid", wamid=wamid)
            continue

        if not settings.BOT_ENABLED:
            # Candado dormido: se audita la entrada pero no se contesta.
            logger.info("whatsapp_bot_disabled", wamid=wamid)
            continue

        text = message_text(message)
        logger.info("whatsapp_message_received", wamid=wamid, phone=phone, chars=len(text))
        # La conversación corre en segundo plano para responder 200 a Meta de inmediato:
        # la latencia del LLM no puede colgar la respuesta al webhook. Se retiene la
        # referencia a la task (ver _background_tasks) para que el GC no la mate a medias.
        task = asyncio.create_task(_process_bot_message(phone, text))
        _background_tasks.add(task)
        task.add_done_callback(_background_tasks.discard)

    return {"received": True}
