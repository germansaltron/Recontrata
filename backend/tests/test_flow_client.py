"""Tests unitarios del cliente Flow (firma + construcción de requests).

Sin DB ni HTTP real: la firma se valida contra un vector conocido y las requests se
capturan con un transporte mock de httpx. La firma está calcada del cliente oficial
de Flow (ver app/billing/flow_client.py)."""

import hashlib
import hmac
from urllib.parse import parse_qs

import httpx
import pytest

from app.billing.flow_client import FlowClient, FlowError


def _client(transport=None):
    http = httpx.AsyncClient(transport=transport) if transport else None
    return FlowClient(api_key="K", secret_key="secret", base_url="https://sandbox.flow.cl/api", http_client=http)


def _verify_sig(params: dict, secret: str) -> bool:
    """Recalcula la firma como Flow: sort(keys), concat(key+value) sin 's', HMAC-SHA256."""
    got = params["s"]
    to_sign = "".join(f"{k}{params[k]}" for k in sorted(params) if k != "s")
    expected = hmac.new(secret.encode(), to_sign.encode(), hashlib.sha256).hexdigest()
    return got == expected


class TestSignature:
    def test_known_vector(self):
        # sorted(['a','apiKey','b']) -> 'a1apiKeyKb2', HMAC-SHA256 con 'secret'.
        c = _client()
        sig = c.sign({"apiKey": "K", "b": "2", "a": "1"})
        assert sig == "21f9e7cd6e259f556812aeab0c4f0f687a229ef18db19d9290002ed342a718ee"

    def test_order_independent(self):
        c = _client()
        assert c.sign({"a": "1", "b": "2", "apiKey": "K"}) == c.sign({"b": "2", "apiKey": "K", "a": "1"})

    def test_prepare_adds_apikey_and_valid_signature(self):
        c = _client()
        prepared = c._prepare({"amount": 1000, "subject": "Test"})
        assert prepared["apiKey"] == "K"
        assert prepared["amount"] == "1000"  # numérico → string
        assert _verify_sig(prepared, "secret")

    def test_bool_serialized_as_1_0(self):
        c = _client()
        prepared = c._prepare({"at_period_end": True, "flag": False})
        assert prepared["at_period_end"] == "1"
        assert prepared["flag"] == "0"

    def test_none_values_dropped(self):
        c = _client()
        prepared = c._prepare({"a": "x", "b": None})
        assert "b" not in prepared

    async def test_missing_credentials_raises(self):
        c = FlowClient(api_key="", secret_key="", base_url="https://x")
        with pytest.raises(FlowError):
            await c.get_payment_status("tok")


class TestRequests:
    async def test_get_sends_signed_query(self):
        captured = {}

        def handler(request: httpx.Request) -> httpx.Response:
            captured["url"] = str(request.url)
            captured["params"] = {k: v[0] for k, v in parse_qs(request.url.query.decode()).items()}
            return httpx.Response(200, json={"status": 2, "amount": 5000})

        c = _client(httpx.MockTransport(handler))
        data = await c.get_payment_status("tok123")
        assert data == {"status": 2, "amount": 5000}
        assert captured["url"].startswith("https://sandbox.flow.cl/api/payment/getStatus")
        p = captured["params"]
        assert p["token"] == "tok123" and p["apiKey"] == "K"
        assert _verify_sig(p, "secret")

    async def test_post_sends_signed_form_body(self):
        captured = {}

        def handler(request: httpx.Request) -> httpx.Response:
            captured["ctype"] = request.headers.get("content-type", "")
            captured["params"] = {k: v[0] for k, v in parse_qs(request.content.decode()).items()}
            return httpx.Response(200, json={"customerId": "cus_1"})

        c = _client(httpx.MockTransport(handler))
        data = await c.create_customer(name="Faymex", email="a@b.cl", external_id="org-1")
        assert data == {"customerId": "cus_1"}
        assert "application/x-www-form-urlencoded" in captured["ctype"]
        p = captured["params"]
        assert p["name"] == "Faymex" and p["email"] == "a@b.cl" and p["externalId"] == "org-1"
        assert p["apiKey"] == "K" and _verify_sig(p, "secret")

    async def test_edit_plan_posts_signed_callback(self):
        captured = {}

        def handler(request: httpx.Request) -> httpx.Response:
            captured["url"] = str(request.url)
            captured["params"] = {k: v[0] for k, v in parse_qs(request.content.decode()).items()}
            return httpx.Response(200, json={"planId": "recontrata-pro-monthly", "status": 1})

        c = _client(httpx.MockTransport(handler))
        data = await c.edit_plan("recontrata-pro-monthly", "https://recontrata.cl/api/v1/webhooks/flow")
        assert data["planId"] == "recontrata-pro-monthly"
        assert captured["url"].startswith("https://sandbox.flow.cl/api/plans/edit")
        p = captured["params"]
        assert p["planId"] == "recontrata-pro-monthly"
        assert p["urlCallback"] == "https://recontrata.cl/api/v1/webhooks/flow"
        assert p["apiKey"] == "K" and _verify_sig(p, "secret")

    async def test_get_plan_sends_signed_query(self):
        def handler(request: httpx.Request) -> httpx.Response:
            params = {k: v[0] for k, v in parse_qs(request.url.query.decode()).items()}
            assert params["planId"] == "recontrata-pro-annual" and _verify_sig(params, "secret")
            return httpx.Response(200, json={"planId": "recontrata-pro-annual", "urlCallback": "https://x/cb"})

        c = _client(httpx.MockTransport(handler))
        data = await c.get_plan("recontrata-pro-annual")
        assert data["urlCallback"] == "https://x/cb"

    async def test_http_error_raises_flowerror(self):
        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(400, json={"code": 1201, "message": "apiKey invalido"})

        c = _client(httpx.MockTransport(handler))
        with pytest.raises(FlowError) as exc:
            await c.get_payment_status("tok")
        assert exc.value.code == 1201
        assert "apiKey" in str(exc.value)
