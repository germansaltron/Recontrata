"""Tests de la resolución de IP para el rate limiting (M3).

La clave del límite DEBE ser el IP real del cliente, no el del proxy (Cloudflare/
Railway): si no, todos los clientes comparten una clave y uno agota a todos.
"""
from starlette.requests import Request

from app.ratelimit import client_ip


def _request(headers: dict[str, str], client_host: str = "9.9.9.9") -> Request:
    scope = {
        "type": "http",
        "headers": [(k.lower().encode(), v.encode()) for k, v in headers.items()],
        "client": (client_host, 12345),
    }
    return Request(scope)


def test_cf_connecting_ip_tiene_prioridad():
    r = _request({"CF-Connecting-IP": "1.1.1.1", "X-Forwarded-For": "2.2.2.2"})
    assert client_ip(r) == "1.1.1.1"


def test_x_forwarded_for_toma_el_primero():
    r = _request({"X-Forwarded-For": "3.3.3.3, 4.4.4.4"})
    assert client_ip(r) == "3.3.3.3"


def test_cae_al_remote_address_sin_headers_de_proxy():
    r = _request({}, client_host="5.5.5.5")
    assert client_ip(r) == "5.5.5.5"
