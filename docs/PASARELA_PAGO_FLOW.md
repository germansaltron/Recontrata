# FaenaScore — Diseño de la pasarela de pago (Flow)

> Estado: **PROPUESTA / DISEÑO** — pendiente de aprobación antes de implementar.
> Fecha: 15-jul-2026 · Autor: sesión Claude Code · Decisor: Germán.
> Contexto: es el último pendiente de Recontrata (ver `PROGRESS.md` → "Falta monetización (Flow)").

---

## 0. Resumen en una línea

Construir un módulo de **suscripciones** que enganche los planes ya decididos (Gratis/Pro/Empresa) con la
API de **Flow** en modo **cobro recurrente**, más el **enforcement de límites por plan** dentro del producto.
Hoy no existe **nada** de esto en el código; la landing muestra precios pero los botones van al registro, no a un checkout.

---

## 1. Punto de partida (lo que ya existe y lo que falta)

| Área | Estado hoy |
|---|---|
| Precios y planes decididos | ✅ (Germán, 30-may — ver `PROPUESTA_MONETIZACION.md`) |
| Landing con precios nuevos ($49.990 / $149.990) | ✅ ya reflejado en `Landing.tsx` |
| Modelo de suscripción/plan en la DB | ❌ no existe (`organizations` no tiene `plan`, `trial`, etc.) |
| Enforcement de límites (15 trabajadores en free, etc.) | ❌ no existe — hoy no hay tope real |
| Integración Flow (cliente, firma, endpoints, webhook) | ❌ no existe (0 archivos) |
| Checkout / página de suscripción | ❌ no existe (los 3 CTA de precios van a registro) |

**Nota de proveedor:** `PROPUESTA_MONETIZACION.md` (30-may) mencionaba Webpay/Transbank; la decisión vigente es
**Flow**, que por debajo ofrece Webpay + tarjetas + transferencia. Este documento asume Flow.

---

## 2. Planes (fuente de verdad para el código)

Eje de cobro: **trabajadores activos** = trabajadores (`is_active=true`) asignados a proyectos con
`status='active'`, contados distinto. Supervisores (usuarios/`org_members`) e historial: **ilimitados en todos los planes**.

| Plan (código) | Nombre comercial | Trab. activos | Proyectos activos | Mensual CLP | Anual CLP (2 meses gratis) |
|---|---|---|---|---|---|
| `free` | Gratis "Capataz" | 15 | 1 | $0 | $0 |
| `pro` | Pro "Faena" ⭐ | 100 | ∞ | $49.990 | $499.900 |
| `empresa` | Empresa "Contratista" | 500 | ∞ | $149.990 | $1.499.900 |
| `enterprise` | Enterprise | ∞ | ∞ | Cotización (fuera de self-serve) | Contrato |

Estos límites viven como **constantes en el código** (`app/billing/plans.py`), no en la DB, porque cambian
por release, no por dato. Los `planId` que Flow genera al crear cada plan se guardan en configuración (env).

Trial: **14 días** del plan Pro (nativo en Flow vía `trial_period_days`).

---

## 3. Enfoque de integración con Flow

### 3.1 Decisión: API de **Suscripciones** (cobro recurrente automático), no pago único

Flow tiene dos caminos:

- **Pago único** (`payment/create`): sirve para una compra puntual; obliga a gestionar renovaciones a mano. ❌
- **Suscripciones** (`customer` + `plans` + `subscription`): Flow **cobra la tarjeta tokenizada automáticamente**
  cada período y reintenta si falla (dunning). ✅ Es el modelo correcto para un SaaS mensual/anual con trial.

### 3.2 API de Flow — referencia verificada

- Base URL: **prod** `https://www.flow.cl/api` · **sandbox** `https://sandbox.flow.cl/api`
- **Firma** (todas las requests): ordenar parámetros alfabéticamente, concatenar `nombre+valor`,
  firmar con **HMAC-SHA256** usando `secretKey` → parámetro `s`.
- Credenciales: `apiKey` + `secretKey` (por comercio; sandbox y prod son distintas).
- Endpoints usados:
  - `POST customer/create` (`name`, `email`, `externalId`) → devuelve `customerId`.
  - `POST customer/register` (`customerId`, `url_return`) → devuelve `url` + `token` para registrar tarjeta.
  - `GET customer/getRegisterStatus` (`token`) → resultado del registro de tarjeta.
  - `POST plans/create` (`amount`, `currency`=CLP, `interval` 3=mensual/4=anual, `trial_period_days`) → `planId`.
  - `POST subscription/create` (`planId`, `customerId`, `trial_period_days`) → suscripción.
  - `GET payment/getStatus` (`token`) — para confirmar cobros.
- **Webhook** (`urlConfirmation`): notificación **servidor-a-servidor** que Flow POSTea cuando se concreta un
  cobro/evento; **no** confía en nuestra auth (Clerk). Distinto de `urlReturn` (redirección del navegador del usuario).

### 3.3 Flujo de alta (checkout)

```
Usuario (org, logueado) elige plan Pro mensual
  → Backend: crea/recupera Flow customer (externalId = org_id)  [customer/create]
  → Backend: inicia registro de tarjeta                          [customer/register] → url Flow
  → Redirige el navegador a la URL de Flow (registro de tarjeta)
  → Flow redirige de vuelta a urlReturn (/billing/return?token=)
  → Backend: confirma tarjeta                                    [customer/getRegisterStatus]
  → Backend: crea la suscripción con trial 14 días               [subscription/create]
  → Suscripción queda en estado "trialing"
Luego, cada período:
  → Flow cobra la tarjeta y llama urlConfirmation (webhook)
  → Backend verifica firma, registra payment_event y actualiza el estado de la suscripción
```

El plan **Free no toca Flow**: es solo enforcement de límites. Solo Pro/Empresa crean customer+subscription.

---

## 4. Modelo de datos (nuevas tablas)

Migración Alembic nueva. Dos tablas; `organizations` no cambia (el plan se deriva de la suscripción).

### 4.1 `subscriptions` (1 activa por organización)

| Columna | Tipo | Notas |
|---|---|---|
| `id` | UUID PK | |
| `org_id` | UUID FK → organizations (unique) | 1:1 con la org |
| `plan` | str | `free` \| `pro` \| `empresa` \| `enterprise` |
| `billing_period` | str | `monthly` \| `annual` (null en free) |
| `status` | str | `trialing` \| `active` \| `past_due` \| `canceled` \| `incomplete` |
| `flow_customer_id` | str null | hash de Flow |
| `flow_subscription_id` | str null | id de la suscripción en Flow |
| `flow_plan_id` | str null | planId de Flow usado |
| `trial_ends_at` | datetime null | |
| `current_period_start` | datetime null | |
| `current_period_end` | datetime null | usada para suspender al vencer sin pago |
| `canceled_at` | datetime null | |
| `created_at` / `updated_at` | datetime | |

Toda org **nace en `free`** (se crea una fila `free` al crear la organización).

### 4.2 `payment_events` (auditoría de webhooks/cobros)

| Columna | Tipo | Notas |
|---|---|---|
| `id` | UUID PK | |
| `org_id` | UUID FK | |
| `subscription_id` | UUID FK null | |
| `flow_event_type` | str | tipo reportado por Flow |
| `flow_token` | str null | token del evento |
| `commerce_order` | str null | idempotencia |
| `status` | str | resultado del cobro |
| `amount` | int null | CLP |
| `signature_valid` | bool | resultado de verificar la firma |
| `raw_payload` | JSONB | payload completo para trazabilidad |
| `processed_at` | datetime null | null = recibido pero no procesado |
| `created_at` | datetime | |

Idempotencia: índice único por (`flow_token`) o (`commerce_order`) para no procesar dos veces un reintento de Flow.

---

## 5. Endpoints backend (nuevos)

Router `app/api/v1/billing.py` + webhook público aparte.

| Método | Ruta | Auth | Función |
|---|---|---|---|
| GET | `/api/v1/organizations/{org_id}/billing/subscription` | Clerk | Estado actual: plan, status, uso (X/límite), trial |
| POST | `/api/v1/organizations/{org_id}/billing/checkout` | Clerk | Body `{plan, billing_period}` → inicia registro tarjeta, devuelve URL de Flow |
| POST | `/api/v1/organizations/{org_id}/billing/cancel` | Clerk | Cancela la suscripción (queda hasta fin de período) |
| GET | `/api/v1/billing/return` | pública | `url_return` de Flow: confirma tarjeta y crea la suscripción; redirige al front |
| POST | `/api/v1/webhooks/flow` | **pública, firmada** | `urlConfirmation`: verifica firma, registra `payment_event`, actualiza suscripción |

El webhook **no** usa Clerk (Flow no puede autenticarse); se protege verificando la firma `s` y re-consultando
a Flow (`getStatus`) antes de dar por bueno un cobro. Debe quedar **excluido** de cualquier middleware de auth
y del rewrite del SPA.

---

## 6. Enforcement de límites (el "candado" del freemium)

Servicio `app/billing/enforcement.py` con `assert_can_add_worker(org)` / `assert_can_add_project(org)`.

- Se llama en los endpoints que **hacen crecer** el uso:
  - `POST …/projects/{id}/workers` (asignar trabajador a proyecto)
  - `POST …/workers/import` (import masivo — validar el total resultante)
  - `POST …/projects` (crear proyecto, para el tope de 1 proyecto activo del free)
- Cálculo de "trabajadores activos": `COUNT(DISTINCT worker_id)` en `project_workers` unido a `projects`
  con `status='active'` y `workers.is_active=true`, filtrado por `org_id`.
- Al exceder → **HTTP 402 Payment Required** con un cuerpo estructurado
  (`{code: "PLAN_LIMIT", limit, current, plan}`) que el front convierte en el **paywall emocional**
  ("no pierdas el historial que ya construiste").
- **El historial nunca se borra** al bajar de plan (refuerza switching cost). Un downgrade que deje a la org
  por encima del tope **bloquea agregar** más, pero conserva y muestra todo lo existente (solo lectura para el excedente).

Estados de suscripción → acceso:
- `trialing` / `active` → acceso completo al plan.
- `past_due` → **período de gracia** (propuesto: 7 días) con banner; luego se degrada a `free` (no se borra nada).
- `canceled` → al terminar el período pagado, vuelve a `free`.

---

## 7. Frontend (nuevo)

- Página **`Suscripción`** (`pages/Billing.tsx`) en el AppShell: plan actual, uso (barra X/límite),
  botones Upgrade, botón Cancelar, estado de trial ("te quedan N días").
- **Paywall modal** reutilizable: aparece ante un 402 `PLAN_LIMIT`; copy de "no pierdas el historial".
- CTAs de precios en `Landing.tsx`: si el usuario está logueado → `checkout`; si no → registro (como hoy).
- Página **`/billing/return`**: maneja el regreso desde Flow (éxito/fracaso del registro de tarjeta) con `sonner`.
- Banner global de `past_due` (gracia) y de trial por vencer.

---

## 8. Configuración y secretos (Railway)

Nuevas variables (sandbox primero, luego prod):

```
FLOW_API_KEY=
FLOW_SECRET_KEY=
FLOW_API_BASE=https://sandbox.flow.cl/api      # prod: https://www.flow.cl/api
FLOW_PLAN_ID_PRO_MONTHLY=
FLOW_PLAN_ID_PRO_ANNUAL=
FLOW_PLAN_ID_EMPRESA_MONTHLY=
FLOW_PLAN_ID_EMPRESA_ANNUAL=
BILLING_RETURN_URL=https://faenascore-production.up.railway.app/billing/return
FLOW_WEBHOOK_URL=https://faenascore-production.up.railway.app/api/v1/webhooks/flow
```

Los `planId` se generan **una vez** con un script (`scripts/flow_bootstrap_plans.py`) que llama `plans/create`
y devuelve los IDs a pegar en Railway. Nunca commitear `apiKey`/`secretKey`.

---

## 9. Plan de implementación (fases sugeridas)

1. **Modelo + migración** (`subscriptions`, `payment_events`) + toda org nace en `free`.
2. **Enforcement de límites** (402 `PLAN_LIMIT`) + tests. *Ya aporta valor solo (candado freemium) sin cobro.*
3. **Cliente Flow** (`app/billing/flow_client.py`): firma HMAC + wrappers de endpoints + tests de firma.
4. **Script bootstrap de planes** en Flow (sandbox) → obtener `planId`s.
5. **Endpoints checkout / return / cancel** + creación de customer/subscription.
6. **Webhook** `urlConfirmation` firmado + idempotencia + actualización de estados.
7. **Frontend**: página Suscripción, paywall modal, return, banners.
8. **QA end-to-end en sandbox** (tarjetas de prueba de Flow) → luego switch a prod.

---

## 10. Decisiones de negocio (resueltas — Germán, 15-jul-2026)

1. **Cobro recurrente (auto-cobro) confirmado.** Se usa la API de Suscripciones de Flow. ✅
2. **Periodicidad v1: mensual y anual.** Se crean en Flow los 4 planes de pago
   (Pro mensual/anual, Empresa mensual/anual). El anual aplica "2 meses gratis" (precio anual ya definido). ✅
3. **Transferencia + factura electrónica (SII): fuera de la v1.** V1 = solo tarjeta/Webpay self-serve vía Flow.
   El track de transferencia+factura se maneja manual por ahora y se automatiza en una fase posterior. ✅
4. **Descuento fundador –50% de por vida: con Cupones de Flow.** Se crea un cupón recurrente –50% y se aplica
   a la suscripción de los primeros 10 design partners al momento de `subscription/create`. ✅
5. **Período de gracia en `past_due`: 7 días** (valor por defecto adoptado; ajustable). ✅
6. **Política de excedente al bajar de plan: conservar todo, bloquear agregar** (el historial nunca se borra). ✅

---

## Fuentes

- API de Flow (verificada): https://developers.flow.cl/en/api · https://www.flow.cl/docs/api.html
- Cliente oficial PHP (referencia de firma/endpoints): https://github.com/flowcl/PHP-API-CLIENT
- Decisiones de pricing: `PROPUESTA_MONETIZACION.md` · Diferimiento del cobro en beta: `BETA_SETUP.md`
