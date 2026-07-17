"""Envío de mensajes a WhatsApp (Meta Cloud API).

Async con httpx. Sin token configurado (dev/tests), no llama a la red: loguea y devuelve
un id ficticio, para poder probar el flujo completo sin credenciales reales.
"""

import httpx
import structlog

from app.config import settings

logger = structlog.get_logger()


async def send_whatsapp_text(to: str, text: str) -> str | None:
    """Envía un mensaje de texto por WhatsApp. Devuelve el wamid saliente, o None.

    No revienta si Meta falla: loguea y devuelve None (el webhook no puede caerse por
    un error de envío).
    """
    if not settings.WHATSAPP_TOKEN or not settings.WHATSAPP_PHONE_ID:
        logger.info("whatsapp_send_dev_mode", to=to, chars=len(text))
        return "dev-no-token"

    url = f"{settings.WHATSAPP_API_URL}/{settings.WHATSAPP_PHONE_ID}/messages"
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to,
        "type": "text",
        "text": {"body": text},
    }
    headers = {"Authorization": f"Bearer {settings.WHATSAPP_TOKEN}"}
    try:
        async with httpx.AsyncClient(timeout=20) as client:
            r = await client.post(url, json=payload, headers=headers)
            r.raise_for_status()
            data = r.json()
        wamid = (data.get("messages") or [{}])[0].get("id")
        logger.info("whatsapp_sent", to=to, wamid=wamid)
        return wamid
    except Exception as e:  # noqa: BLE001
        logger.warning("whatsapp_send_failed", to=to, error=str(e))
        return None
