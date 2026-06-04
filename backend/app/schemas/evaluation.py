import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, model_validator

# Minimo de caracteres exigido al motivo cuando NO se recomienda recontratar.
REHIRE_REASON_MIN_CHARS = 3


def _normalize_reason(reason: str | None) -> str | None:
    """Trim del motivo; cadena vacia se trata como ausencia de motivo."""
    if reason is None:
        return None
    reason = reason.strip()
    return reason or None


def validate_rehire_reason(would_rehire: str | None, rehire_reason: str | None) -> None:
    """Regla de negocio: si NO se recomienda recontratar sin reservas, el motivo es obligatorio.

    Se aplica tanto al crear como al editar (sobre el estado final de la evaluacion).
    Da derecho a una justificacion trazable de una decision que afecta al trabajador.
    """
    if would_rehire is not None and would_rehire != "yes":
        normalized = _normalize_reason(rehire_reason)
        if normalized is None or len(normalized) < REHIRE_REASON_MIN_CHARS:
            raise ValueError(
                f"Debes indicar el motivo (mínimo {REHIRE_REASON_MIN_CHARS} caracteres) "
                "cuando no recomiendas recontratar."
            )


class EvaluationCreate(BaseModel):
    project_id: uuid.UUID
    worker_id: uuid.UUID
    score_quality: int = Field(..., ge=1, le=5)
    score_safety: int = Field(..., ge=1, le=5)
    score_punctuality: int = Field(..., ge=1, le=5)
    score_teamwork: int = Field(..., ge=1, le=5)
    score_technical: int = Field(..., ge=1, le=5)
    would_rehire: Literal["yes", "reservations", "no"]
    rehire_reason: str | None = None
    comment: str | None = None

    @model_validator(mode="after")
    def _check_rehire_reason(self) -> "EvaluationCreate":
        self.rehire_reason = _normalize_reason(self.rehire_reason)
        validate_rehire_reason(self.would_rehire, self.rehire_reason)
        return self


class EvaluationUpdate(BaseModel):
    score_quality: int | None = Field(None, ge=1, le=5)
    score_safety: int | None = Field(None, ge=1, le=5)
    score_punctuality: int | None = Field(None, ge=1, le=5)
    score_teamwork: int | None = Field(None, ge=1, le=5)
    score_technical: int | None = Field(None, ge=1, le=5)
    would_rehire: Literal["yes", "reservations", "no"] | None = None
    rehire_reason: str | None = None
    comment: str | None = None

    @model_validator(mode="after")
    def _normalize(self) -> "EvaluationUpdate":
        # El motivo se normaliza siempre; la regla obligatoria se valida en el
        # endpoint sobre el estado final (puede depender de campos no enviados).
        if "rehire_reason" in self.model_fields_set:
            self.rehire_reason = _normalize_reason(self.rehire_reason)
        return self


class EvaluationBatchCreate(BaseModel):
    evaluations: list[EvaluationCreate]


class EvaluationAuditEntry(BaseModel):
    id: uuid.UUID
    action: str
    actor_name: str | None = None
    snapshot: dict
    changed_fields: list[str] | None = None
    created_at: datetime
    model_config = {"from_attributes": True}


class EvaluationResponse(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    project_name: str = ""
    worker_id: uuid.UUID
    worker_name: str = ""
    evaluator_name: str | None = None
    score_quality: int
    score_safety: int
    score_punctuality: int
    score_teamwork: int
    score_technical: int
    score_average: float
    would_rehire: str
    rehire_reason: str | None
    comment: str | None
    created_at: datetime
    model_config = {"from_attributes": True}
