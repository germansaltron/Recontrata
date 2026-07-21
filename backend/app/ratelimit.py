"""Rate limiting (slowapi) para los endpoints PÚBLICOS (sin Clerk).

La clave del límite es el IP REAL del cliente: detrás de Cloudflare/Railway,
`request.client.host` es el proxy (todos los clientes compartirían una sola clave y
un cliente agotaría el límite de todos). Por eso se lee `CF-Connecting-IP` (lo pone
Cloudflare con el IP del visitante) y se cae a `X-Forwarded-For`.

Storage in-memory: correcto con 1 réplica en Railway. Con >1 réplica el límite sería
por-réplica (límite efectivo = N × límite), aceptable como protección anti-abuso.

Solo se limitan los endpoints abiertos (webhook de Flow, Portal del Trabajador). El
webhook de WhatsApp/Meta NO se limita a propósito: ya lo protege la firma HMAC y Meta
reintenta —un 429 podría hacer que marque el endpoint como no saludable.
"""
from fastapi import Request
from slowapi import Limiter
from slowapi.util import get_remote_address


def client_ip(request: Request) -> str:
    cf = request.headers.get("CF-Connecting-IP")
    if cf:
        return cf.strip()
    xff = request.headers.get("X-Forwarded-For")
    if xff:
        return xff.split(",")[0].strip()
    return get_remote_address(request)


limiter = Limiter(key_func=client_ip)
