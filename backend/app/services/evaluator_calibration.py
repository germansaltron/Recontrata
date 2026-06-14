"""Calibración de evaluadores (Fase 5, anti-sesgo).

Detecta sesgos sistemáticos en quién evalúa, para que el puntaje sea más justo y
defendible:

- **Indulgencia / severidad**: un evaluador cuyo promedio se desvía mucho del
  promedio de la organización (puntúa siempre más alto o más bajo que el resto).
- **Efecto halo**: un evaluador que casi no diferencia entre las 5 dimensiones
  (le pone notas parecidas a todo), medido por la dispersión interna promedio.

Las funciones son puras (sin DB) para poder testearlas con datos sintéticos.
"""
from dataclasses import dataclass, field
from statistics import mean, pstdev

# Umbrales por defecto (ajustables desde el endpoint si hiciera falta).
DEFAULT_MIN_SAMPLE = 5          # mínimo de evaluaciones para marcar sesgo con confianza
DEFAULT_LENIENCY_THRESHOLD = 0.5   # desviación (en puntos 1-5) respecto a la media de la org
DEFAULT_HALO_THRESHOLD = 0.5       # dispersión interna promedio bajo la cual hay efecto halo


@dataclass
class EvalInput:
    evaluator_id: str | None
    evaluator_name: str | None
    quality: int
    safety: int
    punctuality: int
    teamwork: int
    technical: int

    @property
    def dimensions(self) -> list[int]:
        return [self.quality, self.safety, self.punctuality, self.teamwork, self.technical]

    @property
    def average(self) -> float:
        return sum(self.dimensions) / 5.0


@dataclass
class EvaluatorStats:
    evaluator_id: str | None
    evaluator_name: str | None
    evaluation_count: int
    mean_score: float
    leniency_delta: float
    dimension_spread: float
    flags: list[str] = field(default_factory=list)


@dataclass
class CalibrationResult:
    org_mean: float | None
    min_sample: int
    leniency_threshold: float
    halo_threshold: float
    evaluators: list[EvaluatorStats]


# Etiqueta para evaluaciones sin evaluador identificado.
_UNKNOWN_KEY = "__unknown__"


def compute_calibration(
    evals: list[EvalInput],
    min_sample: int = DEFAULT_MIN_SAMPLE,
    leniency_threshold: float = DEFAULT_LENIENCY_THRESHOLD,
    halo_threshold: float = DEFAULT_HALO_THRESHOLD,
) -> CalibrationResult:
    if not evals:
        return CalibrationResult(
            org_mean=None, min_sample=min_sample,
            leniency_threshold=leniency_threshold, halo_threshold=halo_threshold,
            evaluators=[],
        )

    org_mean = round(mean(e.average for e in evals), 2)

    # Agrupar por evaluador.
    groups: dict[str, list[EvalInput]] = {}
    names: dict[str, str | None] = {}
    for e in evals:
        key = e.evaluator_id or _UNKNOWN_KEY
        groups.setdefault(key, []).append(e)
        names[key] = e.evaluator_name

    evaluators: list[EvaluatorStats] = []
    for key, items in groups.items():
        count = len(items)
        ev_mean = round(mean(i.average for i in items), 2)
        leniency_delta = round(ev_mean - org_mean, 2)
        # Dispersión interna: cuánto varía un evaluador entre las 5 dimensiones,
        # promediada sobre sus evaluaciones. Baja => efecto halo.
        dimension_spread = round(mean(pstdev(i.dimensions) for i in items), 2)

        flags: list[str] = []
        if count < min_sample:
            flags.append("low_sample")
        else:
            if leniency_delta >= leniency_threshold:
                flags.append("lenient")
            elif leniency_delta <= -leniency_threshold:
                flags.append("severe")
            if dimension_spread < halo_threshold:
                flags.append("halo")

        evaluators.append(EvaluatorStats(
            evaluator_id=None if key == _UNKNOWN_KEY else key,
            evaluator_name=names[key],
            evaluation_count=count,
            mean_score=ev_mean,
            leniency_delta=leniency_delta,
            dimension_spread=dimension_spread,
            flags=flags,
        ))

    # Orden: primero los más desviados (más lejos de 0), para que los casos a revisar suban.
    evaluators.sort(key=lambda s: abs(s.leniency_delta), reverse=True)
    return CalibrationResult(
        org_mean=org_mean, min_sample=min_sample,
        leniency_threshold=leniency_threshold, halo_threshold=halo_threshold,
        evaluators=evaluators,
    )
