import json

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    # App
    APP_NAME: str = "Recontrata"
    # Secure-by-default: prod debe dejar DEBUG y AUTH_MOCK_ENABLED en False.
    # Si la env var falta en Railway, falla cerrado (sin logs SQL, sin mock auth).
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://faenascore:faenascore_dev@localhost:5432/faenascore"

    # Evaluaciones
    # Ventana (horas) durante la cual una evaluación puede editarse tras crearse.
    # Pasado este plazo queda bloqueada para preservar la integridad del historial.
    EVALUATION_EDIT_WINDOW_HOURS: int = 72

    # Auth
    AUTH_MOCK_ENABLED: bool = False
    ALLOW_MOCK_IN_PROD: bool = False
    CLERK_SECRET_KEY: str = ""
    CLERK_JWKS_URL: str = ""
    CLERK_ISSUER: str = ""
    CLERK_AUDIENCE: str = ""

    # Pasarela de pago (Flow) — ver docs/PASARELA_PAGO_FLOW.md.
    # Vacío por defecto: el cliente no puede firmar sin credenciales (falla explícito).
    # Sandbox: https://sandbox.flow.cl/api · Producción: https://www.flow.cl/api
    FLOW_API_KEY: str = ""
    FLOW_API_SECRET: str = ""
    FLOW_API_BASE: str = "https://sandbox.flow.cl/api"
    # planId (creados una vez en Flow con scripts/flow_bootstrap_plans.py).
    FLOW_PLAN_ID_PRO_MONTHLY: str = ""
    FLOW_PLAN_ID_PRO_ANNUAL: str = ""
    FLOW_PLAN_ID_EMPRESA_MONTHLY: str = ""
    FLOW_PLAN_ID_EMPRESA_ANNUAL: str = ""
    # Cupón fundador (-50% de por vida) para los design partners.
    FLOW_COUPON_FOUNDER: str = ""
    # URLs de retorno/notificación (Railway build/runtime).
    BILLING_RETURN_URL: str = ""
    FLOW_WEBHOOK_URL: str = ""

    # Observabilidad (Sentry) — opcional. Si SENTRY_DSN está vacío, no se inicializa
    # (no-op): el código queda listo y solo hay que pegar el DSN en Railway.
    SENTRY_DSN: str = ""
    SENTRY_ENVIRONMENT: str = "production"
    SENTRY_TRACES_SAMPLE_RATE: float = 0.1

    # CORS
    CORS_ORIGINS: str = '["http://localhost:5173"]'

    @property
    def cors_origins_list(self) -> list[str]:
        v = self.CORS_ORIGINS.strip()
        if not v:
            return ["http://localhost:5173"]
        if v.startswith("["):
            return json.loads(v)
        return [origin.strip() for origin in v.split(",") if origin.strip()]

    @property
    def async_database_url(self) -> str:
        url = self.DATABASE_URL
        if url.startswith("postgresql://"):
            return url.replace("postgresql://", "postgresql+asyncpg://", 1)
        return url


settings = Settings()
