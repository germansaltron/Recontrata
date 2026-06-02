"""Admin/demo endpoints. Secured by X-Admin-Token header matching ADMIN_TOKEN env var."""

import os
import random
import secrets
import uuid
from datetime import date, timedelta

from fastapi import APIRouter, Header, HTTPException
from sqlalchemy import delete, insert, select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.config import settings
from app.models.evaluation import Evaluation
from app.models.organization import Organization
from app.models.project import Project
from app.models.project_worker import ProjectWorker
from app.models.worker import Worker
from app.services.rut_validator import format_rut
from app.services.score_calculator import compute_average

router = APIRouter(prefix="/admin", tags=["admin"])

# Dedicated engine with statement_timeout disabled (Supabase transaction pool
# default is 2s which is too tight for bulk inserts with statement_cache_size=0).
_admin_engine = create_async_engine(
    settings.async_database_url,
    pool_size=2, max_overflow=0, pool_pre_ping=True,
    connect_args={
        "statement_cache_size": 0,
        "prepared_statement_cache_size": 0,
        "server_settings": {"statement_timeout": "0"},
    },
)
_admin_session = async_sessionmaker(_admin_engine, expire_on_commit=False)

FIRST_NAMES = ["José", "Juan", "Luis", "Carlos", "Pedro", "Miguel", "Jorge", "Manuel", "Francisco", "Ricardo", "Héctor", "Raúl", "Sergio", "Diego", "Rodrigo", "Cristián", "Felipe", "Matías", "Sebastián", "Claudio"]
LAST_NAMES = ["González", "Muñoz", "Rojas", "Díaz", "Pérez", "Silva", "Soto", "Contreras", "López", "Morales", "Araya", "Fuentes", "Valenzuela", "Reyes", "Vargas", "Castillo", "Espinoza", "Sepúlveda", "Torres", "Aguilar"]
SPECIALTIES = ["Soldador", "Mecánico", "Eléctrico", "Instrumentista", "Cañerista", "Calderero", "Operador Grúa", "Rigger", "Pintor Industrial", "Andamiero", "Supervisor", "Prevencionista"]
CLIENTS = ["Codelco Andina", "Anglo American Los Bronces", "Minera Escondida"]
LOCATIONS = ["Los Andes, Región de Valparaíso", "Calama, Región de Antofagasta", "Copiapó, Región de Atacama"]
PROJECT_NAMES = ["Mantención Mayor Concentradora", "Ampliación Planta SX-EW", "Shutdown Molino SAG Q1"]
REHIRE_COMMENTS = {
    "yes": ["Excelente desempeño.", "Buen trabajo, cumple plazos.", "Recomendado 100%."],
    "reservations": ["Cumple pero necesita más supervisión.", "Llega atrasado a veces."],
    "no": ["No cumplió estándares de seguridad.", "Mala actitud."],
}


def _compute_dv(body: int) -> str:
    total, mult = 0, 2
    for d in reversed(str(body)):
        total += int(d) * mult
        mult = mult + 1 if mult < 7 else 2
    r = 11 - (total % 11)
    return "0" if r == 11 else ("K" if r == 10 else str(r))


def _gen_rut(seed: int) -> str:
    body = 10_000_000 + (seed * 7919) % 15_000_000
    return format_rut(f"{body}{_compute_dv(body)}")


def _check_admin_token(x_admin_token: str | None) -> None:
    expected = os.getenv("ADMIN_TOKEN", "")
    # Falla cerrado: sin un token fuerte (>=32 chars) configurado, el endpoint
    # destructivo queda inaccesible. Comparación de tiempo constante (anti-timing).
    if len(expected) < 32:
        raise HTTPException(status_code=403, detail="Forbidden")
    if not x_admin_token or not secrets.compare_digest(x_admin_token, expected):
        raise HTTPException(status_code=403, detail="Forbidden")


@router.post("/seed-demo/{org_id}")
async def seed_demo(
    org_id: uuid.UUID,
    wipe: bool = True,
    x_admin_token: str | None = Header(None),
):
    _check_admin_token(x_admin_token)
    rng = random.Random(42)

    async with _admin_session() as db:
        org = (await db.execute(select(Organization).where(Organization.id == org_id))).scalar_one_or_none()
        if not org:
            raise HTTPException(status_code=404, detail="Org not found")

        if wipe:
            await db.execute(delete(Evaluation).where(Evaluation.org_id == org_id))
            await db.execute(delete(ProjectWorker).where(
                ProjectWorker.project_id.in_(select(Project.id).where(Project.org_id == org_id))
            ))
            await db.execute(delete(Project).where(Project.org_id == org_id))
            await db.execute(delete(Worker).where(Worker.org_id == org_id))
            await db.commit()

        # Projects
        statuses_dates = [
            ("active", date.today() - timedelta(days=30), date.today() + timedelta(days=60)),
            ("active", date.today() - timedelta(days=60), date.today() + timedelta(days=30)),
            ("completed", date.today() - timedelta(days=180), date.today() - timedelta(days=30)),
        ]
        project_rows = [
            {
                "org_id": org_id,
                "name": PROJECT_NAMES[i],
                "client_name": CLIENTS[i],
                "location": LOCATIONS[i],
                "start_date": start,
                "end_date": end,
                "status": status,
            }
            for i, (status, start, end) in enumerate(statuses_dates)
        ]
        res = await db.execute(insert(Project).returning(Project.id).values(project_rows))
        project_ids = [r[0] for r in res.all()]
        await db.commit()

        # Workers
        existing = {r[0] for r in (await db.execute(select(Worker.rut).where(Worker.org_id == org_id))).all()}
        worker_rows = []
        for i in range(20):
            rut = _gen_rut(i + 1)
            if rut in existing:
                continue
            worker_rows.append({
                "org_id": org_id, "rut": rut,
                "first_name": rng.choice(FIRST_NAMES),
                "last_name": rng.choice(LAST_NAMES),
                "specialty": rng.choice(SPECIALTIES),
                "phone": f"+569{rng.randint(10000000, 99999999)}",
                "email": None, "is_active": True,
            })
        if worker_rows:
            res = await db.execute(insert(Worker).returning(Worker.id).values(worker_rows))
            worker_ids = [r[0] for r in res.all()]
        else:
            worker_ids = [r[0] for r in (await db.execute(select(Worker.id).where(Worker.org_id == org_id))).all()]
        await db.commit()

        # Assignments
        assignments: dict[uuid.UUID, list[uuid.UUID]] = {}
        assign_rows = []
        for pid in project_ids:
            team = rng.sample(worker_ids, rng.randint(10, min(14, len(worker_ids))))
            assignments[pid] = team
            for wid in team:
                assign_rows.append({"project_id": pid, "worker_id": wid})
        if assign_rows:
            await db.execute(insert(ProjectWorker).values(assign_rows))
            await db.commit()

        # Evaluations
        evals_rows = []
        seen: set[tuple[uuid.UUID, uuid.UUID]] = set()
        while len(evals_rows) < 40:
            pid = rng.choice(project_ids)
            wid = rng.choice(assignments[pid])
            if (pid, wid) in seen:
                continue
            seen.add((pid, wid))
            scores = [rng.choices([1, 2, 3, 4, 5], weights=[2, 5, 20, 40, 33])[0] for _ in range(5)]
            avg = compute_average(*scores)
            if avg >= 4.0:
                rehire = rng.choices(["yes", "reservations"], weights=[85, 15])[0]
            elif avg >= 3.0:
                rehire = rng.choices(["yes", "reservations", "no"], weights=[40, 45, 15])[0]
            else:
                rehire = rng.choices(["reservations", "no"], weights=[30, 70])[0]
            comment = rng.choice(REHIRE_COMMENTS[rehire]) if rng.random() < 0.6 else None
            reason = comment if rehire != "yes" and comment else None
            evals_rows.append({
                "org_id": org_id, "project_id": pid, "worker_id": wid,
                "score_quality": scores[0], "score_safety": scores[1],
                "score_punctuality": scores[2], "score_teamwork": scores[3],
                "score_technical": scores[4], "score_average": avg,
                "would_rehire": rehire, "rehire_reason": reason, "comment": comment,
            })
        await db.execute(insert(Evaluation).values(evals_rows))
        await db.commit()

        return {
            "projects": len(project_ids),
            "workers": len(worker_rows) if worker_rows else len(worker_ids),
            "evaluations": len(evals_rows),
        }
