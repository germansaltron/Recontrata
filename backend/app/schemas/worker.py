import uuid
from datetime import date, datetime

from pydantic import BaseModel, Field, field_validator

from app.schemas.worker_consent import WorkerConsentResponse
from app.services.rut_validator import validate_rut, format_rut


class WorkerCreate(BaseModel):
    rut: str = Field(..., max_length=12)
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    specialty: str = Field(..., min_length=1, max_length=100)
    phone: str | None = None
    email: str | None = None
    certifications: str | None = None
    notes: str | None = None

    @field_validator("rut")
    @classmethod
    def validate_and_format_rut(cls, v: str) -> str:
        if not validate_rut(v):
            raise ValueError("RUT invalido")
        return format_rut(v)


class WorkerUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    specialty: str | None = None
    phone: str | None = None
    email: str | None = None
    certifications: str | None = None
    notes: str | None = None
    is_active: bool | None = None


class WorkerResponse(BaseModel):
    id: uuid.UUID
    rut: str
    first_name: str
    last_name: str
    specialty: str
    phone: str | None
    email: str | None
    is_active: bool
    evaluation_count: int = 0
    avg_score: float | None = None
    created_at: datetime
    model_config = {"from_attributes": True}


class ScoreBreakdown(BaseModel):
    quality: float
    safety: float
    punctuality: float
    teamwork: float
    technical: float
    overall: float


class ScoreTrendPoint(BaseModel):
    project_name: str
    date: date | None
    score_average: float


class RehireStats(BaseModel):
    yes: int
    reservations: int
    no: int


class EvaluationSummary(BaseModel):
    id: uuid.UUID
    project_name: str
    score_average: float
    would_rehire: str
    comment: str | None
    evaluator_name: str | None
    created_at: datetime


class WorkerDetailResponse(WorkerResponse):
    certifications: str | None
    notes: str | None
    avg_scores: ScoreBreakdown | None = None
    score_trend: list[ScoreTrendPoint] = []
    rehire_stats: RehireStats = RehireStats(yes=0, reservations=0, no=0)
    evaluations: list[EvaluationSummary] = []
    consent: WorkerConsentResponse | None = None


class WorkerImportResult(BaseModel):
    created: int
    updated: int
    errors: list[str]
