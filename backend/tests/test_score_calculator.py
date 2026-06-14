from app.services.score_calculator import (
    DEFAULT_INDUSTRY,
    DIMENSIONS,
    WEIGHT_PROFILES,
    compute_average,
    compute_weighted,
    get_profile,
)


class TestComputeAverage:
    def test_all_fives(self):
        assert compute_average(5, 5, 5, 5, 5) == 5.0

    def test_all_ones(self):
        assert compute_average(1, 1, 1, 1, 1) == 1.0

    def test_mixed_returns_rounded_two_decimals(self):
        # (3+4+5+4+3)/5 = 19/5 = 3.8
        assert compute_average(3, 4, 5, 4, 3) == 3.8

    def test_rounding_behavior(self):
        # (1+2+3+4+5)/5 = 3.0
        assert compute_average(1, 2, 3, 4, 5) == 3.0

    def test_two_decimal_precision(self):
        # (4+4+4+5+5)/5 = 22/5 = 4.4
        assert compute_average(4, 4, 4, 5, 5) == 4.4


class TestWeightProfiles:
    def test_every_profile_sums_to_one(self):
        for key, profile in WEIGHT_PROFILES.items():
            total = sum(profile["weights"].values())
            assert abs(total - 1.0) < 1e-9, f"{key} suma {total}"

    def test_every_profile_defines_all_dimensions(self):
        for key, profile in WEIGHT_PROFILES.items():
            assert set(profile["weights"]) == set(DIMENSIONS), key

    def test_default_industry_exists(self):
        assert DEFAULT_INDUSTRY in WEIGHT_PROFILES

    def test_default_profile_safety_outweighs_punctuality(self):
        # El corazón de la propuesta defendible: Seguridad pesa más que Puntualidad.
        w = WEIGHT_PROFILES[DEFAULT_INDUSTRY]["weights"]
        assert w["safety"] > w["punctuality"]


class TestGetProfile:
    def test_known_industry(self):
        assert get_profile("logistica") is WEIGHT_PROFILES["logistica"]

    def test_unknown_industry_falls_back_to_default(self):
        assert get_profile("inexistente") is WEIGHT_PROFILES[DEFAULT_INDUSTRY]

    def test_none_falls_back_to_default(self):
        assert get_profile(None) is WEIGHT_PROFILES[DEFAULT_INDUSTRY]


class TestComputeWeighted:
    def test_all_equal_scores_equal_average_regardless_of_profile(self):
        # Si todas las dimensiones valen lo mismo, ponderar no cambia el resultado.
        for industry in WEIGHT_PROFILES:
            assert compute_weighted(4, 4, 4, 4, 4, industry) == 4.0

    def test_general_profile_equals_simple_average(self):
        assert compute_weighted(1, 2, 3, 4, 5, "general") == compute_average(1, 2, 3, 4, 5)

    def test_safety_weighted_more_than_punctuality(self):
        # Trabajador con Seguridad alta y Puntualidad baja vs. el inverso:
        # en construcción/minería el primero debe puntuar más alto.
        safe_worker = compute_weighted(3, 5, 1, 3, 3, "construccion_mineria")
        punctual_worker = compute_weighted(3, 1, 5, 3, 3, "construccion_mineria")
        assert safe_worker > punctual_worker

    def test_known_value_default_profile(self):
        # quality 4*.25 + safety 5*.30 + punctuality 2*.10 + teamwork 3*.15 + technical 4*.20
        # = 1.0 + 1.5 + 0.2 + 0.45 + 0.8 = 3.95
        assert compute_weighted(4, 5, 2, 3, 4, "construccion_mineria") == 3.95

    def test_unknown_industry_uses_default(self):
        assert compute_weighted(4, 5, 2, 3, 4, "inexistente") == compute_weighted(
            4, 5, 2, 3, 4, "construccion_mineria"
        )

    def test_result_in_1_to_5_scale(self):
        assert compute_weighted(5, 5, 5, 5, 5, "energia") == 5.0
        assert compute_weighted(1, 1, 1, 1, 1, "energia") == 1.0
