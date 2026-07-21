"""Motor de conversación del bot de ventas.

Orquesta Claude (Sonnet 5) con tool-use sobre el estado guardado por teléfono. Config del
LLM según docs/BOT_WHATSAPP.md: thinking DESHABILITADO (Sonnet 5 corre adaptativo si se
omite), effort BAJO, SIN temperature/top_p (Sonnet 5 los rechaza), y prompt de sistema
CACHEADO (es la parte pesada y estable).

El historial se maneja como OBJETOS (no se serializa a texto y se re-parsea, como en el
bot de Faymex, que se rompía con un salto de línea). Las vueltas de tool-use NO se
persisten: solo se guarda el texto final del asistente.
"""

from datetime import datetime, timedelta, timezone

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.notifications import send_escalation_email, send_lead_email
from app.bot.prompts import SYSTEM_PROMPT
from app.bot.tools import TOOLS
from app.config import settings
from app.models.bot import BotConversation, BotLead, BotMessage

logger = structlog.get_logger()

MAX_HISTORY = 20  # últimos N turnos que se le mandan al modelo
MAX_TOOL_ITERATIONS = 5  # tope de vueltas de tool-use por mensaje


def _now() -> datetime:
    return datetime.now(timezone.utc)


class BotEngine:
    """Procesa un mensaje entrante y devuelve la respuesta de texto (o None si el bot
    está en pausa por handoff). El cliente de Anthropic se inyecta para poder testear."""

    def __init__(self, db: AsyncSession, anthropic_client):
        self.db = db
        self.client = anthropic_client
        # Avisos por correo pendientes: se acumulan durante el tool-use y se mandan tras
        # el commit (así un fallo de correo no revierte la conversación). Cada entrada es
        # ("lead"|"escalation", datos, transcripción).
        self._pending: list[tuple] = []

    async def handle_message(self, phone: str, text: str) -> str | None:
        self._pending = []
        conv = await self._get_or_create_conversation(phone)
        await self._add_message(conv, "user", text)

        if conv.handed_off:
            # Bot en pausa: un humano se hizo cargo. Se guarda el mensaje pero no se
            # responde (el equipo atiende esta conversación).
            conv.last_message_at = _now()
            await self.db.commit()
            logger.info("bot_handed_off_silent", phone=phone)
            return None

        messages = await self._build_messages(conv)
        reply = await self._run_llm(conv, messages)

        if reply:
            await self._add_message(conv, "assistant", reply)
        conv.last_message_at = _now()
        await self.db.commit()

        await self._flush_notifications()
        return reply

    async def _flush_notifications(self) -> None:
        """Envía los avisos pendientes tras el commit. Mejor esfuerzo: nunca revienta."""
        for kind, data, transcript in self._pending:
            try:
                if kind == "lead":
                    await send_lead_email(data, transcript)
                elif kind == "escalation":
                    await send_escalation_email(data["phone"], data.get("reason", ""), transcript)
            except Exception as e:  # noqa: BLE001
                logger.warning("bot_notification_failed", kind=kind, error=str(e))
        self._pending = []

    # --- Estado de la conversación ------------------------------------------

    async def _get_or_create_conversation(self, phone: str) -> BotConversation:
        """La conversación más reciente del teléfono, o una nueva si expiró la sesión.

        `.limit(1)` a propósito: un teléfono acumula varias conversaciones y sin el
        límite un `scalar_one` reventaría (el bug que dejó mudo al bot de Faymex)."""
        row = (
            await self.db.execute(
                select(BotConversation)
                .where(BotConversation.phone == phone)
                .order_by(BotConversation.created_at.desc())
                .limit(1)
            )
        ).scalars().first()

        if row is not None:
            last = row.last_message_at
            if last.tzinfo is None:
                last = last.replace(tzinfo=timezone.utc)
            fresh = _now() - last < timedelta(minutes=settings.SESSION_TIMEOUT_MINUTES)
            if fresh:
                return row

        conv = BotConversation(phone=phone, state="new")
        self.db.add(conv)
        await self.db.flush()  # asigna id
        return conv

    async def _add_message(self, conv: BotConversation, role: str, content: str) -> None:
        self.db.add(BotMessage(conversation_id=conv.id, role=role, content=content))

    async def _build_messages(self, conv: BotConversation) -> list[dict]:
        rows = (
            await self.db.execute(
                select(BotMessage)
                .where(BotMessage.conversation_id == conv.id)
                .order_by(BotMessage.created_at.asc())
            )
        ).scalars().all()
        history = [{"role": m.role, "content": m.content} for m in rows]
        return history[-MAX_HISTORY:]

    async def _transcript(self, conv: BotConversation) -> list[tuple[str, str]]:
        """La conversación como (role, texto), para incluirla en los correos de aviso."""
        rows = (
            await self.db.execute(
                select(BotMessage)
                .where(BotMessage.conversation_id == conv.id)
                .order_by(BotMessage.created_at.asc())
            )
        ).scalars().all()
        return [(m.role, m.content) for m in rows]

    # --- LLM + tool-use -----------------------------------------------------

    async def _run_llm(self, conv: BotConversation, messages: list[dict]) -> str:
        for _ in range(MAX_TOOL_ITERATIONS):
            resp = await self.client.messages.create(
                model=settings.BOT_MODEL,
                max_tokens=500,
                thinking={"type": "disabled"},
                output_config={"effort": "low"},
                system=[
                    {"type": "text", "text": SYSTEM_PROMPT, "cache_control": {"type": "ephemeral"}}
                ],
                tools=TOOLS,
                messages=messages,
            )

            if resp.stop_reason == "tool_use":
                messages.append({"role": "assistant", "content": resp.content})
                tool_results = []
                for block in resp.content:
                    if getattr(block, "type", None) == "tool_use":
                        result = await self._execute_tool(conv, block.name, dict(block.input))
                        tool_results.append(
                            {"type": "tool_result", "tool_use_id": block.id, "content": result}
                        )
                messages.append({"role": "user", "content": tool_results})
                continue

            # Turno normal: extraer el texto.
            return "".join(
                getattr(b, "text", "") for b in resp.content if getattr(b, "type", None) == "text"
            ).strip()

        logger.warning("bot_tool_loop_exhausted", phone=conv.phone)
        return ""

    async def _execute_tool(self, conv: BotConversation, name: str, inp: dict) -> str:
        logger.info("bot_tool_call", tool=name, phone=conv.phone)

        if name == "registrar_prospecto":
            if conv.notified_at is not None:
                return "Este prospecto ya estaba registrado; no lo registres de nuevo."
            lead = BotLead(
                conversation_id=conv.id,
                phone=conv.phone,
                name=inp.get("name"),
                company=inp.get("company"),
                email=inp.get("email"),
                industry=inp.get("industry"),
                workers_estimate=inp.get("workers_estimate"),
                interest=inp.get("interest"),
                notified_at=_now(),
            )
            self.db.add(lead)
            conv.state = "derived"
            conv.notified_at = _now()
            conv.collect_turns = (conv.collect_turns or 0) + 1
            conv.collected = {**(conv.collected or {}), **{k: v for k, v in inp.items() if v}}
            snapshot = {**{k: inp.get(k) for k in
                           ("name", "company", "email", "industry", "workers_estimate", "interest")},
                        "phone": conv.phone}
            self._pending.append(("lead", snapshot, await self._transcript(conv)))
            return (
                "Prospecto registrado; el equipo comercial será avisado. "
                "Confirma a la persona, breve y cordial, que la contactarán pronto."
            )

        if name == "derivar_a_soporte":
            conv.state = "support"
            return (
                "Es un cliente existente con una consulta de soporte. Entrégale el correo "
                f"{settings.BOT_SUPPORT_EMAIL} para que lo ayuden, y cierra con amabilidad. "
                "No intentes resolver el problema técnico."
            )

        if name == "escalar_a_humano":
            conv.handed_off = True
            conv.notified_at = _now()
            self._pending.append(
                ("escalation", {"phone": conv.phone, "reason": inp.get("reason", "")},
                 await self._transcript(conv))
            )
            return (
                "Escalado a una persona del equipo; el bot queda en pausa en esta "
                "conversación. Dile que un miembro del equipo le va a responder."
            )

        return "Herramienta desconocida."
