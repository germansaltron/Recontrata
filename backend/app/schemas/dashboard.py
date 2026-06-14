import uuid
from datetime import datetime

from pydantic import BaseModel


class SpecialtyCount(BaseModel):
    specialty: str
    count: int


class DashboardStats(BaseModel):
    project_count: int
    active_project_count: int
    worker_count: int
    evaluation_count: int
    avg_score_overall: float | None
    rehire_rate: float | None
    specialty_distribution: list[SpecialtyCount]


class TopWorkerItem(BaseModel):
    id: uuid.UUID
    full_name: str
    specialty: str
    avg_score: float
    evaluation_count: int
    would_rehire_pct: float


class RecentEvaluationItem(BaseModel):
    id: uuid.UUID
    worker_id: uuid.UUID
    worker_name: str
    project_name: str
    score_average: float
    score_weighted: float = 0.0
    would_rehire: str
    created_at: datetime
