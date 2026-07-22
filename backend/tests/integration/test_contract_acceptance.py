"""Tests del registro de aceptación del Contrato/Términos (gate de primer ingreso)."""
from sqlalchemy import func, select

from app.legal import CONTRACT_VERSION
from app.models.contract_acceptance import ContractAcceptance

API = "/api/v1"


class TestContractAcceptance:
    async def test_nuevo_usuario_no_ha_aceptado(self, hx):
        user = await hx.create_user("nuevo")
        hx.act_as(user)
        r = await hx.client.get(f"{API}/legal/contract-status")
        assert r.status_code == 200, r.text
        body = r.json()
        assert body["current_version"] == CONTRACT_VERSION
        assert body["accepted"] is False

    async def test_aceptar_registra_y_marca_aceptado(self, hx):
        user = await hx.create_user("acepta")
        hx.act_as(user)
        r = await hx.client.post(f"{API}/legal/accept")
        assert r.status_code == 200, r.text
        assert r.json()["accepted"] is True

        r2 = await hx.client.get(f"{API}/legal/contract-status")
        assert r2.json()["accepted"] is True

        # Se guardó la evidencia (versión + timestamp).
        async with hx.session_maker() as s:
            rec = (await s.execute(
                select(ContractAcceptance).where(ContractAcceptance.user_id == user.id)
            )).scalar_one()
        assert rec.contract_version == CONTRACT_VERSION
        assert rec.accepted_at is not None

    async def test_aceptar_es_idempotente(self, hx):
        user = await hx.create_user("idem")
        hx.act_as(user)
        await hx.client.post(f"{API}/legal/accept")
        await hx.client.post(f"{API}/legal/accept")
        async with hx.session_maker() as s:
            n = (await s.execute(
                select(func.count()).select_from(ContractAcceptance)
                .where(ContractAcceptance.user_id == user.id)
            )).scalar_one()
        assert n == 1
