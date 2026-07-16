"""Modelos del bot de WhatsApp (ventas).

Deliberadamente desacoplados del producto: ninguna tabla referencia `organizations`
ni `workers`. El bot atiende prospectos, no clientes autenticados, así que no lee
datos personales de trabajadores (Ley 21.719). Ver docs/BOT_WHATSAPP.md.
"""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base


class BotInboundEvent(Base):
    """Auditoría e idempotencia de los webhooks entrantes de Meta.

    Meta reintenta la entrega si no recibe un 2xx a tiempo, así que el mismo mensaje
    puede llegar más de una vez. `wamid` (el id de mensaje de WhatsApp) es único: el
    insert conflictivo es la señal de que ya lo procesamos. Mismo patrón que
    `PaymentEvent.flow_token` en billing.
    """

    __tablename__ = "bot_inbound_events"
    __table_args__ = (Index("ix_bot_inbound_events_wamid", "wamid", unique=True),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    wamid: Mapped[str] = mapped_column(String(128), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(32), nullable=True)
    signature_valid: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    raw_payload: Mapped[dict] = mapped_column(JSONB, nullable=False, server_default="{}")
    processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class BotConversation(Base):
    """Una conversación con un número de WhatsApp.

    La sesión expira a los `SESSION_TIMEOUT_MINUTES`: pasado ese tiempo, el siguiente
    mensaje abre una conversación nueva. Por eso `phone` NO es único — un mismo número
    acumula varias conversaciones en el tiempo.
    """

    __tablename__ = "bot_conversations"
    __table_args__ = (Index("ix_bot_conversations_phone", "phone"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    phone: Mapped[str] = mapped_column(String(32), nullable=False)

    # state: new|collecting|derived|support|closed
    state: Mapped[str] = mapped_column(String(20), nullable=False, server_default="new")
    # Datos del prospecto recogidos hasta ahora (nombre, empresa, correo, ...).
    collected: Mapped[dict] = mapped_column(JSONB, nullable=False, server_default="{}")
    # Turnos de captura reales. Separado de un contador global a propósito: en el bot de
    # Faymex, medir contra el total hizo que dos saludos agotaran el presupuesto y el lead
    # se derivara sin pedir datos jamás (docs/fix_lead_sin_datos_16jun2026.md de ese repo).
    collect_turns: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")

    # Bot pausado: un humano se hizo cargo de esta conversación.
    handed_off: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    # Guard anti-duplicado: si ya avisamos por correo, no volvemos a avisar.
    notified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    last_message_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    messages: Mapped[list["BotMessage"]] = relationship(
        "BotMessage", back_populates="conversation", cascade="all, delete-orphan"
    )


class BotMessage(Base):
    """Un turno de la conversación. `role` usa el vocabulario de la API de Claude
    (`user`/`assistant`) para poder armar el historial sin traducir."""

    __tablename__ = "bot_messages"
    __table_args__ = (Index("ix_bot_messages_conversation_id", "conversation_id"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    conversation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bot_conversations.id", ondelete="CASCADE"), nullable=False
    )
    role: Mapped[str] = mapped_column(String(16), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    conversation: Mapped["BotConversation"] = relationship("BotConversation", back_populates="messages")


class BotLead(Base):
    """Prospecto capturado. Es el entregable del bot."""

    __tablename__ = "bot_leads"
    __table_args__ = (Index("ix_bot_leads_conversation_id", "conversation_id"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    conversation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bot_conversations.id", ondelete="CASCADE"), nullable=False
    )
    phone: Mapped[str] = mapped_column(String(32), nullable=False)
    name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    company: Mapped[str | None] = mapped_column(String(160), nullable=True)
    email: Mapped[str | None] = mapped_column(String(160), nullable=True)
    industry: Mapped[str | None] = mapped_column(String(80), nullable=True)
    workers_estimate: Mapped[str | None] = mapped_column(String(40), nullable=True)
    interest: Mapped[str | None] = mapped_column(Text, nullable=True)
    notified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
