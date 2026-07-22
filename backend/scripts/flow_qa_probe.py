"""Sonda de QA contra el sandbox de Flow: ejercita el flujo de suscripción y muestra
las RESPUESTAS CRUDAS para confirmar los nombres de campos (customerId, token,
subscriptionId, estado del registro) que checkout.py asume (# QA).

Fase 1 (crea cliente + inicia registro de tarjeta):
    python scripts/flow_qa_probe.py

Luego abre la URL que imprime, registra la tarjeta de PRUEBA, y corre la fase 2:
    python scripts/flow_qa_probe.py --token <TOKEN> --customer <CUSTOMER_ID>
"""
import argparse
import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.billing.flow_client import FlowClient  # noqa: E402
from app.billing.checkout import flow_plan_id  # noqa: E402
from app.billing.plans import BillingPeriod, Plan  # noqa: E402
from app.config import settings  # noqa: E402


def show(label, data):
    print(f"\n=== {label} ===")
    print(json.dumps(data, indent=2, ensure_ascii=False))


async def phase1():
    c = FlowClient()
    print("Flow base:", settings.FLOW_API_BASE)
    cust = await c.create_customer(
        name="QA Saltronic", email="contacto@saltronic.cl", external_id="qa-probe-org"
    )
    show("create_customer (respuesta cruda)", cust)
    customer_id = cust.get("customerId")
    if not customer_id:
        print("\n!! create_customer NO devolvio 'customerId'. Revisa el nombre del campo arriba.")
        return
    reg = await c.register_card(
        customer_id=customer_id,
        url_return=settings.BILLING_RETURN_URL or "https://recontrata.cl/api/v1/billing/return",
    )
    show("register_card (respuesta cruda)", reg)
    url, token = reg.get("url"), reg.get("token")
    print("\n>>> 1) ABRE ESTA URL Y REGISTRA LA TARJETA DE PRUEBA:")
    print(f"    {url}?token={token}")
    print("\n>>> 2) Luego corre la fase 2:")
    print(f"    python scripts/flow_qa_probe.py --token {token} --customer {customer_id}")


async def phase2(token: str, customer_id: str):
    c = FlowClient()
    st = await c.get_register_status(token)
    show("get_register_status (respuesta cruda)", st)
    plan_id = flow_plan_id(Plan.PRO, BillingPeriod.MONTHLY)
    print(f"\nCreando suscripcion con planId={plan_id} ...")
    sub = await c.create_subscription(
        plan_id=plan_id, customer_id=customer_id, trial_period_days=14
    )
    show("create_subscription (respuesta cruda)", sub)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--token")
    ap.add_argument("--customer")
    args = ap.parse_args()
    if args.token and args.customer:
        asyncio.run(phase2(args.token, args.customer))
    else:
        asyncio.run(phase1())
