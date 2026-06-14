from app.services.evaluator_calibration import (
    EvalInput,
    compute_calibration,
)


def _ev(eid, q, s, p, t, tech, name=None):
    return EvalInput(evaluator_id=eid, evaluator_name=name or eid, quality=q, safety=s,
                     punctuality=p, teamwork=t, technical=tech)


class TestEmpty:
    def test_no_evals(self):
        r = compute_calibration([])
        assert r.org_mean is None
        assert r.evaluators == []


class TestBasics:
    def test_single_evaluator_no_bias_flag_with_enough_sample(self):
        # 5 evals iguales => leniency_delta 0, spread 0 => halo (no diferencia dims)
        evals = [_ev("a", 3, 3, 3, 3, 3) for _ in range(5)]
        r = compute_calibration(evals)
        assert r.org_mean == 3.0
        e = r.evaluators[0]
        assert e.evaluation_count == 5
        assert e.leniency_delta == 0.0
        assert "lenient" not in e.flags and "severe" not in e.flags
        # Todas las dims iguales => spread 0 => halo
        assert e.dimension_spread == 0.0
        assert "halo" in e.flags

    def test_low_sample_flag(self):
        evals = [_ev("a", 5, 1, 3, 4, 2) for _ in range(3)]
        r = compute_calibration(evals)
        e = r.evaluators[0]
        assert "low_sample" in e.flags
        # con muestra baja no marcamos sesgo aunque haya delta
        assert "lenient" not in e.flags and "severe" not in e.flags


class TestLeniencySeverity:
    def test_lenient_and_severe_detected(self):
        # Evaluador A puntua alto (5), B puntua bajo (1). Media org = 3.
        evals = [_ev("A", 5, 5, 5, 5, 5) for _ in range(5)]
        evals += [_ev("B", 1, 1, 1, 1, 1) for _ in range(5)]
        r = compute_calibration(evals)
        assert r.org_mean == 3.0
        by_id = {e.evaluator_id: e for e in r.evaluators}
        assert by_id["A"].leniency_delta == 2.0
        assert "lenient" in by_id["A"].flags
        assert by_id["B"].leniency_delta == -2.0
        assert "severe" in by_id["B"].flags

    def test_within_threshold_not_flagged(self):
        # A levemente arriba pero bajo el umbral 0.5
        evals = [_ev("A", 4, 3, 3, 3, 3) for _ in range(5)]   # avg 3.2
        evals += [_ev("B", 3, 3, 3, 3, 3) for _ in range(5)]  # avg 3.0
        r = compute_calibration(evals)
        by_id = {e.evaluator_id: e for e in r.evaluators}
        # org_mean = 3.1; A delta = 0.1 -> sin flag de sesgo
        assert "lenient" not in by_id["A"].flags
        assert "severe" not in by_id["A"].flags


class TestHalo:
    def test_halo_when_dimensions_uniform(self):
        evals = [_ev("A", 4, 4, 4, 4, 4) for _ in range(6)]
        r = compute_calibration(evals)
        e = r.evaluators[0]
        assert e.dimension_spread == 0.0
        assert "halo" in e.flags

    def test_no_halo_when_dimensions_vary(self):
        # Dimensiones bien dispersas => spread alto, sin halo
        evals = [_ev("A", 1, 5, 1, 5, 3) for _ in range(6)]
        r = compute_calibration(evals)
        e = r.evaluators[0]
        assert e.dimension_spread >= 1.0
        assert "halo" not in e.flags


class TestOrdering:
    def test_sorted_by_abs_delta_desc(self):
        evals = [_ev("mid", 3, 3, 3, 3, 3) for _ in range(5)]
        evals += [_ev("hi", 5, 5, 5, 5, 5) for _ in range(5)]
        evals += [_ev("lo", 2, 2, 2, 2, 2) for _ in range(5)]
        r = compute_calibration(evals)
        # El primero debe ser el de mayor |delta|
        deltas = [abs(e.leniency_delta) for e in r.evaluators]
        assert deltas == sorted(deltas, reverse=True)
