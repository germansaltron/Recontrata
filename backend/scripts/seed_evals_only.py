"""Seed only evaluations for an org that already has projects and workers."""

import asyncio
import random
import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import insert, select

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.config import settings

# Dedicated engine with statement_timeout disabled (Supabase transaction pool
# enforces ~8s by default which hangs with statement_cache_size=0).
_engine = create_async_engine(
    settings.async_database_url,
    pool_size=3,
    max_overflow=0,
    connect_args={
        "statement_cache_size": 0,
        "prepared_statement_cache_size": 0,
        "server_settings": {"statement_timeout": "0"},
    },
)
async_session = async_sessionmaker(_engine, expire_on_commit=False)
engine = _engine
from app.models.evaluation import Evaluation
from app.models.organization import Organization
from app.models.project import Project
from app.models.project_worker import ProjectWorker
from app.models.worker import Worker
from app.services.score_calculator import DEFAULT_INDUSTRY, compute_average, compute_weighted

REHIRE_COMMENTS = {
    "yes": ["Excelente desempeno.", "Buen trabajo, cumple plazos.", "Recomendado 100%."],
    "reservations": ["Cumple pero necesita mas supervision.", "Llega atrasado a veces."],
    "no": ["No cumplio estandares de seguridad.", "Mala actitud con el equipo."],
}


async def main(slug: str):
    rng = random.Random(42)
    async with async_session() as s:
        org = (await s.execute(select(Organization).where(Organization.slug == slug))).scalar_one()
        print(f"ORG: {org.id}")

        pws = (await s.execute(
            select(ProjectWorker.project_id, ProjectWorker.worker_id)
            .join(Project, Project.id == ProjectWorker.project_id)
            .where(Project.org_id == org.id)
        )).all()
        print(f"Assignments: {len(pws)}")
        assignments_by_proj: dict[uuid.UUID, list[uuid.UUID]] = {}
        for pid, wid in pws:
            assignments_by_proj.setdefault(pid, []).append(wid)

        project_ids = list(assignments_by_proj.keys())
        rows = []
        seen = set()
        target = 40
        while len(rows) < target:
            pid = rng.choice(project_ids)
            wid = rng.choice(assignments_by_proj[pid])
            if (pid, wid) in seen:
                continue
            seen.add((pid, wid))
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
            rows.append({
                "org_id": org.id,
                "project_id": pid,
                "worker_id": wid,
                "score_quality": scores[0], "score_safety": scores[1],
                "score_punctuality": scores[2], "score_teamwork": scores[3],
                "score_technical": scores[4], "score_average": avg, "score_weighted": weighted,
                "would_rehire": rehire, "rehire_reason": reason, "comment": comment,
            })
        print(f"Generated {len(rows)} rows")

        for i, r in enumerate(rows):
            await s.execute(insert(Evaluation).values([r]))
            await s.commit()
            if (i + 1) % 10 == 0:
                print(f"  inserted {i+1}/{len(rows)}", flush=True)

    await engine.dispose()
    print("DONE")


if __name__ == "__main__":
    asyncio.run(main(sys.argv[1]))
