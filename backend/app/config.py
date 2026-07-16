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

    # Billing: candado de límites de plan. OFF por defecto (secure-by-default para el
    # beta: los testers/design partners tienen acceso libre). Prender (=True) recién al
    # activar el cobro con Flow. Ver docs/PASARELA_PAGO_FLOW.md.
    BILLING_ENFORCEMENT_ENABLED: bool = False

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

    # Bot de WhatsApp (ventas) — ver docs/BOT_WHATSAPP.md.
    # Candado dormido: con BOT_ENABLED=False el webhook responde 200 pero no procesa
    # ni contesta nada. Prender recién con el número definitivo dado de alta en Meta.
    BOT_ENABLED: bool = False
    # Credenciales de Meta. Vacías por defecto: sin APP_SECRET no se puede validar la
    # firma del webhook, y el endpoint rechaza todo (falla cerrado).
    META_APP_SECRET: str = ""
    WHATSAPP_TOKEN: str = ""
    WHATSAPP_PHONE_ID: str = ""
    WHATSAPP_VERIFY_TOKEN: str = ""
    WHATSAPP_API_URL: str = "https://graph.facebook.com/v22.0"

    # LLM del bot. Sonnet (no Opus): es un bot comercial, no necesita el tier alto.
    ANTHROPIC_API_KEY: str = ""
    BOT_MODEL: str = "claude-sonnet-5"

    # Correo de leads (Resend) y derivación de soporte.
    RESEND_API_KEY: str = ""
    BOT_FROM_EMAIL: str = "bot@recontrata.cl"
    BOT_LEAD_EMAILS: str = '["gsaltron@gmail.com"]'
    BOT_SUPPORT_EMAIL: str = "atencion@recontrata.cl"

    # Marcha blanca: ALERTS_TEST_MODE redirige TODAS las alertas a ALERTS_TEST_EMAILS.
    # Default True para que un despliegue accidental no le escriba a nadie real.
    ALERTS_TEST_MODE: bool = True
    ALERTS_TEST_EMAILS: str = '["gsaltron@gmail.com"]'

    # Conversación.
    MESSAGE_BUFFER_SECONDS: int = 3
    SESSION_TIMEOUT_MINUTES: int = 30
    MAX_TURNS: int = 3
    BLOCKED_NUMBERS: str = "[]"

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

    @staticmethod
    def _as_list(raw: str) -> list[str]:
        """Parsea una env var que puede venir como JSON (["a","b"]) o separada por comas."""
        v = raw.strip()
        if not v:
            return []
        if v.startswith("["):
            return json.loads(v)
        return [item.strip() for item in v.split(",") if item.strip()]

    @property
    def bot_lead_emails_list(self) -> list[str]:
        return self._as_list(self.BOT_LEAD_EMAILS)

    @property
    def alerts_test_emails_list(self) -> list[str]:
        return self._as_list(self.ALERTS_TEST_EMAILS)

    @property
    def blocked_numbers_digits(self) -> set[str]:
        """Números bloqueados normalizados a solo dígitos, para comparar sin importar
        el formato (+56 9 1234 5678 == 56912345678)."""
        return {"".join(c for c in n if c.isdigit()) for n in self._as_list(self.BLOCKED_NUMBERS)}

    @property
    def async_database_url(self) -> str:
        url = self.DATABASE_URL
        if url.startswith("postgresql://"):
            return url.replace("postgresql://", "postgresql+asyncpg://", 1)
        return url


settings = Settings()
