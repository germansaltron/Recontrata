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


class CheckoutRequest(BaseModel):
    """Plan y período que el cliente quiere contratar. Se validan en el service
    (deben ser self-serve: pro|empresa × monthly|annual)."""

    plan: str
    billing_period: str


class CheckoutResponse(BaseModel):
    """URL de Flow a la que el frontend redirige al usuario para registrar su tarjeta."""

    redirect_url: str
