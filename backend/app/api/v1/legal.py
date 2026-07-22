"""Aceptación del Contrato / Términos de Servicio.

El gate del frontend consulta `contract-status` en el primer ingreso; si el usuario no
ha aceptado la versión vigente, muestra el paso obligatorio y luego llama a `accept`.
La aceptación se registra con IP y user-agent como prueba (Ley N° 19.799)."""

import structlog
from fastapi import APIRouter, Depends, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.legal import CONTRACT_VERSION
from app.models.contract_acceptance import ContractAcceptance
from app.models.user import User
from app.ratelimit import client_ip
from app.schemas.legal import ContractStatus

logger = structlog.get_logger()

router = APIRouter(prefix="/legal", tags=["legal"])


async def _has_accepted(db: AsyncSession, user_id, version: str) -> bool:
    row = await db.execute(
        select(ContractAcceptance.id).where(
            ContractAcceptance.user_id == user_id,
            ContractAcceptance.contract_version == version,
        )
    )
    return row.scalar_one_or_none() is not None


@router.get("/contract-status", response_model=ContractStatus)
async def contract_status(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    accepted = await _has_accepted(db, user.id, CONTRACT_VERSION)
    return ContractStatus(current_version=CONTRACT_VERSION, accepted=accepted)


@router.post("/accept", response_model=ContractStatus)
async def accept_contract(
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Registra la aceptación de la versión vigente. Idempotente: si el usuario ya
    aceptó esta versión, no crea un duplicado (el índice único lo garantiza)."""
    if not await _has_accepted(db, user.id, CONTRACT_VERSION):
        db.add(
            ContractAcceptance(
                user_id=user.id,
                contract_version=CONTRACT_VERSION,
                ip=client_ip(request),
                user_agent=(request.headers.get("user-agent") or "")[:400],
            )
        )
        await db.commit()
        logger.info("contract_accepted", user_id=str(user.id), version=CONTRACT_VERSION)
    return ContractStatus(current_version=CONTRACT_VERSION, accepted=True)
