"""Verificación de JWT de Clerk vía JWKS (RS256), con PyJWT.

El JWKS se obtiene de Clerk con httpx async y se cachea (el cliente síncrono de PyJWT
bloquearía el event loop, por eso NO se usa PyJWKClient). PyJWT solo selecciona la clave
por `kid` y decodifica/valida (firma, exp, issuer y audience).
"""

import json
import time

import httpx
import jwt
import structlog
from jwt.algorithms import RSAAlgorithm

from app.config import settings

logger = structlog.get_logger()

_jwks_cache: dict | None = None
_jwks_fetched_at: float = 0
_JWKS_CACHE_TTL = 3600


async def _fetch_jwks() -> dict:
    global _jwks_cache, _jwks_fetched_at

    now = time.time()
    if _jwks_cache and (now - _jwks_fetched_at) < _JWKS_CACHE_TTL:
        return _jwks_cache

    async with httpx.AsyncClient() as client:
        resp = await client.get(settings.CLERK_JWKS_URL)
        resp.raise_for_status()
        _jwks_cache = resp.json()
        _jwks_fetched_at = now
        logger.info("Fetched JWKS from Clerk", url=settings.CLERK_JWKS_URL)
        return _jwks_cache


def _invalidate_jwks_cache() -> None:
    global _jwks_cache, _jwks_fetched_at
    _jwks_cache = None
    _jwks_fetched_at = 0


def _signing_key(token: str, jwks: dict):
    """Clave pública del JWKS que corresponde al `kid` del token (RS256)."""
    try:
        kid = jwt.get_unverified_header(token).get("kid")
    except jwt.PyJWTError as e:
        raise jwt.InvalidTokenError(f"Cabecera de token inválida: {e}") from e
    for jwk in jwks.get("keys", []):
        if jwk.get("kid") == kid:
            return RSAAlgorithm.from_jwk(json.dumps(jwk))
    raise jwt.InvalidTokenError("Ninguna clave del JWKS coincide con el kid del token")


def _decode(token: str, jwks: dict) -> dict:
    return jwt.decode(
        token,
        key=_signing_key(token, jwks),
        algorithms=["RS256"],
        issuer=settings.CLERK_ISSUER or None,
        audience=settings.CLERK_AUDIENCE or None,
        options={"verify_aud": bool(settings.CLERK_AUDIENCE)},
    )


async def verify_clerk_token(token: str) -> dict:
    jwks = await _fetch_jwks()
    try:
        return _decode(token, jwks)
    except jwt.PyJWTError:
        # Puede ser que Clerk haya rotado la clave (kid nuevo) y tengamos el JWKS viejo
        # en caché: se invalida, se re-descarga y se reintenta UNA vez. Si vuelve a
        # fallar (token realmente inválido/expirado), la excepción se propaga.
        _invalidate_jwks_cache()
        jwks = await _fetch_jwks()
        return _decode(token, jwks)
