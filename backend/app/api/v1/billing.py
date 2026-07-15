"""Endpoints de facturación / suscripción.

Fase 1-2: solo lectura (plan actual + uso), que alimenta la barra de uso y el paywall
del frontend. El checkout/cancel/webhook con Flow llegan en fases posteriores
(ver `docs/PASARELA_PAGO_FLOW.md`)."""

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.billing.enforcement import count_active_projects, count_active_workers, get_effective_plan
from app.billing.plans import PLAN_DISPLAY_NAME, get_limits
from app.database import get_db
from app.dependencies import get_org_member
from app.models.organization import OrgMember
from app.models.subscription import Subscription
from app.schemas.billing import PlanUsage, SubscriptionResponse

router = APIRouter(prefix="/organizations/{org_id}/billing", tags=["billing"])


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
