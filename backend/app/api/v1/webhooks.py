"""Webhooks entrantes de Flow (urlConfirmation).

Flow NO firma la notificación: solo envía el `token` por POST form-urlencoded. El estado
autoritativo se obtiene re-consultando a Flow (payment/getStatus) con nuestra credencial.
Por eso este endpoint es público (sin Clerk) pero solo confía en lo que Flow responde.

Ver docs/PASARELA_PAGO_FLOW.md §5.
"""

import structlog
from fastapi import APIRouter, Depends, Form, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.billing.flow_client import FlowClient, FlowError
from app.billing.service import apply_payment_result, normalize_payment_status
from app.database import get_db

logger = structlog.get_logger()

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


def get_flow_client() -> FlowClient:
    """Factory inyectable (los tests la sobrescriben con un cliente stub)."""
    return FlowClient()


@router.post("/flow")
async def flow_confirmation(
    token: str = Form(...),
    db: AsyncSession = Depends(get_db),
    client: FlowClient = Depends(get_flow_client),
):
    try:
        payload = await client.get_payment_status(token)
    except FlowError as e:
        # No pudimos verificar con Flow: devolvemos 503 para que Flow reintente.
        logger.warning("flow_webhook_verify_failed", token=token, error=str(e))
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="No se pudo verificar con Flow")

    result = normalize_payment_status(token, payload)
    event = await apply_payment_result(db, result)
    logger.info(
        "flow_webhook_processed",
        token=token,
        status=result.flow_status,
        subscription_id=str(event.subscription_id) if event.subscription_id else None,
    )
    return {"received": True}
