from datetime import datetime

from pydantic import BaseModel


class PlanUsage(BaseModel):
    """Uso facturable actual vs. el tope del plan. `*_limit` = null → ilimitado."""

    active_workers: int
    active_workers_limit: int | None
    active_projects: int
    active_projects_limit: int | None


class SubscriptionResponse(BaseModel):
    plan: str
    plan_display_name: str
    billing_period: str | None
    status: str
    trial_ends_at: datetime | None
    current_period_end: datetime | None
    canceled_at: datetime | None
    usage: PlanUsage
