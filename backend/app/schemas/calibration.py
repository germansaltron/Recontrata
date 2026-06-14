from pydantic import BaseModel


class EvaluatorCalibration(BaseModel):
    evaluator_id: str | None
    evaluator_name: str | None
    evaluation_count: int
    mean_score: float
    leniency_delta: float
    dimension_spread: float
    flags: list[str]


class CalibrationResponse(BaseModel):
    org_mean: float | None
    min_sample: int
    leniency_threshold: float
    halo_threshold: float
    evaluators: list[EvaluatorCalibration]
