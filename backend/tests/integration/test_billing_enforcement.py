"""Tests del enforcement de límites de plan (Fase 1-2 de la pasarela).

Contra una DB real, verifican el "candado" del freemium:
- toda org nace en el plan free,
- el free topa en 1 proyecto activo y 15 trabajadores activos (402 PLAN_LIMIT),
- proyectos no-activos y trabajadores en proyectos no-activos no cuentan,
- subir a pro levanta los topes,
- una suscripción fuera de trialing/active degrada a los límites del free,
- el endpoint de suscripción reporta el uso correcto.
"""
from sqlalchemy import update

from app.models.subscription import Subscription

API = "/api/v1"


def _dv(body: int) -> str:
    """Dígito verificador de un RUT chileno (módulo 11)."""
    s, m = 0, 2
    for d in reversed(str(body)):
        s += int(d) * m
        m = 2 if m == 7 else m + 1
    r = 11 - (s % 11)
    return "0" if r == 11 else "K" if r == 10 else str(r)


def _rut(n: int) -> str:
    body = 20_000_000 + n
    return f"{body}-{_dv(body)}"


async def _org(hx, name="Constructora Plan"):
    user = await hx.create_user("supervisor")
    hx.act_as(user)
    org = (await hx.client.post(f"{API}/organizations", json={"name": name})).json()["id"]
    return user, org


async def _project(hx, org, name, status="active"):
    return (
        await hx.client.post(f"{API}/organizations/{org}/projects", json={"name": name, "status": status})
    ).json()["id"]


async def _make_workers(hx, org, n, start=0):
    ids = []
    for i in range(start, start + n):
        r = await hx.client.post(
            f"{API}/organizations/{org}/workers",
            json={"rut": _rut(i), "first_name": f"Trab{i}", "last_name": "Prueba", "specialty": "Soldador"},
        )
        assert r.status_code == 201, r.text
        ids.append(r.json()["id"])
    return ids


async def _set_plan(hx, org, plan, status="active"):
    async with hx.session_maker() as s:
        await s.execute(update(Subscription).where(Subscription.org_id == org).values(plan=plan, status=status))
        await s.commit()


class TestSubscriptionDefaults:
    async def test_new_org_is_free_active(self, hx):
        _, org = await _org(hx)
        r = await hx.client.get(f"{API}/organizations/{org}/billing/subscription")
        assert r.status_code == 200, r.text
        body = r.json()
        assert body["plan"] == "free"
        assert body["status"] == "active"
        assert body["usage"]["active_workers_limit"] == 15
        assert body["usage"]["active_projects_limit"] == 1


class TestProjectLimits:
    async def test_free_allows_one_active_project_blocks_second(self, hx):
        _, org = await _org(hx)
        await _project(hx, org, "Faena A")  # 1er activo: ok
        r = await hx.client.post(f"{API}/organizations/{org}/projects", json={"name": "Faena B", "status": "active"})
        assert r.status_code == 402, r.text
        assert r.json()["detail"]["code"] == "PLAN_LIMIT"
        assert r.json()["detail"]["resource"] == "projects"

    async def test_planning_project_does_not_count(self, hx):
        _, org = await _org(hx)
        await _project(hx, org, "Faena A")  # activo
        # Un proyecto en 'planning' no cuenta contra el tope de proyectos activos.
        r = await hx.client.post(f"{API}/organizations/{org}/projects", json={"name": "Futura", "status": "planning"})
        assert r.status_code == 201, r.text

    async def test_reactivating_second_project_blocked(self, hx):
        _, org = await _org(hx)
        await _project(hx, org, "Faena A")  # 1er activo
        planning = await _project(hx, org, "Futura", status="planning")  # no cuenta aún
        # Activar el segundo (planning → active) excede el tope de 1 proyecto activo.
        r = await hx.client.patch(f"{API}/organizations/{org}/projects/{planning}", json={"status": "active"})
        assert r.status_code == 402, r.text
        assert r.json()["detail"]["resource"] == "projects"

    async def test_reactivation_bypass_of_worker_limit_blocked(self, hx):
        """No se puede saltar el tope asignando en 'planning' y luego activando."""
        _, org = await _org(hx)
        # Único proyecto, creado en planning; le asignamos 16 trabajadores (sin tope, no está activo).
        proj = await _project(hx, org, "Faena A", status="planning")
        workers = await _make_workers(hx, org, 16)
        ok = await hx.client.post(f"{API}/organizations/{org}/projects/{proj}/workers", json={"worker_ids": workers})
        assert ok.status_code == 201 and ok.json()["added"] == 16, ok.text
        # Al activarlo, sus 16 trabajadores pasarían a activos → excede el free (15).
        r = await hx.client.patch(f"{API}/organizations/{org}/projects/{proj}", json={"status": "active"})
        assert r.status_code == 402, r.text
        assert r.json()["detail"]["resource"] == "workers"


class TestWorkerLimits:
    async def test_free_blocks_16th_active_worker(self, hx):
        _, org = await _org(hx)
        proj = await _project(hx, org, "Faena A")
        workers = await _make_workers(hx, org, 16)
        ok = await hx.client.post(
            f"{API}/organizations/{org}/projects/{proj}/workers", json={"worker_ids": workers[:15]}
        )
        assert ok.status_code == 201 and ok.json()["added"] == 15, ok.text
        blocked = await hx.client.post(
            f"{API}/organizations/{org}/projects/{proj}/workers", json={"worker_ids": [workers[15]]}
        )
        assert blocked.status_code == 402, blocked.text
        assert blocked.json()["detail"]["code"] == "PLAN_LIMIT"
        assert blocked.json()["detail"]["limit"] == 15

    async def test_batch_that_would_exceed_is_all_or_nothing(self, hx):
        _, org = await _org(hx)
        proj = await _project(hx, org, "Faena A")
        workers = await _make_workers(hx, org, 16)
        # Asignar 16 de una → excede; no debe asignar ninguno (todo o nada).
        r = await hx.client.post(
            f"{API}/organizations/{org}/projects/{proj}/workers", json={"worker_ids": workers}
        )
        assert r.status_code == 402, r.text
        usage = (await hx.client.get(f"{API}/organizations/{org}/billing/subscription")).json()["usage"]
        assert usage["active_workers"] == 0

    async def test_workers_in_inactive_project_do_not_count(self, hx):
        _, org = await _org(hx)
        # Proyecto 'completed' + su asignación no cuenta como activo.
        done = await _project(hx, org, "Faena Cerrada", status="completed")
        workers = await _make_workers(hx, org, 20)
        r = await hx.client.post(
            f"{API}/organizations/{org}/projects/{done}/workers", json={"worker_ids": workers}
        )
        assert r.status_code == 201, r.text  # no toca el tope porque el proyecto no está activo
        usage = (await hx.client.get(f"{API}/organizations/{org}/billing/subscription")).json()["usage"]
        assert usage["active_workers"] == 0

    async def test_pro_plan_raises_worker_limit(self, hx):
        _, org = await _org(hx)
        proj = await _project(hx, org, "Faena A")
        workers = await _make_workers(hx, org, 16)
        await _set_plan(hx, org, "pro")
        r = await hx.client.post(
            f"{API}/organizations/{org}/projects/{proj}/workers", json={"worker_ids": workers}
        )
        assert r.status_code == 201 and r.json()["added"] == 16, r.text
        usage = (await hx.client.get(f"{API}/organizations/{org}/billing/subscription")).json()["usage"]
        assert usage["active_workers"] == 16
        assert usage["active_workers_limit"] == 100


class TestDegradation:
    async def test_past_due_pro_degrades_to_free_limits(self, hx):
        _, org = await _org(hx)
        await _project(hx, org, "Faena A")
        # Pro pero en past_due → límites efectivos = free.
        await _set_plan(hx, org, "pro", status="past_due")
        r = await hx.client.get(f"{API}/organizations/{org}/billing/subscription")
        assert r.json()["usage"]["active_workers_limit"] == 15
        # Y el tope de proyectos activos vuelve a 1.
        blocked = await hx.client.post(
            f"{API}/organizations/{org}/projects", json={"name": "Faena B", "status": "active"}
        )
        assert blocked.status_code == 402, blocked.text
