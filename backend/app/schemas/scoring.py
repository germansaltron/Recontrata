from pydantic import BaseModel


class DimensionWeight(BaseModel):
    key: str
    label: str
    weight: float


class ScoringProfile(BaseModel):
    industry: str
    label: str
    description: str
    weights: list[DimensionWeight]


class ScoringFormulaResponse(BaseModel):
    """Fórmula pública del puntaje de una organización (transparencia, art. 16 Ley 21.719).

    Devuelve el perfil ACTIVO de la org y el catálogo completo de perfiles
    disponibles, para que la decisión sobre cómo se pondera sea inspeccionable.
    """

    active_industry: str
    active_profile: ScoringProfile
    profiles: list[ScoringProfile]
