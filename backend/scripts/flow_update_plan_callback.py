"""Actualiza la urlCallback de los 4 planes de Flow (fix del webhook de renovaciones).

Contexto: cuando se corrió el bootstrap de producción, FLOW_WEBHOOK_URL no estaba en el
entorno, así que los planes de Flow quedaron sin URL de notificación. Sin ella, Flow no
avisa a la app cuando cobra la renovación (a los 14 días del trial). Este script fija la
urlCallback en cada plan.

⚠️ Restricción de Flow: si un plan YA tiene suscriptores, plans/edit solo permite modificar
trial_period_days; la urlCallback queda de solo lectura. Por eso hay que correr esto ANTES
de la primera suscripción real.

Requiere credenciales de Flow y el webhook en el entorno:
    FLOW_API_KEY, FLOW_API_SECRET, FLOW_API_BASE, FLOW_WEBHOOK_URL

Uso:
    python scripts/flow_update_plan_callback.py            # actualiza los 4 planes
    python scripts/flow_update_plan_callback.py --dry-run  # solo muestra qué haría
    python scripts/flow_update_plan_callback.py --verify   # solo lee y muestra la urlCallback actual
"""

import argparse
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.billing.flow_client import FlowClient, FlowError  # noqa: E402
from app.config import settings  # noqa: E402

# Los mismos planId determinísticos del bootstrap (Pro/Empresa × mensual/anual).
PLAN_IDS = [
    "recontrata-pro-monthly",
    "recontrata-pro-annual",
    "recontrata-empresa-monthly",
    "recontrata-empresa-annual",
]


async def main(dry_run: bool, verify_only: bool) -> None:
    print(f"Flow base URL: {settings.FLOW_API_BASE}")
    if not settings.FLOW_API_KEY or not settings.FLOW_API_SECRET:
        print("ERROR: faltan FLOW_API_KEY / FLOW_API_SECRET en el entorno.")
        sys.exit(1)

    client = FlowClient()

    if verify_only:
        print("\nurlCallback actual de cada plan:\n")
        for plan_id in PLAN_IDS:
            try:
                resp = await client.get_plan(plan_id)
                print(f"  {plan_id}: urlCallback={resp.get('urlCallback')!r}  status={resp.get('status')}")
            except FlowError as e:
                print(f"  {plan_id}: ERROR al consultar ({e}).")
        return

    callback = settings.FLOW_WEBHOOK_URL
    if not callback:
        print("ERROR: falta FLOW_WEBHOOK_URL en el entorno (la URL que se va a fijar).")
        sys.exit(1)
    print(f"urlCallback a fijar: {callback}\n")

    for plan_id in PLAN_IDS:
        if dry_run:
            print(f"  [dry-run] plans/edit {plan_id} → urlCallback={callback}")
            continue
        try:
            await client.edit_plan(plan_id, callback)
            # Re-consulta para confirmar que quedó aplicada (no confiar en el 200 a secas).
            resp = await client.get_plan(plan_id)
            got = resp.get("urlCallback")
            ok = "OK" if got == callback else f"⚠️ quedó {got!r}"
            print(f"  {plan_id}: {ok}")
        except FlowError as e:
            hint = ""
            if "subscrib" in str(e).lower() or "suscri" in str(e).lower():
                hint = "  (¿el plan ya tiene suscriptores? entonces urlCallback es de solo lectura)"
            print(f"  {plan_id}: ERROR ({e}).{hint}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fija la urlCallback en los planes de Recontrata en Flow.")
    parser.add_argument("--dry-run", action="store_true", help="No llama a Flow; solo muestra qué haría.")
    parser.add_argument("--verify", action="store_true", help="Solo lee y muestra la urlCallback actual de cada plan.")
    args = parser.parse_args()
    asyncio.run(main(args.dry_run, args.verify))
