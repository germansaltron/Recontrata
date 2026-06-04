"""Tests Fase 1 (confianza/legal) — sin DB.

Cubren L2 (rehire_reason obligatorio) y el snapshot de auditoría (L3/L5).
"""
import uuid

import pytest
from pydantic import ValidationError

from app.schemas.evaluation import (
    EvaluationCreate,
    EvaluationUpdate,
    validate_rehire_reason,
)


def _base_scores() -> dict:
    return dict(
        project_id=uuid.uuid4(),
        worker_id=uuid.uuid4(),
        score_quality=3,
        score_safety=3,
        score_punctuality=3,
        score_teamwork=3,
        score_technical=3,
    )


# ---- L2: rehire_reason obligatorio cuando no se recomienda recontratar ----

def test_create_no_rehire_without_reason_rejected():
    with pytest.raises(ValidationError):
        EvaluationCreate(**_base_scores(), would_rehire="no")


def test_create_reservations_without_reason_rejected():
    with pytest.raises(ValidationError):
        EvaluationCreate(**_base_scores(), would_rehire="reservations")


def test_create_no_rehire_reason_too_short_rejected():
    with pytest.raises(ValidationError):
        EvaluationCreate(**_base_scores(), would_rehire="no", rehire_reason="ab")


def test_create_no_rehire_with_valid_reason_ok():
    ev = EvaluationCreate(**_base_scores(), would_rehire="no", rehire_reason="Llegó tarde reiteradamente")
    assert ev.rehire_reason == "Llegó tarde reiteradamente"


def test_create_yes_rehire_without_reason_ok():
    ev = EvaluationCreate(**_base_scores(), would_rehire="yes")
    assert ev.rehire_reason is None


def test_create_yes_rehire_blank_reason_normalized_to_none():
    ev = EvaluationCreate(**_base_scores(), would_rehire="yes", rehire_reason="   ")
    assert ev.rehire_reason is None


def test_create_whitespace_only_reason_rejected_when_no():
    with pytest.raises(ValidationError):
        EvaluationCreate(**_base_scores(), would_rehire="no", rehire_reason="   ")


def test_validate_rehire_reason_helper():
    # No recomendado sin motivo -> error
    with pytest.raises(ValueError):
        validate_rehire_reason("no", None)
    with pytest.raises(ValueError):
        validate_rehire_reason("reservations", "")
    # Recomendado sin motivo -> OK
    validate_rehire_reason("yes", None)
    # No recomendado con motivo válido -> OK
    validate_rehire_reason("no", "motivo suficiente")
    # would_rehire None (update parcial) -> no valida aquí
    validate_rehire_reason(None, None)


def test_update_normalizes_blank_reason():
    upd = EvaluationUpdate(rehire_reason="  ")
    assert upd.rehire_reason is None


# ---- L3/L5: snapshot de auditoría serializable ----

def test_evaluation_snapshot_is_jsonable():
    from app.services.evaluation_audit import evaluation_snapshot

    class _FakeEval:
        score_quality = 4
        score_safety = 5
        score_punctuality = 3
        score_teamwork = 4
        score_technical = 4
        score_average = 4.0
        would_rehire = "yes"
        rehire_reason = None
        comment = "buen desempeño"
        project_id = uuid.uuid4()
        worker_id = uuid.uuid4()

    snap = evaluation_snapshot(_FakeEval())
    assert snap["score_average"] == 4.0
    assert snap["would_rehire"] == "yes"
    # uuid serializado a str
    assert isinstance(snap["project_id"], str)
    assert isinstance(snap["worker_id"], str)
    # debe ser serializable a JSON sin errores
    import json
    json.dumps(snap)
