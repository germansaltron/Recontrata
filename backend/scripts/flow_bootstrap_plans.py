"""Bootstrap de planes en Flow (Fase 4 de la pasarela).

Crea en Flow los 4 planes de pago (Pro/Empresa × mensual/anual) e imprime los planId
para pegarlos en las variables de entorno de Railway (FLOW_PLAN_ID_*).

Requiere credenciales de Flow en el entorno:
    FLOW_API_KEY, FLOW_API_SECRET, FLOW_API_BASE (sandbox por defecto)

Uso:
    python scripts/flow_bootstrap_plans.py            # crea los planes
    python scripts/flow_bootstrap_plans.py --dry-run  # solo muestra qué crearía

Idempotencia: usa planId determinísticos (recontrata-pro-monthly, etc.). Si un plan ya
existe en Flow, Flow devuelve error y este script lo reporta sin abortar el resto.
"""

import argparse
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.billing.flow_client import FlowClient, FlowError  # noqa: E402
from app.billing.plans import BillingPeriod, Plan, PLAN_PRICES_CLP, TRIAL_PERIOD_DAYS  # noqa: E402
from app.config import settings  # noqa: E402

# interval de Flow: 3 = mensual, 4 = anual.
FLOW_INTERVAL = {BillingPeriod.MONTHLY: 3, BillingPeriod.ANNUAL: 4}

# (plan, período) -> (planId determinístico, nombre visible, variable de entorno destino)
PLAN_DEFS = [
    (Plan.PRO, BillingPeriod.MONTHLY, "recontrata-pro-monthly", "Recontrata Pro (mensual)", "FLOW_PLAN_ID_PRO_MONTHLY"),
    (Plan.PRO, BillingPeriod.ANNUAL, "recontrata-pro-annual", "Recontrata Pro (anual)", "FLOW_PLAN_ID_PRO_ANNUAL"),
    (Plan.EMPRESA, BillingPeriod.MONTHLY, "recontrata-empresa-monthly", "Recontrata Empresa (mensual)", "FLOW_PLAN_ID_EMPRESA_MONTHLY"),
    (Plan.EMPRESA, BillingPeriod.ANNUAL, "recontrata-empresa-annual", "Recontrata Empresa (anual)", "FLOW_PLAN_ID_EMPRESA_ANNUAL"),
]


async def main(dry_run: bool) -> None:
    print(f"Flow base URL: {settings.FLOW_API_BASE}")
    if not settings.FLOW_API_KEY or not settings.FLOW_API_SECRET:
        print("ERROR: faltan FLOW_API_KEY / FLOW_API_SECRET en el entorno.")
        sys.exit(1)

    client = FlowClient()
    print("\nPega estos valores en Railway:\n")
    for plan, period, plan_id, name, env_var in PLAN_DEFS:
        amount = PLAN_PRICES_CLP[(plan, period)]
        interval = FLOW_INTERVAL[period]
        # El trial (14d) solo aplica al plan Pro (self-serve con prueba).
        trial = TRIAL_PERIOD_DAYS if plan == Plan.PRO else 0
        if dry_run:
            print(f"  [dry-run] {env_var}={plan_id}  (amount={amount} CLP, interval={interval}, trial={trial})")
            continue
        try:
            resp = await client.create_plan(
                plan_id=plan_id, name=name, amount=amount, currency="CLP",
                interval=interval, trial_period_days=trial,
                url_callback=settings.FLOW_WEBHOOK_URL or None,
            )
            created_id = resp.get("planId", plan_id)
            print(f"  {env_var}={created_id}")
        except FlowError as e:
            print(f"  {env_var}: ERROR al crear ({e}). Si ya existe, reutiliza planId={plan_id}.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Crea los planes de Recontrata en Flow.")
    parser.add_argument("--dry-run", action="store_true", help="No llama a Flow; solo muestra qué crearía.")
    args = parser.parse_args()
    asyncio.run(main(args.dry_run))
