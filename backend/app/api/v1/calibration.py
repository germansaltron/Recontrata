import uuid

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_org_admin
from app.models.evaluation import Evaluation
from app.models.organization import OrgMember
from app.models.user import User
from app.schemas.calibration import CalibrationResponse, EvaluatorCalibration
from app.services.evaluator_calibration import EvalInput, compute_calibration

router = APIRouter(prefix="/organizations/{org_id}/calibration", tags=["calibration"])


@router.get("", response_model=CalibrationResponse)
async def get_calibration(
    org_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _admin: OrgMember = Depends(get_org_admin),
):
    """Calibración de evaluadores: detecta indulgencia/severidad y efecto halo.

    Restringido a admin: es información sensible sobre el desempeño de los
    supervisores, no de los trabajadores.
    """
    rows = (await db.execute(
        select(
            Evaluation.evaluator_id, User.full_name,
            Evaluation.score_quality, Evaluation.score_safety, Evaluation.score_punctuality,
            Evaluation.score_teamwork, Evaluation.score_technical,
        )
        .outerjoin(User, User.id == Evaluation.evaluator_id)
        .where(Evaluation.org_id == org_id, Evaluation.deleted_at.is_(None))
    )).all()

    evals = [
        EvalInput(
            evaluator_id=str(eid) if eid else None,
            evaluator_name=name,
            quality=q, safety=s, punctuality=p, teamwork=t, technical=tech,
        )
        for eid, name, q, s, p, t, tech in rows
    ]

    result = compute_calibration(evals)

    return CalibrationResponse(
        org_mean=result.org_mean,
        min_sample=result.min_sample,
        leniency_threshold=result.leniency_threshold,
        halo_threshold=result.halo_threshold,
        evaluators=[
            EvaluatorCalibration(
                evaluator_id=e.evaluator_id, evaluator_name=e.evaluator_name,
                evaluation_count=e.evaluation_count, mean_score=e.mean_score,
                leniency_delta=e.leniency_delta, dimension_spread=e.dimension_spread,
                flags=e.flags,
            )
            for e in result.evaluators
        ],
    )
