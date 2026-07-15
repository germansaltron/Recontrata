from contextlib import asynccontextmanager
from pathlib import Path

import structlog
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api.v1.health import router as health_router
from app.api.v1.auth import router as auth_router
from app.api.v1.organizations import router as organizations_router
from app.api.v1.projects import router as projects_router
from app.api.v1.workers import router as workers_router
from app.api.v1.evaluations import router as evaluations_router
from app.api.v1.dashboard import router as dashboard_router
from app.api.v1.scoring import router as scoring_router
from app.api.v1.portal import router as portal_router
from app.api.v1.calibration import router as calibration_router
from app.api.v1.admin import router as admin_router
from app.api.v1.billing import router as billing_router
from app.api.v1.webhooks import router as webhooks_router
from app.config import settings
from app.database import engine
from app.errors import ErrorCode

try:
    import sentry_sdk
except ImportError:  # sentry-sdk no instalado en algún entorno local: degradar a no-op
    sentry_sdk = None

logger = structlog.get_logger()

# Observabilidad: inicializa Sentry solo si hay DSN configurado (no-op en su ausencia).
# La integración de FastAPI se autodetecta; send_default_pii=False evita filtrar datos
# personales de trabajadores en los eventos de error.
if sentry_sdk and settings.SENTRY_DSN:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        environment=settings.SENTRY_ENVIRONMENT,
        traces_sample_rate=settings.SENTRY_TRACES_SAMPLE_RATE,
        send_default_pii=False,
    )
    logger.info("Sentry inicializado", environment=settings.SENTRY_ENVIRONMENT)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Recontrata API", debug=settings.DEBUG, mock_auth=settings.AUTH_MOCK_ENABLED)
    if not settings.DEBUG and settings.AUTH_MOCK_ENABLED and not settings.ALLOW_MOCK_IN_PROD:
        raise RuntimeError("AUTH_MOCK_ENABLED=True is not allowed when DEBUG=False. Set ALLOW_MOCK_IN_PROD=True to override (testing only).")
    if settings.AUTH_MOCK_ENABLED and settings.ALLOW_MOCK_IN_PROD:
        logger.warning("Running with mock auth in production — anyone can access all data. Disable ALLOW_MOCK_IN_PROD before real launch.")
    yield
    await engine.dispose()
    logger.info("Shutting down Recontrata API")


app = FastAPI(title=settings.APP_NAME, version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Admin-Token"],
)


@app.middleware("http")
async def security_headers(request: Request, call_next):
    """Cabeceras de seguridad HTTP (clickjacking, MIME sniffing, referrer, HSTS)."""
    response = await call_next(request)
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    if not settings.DEBUG:
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled exception", path=request.url.path, method=request.method, error=str(exc), exc_info=True)
    # El handler "consume" la excepción, así que la reportamos a Sentry explícitamente
    # (si está configurado; capture_exception es no-op sin init).
    if sentry_sdk and settings.SENTRY_DSN:
        sentry_sdk.capture_exception(exc)
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred.", "code": ErrorCode.INTERNAL_ERROR},
    )


# Routers
app.include_router(health_router, prefix="/api")
app.include_router(auth_router, prefix="/api/v1")
app.include_router(organizations_router, prefix="/api/v1")
app.include_router(projects_router, prefix="/api/v1")
app.include_router(workers_router, prefix="/api/v1")
app.include_router(evaluations_router, prefix="/api/v1")
app.include_router(dashboard_router, prefix="/api/v1")
app.include_router(scoring_router, prefix="/api/v1")
app.include_router(portal_router, prefix="/api/v1")
app.include_router(calibration_router, prefix="/api/v1")
app.include_router(admin_router, prefix="/api/v1")
app.include_router(billing_router, prefix="/api/v1")
app.include_router(webhooks_router, prefix="/api/v1")

# Serve frontend static files (production: built by Dockerfile)
static_dir = Path(__file__).parent.parent / "static"
if static_dir.exists():
    assets_dir = static_dir / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")
    index_file = static_dir / "index.html"

    # El service worker y el shell HTML NUNCA deben quedar cacheados por el CDN
    # (Cloudflare) ni por el navegador: de lo contrario los clientes se quedan con
    # un SW o un index viejos y nunca toman la actualizacion. Los assets hasheados
    # (/assets/*, workbox-*.js) si son inmutables y se pueden cachear sin problema.
    NO_CACHE = {"Cache-Control": "no-cache, no-store, must-revalidate"}

    @app.get("/{full_path:path}", include_in_schema=False)
    async def spa_fallback(full_path: str):
        if full_path.startswith("api"):
            raise HTTPException(status_code=404)
        candidate = static_dir / full_path
        if full_path and candidate.is_file():
            # sw.js debe revalidarse siempre para que los updates lleguen al cliente.
            if full_path == "sw.js":
                return FileResponse(str(candidate), headers=NO_CACHE)
            return FileResponse(str(candidate))
        # El shell (index.html) tampoco se cachea: asi el nuevo bundle entra al instante.
        return FileResponse(str(index_file), headers=NO_CACHE)
