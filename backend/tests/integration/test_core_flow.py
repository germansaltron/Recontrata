"""Tests de flujo central del producto (QA de lanzamiento).

Verifican, contra una DB real, las reglas de negocio de mayor riesgo reputacional
que no cubren los demás tests de integración:

- Flujo feliz completo: org -> proyecto -> trabajador -> evaluación.
- Cálculo del puntaje ponderado vía API (coincide con la fórmula por industria).
- Prevención de evaluación duplicada (409).
- Ventana de edición: editar una evaluación vencida da 409.
- Soft-delete permite re-evaluar el mismo par proyecto-trabajador.
- RUT duplicado en la misma org da 409.
- Portal del trabajador: derecho a réplica y opt-out (revocación de consentimiento).
"""
from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import update

from app.models.evaluation import Evaluation

API = "/api/v1"


async def _bootstrap(hx):
    """Crea un usuario, su org, un proyecto y un trabajador. Devuelve ids."""
    user = await hx.create_user("supervisor")
    hx.act_as(user)
    org = (await hx.client.post(f"{API}/organizations", json={"name": "Constructora QA"})).json()["id"]
    proj = (await hx.client.post(
        f"{API}/organizations/{org}/projects", json={"name": "Obra Norte"}
    )).json()["id"]
    worker = (await hx.client.post(
        f"{API}/organizations/{org}/workers",
        json={"rut": "12.345.678-5", "first_name": "Juan", "last_name": "Pérez", "specialty": "Soldador"},
    )).json()["id"]
    return {"user": user, "org": org, "proj": proj, "worker": worker}


async def _evaluate(hx, org, proj, worker, **scores):
    payload = {
        "project_id": proj, "worker_id": worker,
        "score_quality": 4, "score_safety": 5, "score_punctuality": 3,
        "score_teamwork": 4, "score_technical": 4, "would_rehire": "yes",
    }
    payload.update(scores)
    return await hx.client.post(f"{API}/organizations/{org}/evaluations", json=payload)


class TestHappyPath:
    async def test_full_flow_and_weighted_score(self, hx):
        ctx = await _bootstrap(hx)
        r = await _evaluate(hx, ctx["org"], ctx["proj"], ctx["worker"])
        assert r.status_code == 201, r.text
        body = r.json()
        # Promedio simple: (4+5+3+4+4)/5 = 4.0
        assert body["score_average"] == 4.0
        # Ponderado minería (default): 4*.25 + 5*.30 + 3*.10 + 4*.15 + 4*.20
        #                            = 1.0 + 1.5 + 0.3 + 0.6 + 0.8 = 4.2
        assert body["score_weighted"] == 4.2

    async def test_weighted_changes_with_industry(self, hx):
        ctx = await _bootstrap(hx)
        # Cambiar a 'general' (todos 0.20) => ponderado == promedio simple.
        await hx.client.patch(f"{API}/organizations/{ctx['org']}", json={"industry": "general"})
        r = await _evaluate(hx, ctx["org"], ctx["proj"], ctx["worker"])
        assert r.json()["score_weighted"] == 4.0


class TestBusinessRules:
    async def test_duplicate_evaluation_rejected(self, hx):
        ctx = await _bootstrap(hx)
        assert (await _evaluate(hx, ctx["org"], ctx["proj"], ctx["worker"])).status_code == 201
        dup = await _evaluate(hx, ctx["org"], ctx["proj"], ctx["worker"])
        assert dup.status_code == 409, dup.text

    async def test_rehire_no_requires_reason(self, hx):
        ctx = await _bootstrap(hx)
        r = await _evaluate(hx, ctx["org"], ctx["proj"], ctx["worker"], would_rehire="no")
        assert r.status_code == 422, r.text  # falta rehire_reason

    async def test_duplicate_rut_rejected(self, hx):
        ctx = await _bootstrap(hx)
        r = await hx.client.post(
            f"{API}/organizations/{ctx['org']}/workers",
            json={"rut": "12.345.678-5", "first_name": "Otro", "last_name": "Igual", "specialty": "Mecánico"},
        )
        assert r.status_code == 409, r.text

    async def test_edit_window_expired(self, hx):
        ctx = await _bootstrap(hx)
        eval_id = (await _evaluate(hx, ctx["org"], ctx["proj"], ctx["worker"])).json()["id"]
        # Retroceder created_at 100h (ventana = 72h) para simular una evaluación vieja.
        async with hx.session_maker() as s:
            await s.execute(
                update(Evaluation).where(Evaluation.id == eval_id).values(
                    created_at=datetime.now(timezone.utc) - timedelta(hours=100)
                )
            )
            await s.commit()
        r = await hx.client.patch(
            f"{API}/organizations/{ctx['org']}/evaluations/{eval_id}", json={"score_quality": 1}
        )
        assert r.status_code == 409, r.text

    async def test_soft_delete_allows_reevaluation(self, hx):
        ctx = await _bootstrap(hx)
        eval_id = (await _evaluate(hx, ctx["org"], ctx["proj"], ctx["worker"])).json()["id"]
        # Borrar (soft-delete) y volver a evaluar el mismo par debe permitirse.
        d = await hx.client.delete(f"{API}/organizations/{ctx['org']}/evaluations/{eval_id}")
        assert d.status_code == 204, d.text
        again = await _evaluate(hx, ctx["org"], ctx["proj"], ctx["worker"])
        assert again.status_code == 201, again.text


class TestWorkerPortalRights:
    async def _setup_portal(self, hx):
        ctx = await _bootstrap(hx)
        eval_id = (await _evaluate(hx, ctx["org"], ctx["proj"], ctx["worker"])).json()["id"]
        token = (await hx.client.post(
            f"{API}/organizations/{ctx['org']}/workers/{ctx['worker']}/portal-link"
        )).json()["token"]
        return ctx, eval_id, token

    async def test_worker_can_reply_to_evaluation(self, hx):
        ctx, eval_id, token = await self._setup_portal(hx)
        hx.act_as(None)  # portal es público
        r = await hx.client.post(
            f"{API}/portal/{token}/evaluations/{eval_id}/reply",
            json={"reply": "No estoy de acuerdo con la nota de puntualidad."},
        )
        assert r.status_code == 200, r.text
        assert r.json()["worker_reply"] == "No estoy de acuerdo con la nota de puntualidad."
        assert r.json()["worker_reply_at"] is not None

    async def test_worker_opt_out_revokes_consent(self, hx):
        ctx, eval_id, token = await self._setup_portal(hx)
        hx.act_as(None)
        r = await hx.client.post(f"{API}/portal/{token}/opt-out", json={"notes": None})
        assert r.status_code == 204, r.text
        # El supervisor ve el consentimiento revocado.
        hx.act_as(ctx["user"])
        c = await hx.client.get(
            f"{API}/organizations/{ctx['org']}/workers/{ctx['worker']}/consent"
        )
        assert c.json()["status"] == "revoked"

    async def test_reply_to_other_workers_eval_404(self, hx):
        ctx, eval_id, token = await self._setup_portal(hx)
        hx.act_as(None)
        r = await hx.client.post(
            f"{API}/portal/{token}/evaluations/00000000-0000-0000-0000-000000000000/reply",
            json={"reply": "intento de réplica ajena"},
        )
        assert r.status_code == 404, r.text
