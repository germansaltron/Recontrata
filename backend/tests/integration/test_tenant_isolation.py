"""Tests de aislamiento multi-tenant + auditoría de PII (Fase 5, apuesta #5).

Garantizan, contra una DB real, que un usuario de la organización A no puede leer
ni escribir datos de la organización B por ningún endpoint, y que el Portal del
Trabajador no filtra PII sensible (identidad del evaluador).

Estos tests son el CI gate de seguridad: si alguien rompe el scoping por org_id,
fallan.
"""
import pytest

API = "/api/v1"


async def _new_org(hx, user, name: str) -> str:
    hx.act_as(user)
    r = await hx.client.post(f"{API}/organizations", json={"name": name})
    assert r.status_code == 201, r.text
    return r.json()["id"]


async def _new_worker(hx, user, org_id: str, rut: str) -> str:
    hx.act_as(user)
    r = await hx.client.post(
        f"{API}/organizations/{org_id}/workers",
        json={"rut": rut, "first_name": "Trab", "last_name": "Demo", "specialty": "Soldador"},
    )
    assert r.status_code == 201, r.text
    return r.json()["id"]


@pytest.fixture
async def two_tenants(hx):
    """Dos orgs con dueños distintos; devuelve datos para probar cruces."""
    user_a = await hx.create_user("alice")
    user_b = await hx.create_user("bob")
    org_a = await _new_org(hx, user_a, "Org A")
    org_b = await _new_org(hx, user_b, "Org B")
    worker_b = await _new_worker(hx, user_b, org_b, "11.111.111-1")
    return {"a": user_a, "b": user_b, "org_a": org_a, "org_b": org_b, "worker_b": worker_b}


class TestReadIsolation:
    @pytest.mark.parametrize("path", [
        "",                       # GET /organizations/{org}
        "/dashboard/stats",
        "/dashboard/top-workers",
        "/workers",
        "/evaluations",
        "/scoring/formula",
        "/calibration",
    ])
    async def test_user_a_cannot_read_org_b(self, hx, two_tenants, path):
        hx.act_as(two_tenants["a"])
        r = await hx.client.get(f"{API}/organizations/{two_tenants['org_b']}{path}")
        assert r.status_code == 403, f"{path} devolvió {r.status_code}: {r.text}"

    async def test_user_a_cannot_read_worker_b_via_own_org(self, hx, two_tenants):
        # IDOR: A es miembro de su org, pero pide un worker de B bajo el path de A -> 404
        hx.act_as(two_tenants["a"])
        r = await hx.client.get(
            f"{API}/organizations/{two_tenants['org_a']}/workers/{two_tenants['worker_b']}"
        )
        assert r.status_code == 404, r.text


class TestWriteIsolation:
    async def test_user_a_cannot_create_worker_in_org_b(self, hx, two_tenants):
        hx.act_as(two_tenants["a"])
        r = await hx.client.post(
            f"{API}/organizations/{two_tenants['org_b']}/workers",
            json={"rut": "22.222.222-2", "first_name": "X", "last_name": "Y", "specialty": "Soldador"},
        )
        assert r.status_code == 403, r.text

    async def test_user_a_cannot_change_org_b_industry(self, hx, two_tenants):
        hx.act_as(two_tenants["a"])
        r = await hx.client.patch(
            f"{API}/organizations/{two_tenants['org_b']}", json={"industry": "logistica"}
        )
        assert r.status_code == 403, r.text

    async def test_user_a_cannot_generate_portal_link_for_worker_b(self, hx, two_tenants):
        hx.act_as(two_tenants["a"])
        r = await hx.client.post(
            f"{API}/organizations/{two_tenants['org_b']}/workers/{two_tenants['worker_b']}/portal-link"
        )
        assert r.status_code == 403, r.text

    async def test_user_a_cannot_evaluate_worker_from_org_b(self, hx, two_tenants):
        # Evaluar en la PROPIA org (A) pero apuntando a un worker de B debe dar 404:
        # de lo contrario se crearía una evaluación cruzada que ensucia el portal del
        # worker de B. (Aislamiento en la creación de evaluaciones — hallazgo M2.)
        hx.act_as(two_tenants["a"])
        proj_a = (await hx.client.post(
            f"{API}/organizations/{two_tenants['org_a']}/projects", json={"name": "Obra A"}
        )).json()["id"]
        r = await hx.client.post(
            f"{API}/organizations/{two_tenants['org_a']}/evaluations",
            json={"project_id": proj_a, "worker_id": two_tenants["worker_b"],
                  "score_quality": 4, "score_safety": 5, "score_punctuality": 3,
                  "score_teamwork": 4, "score_technical": 4, "would_rehire": "yes"},
        )
        assert r.status_code == 404, r.text

    async def test_user_a_cannot_evaluate_into_project_from_org_b(self, hx, two_tenants):
        # Worker válido de A pero project de B: también 404.
        worker_a = await _new_worker(hx, two_tenants["a"], two_tenants["org_a"], "11.111.111-1")
        hx.act_as(two_tenants["b"])
        proj_b = (await hx.client.post(
            f"{API}/organizations/{two_tenants['org_b']}/projects", json={"name": "Obra B"}
        )).json()["id"]
        hx.act_as(two_tenants["a"])
        r = await hx.client.post(
            f"{API}/organizations/{two_tenants['org_a']}/evaluations",
            json={"project_id": proj_b, "worker_id": worker_a,
                  "score_quality": 4, "score_safety": 5, "score_punctuality": 3,
                  "score_teamwork": 4, "score_technical": 4, "would_rehire": "yes"},
        )
        assert r.status_code == 404, r.text


class TestPositiveControl:
    """El harness no falla por bloquear todo: el dueño SÍ accede a su org."""

    async def test_owner_can_read_own_org(self, hx, two_tenants):
        hx.act_as(two_tenants["b"])
        r = await hx.client.get(f"{API}/organizations/{two_tenants['org_b']}/dashboard/stats")
        assert r.status_code == 200, r.text

    async def test_non_member_gets_403_not_500(self, hx, two_tenants):
        hx.act_as(two_tenants["a"])
        r = await hx.client.get(f"{API}/organizations/{two_tenants['org_b']}/workers")
        assert r.status_code == 403


class TestPortalPII:
    async def _setup_worker_with_eval(self, hx, user, org_id):
        worker = await _new_worker(hx, user, org_id, "9.876.543-3")
        hx.act_as(user)
        proj = (await hx.client.post(f"{API}/organizations/{org_id}/projects", json={"name": "Obra"})).json()["id"]
        await hx.client.post(
            f"{API}/organizations/{org_id}/evaluations",
            json={"project_id": proj, "worker_id": worker, "score_quality": 4, "score_safety": 5,
                  "score_punctuality": 3, "score_teamwork": 4, "score_technical": 4,
                  "would_rehire": "yes"},
        )
        link = (await hx.client.post(f"{API}/organizations/{org_id}/workers/{worker}/portal-link")).json()
        return worker, link["token"]

    async def test_portal_hides_evaluator_identity(self, hx, two_tenants):
        _, token = await self._setup_worker_with_eval(hx, two_tenants["b"], two_tenants["org_b"])
        # El portal es público (sin auth); no debe exponer al evaluador.
        hx.act_as(None)
        r = await hx.client.get(f"{API}/portal/{token}")
        assert r.status_code == 200, r.text
        body = r.json()
        assert body["evaluations"], "debería haber al menos una evaluación"
        ev = body["evaluations"][0]
        assert "evaluator_name" not in ev
        assert "evaluator_id" not in ev
        # Sí ve sus puntajes y el motivo (transparencia), pero no quién lo evaluó.
        assert "score_weighted" in ev

    async def test_portal_only_returns_own_worker(self, hx, two_tenants):
        worker, token = await self._setup_worker_with_eval(hx, two_tenants["b"], two_tenants["org_b"])
        hx.act_as(None)
        r = await hx.client.get(f"{API}/portal/{token}")
        assert r.json()["rut"] == "9.876.543-3"

    async def test_invalid_portal_token_404(self, hx, two_tenants):
        hx.act_as(None)
        r = await hx.client.get(f"{API}/portal/token-inexistente-xyz")
        assert r.status_code == 404
