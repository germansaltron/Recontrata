"""Lógica del checkout de suscripciones con Flow (Fase 5).

Flujo de Flow (API de Suscripciones), en dos tramos separados por la redirección del
usuario a Flow para registrar su tarjeta:

  1. start_checkout  → crea/reutiliza el customer en Flow, guarda el plan elegido como
     "pendiente" en la suscripción, e inicia el registro de tarjeta (customer/register).
     Devuelve la URL de Flow a la que el frontend redirige al usuario.
  2. (el usuario registra su tarjeta en Flow y Flow lo devuelve a /billing/return)
     complete_return → confirma el registro (customer/getRegisterStatus) y, si quedó OK,
     crea la suscripción (subscription/create) con el plan pendiente. Activa el plan.
  3. cancel_subscription → cancela al fin del período pagado.

Separado del endpoint para poder testear la lógica sin HTTP. Los nombres exactos de
algunos campos de las respuestas de Flow (getRegisterStatus, subscription/create) están
marcados con `# QA:` porque deben reconfirmarse contra el sandbox real al hacer el E2E.
"""

import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.billing.flow_client import FlowClient, FlowError
from app.billing.plans import (
    SELF_SERVE_PLANS,
    TRIAL_PERIOD_DAYS,
    BillingPeriod,
    Plan,
    SubscriptionStatus,
)
from app.config import settings
from app.models.subscription import Subscription


class CheckoutError(Exception):
    """Error de negocio del checkout (plan inválido, plan sin ID configurado, etc.)."""


@dataclass
class CheckoutStart:
    """Resultado de iniciar el checkout: la URL de Flow para registrar la tarjeta."""

    redirect_url: str
    flow_token: str


def flow_plan_id(plan: Plan, period: BillingPeriod) -> str:
    """planId configurado en Flow para (plan, período), desde las env vars
    FLOW_PLAN_ID_PRO_MONTHLY, ..._ANNUAL, FLOW_PLAN_ID_EMPRESA_*."""
    attr = f"FLOW_PLAN_ID_{plan.value.upper()}_{period.value.upper()}"
    plan_id = getattr(settings, attr, "")
    if not plan_id:
        raise CheckoutError(
            f"No hay planId de Flow configurado para {plan.value}/{period.value} "
            f"(falta {attr}; correr scripts/flow_bootstrap_plans.py)."
        )
    return plan_id


def _validate_plan(plan_str: str, period_str: str) -> tuple[Plan, BillingPeriod]:
    try:
        plan = Plan(plan_str)
        period = BillingPeriod(period_str)
    except ValueError as e:
        raise CheckoutError(f"Plan o período inválido: {e}") from e
    if plan not in SELF_SERVE_PLANS:
        raise CheckoutError(f"El plan {plan.value} no se contrata en línea.")
    return plan, period


async def _find_customer_id_by_external_id(client: FlowClient, external_id: str) -> str | None:
    """Busca en Flow (customer/list, paginado) el customerId cuyo externalId coincide.
    Se usa para recuperar un cliente creado en un intento previo que no persistió su id."""
    start = 0
    for _ in range(50):  # backstop: hasta 50 páginas (5.000 clientes) para no colgarse
        resp = await client.list_customers(start=start, limit=100)
        data = resp.get("data") or []
        for customer in data:
            ext = customer.get("externalId", customer.get("external_id"))
            if str(ext) == str(external_id):
                return customer.get("customerId")
        if not resp.get("hasMore"):
            break
        start += len(data) or 100
    return None


async def start_checkout(
    db: AsyncSession,
    subscription: Subscription,
    org_name: str,
    user_email: str,
    plan_str: str,
    period_str: str,
    client: FlowClient,
) -> CheckoutStart:
    """Inicia el registro de tarjeta en Flow y deja el plan elegido como pendiente."""
    plan, period = _validate_plan(plan_str, period_str)
    # Verifica que el plan tenga planId configurado ANTES de tocar Flow (falla claro).
    flow_plan_id(plan, period)

    # Customer en Flow: se crea una vez por org y se reutiliza (external_id = org_id).
    if not subscription.flow_customer_id:
        external_id = str(subscription.org_id)
        try:
            resp = await client.create_customer(
                name=org_name or "Cliente Recontrata",
                email=user_email,
                external_id=external_id,
            )
            customer_id = resp.get("customerId")  # validado en sandbox 22-jul
            if not customer_id:
                raise CheckoutError("Flow no devolvió customerId al crear el cliente.")
        except FlowError as e:
            # Recuperación de cliente huérfano: si un intento previo ya creó el customer en
            # Flow pero no alcanzó a persistir el id (falló antes del commit), Flow responde
            # "There is a customer with this externalId". En ese caso lo buscamos y reutilizamos
            # en vez de fallar.
            if "externalid" in str(e).lower():
                customer_id = await _find_customer_id_by_external_id(client, external_id)
                if not customer_id:
                    raise CheckoutError(f"No se pudo crear ni recuperar el cliente en Flow: {e}") from e
            else:
                raise CheckoutError(f"No se pudo crear el cliente en Flow: {e}") from e
        subscription.flow_customer_id = customer_id
        # Persistir de inmediato: si el registro de tarjeta falla más abajo, el customer ya
        # queda asociado y un reintento no volverá a crearlo (evita el huérfano).
        await db.commit()

    # Guarda el plan elegido como pendiente (se concreta en el return).
    subscription.pending_plan = plan.value
    subscription.pending_period = period.value

    # Inicia el registro de tarjeta: Flow devuelve { url, token }. Redirigimos a esa url.
    try:
        reg = await client.register_card(
            customer_id=subscription.flow_customer_id,
            url_return=settings.BILLING_RETURN_URL,
        )
    except FlowError as e:
        raise CheckoutError(f"No se pudo iniciar el registro de tarjeta en Flow: {e}") from e

    url = reg.get("url")
    token = reg.get("token")
    if not url or not token:
        raise CheckoutError("Flow no devolvió url/token para el registro de tarjeta.")

    await db.commit()
    return CheckoutStart(redirect_url=f"{url}?token={token}", flow_token=token)


async def complete_return(db: AsyncSession, token: str, client: FlowClient) -> Subscription:
    """Tras el registro de tarjeta, confirma con Flow y crea la suscripción del plan
    pendiente. Devuelve la suscripción actualizada. Idempotente: si ya hay una
    suscripción de Flow activa para ese customer, no crea otra."""
    try:
        status = await client.get_register_status(token)
    except FlowError as e:
        raise CheckoutError(f"No se pudo verificar el registro de tarjeta: {e}") from e

    customer_id = status.get("customerId")  # validado en sandbox 22-jul
    # Flow: status "1" = tarjeta registrada correctamente (validado contra el sandbox).
    ok = bool(customer_id) and str(status.get("status")) == "1"
    if not customer_id:
        raise CheckoutError("Flow no devolvió customerId al confirmar la tarjeta.")

    row = await db.execute(
        select(Subscription).where(Subscription.flow_customer_id == customer_id)
    )
    sub = row.scalar_one_or_none()
    if sub is None:
        raise CheckoutError("No se encontró la suscripción del cliente que volvió de Flow.")

    if not ok:
        # El registro de tarjeta no quedó bien: no se crea suscripción, se limpia lo pendiente.
        sub.pending_plan = None
        sub.pending_period = None
        await db.commit()
        raise CheckoutError("El registro de la tarjeta no se completó en Flow.")

    # Idempotencia: si ya tiene suscripción de Flow, no se crea otra (doble return).
    if sub.flow_subscription_id:
        return sub

    plan = Plan(sub.pending_plan) if sub.pending_plan else None
    period = BillingPeriod(sub.pending_period) if sub.pending_period else None
    if plan is None or period is None:
        raise CheckoutError("No hay plan pendiente para crear la suscripción.")

    plan_id = flow_plan_id(plan, period)
    coupon = settings.FLOW_COUPON_FOUNDER or None
    try:
        created = await client.create_subscription(
            plan_id=plan_id,
            customer_id=customer_id,
            trial_period_days=TRIAL_PERIOD_DAYS,
            coupon_id=coupon,
        )
    except FlowError as e:
        raise CheckoutError(f"No se pudo crear la suscripción en Flow: {e}") from e

    sub_id = created.get("subscriptionId")  # validado en sandbox 22-jul
    now = datetime.now(timezone.utc)
    sub.plan = plan.value
    sub.billing_period = period.value
    sub.status = SubscriptionStatus.TRIALING.value
    sub.flow_subscription_id = sub_id
    sub.flow_plan_id = plan_id
    sub.trial_ends_at = now + timedelta(days=TRIAL_PERIOD_DAYS)
    sub.current_period_start = now
    sub.pending_plan = None
    sub.pending_period = None
    await db.commit()
    await db.refresh(sub)
    return sub


async def cancel_subscription(db: AsyncSession, subscription: Subscription, client: FlowClient) -> Subscription:
    """Cancela la suscripción en Flow y marca canceled_at.

    Si está en trial, cancela de INMEDIATO (at_period_end=False) para garantizar que Flow
    no alcance a cobrar el primer período al terminar la prueba. Si es un plan pagado en
    curso, cancela al FIN del período ya pagado (at_period_end=True) para no perder los
    días que el cliente ya pagó."""
    if not subscription.flow_subscription_id:
        raise CheckoutError("La organización no tiene una suscripción de pago activa.")
    in_trial = subscription.status == SubscriptionStatus.TRIALING.value
    try:
        await client.cancel_subscription(subscription.flow_subscription_id, at_period_end=not in_trial)
    except FlowError as e:
        raise CheckoutError(f"No se pudo cancelar la suscripción en Flow: {e}") from e

    subscription.status = SubscriptionStatus.CANCELED.value
    subscription.canceled_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(subscription)
    return subscription
