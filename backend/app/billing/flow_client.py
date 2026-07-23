"""Cliente de la API de Flow (pasarela de pago chilena).

La firma está calcada del cliente oficial de Flow (flowcl/PHP-API-CLIENT,
lib/FlowApi.class.php):

    $params = array("apiKey" => $this->apiKey) + $params;
    $params["s"] = sign($params);   // s NO entra en su propio cálculo
    sign(): sort(keys); toSign = concat(key + value); hash_hmac('sha256', toSign, secretKey)

- GET  → parámetros en query string.
- POST → parámetros en form-urlencoded (application/x-www-form-urlencoded).
- La firma es HMAC-SHA256 en hex minúscula sobre los valores CRUDOS (sin URL-encode),
  con las claves ordenadas alfabéticamente y concatenadas como `clave+valor` sin separador.

Base sandbox: https://sandbox.flow.cl/api · producción: https://www.flow.cl/api

Nota: la firma y la mecánica GET/POST están verificadas contra el cliente oficial.
Los nombres/párametros de algunos endpoints de suscripción (cupones, cancelación) deben
reconfirmarse contra el sandbox real al cablear la Fase 5; van marcados abajo.
"""

import hashlib
import hmac
from typing import Any

import httpx

from app.config import settings


class FlowError(Exception):
    """Error devuelto por Flow (o de transporte al invocarlo)."""

    def __init__(self, message: str, code: Any = None, http_status: int | None = None):
        super().__init__(message)
        self.code = code
        self.http_status = http_status


class FlowClient:
    def __init__(
        self,
        api_key: str | None = None,
        secret_key: str | None = None,
        base_url: str | None = None,
        http_client: httpx.AsyncClient | None = None,
    ):
        self.api_key = api_key if api_key is not None else settings.FLOW_API_KEY
        self.secret_key = secret_key if secret_key is not None else settings.FLOW_API_SECRET
        self.base_url = (base_url if base_url is not None else settings.FLOW_API_BASE).rstrip("/")
        # Cliente httpx inyectable (para tests con transporte mock).
        self._client = http_client

    # --- Firma ---

    def sign(self, params: dict[str, str]) -> str:
        """HMAC-SHA256 (hex) de las claves ordenadas concatenadas como clave+valor."""
        to_sign = "".join(f"{k}{params[k]}" for k in sorted(params))
        return hmac.new(self.secret_key.encode("utf-8"), to_sign.encode("utf-8"), hashlib.sha256).hexdigest()

    def _prepare(self, params: dict[str, Any]) -> dict[str, str]:
        """Agrega apiKey, normaliza a string, descarta None y firma. Devuelve params + s."""
        if not self.api_key or not self.secret_key:
            raise FlowError("Faltan credenciales de Flow (FLOW_API_KEY / FLOW_API_SECRET)")
        prepared: dict[str, str] = {"apiKey": self.api_key}
        for key, value in params.items():
            if value is None:
                continue
            prepared[key] = _to_str(value)
        prepared["s"] = self.sign(prepared)
        return prepared

    # --- Transporte ---

    async def _request(self, method: str, service: str, params: dict[str, Any]) -> dict[str, Any]:
        prepared = self._prepare(params)
        url = f"{self.base_url}/{service}"
        client = self._client or httpx.AsyncClient(timeout=20.0)
        owns_client = self._client is None
        try:
            if method == "GET":
                resp = await client.get(url, params=prepared)
            else:
                resp = await client.post(url, data=prepared)
        except httpx.HTTPError as e:
            raise FlowError(f"Error de transporte con Flow: {e}") from e
        finally:
            if owns_client:
                await client.aclose()

        try:
            data = resp.json() if resp.content else {}
        except ValueError:
            data = {}
        if resp.status_code >= 400:
            raise FlowError(
                (data.get("message") if isinstance(data, dict) else None) or f"Flow HTTP {resp.status_code}",
                code=data.get("code") if isinstance(data, dict) else None,
                http_status=resp.status_code,
            )
        return data if isinstance(data, dict) else {"data": data}

    async def get(self, service: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        return await self._request("GET", service, params or {})

    async def post(self, service: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        return await self._request("POST", service, params or {})

    # --- Clientes (customer) ---

    async def create_customer(self, name: str, email: str, external_id: str) -> dict[str, Any]:
        """POST customer/create → { customerId, ... }."""
        return await self.post("customer/create", {"name": name, "email": email, "externalId": external_id})

    async def register_card(self, customer_id: str, url_return: str) -> dict[str, Any]:
        """POST customer/register → { url, token } (redirigir al usuario a url?token=)."""
        return await self.post("customer/register", {"customerId": customer_id, "url_return": url_return})

    async def get_register_status(self, token: str) -> dict[str, Any]:
        """GET customer/getRegisterStatus → resultado del registro de tarjeta."""
        return await self.get("customer/getRegisterStatus", {"token": token})

    async def list_customers(
        self, start: int = 0, limit: int = 100, filter: str | None = None, status: int | None = None
    ) -> dict[str, Any]:
        """GET customer/list → { total, hasMore, data: [ {customerId, externalId, ...}, ... ] }.
        `filter` busca por nombre del cliente. `limit` máx 100."""
        return await self.get(
            "customer/list", {"start": start, "limit": limit, "filter": filter, "status": status}
        )

    # --- Planes (plans) ---

    async def create_plan(
        self,
        plan_id: str,
        name: str,
        amount: int,
        currency: str = "CLP",
        interval: int = 3,
        trial_period_days: int = 0,
        url_callback: str | None = None,
    ) -> dict[str, Any]:
        """POST plans/create. interval: 1=diario, 2=semanal, 3=mensual, 4=anual.
        Usado por scripts/flow_bootstrap_plans.py (Fase 4)."""
        return await self.post(
            "plans/create",
            {
                "planId": plan_id,
                "name": name,
                "amount": amount,
                "currency": currency,
                "interval": interval,
                "trial_period_days": trial_period_days,
                "urlCallback": url_callback,
            },
        )

    async def edit_plan(self, plan_id: str, url_callback: str) -> dict[str, Any]:
        """POST plans/edit → actualiza la urlCallback de un plan existente.

        Restricción de Flow: si el plan YA tiene suscriptores, solo se puede editar
        `trial_period_days`; el resto de campos (incl. urlCallback) queda de solo lectura.
        Por eso hay que fijar el callback ANTES de la primera suscripción."""
        return await self.post("plans/edit", {"planId": plan_id, "urlCallback": url_callback})

    async def get_plan(self, plan_id: str) -> dict[str, Any]:
        """GET plans/get → datos del plan (para verificar la urlCallback aplicada)."""
        return await self.get("plans/get", {"planId": plan_id})

    # --- Suscripciones (subscription) ---
    # NOTA: los nombres de parámetros de cupón/cancelación deben reconfirmarse contra
    # el sandbox real al cablear la Fase 5.

    async def create_subscription(
        self,
        plan_id: str,
        customer_id: str,
        trial_period_days: int | None = None,
        coupon_id: str | None = None,
        subscription_start: str | None = None,
    ) -> dict[str, Any]:
        """POST subscription/create → { subscriptionId, status, ... }."""
        return await self.post(
            "subscription/create",
            {
                "planId": plan_id,
                "customerId": customer_id,
                "trial_period_days": trial_period_days,
                "couponId": coupon_id,
                "subscription_start": subscription_start,
            },
        )

    async def get_subscription(self, subscription_id: str) -> dict[str, Any]:
        """GET subscription/get → estado de la suscripción."""
        return await self.get("subscription/get", {"subscriptionId": subscription_id})

    async def cancel_subscription(self, subscription_id: str, at_period_end: bool = True) -> dict[str, Any]:
        """POST subscription/cancel. at_period_end=True cancela al fin del período pagado."""
        return await self.post(
            "subscription/cancel",
            {"subscriptionId": subscription_id, "at_period_end": 1 if at_period_end else 0},
        )

    # --- Pagos (payment) ---

    async def get_payment_status(self, token: str) -> dict[str, Any]:
        """GET payment/getStatus → estado autoritativo de un pago (status: 1..4)."""
        return await self.get("payment/getStatus", {"token": token})


def _to_str(value: Any) -> str:
    """Serializa como Flow espera: bool → '1'/'0', el resto → str()."""
    if isinstance(value, bool):
        return "1" if value else "0"
    return str(value)
