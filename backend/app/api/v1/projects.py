import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_org_member
from app.errors import ErrorCode
from app.models.evaluation import Evaluation
from app.models.organization import OrgMember
from app.models.project import Project
from app.models.project_worker import ProjectWorker
from app.models.worker import Worker
from app.schemas.pagination import PaginatedResponse
from app.schemas.project import AssignWorkersRequest, ProjectCreate, ProjectResponse, ProjectUpdate

router = APIRouter(prefix="/organizations/{org_id}/projects", tags=["projects"])


async def _get_project(org_id: uuid.UUID, project_id: uuid.UUID, db: AsyncSession) -> Project:
    result = await db.execute(
        select(Project).where(Project.id == project_id, Project.org_id == org_id)
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail={"detail": "Project not found", "code": ErrorCode.PROJECT_NOT_FOUND})
    return project


@router.get("", response_model=PaginatedResponse[ProjectResponse])
async def list_projects(
    org_id: uuid.UUID,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    status_filter: str | None = Query(None, alias="status"),
    search: str | None = None,
    db: AsyncSession = Depends(get_db),
    _member: OrgMember = Depends(get_org_member),
):
    query = select(Project).where(Project.org_id == org_id)
    count_query = select(func.count(Project.id)).where(Project.org_id == org_id)

    if status_filter:
        query = query.where(Project.status == status_filter)
        count_query = count_query.where(Project.status == status_filter)
    if search:
        query = query.where(Project.name.ilike(f"%{search}%"))
        count_query = count_query.where(Project.name.ilike(f"%{search}%"))

    total = (await db.execute(count_query)).scalar() or 0
    offset = (page - 1) * size

    # Correlated scalar subqueries: worker/eval counts resolved in the same SELECT (no N+1).
    wc_subq = (
        select(func.count(ProjectWorker.id))
        .where(ProjectWorker.project_id == Project.id)
        .correlate(Project)
        .scalar_subquery()
    )
    ec_subq = (
        select(func.count(Evaluation.id))
        .where(Evaluation.project_id == Project.id, Evaluation.deleted_at.is_(None))
        .correlate(Project)
        .scalar_subquery()
    )
    result = await db.execute(
        query.add_columns(wc_subq.label("wc"), ec_subq.label("ec"))
        .order_by(Project.created_at.desc())
        .offset(offset)
        .limit(size)
    )

    items = []
    for p, wc, ec in result.all():
        resp = ProjectResponse.model_validate(p)
        resp.worker_count = wc or 0
        resp.evaluation_count = ec or 0
        items.append(resp)

    return PaginatedResponse(items=items, total=total, page=page, size=size, pages=(total + size - 1) // size if total else 0)


@router.post("", response_model=ProjectResponse, status_code=201)
async def create_project(
    org_id: uuid.UUID,
    body: ProjectCreate,
    db: AsyncSession = Depends(get_db),
    _member: OrgMember = Depends(get_org_member),
):
    project = Project(org_id=org_id, **body.model_dump())
    db.add(project)
    await db.commit()
    await db.refresh(project)
    resp = ProjectResponse.model_validate(project)
    return resp


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    org_id: uuid.UUID,
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _member: OrgMember = Depends(get_org_member),
):
    project = await _get_project(org_id, project_id, db)
    wc = (await db.execute(select(func.count(ProjectWorker.id)).where(ProjectWorker.project_id == project.id))).scalar() or 0
    ec = (await db.execute(select(func.count(Evaluation.id)).where(Evaluation.project_id == project.id, Evaluation.deleted_at.is_(None)))).scalar() or 0
    resp = ProjectResponse.model_validate(project)
    resp.worker_count = wc
    resp.evaluation_count = ec
    return resp


@router.patch("/{project_id}", response_model=ProjectResponse)
async def update_project(
    org_id: uuid.UUID,
    project_id: uuid.UUID,
    body: ProjectUpdate,
    db: AsyncSession = Depends(get_db),
    _member: OrgMember = Depends(get_org_member),
):
    project = await _get_project(org_id, project_id, db)
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(project, field, value)
    await db.commit()
    await db.refresh(project)
    return ProjectResponse.model_validate(project)


@router.post("/{project_id}/workers", status_code=201)
async def assign_workers(
    org_id: uuid.UUID,
    project_id: uuid.UUID,
    body: AssignWorkersRequest,
    db: AsyncSession = Depends(get_db),
    _member: OrgMember = Depends(get_org_member),
):
    await _get_project(org_id, project_id, db)
    added = 0
    for wid in body.worker_ids:
        # Check worker exists in org
        w = await db.execute(select(Worker).where(Worker.id == wid, Worker.org_id == org_id))
        if not w.scalar_one_or_none():
            continue
        # Check not already assigned
        existing = await db.execute(
            select(ProjectWorker).where(ProjectWorker.project_id == project_id, ProjectWorker.worker_id == wid)
        )
        if existing.scalar_one_or_none():
            continue
        pw = ProjectWorker(project_id=project_id, worker_id=wid, role_in_project=body.role_in_project)
        db.add(pw)
        added += 1
    await db.commit()
    return {"added": added}


@router.delete("/{project_id}/workers/{worker_id}", status_code=204)
async def unassign_worker(
    org_id: uuid.UUID,
    project_id: uuid.UUID,
    worker_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _member: OrgMember = Depends(get_org_member),
):
    # Verifica que el proyecto pertenezca a la org (evita IDOR cross-tenant).
    await _get_project(org_id, project_id, db)
    result = await db.execute(
        select(ProjectWorker).where(ProjectWorker.project_id == project_id, ProjectWorker.worker_id == worker_id)
    )
    pw = result.scalar_one_or_none()
    if pw:
        await db.delete(pw)
        await db.commit()


@router.get("/{project_id}/workers")
async def list_project_workers(
    org_id: uuid.UUID,
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _member: OrgMember = Depends(get_org_member),
):
    await _get_project(org_id, project_id, db)
    result = await db.execute(
        select(Worker, ProjectWorker.role_in_project, ProjectWorker.assigned_at, Evaluation.score_average)
        .join(ProjectWorker, ProjectWorker.worker_id == Worker.id)
        .outerjoin(
            Evaluation,
            (Evaluation.project_id == project_id) & (Evaluation.worker_id == Worker.id) & (Evaluation.deleted_at.is_(None)),
        )
        .where(ProjectWorker.project_id == project_id, Worker.org_id == org_id)
        .order_by(Worker.last_name)
    )
    rows = result.all()

    items = []
    for worker, role, assigned_at, eval_score in rows:
        items.append({
            "id": str(worker.id),
            "rut": worker.rut,
            "first_name": worker.first_name,
            "last_name": worker.last_name,
            "specialty": worker.specialty,
            "role_in_project": role,
            "assigned_at": assigned_at.isoformat() if assigned_at else None,
            "evaluated": eval_score is not None,
            "score_in_project": eval_score,
        })
    return items
