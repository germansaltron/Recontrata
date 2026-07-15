"""Tests del webhook de Flow + máquina de estados de la suscripción (Fase 3 C).

Contra DB real, con el cliente Flow stub-eado (sin HTTP). Verifican:
- pago aprobado (status 2) → suscripción `active` + período seteado,
- idempotencia por token (reintento del webhook no re-aplica),
- pago rechazado/anulado (3/4) → `past_due`,
- resolución de la suscripción por `subscriptionId` y por `commerceOrder=org_id`,
- fallo al verificar con Flow → 503 (para que Flow reintente),
- normalización del payload (unit).
"""
import uuid

from sqlalchemy import func, select, update

from app.api.v1.webhooks import get_flow_client
from app.billing.flow_client import FlowError
from app.billing.service import normalize_payment_status
from app.main import app
from app.models.subscription import PaymentEvent, Subscription

API = "/api/v1"


class StubFlow:
    def __init__(self, payload=None, raise_error=False):
        self.payload = payload or {}
        self.raise_error = raise_error
        self.calls = 0

    async def get_payment_status(self, token):
        self.calls += 1
        if self.raise_error:
            raise FlowError("boom")
        return dict(self.payload, token=token)


def _use_stub(stub):
    app.dependency_overrides[get_flow_client] = lambda: stub


async def _org_with_sub(hx, *, plan="pro", status="trialing", period="monthly", flow_sub=None):
    user = await hx.create_user("owner")
    hx.act_as(user)
    org = (await hx.client.post(f"{API}/organizations", json={"name": "Sub Co"})).json()["id"]
    async with hx.session_maker() as s:
        await s.execute(
            update(Subscription)
            .where(Subscription.org_id == uuid.UUID(org))
            .values(plan=plan, status=status, billing_period=period, flow_subscription_id=flow_sub)
        )
        await s.commit()
    return org


async def _get_sub(hx, org):
    async with hx.session_maker() as s:
        return (await s.execute(select(Subscription).where(Subscription.org_id == uuid.UUID(org)))).scalar_one()


async def _count_events(hx, org):
    async with hx.session_maker() as s:
        return (await s.execute(
            select(func.count(PaymentEvent.id)).where(PaymentEvent.org_id == uuid.UUID(org))
        )).scalar()


class TestWebhookPaid:
    async def test_paid_activates_and_sets_period(self, hx):
        org = await _org_with_sub(hx, status="trialing", flow_sub="fs1")
        _use_stub(StubFlow({"status": 2, "amount": 49990, "subscriptionId": "fs1", "flowOrder": 12345}))
        hx.act_as(None)  # webhook es público

        r = await hx.client.post(f"{API}/webhooks/flow", data={"token": "tok_paid"})
        assert r.status_code == 200, r.text

        sub = await _get_sub(hx, org)
        assert sub.status == "active"
        assert sub.current_period_start is not None and sub.current_period_end is not None
        assert sub.current_period_end > sub.current_period_start
        assert await _count_events(hx, org) == 1

    async def test_idempotent_on_repeated_token(self, hx):
        org = await _org_with_sub(hx, status="trialing", flow_sub="fs1")
        _use_stub(StubFlow({"status": 2, "amount": 49990, "subscriptionId": "fs1"}))
        hx.act_as(None)

        for _ in range(3):
            r = await hx.client.post(f"{API}/webhooks/flow", data={"token": "same_tok"})
            assert r.status_code == 200
        # Un solo evento pese a los 3 reintentos.
        assert await _count_events(hx, org) == 1

    async def test_resolve_by_commerce_order(self, hx):
        org = await _org_with_sub(hx, status="trialing", flow_sub=None)
        # Sin subscriptionId: se resuelve por commerceOrder = org_id (como en el checkout).
        _use_stub(StubFlow({"status": 2, "amount": 49990, "commerceOrder": org}))
        hx.act_as(None)

        r = await hx.client.post(f"{API}/webhooks/flow", data={"token": "tok_co"})
        assert r.status_code == 200, r.text
        assert (await _get_sub(hx, org)).status == "active"


class TestWebhookFailedAndErrors:
    async def test_rejected_sets_past_due(self, hx):
        org = await _org_with_sub(hx, status="active", flow_sub="fs2")
        _use_stub(StubFlow({"status": 3, "amount": 49990, "subscriptionId": "fs2"}))
        hx.act_as(None)

        r = await hx.client.post(f"{API}/webhooks/flow", data={"token": "tok_rej"})
        assert r.status_code == 200, r.text
        assert (await _get_sub(hx, org)).status == "past_due"

    async def test_verify_failure_returns_503(self, hx):
        await _org_with_sub(hx, flow_sub="fs3")
        _use_stub(StubFlow(raise_error=True))
        hx.act_as(None)

        r = await hx.client.post(f"{API}/webhooks/flow", data={"token": "tok_err"})
        assert r.status_code == 503, r.text


class TestNormalization:
    def test_maps_fields_and_coerces_types(self):
        res = normalize_payment_status("tok", {"status": "2", "amount": "49990.0", "flowOrder": 987, "commerceOrder": "org-x"})
        assert res.flow_status == 2 and res.is_paid
        assert res.amount == 49990
        assert res.flow_order == "987"
        assert res.commerce_order == "org-x"

    def test_reads_nested_subscription_id(self):
        res = normalize_payment_status("tok", {"status": 2, "subscriptionData": {"subscriptionId": "fs-nested"}})
        assert res.subscription_id_flow == "fs-nested"

    def test_bad_status_defaults_pending(self):
        res = normalize_payment_status("tok", {"amount": 1000})
        assert res.flow_status == 1 and not res.is_paid
