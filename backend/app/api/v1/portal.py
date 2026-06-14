"""Portal del Trabajador (Fase 5).

Endpoints PÚBLICOS por token: NO usan Clerk ni pertenencia a organización. El
trabajador accede con un enlace privado e impredecible que le comparte el
contratista. Da transparencia (art. 16 Ley 21.719), derecho a réplica y opt-out.
"""
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.errors import ErrorCode
from app.models.evaluation import Evaluation
from app.models.organization import Organization
from app.models.project import Project
from app.models.worker import Worker
from app.models.worker_consent import WorkerConsent
from app.schemas.portal import (
    PortalEvaluation,
    PortalOptOutRequest,
    PortalProfile,
    PortalReplyRequest,
    PortalTrendPoint,
)
from app.api.v1.scoring import _build_profile
from app.services.score_calculator import DEFAULT_INDUSTRY, WEIGHT_PROFILES

router = APIRouter(prefix="/portal", tags=["portal"])


async def _get_worker_by_token(token: str, db: AsyncSession) -> Worker:
    result = await db.execute(select(Worker).where(Worker.portal_token == token))
    worker = result.scalar_one_or_none()
    if not worker:
        raise HTTPException(
            status_code=404,
            detail={"detail": "Enlace no válido o expirado", "code": ErrorCode.WORKER_NOT_FOUND},
        )
    return worker


@router.get("/{token}", response_model=PortalProfile)
async def get_portal(token: str, db: AsyncSession = Depends(get_db)):
    worker = await _get_worker_by_token(token, db)

    org = (await db.execute(
        select(Organization.name, Organization.industry).where(Organization.id == worker.org_id)
    )).one_or_none()
    org_name = org[0] if org else ""
    industry = (org[1] if org else DEFAULT_INDUSTRY) or DEFAULT_INDUSTRY
    if industry not in WEIGHT_PROFILES:
        industry = DEFAULT_INDUSTRY

    eval_rows = (await db.execute(
        select(Evaluation, Project.name, Project.end_date)
        .join(Project, Evaluation.project_id == Project.id)
        .where(Evaluation.worker_id == worker.id, Evaluation.deleted_at.is_(None))
        .order_by(Evaluation.created_at.desc())
    )).all()

    evaluations: list[PortalEvaluation] = []
    trend: list[PortalTrendPoint] = []
    rehire_yes = rehire_res = rehire_no = 0
    weighted_sum = 0.0

    for ev, proj_name, proj_end in eval_rows:
        evaluations.append(PortalEvaluation(
            id=ev.id, project_name=proj_name,
            score_quality=ev.score_quality, score_safety=ev.score_safety,
            score_punctuality=ev.score_punctuality, score_teamwork=ev.score_teamwork,
            score_technical=ev.score_technical, score_average=ev.score_average,
            score_weighted=ev.score_weighted,
            would_rehire=ev.would_rehire, rehire_reason=ev.rehire_reason, comment=ev.comment,
            worker_reply=ev.worker_reply, worker_reply_at=ev.worker_reply_at,
            created_at=ev.created_at,
        ))
        trend.append(PortalTrendPoint(project_name=proj_name, date=proj_end, score_weighted=ev.score_weighted))
        weighted_sum += ev.score_weighted
        if ev.would_rehire == "yes":
            rehire_yes += 1
        elif ev.would_rehire == "reservations":
            rehire_res += 1
        else:
            rehire_no += 1

    n = len(eval_rows)
    avg_score = round(weighted_sum / n, 2) if n else None
    trend.reverse()

    consent_status = (await db.execute(
        select(WorkerConsent.status).where(WorkerConsent.worker_id == worker.id)
    )).scalar_one_or_none() or "pending"

    return PortalProfile(
        worker_name=f"{worker.first_name} {worker.last_name}",
        rut=worker.rut, specialty=worker.specialty, org_name=org_name,
        evaluation_count=n, avg_score=avg_score, consent_status=consent_status,
        rehire_yes=rehire_yes, rehire_reservations=rehire_res, rehire_no=rehire_no,
        formula=_build_profile(industry), score_trend=trend, evaluations=evaluations,
    )


@router.post("/{token}/evaluations/{eval_id}/reply", response_model=PortalEvaluation)
async def reply_to_evaluation(
    token: str, eval_id: str, body: PortalReplyRequest, db: AsyncSession = Depends(get_db)
):
    """Derecho a réplica: el trabajador responde a una evaluación suya."""
    worker = await _get_worker_by_token(token, db)
    result = await db.execute(
        select(Evaluation).where(
            Evaluation.id == eval_id,
            Evaluation.worker_id == worker.id,
            Evaluation.deleted_at.is_(None),
        )
    )
    ev = result.scalar_one_or_none()
    if not ev:
        raise HTTPException(
            status_code=404,
            detail={"detail": "Evaluación no encontrada", "code": ErrorCode.EVALUATION_NOT_FOUND},
        )

    ev.worker_reply = body.reply.strip()
    ev.worker_reply_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(ev)

    proj_name = (await db.execute(
        select(Project.name).where(Project.id == ev.project_id)
    )).scalar_one_or_none() or ""

    return PortalEvaluation(
        id=ev.id, project_name=proj_name,
        score_quality=ev.score_quality, score_safety=ev.score_safety,
        score_punctuality=ev.score_punctuality, score_teamwork=ev.score_teamwork,
        score_technical=ev.score_technical, score_average=ev.score_average,
        score_weighted=ev.score_weighted,
        would_rehire=ev.would_rehire, rehire_reason=ev.rehire_reason, comment=ev.comment,
        worker_reply=ev.worker_reply, worker_reply_at=ev.worker_reply_at,
        created_at=ev.created_at,
    )


@router.post("/{token}/opt-out", status_code=204)
async def opt_out(token: str, body: PortalOptOutRequest, db: AsyncSession = Depends(get_db)):
    """El trabajador solicita dejar de ser evaluado: marca su consentimiento como revocado."""
    worker = await _get_worker_by_token(token, db)
    result = await db.execute(select(WorkerConsent).where(WorkerConsent.worker_id == worker.id))
    consent = result.scalar_one_or_none()
    now = datetime.now(timezone.utc)
    notes = (body.notes or "").strip() or "Baja solicitada por el trabajador desde el portal."

    if consent:
        consent.status = "revoked"
        consent.method = "platform"
        consent.consent_date = now
        consent.notes = notes
    else:
        consent = WorkerConsent(
            worker_id=worker.id, org_id=worker.org_id, status="revoked",
            method="platform", consent_date=now, notes=notes,
        )
        db.add(consent)
    await db.commit()
