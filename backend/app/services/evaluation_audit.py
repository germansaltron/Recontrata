"""Helpers para el rastro de auditoría / versionado de evaluaciones (Fase 1, L3 + L5)."""

import uuid
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.evaluation import Evaluation
from app.models.evaluation_audit import EvaluationAuditLog
from app.models.user import User

# Campos de la evaluación que componen un snapshot de versión.
_SNAPSHOT_FIELDS = (
    "score_quality",
    "score_safety",
    "score_punctuality",
    "score_teamwork",
    "score_technical",
    "score_average",
    "would_rehire",
    "rehire_reason",
    "comment",
)


def _jsonable(value):
    if isinstance(value, (uuid.UUID, datetime)):
        return str(value)
    return value


def evaluation_snapshot(ev: Evaluation) -> dict:
    """Estado serializable (JSON) de una evaluación, para guardar como versión."""
    snap = {field: _jsonable(getattr(ev, field)) for field in _SNAPSHOT_FIELDS}
    snap["project_id"] = _jsonable(ev.project_id)
    snap["worker_id"] = _jsonable(ev.worker_id)
    return snap


def record_evaluation_audit(
    db: AsyncSession,
    ev: Evaluation,
    action: str,
    actor: User | None,
    changed_fields: list[str] | None = None,
) -> EvaluationAuditLog:
    """Agrega (sin commit) una entrada de auditoría con el snapshot actual de la evaluación.

    El commit lo hace el endpoint llamador, dentro de la misma transacción que la mutación,
    de modo que el rastro y el cambio son atómicos.
    """
    entry = EvaluationAuditLog(
        evaluation_id=ev.id,
        org_id=ev.org_id,
        action=action,
        actor_id=actor.id if actor else None,
        actor_name=(actor.full_name or actor.email) if actor else None,
        snapshot=evaluation_snapshot(ev),
        changed_fields=changed_fields,
    )
    db.add(entry)
    return entry
