"""Lógica de negocio de facturación: normaliza el resultado de un pago de Flow y lo
aplica a la suscripción de la organización, de forma idempotente.

Separada del transporte (flow_client) y del endpoint (webhooks) para poder testearla
sin HTTP. Ver docs/PASARELA_PAGO_FLOW.md §5-6.

Estados de pago de Flow (payment/getStatus → campo `status`):
    1 = pendiente · 2 = pagada · 3 = rechazada · 4 = anulada
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.billing.plans import BillingPeriod, SubscriptionStatus
from app.models.subscription import PaymentEvent, Subscription

FLOW_STATUS_PENDING = 1
FLOW_STATUS_PAID = 2
FLOW_STATUS_REJECTED = 3
FLOW_STATUS_VOIDED = 4


@dataclass
class PaymentResult:
    """Resultado de pago normalizado desde el payload de Flow."""

    token: str
    flow_status: int
    commerce_order: str | None = None
    flow_order: str | None = None
    amount: int | None = None
    subscription_id_flow: str | None = None
    raw: dict[str, Any] = field(default_factory=dict)

    @property
    def is_paid(self) -> bool:
        return self.flow_status == FLOW_STATUS_PAID


def normalize_payment_status(token: str, payload: dict[str, Any]) -> PaymentResult:
    """Extrae los campos que nos importan del payload de payment/getStatus.

    Es el ÚNICO punto acoplado a la forma exacta del payload de Flow; si cambia,
    se ajusta aquí. Reconfirmar los nombres de campo contra el sandbox en la Fase 5."""
    amount = payload.get("amount")
    try:
        amount = int(float(amount)) if amount is not None else None
    except (TypeError, ValueError):
        amount = None
    status = payload.get("status")
    try:
        status = int(status)
    except (TypeError, ValueError):
        status = FLOW_STATUS_PENDING
    # Algunos payloads de suscripción anidan la referencia bajo subscriptionData/subscription.
    sub_ref = (
        payload.get("subscriptionId")
        or (payload.get("subscriptionData") or {}).get("subscriptionId")
        or (payload.get("subscription") or {}).get("subscriptionId")
    )
    return PaymentResult(
        token=token,
        flow_status=status,
        commerce_order=payload.get("commerceOrder"),
        flow_order=str(payload["flowOrder"]) if payload.get("flowOrder") is not None else None,
        amount=amount,
        subscription_id_flow=sub_ref,
        raw=payload,
    )


async def _resolve_subscription(db: AsyncSession, result: PaymentResult) -> Subscription | None:
    """Ubica la suscripción del pago: por flow_subscription_id o por commerce_order=org_id."""
    if result.subscription_id_flow:
        row = await db.execute(
            select(Subscription).where(Subscription.flow_subscription_id == result.subscription_id_flow)
        )
        sub = row.scalar_one_or_none()
        if sub:
            return sub
    if result.commerce_order:
        # En el checkout fijamos commerceOrder = org_id (ver Fase 5).
        try:
            org_uuid = uuid.UUID(result.commerce_order)
        except (ValueError, AttributeError):
            org_uuid = None
        if org_uuid is not None:
            row = await db.execute(select(Subscription).where(Subscription.org_id == org_uuid))
            return row.scalar_one_or_none()
    return None


def _add_months(dt: datetime, months: int) -> datetime:
    month_index = dt.month - 1 + months
    year = dt.year + month_index // 12
    month = month_index % 12 + 1
    # Ajuste de día por meses cortos (28-30 días).
    day = min(dt.day, [31, 29 if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0) else 28,
                       31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month - 1])
    return dt.replace(year=year, month=month, day=day)


def _period_end(start: datetime, billing_period: str | None) -> datetime:
    if billing_period == BillingPeriod.ANNUAL.value:
        return _add_months(start, 12)
    return _add_months(start, 1)  # mensual por defecto


async def apply_payment_result(db: AsyncSession, result: PaymentResult) -> PaymentEvent:
    """Registra el evento y transiciona la suscripción. Idempotente por `flow_token`:
    un reintento del webhook con el mismo token devuelve el evento ya procesado sin
    volver a aplicar la transición."""
    # Idempotencia: ¿ya procesamos este token?
    existing = await db.execute(select(PaymentEvent).where(PaymentEvent.flow_token == result.token))
    prev = existing.scalar_one_or_none()
    if prev is not None and prev.processed_at is not None:
        return prev

    sub = await _resolve_subscription(db, result)
    now = datetime.now(timezone.utc)

    event = PaymentEvent(
        org_id=sub.org_id if sub else None,
        subscription_id=sub.id if sub else None,
        flow_event_type="payment.getStatus",
        flow_token=result.token,
        commerce_order=result.commerce_order,
        status="paid" if result.is_paid else "failed",
        amount=result.amount,
        signature_valid=True,  # el estado se confirmó re-consultando a Flow (no por firma del webhook)
        raw_payload=result.raw or {},
        processed_at=now,
    )

    if sub is not None:
        if result.is_paid:
            sub.status = SubscriptionStatus.ACTIVE.value
            sub.current_period_start = now
            sub.current_period_end = _period_end(now, sub.billing_period)
        elif result.flow_status in (FLOW_STATUS_REJECTED, FLOW_STATUS_VOIDED):
            sub.status = SubscriptionStatus.PAST_DUE.value
        db.add(sub)

    db.add(event)
    await db.commit()
    await db.refresh(event)
    return event
