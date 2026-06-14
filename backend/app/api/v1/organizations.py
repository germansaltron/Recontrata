import re
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user, get_org_admin, get_org_member
from app.errors import ErrorCode
from app.models.organization import Organization, OrgMember
from app.models.user import User
from app.schemas.organization import OrganizationCreate, OrganizationResponse, OrganizationUpdate
from app.services.score_calculator import WEIGHT_PROFILES

router = APIRouter(prefix="/organizations", tags=["organizations"])


def _slugify(name: str) -> str:
    slug = re.sub(r"[^\w\s-]", "", name.lower().strip())
    slug = re.sub(r"[\s_]+", "-", slug)
    return slug[:100]


@router.post("", response_model=OrganizationResponse, status_code=201)
async def create_organization(
    body: OrganizationCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    slug = _slugify(body.name)

    # Ensure slug is unique
    existing = await db.execute(select(Organization).where(Organization.slug == slug))
    if existing.scalar_one_or_none():
        slug = f"{slug}-{uuid.uuid4().hex[:6]}"

    org = Organization(name=body.name, slug=slug)
    db.add(org)
    await db.flush()

    # Auto-add creator as admin
    member = OrgMember(org_id=org.id, user_id=user.id, role="admin")
    db.add(member)
    await db.commit()
    await db.refresh(org)

    return OrganizationResponse.model_validate(org)


@router.get("/{org_id}", response_model=OrganizationResponse)
async def get_organization(
    org_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _member: OrgMember = Depends(get_org_member),
):
    result = await db.execute(select(Organization).where(Organization.id == org_id))
    org = result.scalar_one_or_none()
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"detail": "Organization not found", "code": ErrorCode.ORG_NOT_FOUND},
        )
    return OrganizationResponse.model_validate(org)


@router.patch("/{org_id}", response_model=OrganizationResponse)
async def update_organization(
    org_id: uuid.UUID,
    body: OrganizationUpdate,
    db: AsyncSession = Depends(get_db),
    _admin: OrgMember = Depends(get_org_admin),
):
    """Actualiza datos de la organización. La industria define el perfil de pesos
    del puntaje, por eso solo un admin puede cambiarla."""
    result = await db.execute(select(Organization).where(Organization.id == org_id))
    org = result.scalar_one_or_none()
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"detail": "Organization not found", "code": ErrorCode.ORG_NOT_FOUND},
        )

    data = body.model_dump(exclude_unset=True)
    if "industry" in data and data["industry"] is not None:
        if data["industry"] not in WEIGHT_PROFILES:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={"detail": "Industria no válida", "code": ErrorCode.VALIDATION_ERROR},
            )
        org.industry = data["industry"]
    if data.get("name"):
        org.name = data["name"]

    await db.commit()
    await db.refresh(org)
    return OrganizationResponse.model_validate(org)
