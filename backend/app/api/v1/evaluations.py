import uuid
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.dependencies import get_current_user, get_org_member
from app.errors import ErrorCode
from app.models.evaluation import Evaluation
from app.models.evaluation_audit import EvaluationAuditLog
from app.models.organization import Organization, OrgMember
from app.models.project import Project
from app.models.user import User
from app.models.worker import Worker
from app.schemas.evaluation import (
    EvaluationAuditEntry,
    EvaluationBatchCreate,
    EvaluationCreate,
    EvaluationResponse,
    EvaluationUpdate,
    validate_rehire_reason,
)
from app.schemas.pagination import PaginatedResponse
from app.services.evaluation_audit import record_evaluation_audit
from app.services.score_calculator import DEFAULT_INDUSTRY, compute_average, compute_weighted

router = APIRouter(prefix="/organizations/{org_id}/evaluations", tags=["evaluations"])


async def _get_org_industry(org_id: uuid.UUID, db: AsyncSession) -> str:
    """Industria de la org, que determina el perfil de pesos del puntaje."""
    result = await db.execute(select(Organization.industry).where(Organization.id == org_id))
    return result.scalar_one_or_none() or DEFAULT_INDUSTRY

# Campos editables que, al cambiar, cuentan como una nueva versión.
_EDITABLE_FIELDS = (
    "score_quality", "score_safety", "score_punctuality", "score_teamwork",
    "score_technical", "would_rehire", "rehire_reason", "comment",
)


async def _build_response(ev: Evaluation, db: AsyncSession) -> EvaluationResponse:
    proj = await db.execute(select(Project.name).where(Project.id == ev.project_id))
    project_name = proj.scalar_one_or_none() or ""

    w = await db.execute(select(Worker.first_name, Worker.last_name).where(Worker.id == ev.worker_id))
    row = w.one_or_none()
    worker_name = f"{row[0]} {row[1]}" if row else ""

    evaluator_name = None
    if ev.evaluator_id:
        u = await db.execute(select(User.full_name).where(User.id == ev.evaluator_id))
        evaluator_name = u.scalar_one_or_none()

    return EvaluationResponse(
        id=ev.id, project_id=ev.project_id, project_name=project_name,
        worker_id=ev.worker_id, worker_name=worker_name, evaluator_name=evaluator_name,
        score_quality=ev.score_quality, score_safety=ev.score_safety,
        score_punctuality=ev.score_punctuality, score_teamwork=ev.score_teamwork,
        score_technical=ev.score_technical, score_average=ev.score_average,
        score_weighted=ev.score_weighted,
        would_rehire=ev.would_rehire, rehire_reason=ev.rehire_reason,
        comment=ev.comment, created_at=ev.created_at,
    )


async def _create_single(org_id: uuid.UUID, body: EvaluationCreate, evaluator: User, db: AsyncSession) -> Evaluation:
    # Aislamiento multi-tenant: el proyecto y el trabajador DEBEN pertenecer a esta org.
    # Sin esto, un miembro de la org A podría crear una evaluación referenciando el
    # worker/project de la org B (los IDs vienen del body). Mismo patrón de validación
    # que ya usa assign_workers. Se valida antes del duplicate check para fallar rápido.
    proj_ok = await db.execute(
        select(Project.id).where(Project.id == body.project_id, Project.org_id == org_id)
    )
    if proj_ok.scalar_one_or_none() is None:
        raise HTTPException(status_code=404, detail={"detail": "Proyecto no encontrado", "code": ErrorCode.PROJECT_NOT_FOUND})

    worker_ok = await db.execute(
        select(Worker.id).where(Worker.id == body.worker_id, Worker.org_id == org_id)
    )
    if worker_ok.scalar_one_or_none() is None:
        raise HTTPException(status_code=404, detail={"detail": "Trabajador no encontrado", "code": ErrorCode.WORKER_NOT_FOUND})

    # Check duplicate (ignora evaluaciones borradas: se puede re-evaluar tras un soft-delete)
    existing = await db.execute(
        select(Evaluation).where(
            Evaluation.project_id == body.project_id,
            Evaluation.worker_id == body.worker_id,
            Evaluation.deleted_at.is_(None),
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail={"detail": "Ya existe una evaluacion para este trabajador en este proyecto", "code": ErrorCode.EVALUATION_DUPLICATE})

    dims = (body.score_quality, body.score_safety, body.score_punctuality, body.score_teamwork, body.score_technical)
    avg = compute_average(*dims)
    industry = await _get_org_industry(org_id, db)
    weighted = compute_weighted(*dims, industry=industry)

    ev = Evaluation(
        org_id=org_id,
        project_id=body.project_id,
        worker_id=body.worker_id,
        evaluator_id=evaluator.id,
        score_quality=body.score_quality,
        score_safety=body.score_safety,
        score_punctuality=body.score_punctuality,
        score_teamwork=body.score_teamwork,
        score_technical=body.score_technical,
        score_average=avg,
        score_weighted=weighted,
        would_rehire=body.would_rehire,
        rehire_reason=body.rehire_reason,
        comment=body.comment,
    )
    db.add(ev)
    await db.flush()  # asigna ev.id antes de registrar la auditoría
    record_evaluation_audit(db, ev, "create", evaluator)
    return ev


@router.post("", response_model=EvaluationResponse, status_code=201)
async def create_evaluation(
    org_id: uuid.UUID,
    body: EvaluationCreate,
    db: AsyncSession = Depends(get_db),
    _member: OrgMember = Depends(get_org_member),
    user: User = Depends(get_current_user),
):
    ev = await _create_single(org_id, body, user, db)
    await db.commit()
    await db.refresh(ev)
    return await _build_response(ev, db)


@router.post("/batch", status_code=201)
async def create_evaluations_batch(
    org_id: uuid.UUID,
    body: EvaluationBatchCreate,
    db: AsyncSession = Depends(get_db),
    _member: OrgMember = Depends(get_org_member),
    user: User = Depends(get_current_user),
):
    results = []
    errors = []
    for i, ev_data in enumerate(body.evaluations):
        try:
            ev = await _create_single(org_id, ev_data, user, db)
            results.append(str(ev.id))
        except HTTPException as e:
            errors.append({"index": i, "worker_id": str(ev_data.worker_id), "error": e.detail})

    await db.commit()
    return {"created": len(results), "errors": errors}


@router.get("", response_model=PaginatedResponse[EvaluationResponse])
async def list_evaluations(
    org_id: uuid.UUID,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    project_id: uuid.UUID | None = None,
    worker_id: uuid.UUID | None = None,
    db: AsyncSession = Depends(get_db),
    _member: OrgMember = Depends(get_org_member),
):
    from sqlalchemy import func

    query = select(Evaluation).where(Evaluation.org_id == org_id, Evaluation.deleted_at.is_(None))
    count_query = select(func.count(Evaluation.id)).where(Evaluation.org_id == org_id, Evaluation.deleted_at.is_(None))

    if project_id:
        query = query.where(Evaluation.project_id == project_id)
        count_query = count_query.where(Evaluation.project_id == project_id)
    if worker_id:
        query = query.where(Evaluation.worker_id == worker_id)
        count_query = count_query.where(Evaluation.worker_id == worker_id)

    total = (await db.execute(count_query)).scalar() or 0
    offset = (page - 1) * size
    result = await db.execute(query.order_by(Evaluation.created_at.desc()).offset(offset).limit(size))
    evals = result.scalars().all()

    items = [await _build_response(ev, db) for ev in evals]
    return PaginatedResponse(items=items, total=total, page=page, size=size, pages=(total + size - 1) // size if total else 0)


@router.patch("/{eval_id}", response_model=EvaluationResponse)
async def update_evaluation(
    org_id: uuid.UUID,
    eval_id: uuid.UUID,
    body: EvaluationUpdate,
    db: AsyncSession = Depends(get_db),
    _member: OrgMember = Depends(get_org_member),
    user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Evaluation).where(
            Evaluation.id == eval_id, Evaluation.org_id == org_id, Evaluation.deleted_at.is_(None)
        )
    )
    ev = result.scalar_one_or_none()
    if not ev:
        raise HTTPException(status_code=404, detail={"detail": "Evaluation not found", "code": ErrorCode.EVALUATION_NOT_FOUND})

    # Time-lock (L5): pasada la ventana de edición, la evaluación queda bloqueada.
    window = timedelta(hours=settings.EVALUATION_EDIT_WINDOW_HOURS)
    created_at = ev.created_at
    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=timezone.utc)
    if datetime.now(timezone.utc) - created_at > window:
        raise HTTPException(
            status_code=409,
            detail={
                "detail": f"Esta evaluación ya no puede editarse (la edición se permite hasta {settings.EVALUATION_EDIT_WINDOW_HOURS} horas después de crearla).",
                "code": ErrorCode.EVALUATION_EDIT_WINDOW_EXPIRED,
            },
        )

    changes = body.model_dump(exclude_unset=True)
    changed_fields = [f for f in changes if f in _EDITABLE_FIELDS and getattr(ev, f) != changes[f]]

    for field, value in changes.items():
        setattr(ev, field, value)

    # Regla rehire_reason sobre el estado FINAL (puede depender de campos no enviados).
    validate_rehire_reason(ev.would_rehire, ev.rehire_reason)

    # Recompute average + weighted (con el perfil de industria actual de la org)
    dims = (ev.score_quality, ev.score_safety, ev.score_punctuality, ev.score_teamwork, ev.score_technical)
    ev.score_average = compute_average(*dims)
    ev.score_weighted = compute_weighted(*dims, industry=await _get_org_industry(org_id, db))

    if changed_fields:
        record_evaluation_audit(db, ev, "update", user, changed_fields=changed_fields)

    await db.commit()
    await db.refresh(ev)
    return await _build_response(ev, db)


@router.delete("/{eval_id}", status_code=204)
async def delete_evaluation(
    org_id: uuid.UUID,
    eval_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _member: OrgMember = Depends(get_org_member),
    user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Evaluation).where(
            Evaluation.id == eval_id, Evaluation.org_id == org_id, Evaluation.deleted_at.is_(None)
        )
    )
    ev = result.scalar_one_or_none()
    if not ev:
        raise HTTPException(status_code=404, detail={"detail": "Evaluation not found", "code": ErrorCode.EVALUATION_NOT_FOUND})

    # Soft-delete (L3): conserva la fila y deja rastro en el audit log.
    record_evaluation_audit(db, ev, "delete", user)
    ev.deleted_at = datetime.now(timezone.utc)
    await db.commit()


@router.get("/{eval_id}/history", response_model=list[EvaluationAuditEntry])
async def get_evaluation_history(
    org_id: uuid.UUID,
    eval_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _member: OrgMember = Depends(get_org_member),
):
    """Historial de versiones/acciones de una evaluación (incluye borradas)."""
    result = await db.execute(
        select(EvaluationAuditLog)
        .where(EvaluationAuditLog.evaluation_id == eval_id, EvaluationAuditLog.org_id == org_id)
        .order_by(EvaluationAuditLog.created_at.asc())
    )
    return list(result.scalars().all())
