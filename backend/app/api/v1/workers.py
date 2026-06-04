import csv
import io
import uuid

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from fastapi.responses import StreamingResponse
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user, get_org_member
from app.errors import ErrorCode
from app.models.evaluation import Evaluation
from app.models.organization import OrgMember
from app.models.project import Project
from app.models.user import User
from app.models.worker import Worker
from app.models.worker_consent import WorkerConsent
from app.schemas.pagination import PaginatedResponse
from app.schemas.worker_consent import WorkerConsentResponse, WorkerConsentUpsert
from app.schemas.worker import (
    EvaluationSummary,
    RehireStats,
    ScoreBreakdown,
    ScoreTrendPoint,
    WorkerCreate,
    WorkerDetailResponse,
    WorkerImportResult,
    WorkerResponse,
    WorkerUpdate,
)
from app.services.rut_validator import format_rut, validate_rut

router = APIRouter(prefix="/organizations/{org_id}/workers", tags=["workers"])

# Columnas permitidas para ordenar (allowlist contra ORM column injection).
_SORTABLE_COLUMNS = {
    "last_name": Worker.last_name,
    "first_name": Worker.first_name,
    "specialty": Worker.specialty,
    "created_at": Worker.created_at,
}

# Límites de seguridad para el import de Excel.
_MAX_IMPORT_BYTES = 5 * 1024 * 1024  # 5 MB
_MAX_IMPORT_ROWS = 5000
_XLSX_CONTENT_TYPES = {
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/vnd.ms-excel",
    "application/octet-stream",  # algunos navegadores no setean el tipo correcto
}


async def _build_consent_response(worker_id: uuid.UUID, db: AsyncSession) -> WorkerConsentResponse:
    """Devuelve el consentimiento del trabajador, o un estado 'pending' por defecto."""
    result = await db.execute(select(WorkerConsent).where(WorkerConsent.worker_id == worker_id))
    consent = result.scalar_one_or_none()
    if not consent:
        return WorkerConsentResponse(worker_id=worker_id, status="pending")

    recorded_by_name = None
    if consent.recorded_by:
        u = await db.execute(select(User.full_name).where(User.id == consent.recorded_by))
        recorded_by_name = u.scalar_one_or_none()

    return WorkerConsentResponse(
        worker_id=worker_id, status=consent.status, method=consent.method,
        consent_date=consent.consent_date, notes=consent.notes,
        recorded_by_name=recorded_by_name, updated_at=consent.updated_at,
    )


@router.get("", response_model=PaginatedResponse[WorkerResponse])
async def list_workers(
    org_id: uuid.UUID,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    search: str | None = None,
    specialty: str | None = None,
    min_score: float | None = None,
    is_active: bool | None = True,
    sort_by: str = "last_name",
    sort_order: str = "asc",
    db: AsyncSession = Depends(get_db),
    _member: OrgMember = Depends(get_org_member),
):
    eval_count = func.count(Evaluation.id).label("eval_count")
    avg_score = func.avg(Evaluation.score_average).label("avg_score")

    query = (
        select(Worker, eval_count, avg_score)
        .outerjoin(Evaluation, (Evaluation.worker_id == Worker.id) & (Evaluation.deleted_at.is_(None)))
        .where(Worker.org_id == org_id)
        .group_by(Worker.id)
    )

    if is_active is not None:
        query = query.where(Worker.is_active == is_active)
    if specialty:
        query = query.where(Worker.specialty.ilike(f"%{specialty}%"))
    if search:
        query = query.where(
            Worker.first_name.ilike(f"%{search}%")
            | Worker.last_name.ilike(f"%{search}%")
            | Worker.rut.ilike(f"%{search}%")
        )
    if min_score is not None:
        query = query.having(avg_score >= min_score)

    # Count matching rows (honoring min_score via subquery)
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar() or 0

    # Allowlist de columnas ordenables (evita enumerar atributos arbitrarios del modelo).
    sort_col = _SORTABLE_COLUMNS.get(sort_by, Worker.last_name)
    query = query.order_by(sort_col.desc() if sort_order == "desc" else sort_col.asc())

    offset = (page - 1) * size
    rows = (await db.execute(query.offset(offset).limit(size))).all()

    items = [
        WorkerResponse(
            id=w.id, rut=w.rut, first_name=w.first_name, last_name=w.last_name,
            specialty=w.specialty, phone=w.phone, email=w.email, is_active=w.is_active,
            evaluation_count=ec or 0, avg_score=round(avg, 2) if avg is not None else None,
            created_at=w.created_at,
        )
        for w, ec, avg in rows
    ]

    return PaginatedResponse(items=items, total=total, page=page, size=size, pages=(total + size - 1) // size if total else 0)


@router.post("", response_model=WorkerResponse, status_code=201)
async def create_worker(
    org_id: uuid.UUID,
    body: WorkerCreate,
    db: AsyncSession = Depends(get_db),
    _member: OrgMember = Depends(get_org_member),
):
    # Check duplicate RUT
    existing = await db.execute(select(Worker).where(Worker.org_id == org_id, Worker.rut == body.rut))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail={"detail": "RUT ya existe en esta organizacion", "code": ErrorCode.WORKER_DUPLICATE_RUT})

    worker = Worker(org_id=org_id, **body.model_dump())
    db.add(worker)
    await db.commit()
    await db.refresh(worker)
    return WorkerResponse(
        id=worker.id, rut=worker.rut, first_name=worker.first_name, last_name=worker.last_name,
        specialty=worker.specialty, phone=worker.phone, email=worker.email, is_active=worker.is_active,
        created_at=worker.created_at,
    )


@router.get("/export.csv")
async def export_workers_csv(
    org_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _member: OrgMember = Depends(get_org_member),
):
    stmt = (
        select(
            Worker.rut,
            Worker.first_name,
            Worker.last_name,
            Worker.specialty,
            Worker.phone,
            Worker.email,
            Worker.is_active,
            func.count(Evaluation.id).label("eval_count"),
            func.avg(Evaluation.score_average).label("avg_score"),
        )
        .outerjoin(Evaluation, (Evaluation.worker_id == Worker.id) & (Evaluation.deleted_at.is_(None)))
        .where(Worker.org_id == org_id)
        .group_by(Worker.id)
        .order_by(Worker.last_name.asc(), Worker.first_name.asc())
    )
    rows = (await db.execute(stmt)).all()

    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow([
        "RUT", "Nombre", "Apellido", "Especialidad", "Telefono", "Email",
        "Activo", "Evaluaciones", "Score Promedio",
    ])
    for r in rows:
        writer.writerow([
            r.rut, r.first_name, r.last_name, r.specialty, r.phone or "", r.email or "",
            "Si" if r.is_active else "No", r.eval_count or 0,
            f"{round(r.avg_score, 2)}" if r.avg_score is not None else "",
        ])

    buf.seek(0)
    return StreamingResponse(
        iter([buf.getvalue()]),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": 'attachment; filename="trabajadores.csv"'},
    )


@router.post("/import", response_model=WorkerImportResult)
async def import_workers(
    org_id: uuid.UUID,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    _member: OrgMember = Depends(get_org_member),
):
    import openpyxl

    # Validación de tipo MIME (defensa básica; el contenido se valida al parsear).
    if file.content_type and file.content_type not in _XLSX_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"detail": "El archivo debe ser un Excel (.xlsx)", "code": ErrorCode.VALIDATION_ERROR},
        )

    content = await file.read()
    if len(content) > _MAX_IMPORT_BYTES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"detail": "El archivo supera el tamaño máximo de 5 MB", "code": ErrorCode.VALIDATION_ERROR},
        )

    try:
        wb = openpyxl.load_workbook(io.BytesIO(content), read_only=True)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"detail": "No se pudo leer el archivo Excel", "code": ErrorCode.VALIDATION_ERROR},
        )
    ws = wb.active

    rows = list(ws.iter_rows(min_row=2, max_row=_MAX_IMPORT_ROWS + 1, values_only=True))
    created, updated, errors = 0, 0, []

    for i, row in enumerate(rows, start=2):
        if not row or not row[0]:
            continue
        try:
            rut_raw = str(row[0]).strip()
            if not validate_rut(rut_raw):
                errors.append(f"Fila {i}: RUT invalido '{rut_raw}'")
                continue
            rut = format_rut(rut_raw)
            first_name = str(row[1]).strip() if row[1] else ""
            last_name = str(row[2]).strip() if row[2] else ""
            specialty = str(row[3]).strip() if len(row) > 3 and row[3] else "Sin especificar"
            phone = str(row[4]).strip() if len(row) > 4 and row[4] else None
            email = str(row[5]).strip() if len(row) > 5 and row[5] else None
            certs = str(row[6]).strip() if len(row) > 6 and row[6] else None

            if not first_name or not last_name:
                errors.append(f"Fila {i}: Nombre o apellido vacio")
                continue

            existing = await db.execute(select(Worker).where(Worker.org_id == org_id, Worker.rut == rut))
            worker = existing.scalar_one_or_none()

            if worker:
                worker.first_name = first_name
                worker.last_name = last_name
                worker.specialty = specialty
                if phone:
                    worker.phone = phone
                if email:
                    worker.email = email
                if certs:
                    worker.certifications = certs
                updated += 1
            else:
                worker = Worker(
                    org_id=org_id, rut=rut, first_name=first_name, last_name=last_name,
                    specialty=specialty, phone=phone, email=email, certifications=certs,
                )
                db.add(worker)
                created += 1
        except Exception:
            errors.append(f"Fila {i}: error al procesar la fila")

    await db.commit()
    wb.close()
    return WorkerImportResult(created=created, updated=updated, errors=errors)


@router.get("/{worker_id}", response_model=WorkerDetailResponse)
async def get_worker_detail(
    org_id: uuid.UUID,
    worker_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _member: OrgMember = Depends(get_org_member),
):
    result = await db.execute(select(Worker).where(Worker.id == worker_id, Worker.org_id == org_id))
    worker = result.scalar_one_or_none()
    if not worker:
        raise HTTPException(status_code=404, detail={"detail": "Worker not found", "code": ErrorCode.WORKER_NOT_FOUND})

    # Get evaluations with project info
    eval_result = await db.execute(
        select(Evaluation, Project.name, Project.end_date)
        .join(Project, Evaluation.project_id == Project.id)
        .where(Evaluation.worker_id == worker_id, Evaluation.deleted_at.is_(None))
        .order_by(Evaluation.created_at.desc())
    )
    eval_rows = eval_result.all()

    evaluations = []
    score_trend = []
    rehire_yes, rehire_res, rehire_no = 0, 0, 0
    sum_q, sum_s, sum_p, sum_t, sum_tech = 0.0, 0.0, 0.0, 0.0, 0.0

    for ev, proj_name, proj_end in eval_rows:
        evaluator_name = None
        if ev.evaluator_id:
            from app.models.user import User
            u = await db.execute(select(User.full_name).where(User.id == ev.evaluator_id))
            evaluator_name = u.scalar_one_or_none()

        evaluations.append(EvaluationSummary(
            id=ev.id, project_name=proj_name, score_average=ev.score_average,
            would_rehire=ev.would_rehire, comment=ev.comment, evaluator_name=evaluator_name,
            created_at=ev.created_at,
        ))
        score_trend.append(ScoreTrendPoint(project_name=proj_name, date=proj_end, score_average=ev.score_average))

        if ev.would_rehire == "yes":
            rehire_yes += 1
        elif ev.would_rehire == "reservations":
            rehire_res += 1
        else:
            rehire_no += 1

        sum_q += ev.score_quality
        sum_s += ev.score_safety
        sum_p += ev.score_punctuality
        sum_t += ev.score_teamwork
        sum_tech += ev.score_technical

    n = len(eval_rows)
    avg_scores = None
    avg_score = None
    if n > 0:
        avg_scores = ScoreBreakdown(
            quality=round(sum_q / n, 2), safety=round(sum_s / n, 2),
            punctuality=round(sum_p / n, 2), teamwork=round(sum_t / n, 2),
            technical=round(sum_tech / n, 2),
            overall=round((sum_q + sum_s + sum_p + sum_t + sum_tech) / (n * 5), 2),
        )
        avg_score = avg_scores.overall

    # Reverse trend to chronological order
    score_trend.reverse()

    consent = await _build_consent_response(worker_id, db)

    return WorkerDetailResponse(
        id=worker.id, rut=worker.rut, first_name=worker.first_name, last_name=worker.last_name,
        specialty=worker.specialty, phone=worker.phone, email=worker.email, is_active=worker.is_active,
        certifications=worker.certifications, notes=worker.notes,
        evaluation_count=n, avg_score=avg_score, created_at=worker.created_at,
        avg_scores=avg_scores, score_trend=score_trend,
        rehire_stats=RehireStats(yes=rehire_yes, reservations=rehire_res, no=rehire_no),
        evaluations=evaluations, consent=consent,
    )


@router.patch("/{worker_id}", response_model=WorkerResponse)
async def update_worker(
    org_id: uuid.UUID,
    worker_id: uuid.UUID,
    body: WorkerUpdate,
    db: AsyncSession = Depends(get_db),
    _member: OrgMember = Depends(get_org_member),
):
    result = await db.execute(select(Worker).where(Worker.id == worker_id, Worker.org_id == org_id))
    worker = result.scalar_one_or_none()
    if not worker:
        raise HTTPException(status_code=404, detail={"detail": "Worker not found", "code": ErrorCode.WORKER_NOT_FOUND})

    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(worker, field, value)
    await db.commit()
    await db.refresh(worker)

    return WorkerResponse(
        id=worker.id, rut=worker.rut, first_name=worker.first_name, last_name=worker.last_name,
        specialty=worker.specialty, phone=worker.phone, email=worker.email, is_active=worker.is_active,
        created_at=worker.created_at,
    )


@router.delete("/{worker_id}", status_code=204)
async def delete_worker(
    org_id: uuid.UUID,
    worker_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _member: OrgMember = Depends(get_org_member),
):
    result = await db.execute(select(Worker).where(Worker.id == worker_id, Worker.org_id == org_id))
    worker = result.scalar_one_or_none()
    if not worker:
        raise HTTPException(status_code=404, detail={"detail": "Worker not found", "code": ErrorCode.WORKER_NOT_FOUND})
    worker.is_active = False
    await db.commit()


@router.get("/{worker_id}/consent", response_model=WorkerConsentResponse)
async def get_worker_consent(
    org_id: uuid.UUID,
    worker_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _member: OrgMember = Depends(get_org_member),
):
    result = await db.execute(select(Worker.id).where(Worker.id == worker_id, Worker.org_id == org_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail={"detail": "Worker not found", "code": ErrorCode.WORKER_NOT_FOUND})
    return await _build_consent_response(worker_id, db)


@router.put("/{worker_id}/consent", response_model=WorkerConsentResponse)
async def upsert_worker_consent(
    org_id: uuid.UUID,
    worker_id: uuid.UUID,
    body: WorkerConsentUpsert,
    db: AsyncSession = Depends(get_db),
    _member: OrgMember = Depends(get_org_member),
    user: User = Depends(get_current_user),
):
    """Registra o actualiza el consentimiento intra-organización del trabajador (Ley 21.719)."""
    wresult = await db.execute(select(Worker.id).where(Worker.id == worker_id, Worker.org_id == org_id))
    if not wresult.scalar_one_or_none():
        raise HTTPException(status_code=404, detail={"detail": "Worker not found", "code": ErrorCode.WORKER_NOT_FOUND})

    result = await db.execute(select(WorkerConsent).where(WorkerConsent.worker_id == worker_id))
    consent = result.scalar_one_or_none()
    if consent is None:
        consent = WorkerConsent(worker_id=worker_id, org_id=org_id)
        db.add(consent)

    consent.status = body.status
    consent.method = body.method
    consent.consent_date = body.consent_date
    consent.notes = body.notes
    consent.recorded_by = user.id

    await db.commit()
    return await _build_consent_response(worker_id, db)
