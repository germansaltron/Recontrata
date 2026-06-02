"""Regression tests para los fixes de seguridad de la Fase 0 (sin DB)."""

import os

import pytest
from fastapi import HTTPException

from app.api.v1.admin import _check_admin_token
from app.api.v1.workers import (
    _MAX_IMPORT_BYTES,
    _MAX_IMPORT_ROWS,
    _SORTABLE_COLUMNS,
    _XLSX_CONTENT_TYPES,
)
from app.models.worker import Worker


# --- S2: token admin ---

def _set_token(monkeypatch, value):
    if value is None:
        monkeypatch.delenv("ADMIN_TOKEN", raising=False)
    else:
        monkeypatch.setenv("ADMIN_TOKEN", value)


def test_admin_token_missing_env_fails_closed(monkeypatch):
    _set_token(monkeypatch, None)
    with pytest.raises(HTTPException) as exc:
        _check_admin_token("anything")
    assert exc.value.status_code == 403


def test_admin_token_too_short_fails_closed(monkeypatch):
    _set_token(monkeypatch, "short-token")  # < 32 chars
    with pytest.raises(HTTPException):
        _check_admin_token("short-token")


def test_admin_token_wrong_value_rejected(monkeypatch):
    _set_token(monkeypatch, "a" * 40)
    with pytest.raises(HTTPException):
        _check_admin_token("b" * 40)


def test_admin_token_none_header_rejected(monkeypatch):
    _set_token(monkeypatch, "a" * 40)
    with pytest.raises(HTTPException):
        _check_admin_token(None)


def test_admin_token_correct_passes(monkeypatch):
    token = "x" * 40
    _set_token(monkeypatch, token)
    _check_admin_token(token)  # no debe levantar


# --- S5: allowlist de columnas ordenables ---

def test_sortable_columns_allowlist_is_closed():
    expected = {"last_name", "first_name", "specialty", "created_at"}
    assert set(_SORTABLE_COLUMNS) == expected


def test_sortable_columns_excludes_sensitive_attrs():
    # No debe ser posible ordenar por columnas internas/sensibles.
    for forbidden in ("org_id", "id", "email", "phone", "__tablename__"):
        assert forbidden not in _SORTABLE_COLUMNS


def test_sortable_columns_map_to_real_worker_columns():
    for col in _SORTABLE_COLUMNS.values():
        assert col.class_ is Worker


# --- S6: límites del import de Excel ---

def test_import_limits_defined():
    assert _MAX_IMPORT_BYTES == 5 * 1024 * 1024
    assert _MAX_IMPORT_ROWS == 5000
    assert "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" in _XLSX_CONTENT_TYPES
