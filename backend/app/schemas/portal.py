import uuid
from datetime import date, datetime

from pydantic import BaseModel, Field

from app.schemas.scoring import ScoringProfile


class PortalEvaluation(BaseModel):
    """Una evaluación tal como la VE el trabajador.

    Incluye sus puntajes, el resultado de recontratación y el motivo/comentario
    (transparencia), pero NUNCA la identidad del evaluador.
    """

    id: uuid.UUID
    project_name: str
    score_quality: int
    score_safety: int
    score_punctuality: int
    score_teamwork: int
    score_technical: int
    score_average: float
    score_weighted: float
    would_rehire: str
    rehire_reason: str | None
    comment: str | None
    worker_reply: str | None
    worker_reply_at: datetime | None
    created_at: datetime


class PortalTrendPoint(BaseModel):
    project_name: str
    date: date | None
    score_weighted: float


class PortalProfile(BaseModel):
    """Vista pública (por token) del historial de un trabajador en una organización."""

    worker_name: str
    rut: str
    specialty: str
    org_name: str
    evaluation_count: int
    avg_score: float | None
    consent_status: str
    rehire_yes: int
    rehire_reservations: int
    rehire_no: int
    formula: ScoringProfile
    score_trend: list[PortalTrendPoint] = []
    evaluations: list[PortalEvaluation] = []


class PortalReplyRequest(BaseModel):
    reply: str = Field(..., min_length=1, max_length=2000)


class PortalOptOutRequest(BaseModel):
    notes: str | None = Field(None, max_length=2000)


class PortalLinkResponse(BaseModel):
    token: str
    path: str  # ruta relativa del portal, p.ej. /p/<token>
