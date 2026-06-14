"""Seed demo data for a given organization.

Usage:
    python -m scripts.seed_demo --org-id <UUID>
    python -m scripts.seed_demo --org-slug my-org
    python -m scripts.seed_demo --org-slug my-org --wipe

Creates 3 projects, 20 workers, ~40 evaluations with realistic Chilean data.
Skips duplicates based on RUT + project name.
"""

from __future__ import annotations

import argparse
import asyncio
import random
import sys
import uuid
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import delete, insert, select, text


async def _relax_timeout(session) -> None:
    await session.execute(text("SET LOCAL statement_timeout = '60s'"))

from app.database import async_session, engine
from app.models.evaluation import Evaluation
from app.models.organization import Organization
from app.models.project import Project
from app.models.project_worker import ProjectWorker
from app.models.worker import Worker
from app.services.rut_validator import format_rut
from app.services.score_calculator import DEFAULT_INDUSTRY, compute_average, compute_weighted

FIRST_NAMES = [
    "José", "Juan", "Luis", "Carlos", "Pedro", "Miguel", "Jorge", "Manuel",
    "Francisco", "Ricardo", "Héctor", "Raúl", "Sergio", "Diego", "Rodrigo",
    "Cristián", "Felipe", "Matías", "Sebastián", "Claudio",
]
LAST_NAMES = [
    "González", "Muñoz", "Rojas", "Díaz", "Pérez", "Silva", "Soto", "Contreras",
    "López", "Morales", "Araya", "Fuentes", "Valenzuela", "Reyes", "Vargas",
    "Castillo", "Espinoza", "Sepúlveda", "Torres", "Aguilar", "Alarcón",
    "Herrera", "Pizarro", "Navarro", "Carrasco",
]
SPECIALTIES = [
    "Soldador", "Mecánico", "Eléctrico", "Instrumentista", "Cañerista",
    "Calderero", "Operador Grúa", "Rigger", "Pintor Industrial", "Andamiero",
    "Supervisor", "Prevencionista",
]
CLIENTS = [
    "Codelco Andina", "Anglo American Los Bronces", "Minera Escondida",
    "Colbún S.A.", "Enel Generación", "Collahuasi",
]
LOCATIONS = [
    "Los Andes, Región de Valparaíso", "Calama, Región de Antofagasta",
    "Copiapó, Región de Atacama", "Rancagua, Región de O'Higgins",
    "Iquique, Región de Tarapacá", "Puchuncaví, Región de Valparaíso",
]
PROJECT_NAMES = [
    "Mantención Mayor Concentradora", "Ampliación Planta SX-EW",
    "Shutdown Molino SAG Q1", "Instalación Nueva Correa Overland",
    "Detención Programada Chancador Primario", "Overhaul Horno Flash",
]
REHIRE_COMMENTS = {
    "yes": [
        "Excelente desempeño, muy profesional.", "Buen trabajo, cumple plazos.",
        "Recomendado 100%, muy responsable.", "Trabajo impecable, sin observaciones.",
    ],
    "reservations": [
        "Cumple pero necesita mas supervision.", "Llega atrasado a veces.",
        "Buen tecnico pero problemas con el equipo.",
    ],
    "no": [
        "No cumplio estandares de seguridad.", "Mala actitud con el equipo.",
        "Calidad insuficiente para la faena.",
    ],
}


def compute_dv(body: int) -> str:
    total = 0
    multiplier = 2
    for digit in reversed(str(body)):
        total += int(digit) * multiplier
        multiplier = multiplier + 1 if multiplier < 7 else 2
    remainder = 11 - (total % 11)
    if remainder == 11:
        return "0"
    if remainder == 10:
        return "K"
    return str(remainder)


def generate_rut(seed: int) -> str:
    body = 10_000_000 + (seed * 7919) % 15_000_000
    return format_rut(f"{body}{compute_dv(body)}")


async def resolve_org(session, args) -> Organization:
    if args.org_id:
        org = await session.get(Organization, uuid.UUID(args.org_id))
    else:
        stmt = select(Organization).where(Organization.slug == args.org_slug)
        org = (await session.execute(stmt)).scalar_one_or_none()
    if not org:
        raise SystemExit(f"Organization not found: {args.org_id or args.org_slug}")
    return org


async def wipe_org_data(session, org_id: uuid.UUID) -> None:
    # FK cascade handles children; delete projects and workers directly.
    await session.execute(delete(Evaluation).where(Evaluation.org_id == org_id))
    await session.execute(delete(ProjectWorker).where(
        ProjectWorker.project_id.in_(select(Project.id).where(Project.org_id == org_id))
    ))
    await session.execute(delete(Project).where(Project.org_id == org_id))
    await session.execute(delete(Worker).where(Worker.org_id == org_id))
    await session.commit()


async def seed(org: Organization, wipe: bool) -> dict:
    rng = random.Random(42)

    # 1) Wipe in its own small transaction
    if wipe:
        async with async_session() as session:
            await _relax_timeout(session)
            await wipe_org_data(session, org.id)

    # 2) Bulk insert projects (returning ids via RETURNING)
    statuses_dates = [
        ("active", date.today() - timedelta(days=30), date.today() + timedelta(days=60)),
        ("active", date.today() - timedelta(days=60), date.today() + timedelta(days=30)),
        ("completed", date.today() - timedelta(days=180), date.today() - timedelta(days=30)),
    ]
    project_rows = [
        {
            "org_id": org.id,
            "name": PROJECT_NAMES[i],
            "client_name": CLIENTS[i % len(CLIENTS)],
            "location": LOCATIONS[i % len(LOCATIONS)],
            "start_date": start,
            "end_date": end,
            "status": status,
        }
        for i, (status, start, end) in enumerate(statuses_dates)
    ]
    async with async_session() as session:
        await _relax_timeout(session)
        res = await session.execute(insert(Project).returning(Project.id).values(project_rows))
        project_ids = [row[0] for row in res.all()]
        await session.commit()

    # 3) Bulk insert workers
    existing_ruts: set[str] = set()
    async with async_session() as session:
        await _relax_timeout(session)
        rows = (await session.execute(select(Worker.rut).where(Worker.org_id == org.id))).all()
        existing_ruts = {r[0] for r in rows}

    worker_rows = []
    for i in range(20):
        rut = generate_rut(i + 1)
        if rut in existing_ruts:
            continue
        worker_rows.append({
            "org_id": org.id,
            "rut": rut,
            "first_name": rng.choice(FIRST_NAMES),
            "last_name": rng.choice(LAST_NAMES),
            "specialty": rng.choice(SPECIALTIES),
            "phone": f"+569{rng.randint(10000000, 99999999)}",
            "email": None,
            "is_active": True,
        })

    async with async_session() as session:
        await _relax_timeout(session)
        worker_ids: list[uuid.UUID] = []
        # One row at a time to avoid statement timeouts on pooler
        for row in worker_rows:
            res = await session.execute(insert(Worker).returning(Worker.id).values([row]))
            worker_ids.extend(r[0] for r in res.all())
            await session.commit()
        if not worker_rows:
            rows = (await session.execute(select(Worker.id).where(Worker.org_id == org.id))).all()
            worker_ids = [r[0] for r in rows]

    # 4) Bulk assignments
    assignments: dict[uuid.UUID, list[uuid.UUID]] = {}
    assign_rows = []
    for pid in project_ids:
        count = rng.randint(10, min(14, len(worker_ids)))
        team = rng.sample(worker_ids, count)
        assignments[pid] = team
        for wid in team:
            assign_rows.append({"project_id": pid, "worker_id": wid})
    async with async_session() as session:
        await _relax_timeout(session)
        for i in range(0, len(assign_rows), 10):
            chunk = assign_rows[i:i + 10]
            await session.execute(insert(ProjectWorker).values(chunk))
            await session.commit()

    # 5) Bulk evaluations
    evals_rows = []
    seen: set[tuple[uuid.UUID, uuid.UUID]] = set()
    target = 40
    while len(evals_rows) < target:
        pid = rng.choice(project_ids)
        team = assignments[pid]
        wid = rng.choice(team)
        key = (pid, wid)
        if key in seen:
            continue
        seen.add(key)
        scores = [rng.choices([1, 2, 3, 4, 5], weights=[2, 5, 20, 40, 33])[0] for _ in range(5)]
        avg = compute_average(*scores)
        weighted = compute_weighted(*scores, industry=DEFAULT_INDUSTRY)
        if avg >= 4.0:
            rehire = rng.choices(["yes", "reservations"], weights=[85, 15])[0]
        elif avg >= 3.0:
            rehire = rng.choices(["yes", "reservations", "no"], weights=[40, 45, 15])[0]
        else:
            rehire = rng.choices(["reservations", "no"], weights=[30, 70])[0]
        comment = rng.choice(REHIRE_COMMENTS[rehire]) if rng.random() < 0.6 else None
        reason = comment if rehire != "yes" and comment else None
        evals_rows.append({
            "org_id": org.id,
            "project_id": pid,
            "worker_id": wid,
            "score_quality": scores[0],
            "score_safety": scores[1],
            "score_punctuality": scores[2],
            "score_teamwork": scores[3],
            "score_technical": scores[4],
            "score_average": avg,
            "score_weighted": weighted,
            "would_rehire": rehire,
            "rehire_reason": reason,
            "comment": comment,
        })

    async with async_session() as session:
        await _relax_timeout(session)
        for i in range(0, len(evals_rows), 10):
            chunk = evals_rows[i:i + 10]
            await session.execute(insert(Evaluation).values(chunk))
            await session.commit()

    return {
        "projects": len(project_ids),
        "workers": len(worker_rows),
        "evaluations": len(evals_rows),
    }


async def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--org-id", help="Organization UUID")
    group.add_argument("--org-slug", help="Organization slug")
    parser.add_argument("--wipe", action="store_true", help="Delete existing projects/workers/evaluations first")
    args = parser.parse_args()

    async with async_session() as session:
        org = await resolve_org(session, args)

    result = await seed(org, args.wipe)
    print(f"Seeded org '{org.name}' ({org.slug}): {result}")
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
