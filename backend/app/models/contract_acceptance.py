import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models import Base


class ContractAcceptance(Base):
    """Registro de aceptación del Contrato / Términos de Servicio por un usuario.

    Es la PRUEBA de la manifestación de voluntad (Ley N° 19.799): guarda quién aceptó,
    qué versión, cuándo y desde qué IP. Se registra una fila por (usuario, versión); al
    subir una versión nueva del contrato se pide una aceptación nueva. Solo se agrega,
    nunca se modifica ni borra (integridad de la evidencia)."""

    __tablename__ = "contract_acceptances"
    __table_args__ = (
        Index("ix_contract_acceptances_user_id", "user_id"),
        Index("ix_contract_acceptances_user_version", "user_id", "contract_version", unique=True),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    contract_version: Mapped[str] = mapped_column(String(20), nullable=False)
    accepted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    ip: Mapped[str | None] = mapped_column(String(64), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(400), nullable=True)
