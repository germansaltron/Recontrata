import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base


class Subscription(Base):
    """Suscripción de una organización (1:1). Toda org nace en el plan `free`
    (status `active`). Los planes de pago se sincronizan con Flow.
    Ver `docs/PASARELA_PAGO_FLOW.md`."""

    __tablename__ = "subscriptions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    org_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, unique=True
    )

    # Plan y ciclo. `plan`: free|pro|empresa|enterprise. `billing_period`: monthly|annual (null en free).
    plan: Mapped[str] = mapped_column(String(20), nullable=False, server_default="free")
    billing_period: Mapped[str | None] = mapped_column(String(20), nullable=True)
    # status: trialing|active|past_due|canceled|incomplete
    status: Mapped[str] = mapped_column(String(20), nullable=False, server_default="active")

    # Identificadores en Flow (null mientras sea free / sin contratar).
    flow_customer_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    flow_subscription_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    flow_plan_id: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Plan/período elegidos en el checkout, MIENTRAS el usuario registra su tarjeta en
    # Flow. Se leen en /billing/return para crear la suscripción con el plan correcto,
    # sin confiarlo a la URL de retorno (manipulable). Se limpian al concretar.
    pending_plan: Mapped[str | None] = mapped_column(String(20), nullable=True)
    pending_period: Mapped[str | None] = mapped_column(String(20), nullable=True)

    # Ventanas de tiempo.
    trial_ends_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    current_period_start: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    current_period_end: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    canceled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    organization: Mapped["Organization"] = relationship("Organization", back_populates="subscription")


class PaymentEvent(Base):
    """Auditoría de eventos/cobros recibidos de Flow (webhook `urlConfirmation`).
    Se guarda el payload crudo y el resultado de verificar la firma. `flow_token`
    es único para idempotencia (Flow reintenta las notificaciones)."""

    __tablename__ = "payment_events"
    __table_args__ = (
        Index("ix_payment_events_org_id", "org_id"),
        Index("ix_payment_events_flow_token", "flow_token", unique=True),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    # Nullable: un webhook de Flow que no logramos ligar a una org igual se audita.
    org_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True
    )
    subscription_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("subscriptions.id", ondelete="SET NULL"), nullable=True
    )

    flow_event_type: Mapped[str] = mapped_column(String(50), nullable=False)
    flow_token: Mapped[str | None] = mapped_column(String(120), nullable=True)
    commerce_order: Mapped[str | None] = mapped_column(String(120), nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False)
    amount: Mapped[int | None] = mapped_column(Integer, nullable=True)
    signature_valid: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    raw_payload: Mapped[dict] = mapped_column(JSONB, nullable=False, server_default="{}")
    processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
