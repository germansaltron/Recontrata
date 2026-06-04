import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models import Base


class EvaluationAuditLog(Base):
    """Rastro inmutable de cada acción sobre una evaluación (crear/editar/borrar).

    Cumple dos funciones de la Fase 1:
    - Audit log (L3): quién hizo qué y cuándo, con el estado resultante.
    - Versionado (L5): la secuencia de snapshots por evaluación es su historial de versiones.

    Cada fila guarda el snapshot del estado de la evaluación tras la acción (para create/update)
    o el último estado antes de borrar (para delete). No se borra al hacer soft-delete del padre.
    """

    __tablename__ = "evaluation_audit_log"
    __table_args__ = (
        Index("ix_eval_audit_evaluation_id", "evaluation_id"),
        Index("ix_eval_audit_org_id", "org_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    # SET NULL para que el rastro sobreviva aunque algún día se borre físicamente la evaluación.
    evaluation_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("evaluations.id", ondelete="SET NULL"), nullable=True
    )
    org_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    action: Mapped[str] = mapped_column(String(20), nullable=False)  # create | update | delete
    actor_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    actor_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    # Estado de la evaluación tras la acción (JSONB). Es el snapshot de la versión.
    snapshot: Mapped[dict] = mapped_column(JSONB, nullable=False)
    # Lista de campos modificados (solo en update), como JSON.
    changed_fields: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
