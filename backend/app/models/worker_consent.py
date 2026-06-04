import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models import Base


class WorkerConsent(Base):
    """Registro del consentimiento del trabajador para ser evaluado dentro de una organización.

    Alcance (Fase 1): consentimiento INTRA-organización. Cada organización mantiene su propio
    perfil del trabajador (los datos están aislados por `org_id`); este registro documenta que
    el trabajador fue informado o consintió el tratamiento de sus evaluaciones dentro de esa
    organización, en línea con la Ley N° 21.719.

    La portabilidad CROSS-organización (compartir el historial entre empresas — el "Portal del
    Trabajador" de la Fase 5) NO está habilitada y requerirá un consentimiento explícito y
    separado; no se infiere de este registro.
    """

    __tablename__ = "worker_consent"
    __table_args__ = (
        # Un registro de consentimiento por trabajador (el trabajador pertenece a una sola org).
        UniqueConstraint("worker_id", name="uq_worker_consent_worker"),
        Index("ix_worker_consent_org_id", "org_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    worker_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("workers.id", ondelete="CASCADE"), nullable=False
    )
    org_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    # pending | informed | granted | revoked
    status: Mapped[str] = mapped_column(String(20), nullable=False, server_default="pending")
    # verbal | written | email | contract | platform
    method: Mapped[str | None] = mapped_column(String(20), nullable=True)
    consent_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    recorded_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
