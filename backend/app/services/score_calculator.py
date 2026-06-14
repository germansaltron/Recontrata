"""Cálculo del puntaje de desempeño.

El puntaje de un trabajador NO es un promedio plano de las 5 dimensiones: es un
**promedio ponderado** donde cada dimensión pesa según la industria de la
organización. En industrias de alto riesgo (construcción/minería) la Seguridad
pesa más que la Puntualidad, lo que hace el puntaje defendible frente a una
decisión de no recontratar.

La fórmula es PÚBLICA y consultable (transparencia, art. 16 Ley N° 21.719): los
pesos viven acá, se exponen por API y se muestran en la interfaz. Cambiar un peso
es una decisión explícita y trazable, no un número oculto.
"""

# Clave canónica de cada dimensión. El orden coincide con
# score_quality / score_safety / score_punctuality / score_teamwork / score_technical.
DIMENSIONS = ("quality", "safety", "punctuality", "teamwork", "technical")

DIMENSION_LABELS = {
    "quality": "Calidad del Trabajo",
    "safety": "Seguridad",
    "punctuality": "Puntualidad",
    "teamwork": "Trabajo en Equipo",
    "technical": "Habilidad Técnica",
}

# Perfiles de ponderación por industria. Cada perfil DEBE sumar 1.0 (se valida abajo).
# Pensados para faena/terreno: la Seguridad domina en los rubros de mayor riesgo.
WEIGHT_PROFILES: dict[str, dict] = {
    "construccion_mineria": {
        "label": "Construcción / Minería",
        "description": (
            "Alta exigencia de seguridad: la Seguridad es la dimensión de mayor peso, "
            "por sobre la Puntualidad."
        ),
        "weights": {
            "quality": 0.25,
            "safety": 0.30,
            "punctuality": 0.10,
            "teamwork": 0.15,
            "technical": 0.20,
        },
    },
    "energia": {
        "label": "Energía / Eléctrico",
        "description": "Seguridad y dominio técnico priorizados (trabajos energizados, altura).",
        "weights": {
            "quality": 0.20,
            "safety": 0.30,
            "punctuality": 0.10,
            "teamwork": 0.15,
            "technical": 0.25,
        },
    },
    "logistica": {
        "label": "Logística / Transporte",
        "description": "La Puntualidad sube su peso: los plazos y la disponibilidad son críticos.",
        "weights": {
            "quality": 0.20,
            "safety": 0.25,
            "punctuality": 0.25,
            "teamwork": 0.15,
            "technical": 0.15,
        },
    },
    "manufactura": {
        "label": "Manufactura / Taller",
        "description": "La Calidad del trabajo y la terminación pesan más en producción de taller.",
        "weights": {
            "quality": 0.30,
            "safety": 0.20,
            "punctuality": 0.15,
            "teamwork": 0.15,
            "technical": 0.20,
        },
    },
    "general": {
        "label": "General (promedio simple)",
        "description": "Todas las dimensiones pesan igual. Útil cuando no aplica un perfil de riesgo.",
        "weights": {
            "quality": 0.20,
            "safety": 0.20,
            "punctuality": 0.20,
            "teamwork": 0.20,
            "technical": 0.20,
        },
    },
}

# Industria por defecto: el público inicial de Recontrata es faena minera/construcción.
DEFAULT_INDUSTRY = "construccion_mineria"

# Validación de integridad: ningún perfil puede tener pesos que no sumen 1.0
# (con tolerancia para errores de punto flotante).
for _key, _profile in WEIGHT_PROFILES.items():
    _total = sum(_profile["weights"].values())
    if abs(_total - 1.0) > 1e-9:
        raise ValueError(f"El perfil de pesos '{_key}' suma {_total}, debe sumar 1.0")
    if set(_profile["weights"]) != set(DIMENSIONS):
        raise ValueError(f"El perfil de pesos '{_key}' no define exactamente las 5 dimensiones")


def get_profile(industry: str | None) -> dict:
    """Devuelve el perfil de pesos de una industria (o el default si no existe)."""
    return WEIGHT_PROFILES.get(industry or DEFAULT_INDUSTRY, WEIGHT_PROFILES[DEFAULT_INDUSTRY])


def compute_average(
    quality: int,
    safety: int,
    punctuality: int,
    teamwork: int,
    technical: int,
) -> float:
    """Promedio simple (sin ponderar) de las 5 dimensiones.

    Se conserva como referencia/transparencia junto al puntaje ponderado.
    """
    return round((quality + safety + punctuality + teamwork + technical) / 5.0, 2)


def compute_weighted(
    quality: int,
    safety: int,
    punctuality: int,
    teamwork: int,
    technical: int,
    industry: str | None = None,
) -> float:
    """Puntaje ponderado según el perfil de la industria.

    score = Σ(dimensión × peso). Como los pesos suman 1.0, el resultado queda en
    la misma escala 1-5 que cada dimensión.
    """
    w = get_profile(industry)["weights"]
    total = (
        quality * w["quality"]
        + safety * w["safety"]
        + punctuality * w["punctuality"]
        + teamwork * w["teamwork"]
        + technical * w["technical"]
    )
    return round(total, 2)
