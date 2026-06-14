import uuid

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_org_member
from app.models.organization import Organization, OrgMember
from app.schemas.scoring import DimensionWeight, ScoringFormulaResponse, ScoringProfile
from app.services.score_calculator import (
    DEFAULT_INDUSTRY,
    DIMENSION_LABELS,
    DIMENSIONS,
    WEIGHT_PROFILES,
)

router = APIRouter(prefix="/organizations/{org_id}/scoring", tags=["scoring"])


def _build_profile(industry: str) -> ScoringProfile:
    profile = WEIGHT_PROFILES[industry]
    return ScoringProfile(
        industry=industry,
        label=profile["label"],
        description=profile["description"],
        weights=[
            DimensionWeight(key=dim, label=DIMENSION_LABELS[dim], weight=profile["weights"][dim])
            for dim in DIMENSIONS
        ],
    )


@router.get("/formula", response_model=ScoringFormulaResponse)
async def get_scoring_formula(
    org_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _member: OrgMember = Depends(get_org_member),
):
    """Fórmula pública del puntaje: perfil de pesos activo + catálogo completo.

    Hace transparente cómo se construye el puntaje de cada trabajador
    (Seguridad pesa más que Puntualidad en construcción/minería).
    """
    result = await db.execute(select(Organization.industry).where(Organization.id == org_id))
    industry = result.scalar_one_or_none() or DEFAULT_INDUSTRY
    if industry not in WEIGHT_PROFILES:
        industry = DEFAULT_INDUSTRY

    return ScoringFormulaResponse(
        active_industry=industry,
        active_profile=_build_profile(industry),
        profiles=[_build_profile(key) for key in WEIGHT_PROFILES],
    )
