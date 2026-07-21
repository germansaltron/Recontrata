"""Tests de la verificación de JWT de Clerk (migración python-jose → PyJWT).

Se genera un par RSA propio, se publica su clave pública como JWKS (mockeando el fetch
a Clerk) y se firman tokens para ejercitar de verdad la validación: firma, expiración,
issuer, audience y selección por `kid`.
"""
import json
from datetime import datetime, timedelta, timezone

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from jwt.algorithms import RSAAlgorithm

from app import auth
from app.config import settings

KID = "test-kid-1"
ISSUER = "https://clerk.recontrata.test"

# Un solo par RSA para todos los tests (generarlo es lo caro).
_private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)


def _jwks() -> dict:
    pub = json.loads(RSAAlgorithm.to_jwk(_private_key.public_key()))
    pub.update({"kid": KID, "alg": "RS256", "use": "sig"})
    return {"keys": [pub]}


def _token(key=_private_key, kid: str = KID, **overrides) -> str:
    now = datetime.now(timezone.utc)
    claims = {"sub": "user_abc123", "iss": ISSUER, "iat": now, "exp": now + timedelta(minutes=5)}
    claims.update(overrides)
    return jwt.encode(claims, key, algorithm="RS256", headers={"kid": kid})


@pytest.fixture
def clerk_env(monkeypatch):
    monkeypatch.setattr(settings, "CLERK_ISSUER", ISSUER)
    monkeypatch.setattr(settings, "CLERK_AUDIENCE", "")
    jwks = _jwks()

    async def fake_fetch():
        return jwks

    monkeypatch.setattr(auth, "_fetch_jwks", fake_fetch)


async def test_token_valido_devuelve_claims(clerk_env):
    payload = await auth.verify_clerk_token(_token())
    assert payload["sub"] == "user_abc123"


async def test_token_expirado_se_rechaza(clerk_env):
    expired = _token(exp=datetime.now(timezone.utc) - timedelta(minutes=1))
    with pytest.raises(jwt.PyJWTError):
        await auth.verify_clerk_token(expired)


async def test_issuer_incorrecto_se_rechaza(clerk_env):
    with pytest.raises(jwt.PyJWTError):
        await auth.verify_clerk_token(_token(iss="https://atacante.test"))


async def test_kid_desconocido_se_rechaza(clerk_env):
    with pytest.raises(jwt.PyJWTError):
        await auth.verify_clerk_token(_token(kid="kid-que-no-existe"))


async def test_firma_de_otra_clave_se_rechaza(clerk_env):
    otra = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    # Mismo kid (para que encuentre una clave), pero firmado con otra privada.
    with pytest.raises(jwt.PyJWTError):
        await auth.verify_clerk_token(_token(key=otra))


async def test_audience_se_valida_cuando_esta_configurado(monkeypatch):
    monkeypatch.setattr(settings, "CLERK_ISSUER", ISSUER)
    monkeypatch.setattr(settings, "CLERK_AUDIENCE", "recontrata-api")
    jwks = _jwks()

    async def fake_fetch():
        return jwks

    monkeypatch.setattr(auth, "_fetch_jwks", fake_fetch)

    ok = await auth.verify_clerk_token(_token(aud="recontrata-api"))
    assert ok["sub"] == "user_abc123"

    with pytest.raises(jwt.PyJWTError):
        await auth.verify_clerk_token(_token(aud="otra-api"))
