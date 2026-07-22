"""Tests del checkout de suscripciones (Fase 5) con un cliente Flow simulado.

Cubre el flujo completo sin llamar a Flow: iniciar checkout (registro de tarjeta),
retorno desde Flow (creación de la suscripción) y cancelación.
"""
import pytest
from sqlalchemy import select

from app.api.v1.billing import get_flow_client
from app.main import app
from app.models.subscription import Subscription

API = "/api/v1"


class FakeFlow:
    """Cliente de Flow simulado: devuelve respuestas fijas, registra las llamadas."""

    def __init__(self):
        self.calls = []

    async def create_customer(self, name, email, external_id):
        self.calls.append(("create_customer", external_id))
        return {"customerId": "cust_TEST"}

    async def register_card(self, customer_id, url_return):
        self.calls.append(("register_card", customer_id))
        return {"url": "https://sandbox.flow.cl/app/web/register.php", "token": "regtok_TEST"}

    async def get_register_status(self, token):
        self.calls.append(("get_register_status", token))
        return {"customerId": "cust_TEST", "status": "1"}

    async def create_subscription(self, plan_id, customer_id, trial_period_days=None, coupon_id=None):
        self.calls.append(("create_subscription", plan_id))
        return {"subscriptionId": "sub_TEST", "status": "trialing"}

    async def cancel_subscription(self, subscription_id, at_period_end=True):
        self.calls.append(("cancel_subscription", subscription_id))
        return {"status": "canceled"}


@pytest.fixture
def fake_flow(monkeypatch):
    # Plan IDs dummy: el test no debe depender de las env vars FLOW_PLAN_ID_* (que no
    # existen en el CI). El FakeFlow ignora el valor; solo importa que estén definidos.
    from app.config import settings
    monkeypatch.setattr(settings, "FLOW_PLAN_ID_PRO_MONTHLY", "plan-pro-m")
    monkeypatch.setattr(settings, "FLOW_PLAN_ID_PRO_ANNUAL", "plan-pro-a")
    monkeypatch.setattr(settings, "FLOW_PLAN_ID_EMPRESA_MONTHLY", "plan-emp-m")
    monkeypatch.setattr(settings, "FLOW_PLAN_ID_EMPRESA_ANNUAL", "plan-emp-a")
    fake = FakeFlow()
    app.dependency_overrides[get_flow_client] = lambda: fake
    yield fake
    app.dependency_overrides.pop(get_flow_client, None)


async def _new_org(hx, user) -> str:
    hx.act_as(user)
    r = await hx.client.post(f"{API}/organizations", json={"name": "Contratista Test"})
    assert r.status_code == 201, r.text
    return r.json()["id"]


class TestCheckout:
    async def test_flujo_completo_checkout_return_cancel(self, hx, fake_flow):
        user = await hx.create_user("owner")
        org = await _new_org(hx, user)

        # 1) Checkout: inicia el registro de tarjeta y guarda el plan pendiente.
        hx.act_as(user)
        r = await hx.client.post(
            f"{API}/organizations/{org}/billing/checkout",
            json={"plan": "pro", "billing_period": "monthly"},
        )
        assert r.status_code == 200, r.text
        assert "regtok_TEST" in r.json()["redirect_url"]

        async with hx.session_maker() as s:
            sub = (await s.execute(select(Subscription).where(Subscription.org_id == org))).scalar_one()
        assert sub.pending_plan == "pro"
        assert sub.pending_period == "monthly"
        assert sub.flow_customer_id == "cust_TEST"
        assert sub.flow_subscription_id is None  # aún no hay suscripción

        # 2) Retorno de Flow: crea la suscripción (trial). Público, sin auth.
        hx.act_as(None)
        r = await hx.client.get(f"{API}/billing/return", params={"token": "regtok_TEST"})
        assert r.status_code == 303, r.text
        assert "checkout=success" in r.headers["location"]

        async with hx.session_maker() as s:
            sub = (await s.execute(select(Subscription).where(Subscription.org_id == org))).scalar_one()
        assert sub.plan == "pro"
        assert sub.status == "trialing"
        assert sub.flow_subscription_id == "sub_TEST"
        assert sub.trial_ends_at is not None
        assert sub.pending_plan is None  # se limpió

        # 3) Cancelar: queda canceled.
        hx.act_as(user)
        r = await hx.client.post(f"{API}/organizations/{org}/billing/cancel")
        assert r.status_code == 200, r.text

        async with hx.session_maker() as s:
            sub = (await s.execute(select(Subscription).where(Subscription.org_id == org))).scalar_one()
        assert sub.status == "canceled"
        assert sub.canceled_at is not None

    async def test_plan_invalido_da_400(self, hx, fake_flow):
        user = await hx.create_user("owner2")
        org = await _new_org(hx, user)
        hx.act_as(user)
        r = await hx.client.post(
            f"{API}/organizations/{org}/billing/checkout",
            json={"plan": "enterprise", "billing_period": "monthly"},
        )
        assert r.status_code == 400, r.text

    async def test_retorno_token_desconocido_redirige_a_error(self, hx, fake_flow):
        # get_register_status del fake devuelve cust_TEST, pero no hay suscripción con ese
        # customer si no hubo checkout previo → error controlado (redirige a error).
        hx.act_as(None)
        r = await hx.client.get(f"{API}/billing/return", params={"token": "cualquiera"})
        assert r.status_code == 303
        assert "checkout=error" in r.headers["location"]
