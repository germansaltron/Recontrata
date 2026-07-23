"""Endpoints de facturación / suscripción.

- Lectura: plan actual + uso (alimenta la barra de uso y el paywall del frontend).
- Checkout con Flow (Fase 5): iniciar contratación (registro de tarjeta), retorno
  desde Flow (crea la suscripción) y cancelación. La lógica vive en
  `app/billing/checkout.py`; aquí solo van los endpoints. Ver `docs/PASARELA_PAGO_FLOW.md`.
"""

import uuid

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.billing import checkout as checkout_service
from app.billing.enforcement import count_active_projects, count_active_workers, get_effective_plan
from app.billing.flow_client import FlowClient
from app.billing.plans import PLAN_DISPLAY_NAME, get_limits
from app.database import get_db
from app.dependencies import get_current_user, get_org_admin, get_org_member
from app.errors import ErrorCode
from app.models.organization import OrgMember, Organization
from app.models.subscription import Subscription
from app.models.user import User
from app.schemas.billing import CheckoutRequest, CheckoutResponse, PlanUsage, SubscriptionResponse

logger = structlog.get_logger()

router = APIRouter(prefix="/organizations/{org_id}/billing", tags=["billing"])
# Router público para el retorno de Flow (no puede autenticarse con Clerk).
public_router = APIRouter(prefix="/billing", tags=["billing"])


def get_flow_client() -> FlowClient:
    """Factory inyectable (los tests la sobrescriben con un cliente stub)."""
    return FlowClient()


async def _get_subscription(db: AsyncSession, org_id: uuid.UUID) -> Subscription:
    sub = (await db.execute(select(Subscription).where(Subscription.org_id == org_id))).scalar_one_or_none()
    if sub is None:
        raise HTTPException(status_code=404, detail={"detail": "La organización no tiene suscripción", "code": ErrorCode.ORG_NOT_FOUND})
    return sub


@router.get("/subscription", response_model=SubscriptionResponse)
async def get_subscription(
    org_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _member: OrgMember = Depends(get_org_member),
):
    """Estado de la suscripción de la organización + uso facturable actual."""
    result = await db.execute(select(Subscription).where(Subscription.org_id == org_id))
    sub = result.scalar_one_or_none()

    plan = await get_effective_plan(db, org_id)
    limits = get_limits(plan)

    usage = PlanUsage(
        active_workers=await count_active_workers(db, org_id),
        active_workers_limit=limits.max_active_workers,
        active_projects=await count_active_projects(db, org_id),
        active_projects_limit=limits.max_active_projects,
    )

    return SubscriptionResponse(
        plan=sub.plan if sub else plan.value,
        plan_display_name=PLAN_DISPLAY_NAME.get(plan, plan.value),
        billing_period=sub.billing_period if sub else None,
        status=sub.status if sub else "active",
        trial_ends_at=sub.trial_ends_at if sub else None,
        current_period_end=sub.current_period_end if sub else None,
        canceled_at=sub.canceled_at if sub else None,
        usage=usage,
    )


@router.post("/checkout", response_model=CheckoutResponse)
async def create_checkout(
    org_id: uuid.UUID,
    body: CheckoutRequest,
    db: AsyncSession = Depends(get_db),
    _admin: OrgMember = Depends(get_org_admin),
    user: User = Depends(get_current_user),
    client: FlowClient = Depends(get_flow_client),
):
    """Inicia la contratación de un plan: crea el cliente en Flow y devuelve la URL para
    registrar la tarjeta. Solo un admin de la org puede contratar."""
    sub = await _get_subscription(db, org_id)
    org = (await db.execute(select(Organization).where(Organization.id == org_id))).scalar_one_or_none()
    # Flow valida que el email del cliente sea un buzón REAL (no basta con la sintaxis):
    # un placeholder tipo org-<id>@recontrata.cl es rechazado con "email is not valid".
    # Si la cuenta no tiene un email válido (p.ej. el JWT de Clerk no trajo el claim `email`),
    # fallar con un mensaje claro en vez de mandar a Flow un correo inexistente.
    email = (user.email or "").strip()
    domain = email.rsplit("@", 1)[-1] if "@" in email else ""
    if "@" not in email or "." not in domain:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"detail": "Tu cuenta no tiene un email válido para la facturación. "
                              "Verifica que tu correo esté cargado en tu perfil y vuelve a intentar."},
        )
    try:
        result = await checkout_service.start_checkout(
            db, sub, org.name if org else "", email, body.plan, body.billing_period, client
        )
    except checkout_service.CheckoutError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"detail": str(e)})
    return CheckoutResponse(redirect_url=result.redirect_url)


@router.post("/cancel", response_model=SubscriptionResponse)
async def cancel_subscription(
    org_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _admin: OrgMember = Depends(get_org_admin),
    client: FlowClient = Depends(get_flow_client),
):
    """Cancela la suscripción (queda activa hasta fin del período pagado)."""
    sub = await _get_subscription(db, org_id)
    try:
        await checkout_service.cancel_subscription(db, sub, client)
    except checkout_service.CheckoutError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"detail": str(e)})
    return await get_subscription(org_id, db, _admin)


@public_router.get("/return")
async def billing_return(
    token: str = Query(...),
    db: AsyncSession = Depends(get_db),
    client: FlowClient = Depends(get_flow_client),
):
    """Retorno desde Flow tras registrar la tarjeta: confirma y crea la suscripción,
    luego redirige al frontend. Público (Flow no puede autenticarse)."""
    try:
        await checkout_service.complete_return(db, token, client)
        return RedirectResponse(url="/app/suscripcion?checkout=success", status_code=303)
    except checkout_service.CheckoutError as e:
        logger.warning("billing_return_failed", token=token, error=str(e))
        return RedirectResponse(url="/app/suscripcion?checkout=error", status_code=303)
