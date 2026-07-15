"""Catálogo de planes de FaenaScore.

Fuente de verdad de límites y precios. Vive en código (no en la DB) porque cambia
por release, no por dato. Ver `docs/PASARELA_PAGO_FLOW.md`.

Eje de cobro: "trabajadores activos" = trabajadores activos (is_active) asignados a
proyectos con status='active', contados distinto. Supervisores e historial: ilimitados
en todos los planes.
"""

from enum import Enum


class Plan(str, Enum):
    FREE = "free"
    PRO = "pro"
    EMPRESA = "empresa"
    ENTERPRISE = "enterprise"


class BillingPeriod(str, Enum):
    MONTHLY = "monthly"
    ANNUAL = "annual"


class SubscriptionStatus(str, Enum):
    TRIALING = "trialing"
    ACTIVE = "active"
    PAST_DUE = "past_due"
    CANCELED = "canceled"
    INCOMPLETE = "incomplete"


# Estados que otorgan acceso al nivel del plan pagado (fuera de estos → se degrada a free).
ACTIVE_STATUSES = frozenset({SubscriptionStatus.TRIALING, SubscriptionStatus.ACTIVE})


class PlanLimits:
    """Límites de un plan. `None` = ilimitado."""

    def __init__(self, max_active_workers: int | None, max_active_projects: int | None):
        self.max_active_workers = max_active_workers
        self.max_active_projects = max_active_projects


# Límites por plan.
PLAN_LIMITS: dict[Plan, PlanLimits] = {
    Plan.FREE: PlanLimits(max_active_workers=15, max_active_projects=1),
    Plan.PRO: PlanLimits(max_active_workers=100, max_active_projects=None),
    Plan.EMPRESA: PlanLimits(max_active_workers=500, max_active_projects=None),
    Plan.ENTERPRISE: PlanLimits(max_active_workers=None, max_active_projects=None),
}

# Nombre comercial para UI.
PLAN_DISPLAY_NAME: dict[Plan, str] = {
    Plan.FREE: 'Gratis "Capataz"',
    Plan.PRO: 'Pro "Faena"',
    Plan.EMPRESA: 'Empresa "Contratista"',
    Plan.ENTERPRISE: "Enterprise",
}

# Trial (días) al suscribirse a un plan de pago self-serve.
TRIAL_PERIOD_DAYS = 14

# Precios en CLP (referencia y bootstrap de planes en Flow). El plan free no cobra;
# Enterprise es a cotización (fuera de self-serve).
PLAN_PRICES_CLP: dict[tuple[Plan, BillingPeriod], int] = {
    (Plan.PRO, BillingPeriod.MONTHLY): 49_990,
    (Plan.PRO, BillingPeriod.ANNUAL): 499_900,
    (Plan.EMPRESA, BillingPeriod.MONTHLY): 149_990,
    (Plan.EMPRESA, BillingPeriod.ANNUAL): 1_499_900,
}

# Planes que se pueden contratar self-serve (los que pasan por Flow).
SELF_SERVE_PLANS = frozenset({Plan.PRO, Plan.EMPRESA})


def get_limits(plan: str | Plan) -> PlanLimits:
    """Devuelve los límites de un plan; cae en FREE si el valor es desconocido."""
    try:
        return PLAN_LIMITS[Plan(plan)]
    except ValueError:
        return PLAN_LIMITS[Plan.FREE]
