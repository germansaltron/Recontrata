"""Tests de integración del webhook de WhatsApp: recepción punta a punta con DB real.

Lo que se prueba aquí y no se puede probar sin DB: la idempotencia por `wamid` (el
índice unique es el árbitro) y que una firma inválida no deje rastro.
"""

import json

import pytest
from sqlalchemy import func, select

from app.config import settings
from app.models.bot import BotInboundEvent
from tests.test_bot_webhook import APP_SECRET, sign, wa_payload

VERIFY_TOKEN = "recontrata-verify-test"


@pytest.fixture
def meta_env(monkeypatch):
    monkeypatch.setattr(settings, "META_APP_SECRET", APP_SECRET)
    monkeypatch.setattr(settings, "WHATSAPP_VERIFY_TOKEN", VERIFY_TOKEN)
    monkeypatch.setattr(settings, "BLOCKED_NUMBERS", "[]")
    monkeypatch.setattr(settings, "BOT_ENABLED", False)


async def _count_events(hx) -> int:
    async with hx.session_maker() as s:
        return (await s.execute(select(func.count()).select_from(BotInboundEvent))).scalar_one()


async def _post(hx, payload: dict, *, secret: str = APP_SECRET):
    body = json.dumps(payload).encode()
    return await hx.client.post(
        "/api/v1/whatsapp/webhook",
        content=body,
        headers={"X-Hub-Signature-256": sign(body, secret), "Content-Type": "application/json"},
    )


class TestVerificacionURL:
    async def test_token_correcto_devuelve_el_challenge(self, hx, meta_env):
        r = await hx.client.get(
            "/api/v1/whatsapp/webhook",
            params={"hub.mode": "subscribe", "hub.verify_token": VERIFY_TOKEN, "hub.challenge": "1234"},
        )
        assert r.status_code == 200
        assert r.text == "1234"

    async def test_token_incorrecto_403(self, hx, meta_env):
        r = await hx.client.get(
            "/api/v1/whatsapp/webhook",
            params={"hub.mode": "subscribe", "hub.verify_token": "malo", "hub.challenge": "1234"},
        )
        assert r.status_code == 403

    async def test_sin_token_configurado_403(self, hx, meta_env, monkeypatch):
        monkeypatch.setattr(settings, "WHATSAPP_VERIFY_TOKEN", "")
        r = await hx.client.get(
            "/api/v1/whatsapp/webhook",
            params={"hub.mode": "subscribe", "hub.verify_token": "", "hub.challenge": "1234"},
        )
        assert r.status_code == 403


class TestRecepcion:
    async def test_firma_valida_audita_el_mensaje(self, hx, meta_env):
        r = await _post(hx, wa_payload())
        assert r.status_code == 200
        assert await _count_events(hx) == 1

        async with hx.session_maker() as s:
            ev = (await s.execute(select(BotInboundEvent))).scalar_one()
        assert ev.wamid == "wamid.TEST1"
        assert ev.phone == "56912345678"
        assert ev.signature_valid is True

    async def test_firma_invalida_no_procesa_nada(self, hx, meta_env):
        """Responde 200 igual (no le damos señal a quien sondea) pero no guarda nada."""
        r = await _post(hx, wa_payload(), secret="secreto_del_atacante")
        assert r.status_code == 200
        assert await _count_events(hx) == 0

    async def test_sin_firma_no_procesa_nada(self, hx, meta_env):
        r = await hx.client.post("/api/v1/whatsapp/webhook", json=wa_payload())
        assert r.status_code == 200
        assert await _count_events(hx) == 0

    async def test_wamid_repetido_se_procesa_una_sola_vez(self, hx, meta_env):
        """El reintento de Meta es el caso real: mismo mensaje, dos entregas."""
        p = wa_payload(wamid="wamid.REINTENTO")
        r1 = await _post(hx, p)
        r2 = await _post(hx, p)
        assert r1.status_code == 200 and r2.status_code == 200
        assert await _count_events(hx) == 1

    async def test_mensajes_distintos_se_procesan_ambos(self, hx, meta_env):
        await _post(hx, wa_payload(wamid="wamid.A"))
        await _post(hx, wa_payload(wamid="wamid.B"))
        assert await _count_events(hx) == 2

    async def test_numero_bloqueado_se_ignora(self, hx, meta_env, monkeypatch):
        monkeypatch.setattr(settings, "BLOCKED_NUMBERS", '["56999999999"]')
        r = await _post(hx, wa_payload(phone="56999999999"))
        assert r.status_code == 200
        assert await _count_events(hx) == 0

    async def test_json_invalido_responde_200(self, hx, meta_env):
        """Nunca 5xx: Meta degrada la entrega si el endpoint parece caído."""
        body = b"esto no es json"
        r = await hx.client.post(
            "/api/v1/whatsapp/webhook",
            content=body,
            headers={"X-Hub-Signature-256": sign(body), "Content-Type": "application/json"},
        )
        assert r.status_code == 200
        assert await _count_events(hx) == 0

    async def test_evento_de_estado_no_crea_registro(self, hx, meta_env):
        payload = {"entry": [{"changes": [{"value": {"statuses": [{"id": "wamid.X", "status": "read"}]}}]}]}
        r = await _post(hx, payload)
        assert r.status_code == 200
        assert await _count_events(hx) == 0
