"""Enforcement de límites de plan (el "candado" del freemium).

Conteo de uso facturable y helpers que lanzan HTTP 402 (Payment Required) con un
cuerpo estructurado que el frontend convierte en el paywall. Ver `docs/PASARELA_PAGO_FLOW.md`.

Definiciones facturables:
- "trabajadores activos" = COUNT(DISTINCT worker) de trabajadores is_active asignados
  a proyectos con status='active' en la organización.
- "proyectos activos" = proyectos con status='active' en la organización.
"""

import uuid

from fastapi import HTTPException, status
from sqlalchemy import distinct, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.billing.plans import Plan, PlanLimits, get_limits
from app.errors import ErrorCode
from app.models.project import Project
from app.models.project_worker import ProjectWorker
from app.models.subscription import Subscription
from app.models.worker import Worker

ACTIVE_PROJECT_STATUS = "active"


async def get_effective_plan(db: AsyncSession, org_id: uuid.UUID) -> Plan:
    """Plan efectivo de la organización. Una org sin suscripción se trata como free."""
    from app.billing.plans import ACTIVE_STATUSES, SubscriptionStatus

    result = await db.execute(select(Subscription).where(Subscription.org_id == org_id))
    sub = result.scalar_one_or_none()
    if sub is None:
        return Plan.FREE
    # Fuera de trialing/active se degrada a los límites del free (el historial se
    # conserva, pero el tope efectivo es el gratuito).
    try:
        st = SubscriptionStatus(sub.status)
    except ValueError:
        st = SubscriptionStatus.INCOMPLETE
    if st not in ACTIVE_STATUSES:
        return Plan.FREE
    try:
        return Plan(sub.plan)
    except ValueError:
        return Plan.FREE


async def count_active_workers(db: AsyncSession, org_id: uuid.UUID) -> int:
    """Trabajadores activos (distinct) asignados a proyectos activos de la org."""
    stmt = (
        select(func.count(distinct(ProjectWorker.worker_id)))
        .select_from(ProjectWorker)
        .join(Project, Project.id == ProjectWorker.project_id)
        .join(Worker, Worker.id == ProjectWorker.worker_id)
        .where(
            Project.org_id == org_id,
            Project.status == ACTIVE_PROJECT_STATUS,
            Worker.is_active.is_(True),
        )
    )
    return (await db.execute(stmt)).scalar() or 0


async def count_active_projects(db: AsyncSession, org_id: uuid.UUID) -> int:
    """Proyectos con status='active' en la org."""
    stmt = select(func.count(Project.id)).where(
        Project.org_id == org_id, Project.status == ACTIVE_PROJECT_STATUS
    )
    return (await db.execute(stmt)).scalar() or 0


def _raise_plan_limit(plan: Plan, resource: str, current: int, limit: int) -> None:
    raise HTTPException(
        status_code=status.HTTP_402_PAYMENT_REQUIRED,
        detail={
            "detail": (
                f"Alcanzaste el límite del plan {plan.value} "
                f"({limit} {'trabajadores activos' if resource == 'workers' else 'proyecto(s) activo(s)'}). "
                "Sube de plan para seguir creciendo — tu historial se conserva completo."
            ),
            "code": ErrorCode.PLAN_LIMIT,
            "resource": resource,
            "plan": plan.value,
            "limit": limit,
            "current": current,
        },
    )


async def assert_can_add_active_workers(
    db: AsyncSession, org_id: uuid.UUID, adding: int = 1
) -> None:
    """Verifica que asignar `adding` trabajadores activos nuevos no exceda el plan.

    `adding` = cantidad de trabajadores que quedarían activos y que HOY no lo están
    (ya descontados los duplicados / los ya asignados a un proyecto activo)."""
    if adding <= 0:
        return
    plan = await get_effective_plan(db, org_id)
    limits: PlanLimits = get_limits(plan)
    if limits.max_active_workers is None:
        return
    current = await count_active_workers(db, org_id)
    if current + adding > limits.max_active_workers:
        _raise_plan_limit(plan, "workers", current, limits.max_active_workers)


async def assert_can_add_active_project(db: AsyncSession, org_id: uuid.UUID) -> None:
    """Verifica que crear/activar un proyecto activo más no exceda el plan."""
    plan = await get_effective_plan(db, org_id)
    limits: PlanLimits = get_limits(plan)
    if limits.max_active_projects is None:
        return
    current = await count_active_projects(db, org_id)
    if current + 1 > limits.max_active_projects:
        _raise_plan_limit(plan, "projects", current, limits.max_active_projects)
