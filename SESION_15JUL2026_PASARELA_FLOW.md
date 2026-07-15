# Sesión 15-jul-2026 — Pasarela de pago (Flow)

> Trabajo sobre el **último pendiente de Recontrata (FaenaScore)**: la monetización con **Flow**.
> Detalle de arquitectura y decisiones en `docs/PASARELA_PAGO_FLOW.md`; estado vivo en `PROGRESS.md`.

## Resumen

Se pasó de **0% de pasarela** a tener **construido y probado todo lo que no depende de la cuenta Flow**:
diseño aprobado, modelo de suscripción, enforcement de límites (candado freemium), frontend del candado,
cliente Flow con firma verificada y webhook con máquina de estados. Lo único que falta es **ejecutar contra
el sandbox de Flow** (crear planes, checkout, QA E2E), que necesita las credenciales de la cuenta empresa.

**Backend 114/114 tests · Frontend build+lint · CI verde · todo en `master`.**

## Punto de partida

- El repo principal `germansaltron/Recontrata` no estaba clonado localmente; se clonó y montó el entorno
  (backend FastAPI + venv, frontend React 19/Vite, Postgres en Docker puerto **5434** por override local).
- La pasarela no estaba empezada: la landing mostraba precios pero los botones iban al registro; sin modelo
  de suscripción, sin enforcement, sin integración Flow. Diferida a propósito en el beta (`BETA_SETUP.md`).

## Decisiones de negocio (Germán, 15-jul)

1. Cobro **recurrente** (API de Suscripciones de Flow).
2. Periodicidad v1: **mensual y anual**.
3. Transferencia + factura electrónica (SII): **fuera de la v1** (v1 = tarjeta/Webpay self-serve).
4. Descuento fundador –50% de por vida: **con Cupones de Flow**.
5. Gracia `past_due` = **7 días**; excedente al bajar de plan = **conservar todo, bloquear agregar**.

## Lo construido (por commit)

| Commit | Qué |
|---|---|
| `8cad640` | Diseño de la pasarela (`docs/PASARELA_PAGO_FLOW.md`): arquitectura, API de Flow verificada, 8 fases, decisiones. |
| `3057060` | **Fase 1-2**: modelo `Subscription`+`PaymentEvent` (migración `1ac66b2f6de5`, backfill a `free`), catálogo de planes en código, **enforcement** → HTTP 402 `PLAN_LIMIT` en crear proyecto / asignar trabajadores / reactivar proyecto. `GET .../billing/subscription`. 10 tests. |
| `e6a569f` | **Frontend del candado freemium**: página Suscripción (`/app/suscripcion`), paywall modal global (cualquier 402 lo abre), chip de plan/uso en el sidebar, CTAs de la landing. Verificado E2E en navegador. |
| `c7e32e8` | **Fase 3+6**: cliente Flow (`flow_client.py`, firma HMAC calcada del cliente oficial), `service.py` (máquina de estados idempotente), webhook `POST /api/v1/webhooks/flow`, `scripts/flow_bootstrap_plans.py`. Migración `22502bd4cbd9` (org_id nullable). 17 tests. |

### Reglas de negocio clave del enforcement
- **Trabajador activo** = trabajador `is_active` asignado a proyecto con `status='active'` (contado distinto).
  **Proyecto activo** = `status='active'`. Supervisores e historial: ilimitados en todos los planes.
- Límites: **free** 15 trab./1 proyecto · **pro** 100/∞ · **empresa** 500/∞ · **enterprise** ∞.
- Fuera de `trialing`/`active` la suscripción **degrada a límites free**; el historial **nunca se borra**.

### Decisión técnica verificada
- **Flow no firma el webhook**: solo envía el `token`. El handler **re-consulta `payment/getStatus`**
  (request firmada con nuestro secret) para obtener el estado autoritativo. Idempotencia por `flow_token`.
- Firma de Flow (del cliente oficial `flowcl/PHP-API-CLIENT`): claves ordenadas, concatenación `clave+valor`,
  `apiKey` incluido en la firma, HMAC-SHA256 hex, parámetro `s` agregado aparte. GET=query, POST=form-urlencoded.

## Lo que falta (necesita la cuenta Flow — sandbox)

1. **Ejecutar** `python scripts/flow_bootstrap_plans.py` con `FLOW_API_KEY`/`FLOW_API_SECRET` → pegar los 4
   `planId` en Railway.
2. **Fase 5**: endpoints checkout / return / cancel + creación de customer/subscription + conectar el botón
   "Mejorar" del frontend (hoy muestra un toast honesto "el pago se habilita muy pronto").
3. **Fase 8**: QA E2E en sandbox con tarjetas de prueba de Flow → switch a producción.

> Todo el código y su lógica ya están construidos y probados; solo queda la **ejecución real contra Flow**.

## Cómo correr localmente

```bash
docker compose up -d                     # Postgres (override local: 5434)
cd backend && source .venv/Scripts/activate
alembic upgrade head
python -m uvicorn app.main:app --port 8001 --host 127.0.0.1
# Frontend (usar localhost, no 127.0.0.1, por CORS):
cd frontend && npx vite --port 5173
# Tests (DB de test aparte):
#   CREATE DATABASE faenascore_test;  (una vez)
cd backend && TEST_DATABASE_URL="postgresql+asyncpg://faenascore:faenascore_dev@localhost:5434/faenascore_test" python -m pytest -q
```

Notas de entorno: prod **no** tiene auto-deploy (deploy = `railway up`); el `Dockerfile` corre
`alembic upgrade head` al arrancar, así que las migraciones se aplican solas al desplegar.

## Estado de despliegue (al cierre del 15-jul)

- **Producción intacta y operativa**: recontrata.cl 200, API `/api/health` 200 (`database: connected`).
  **Nada de esta sesión está desplegado** (no hay auto-deploy; no se corrió `railway up`). Los testers siguen
  en la versión previa → nada se rompió para ellos.
- **⚠️ Antes de desplegar el enforcement de planes durante el beta**: la migración pone a todas las orgs en
  `free` (tope 15 trab./1 proyecto) y los testers son design partners con acceso libre. Ver el bloque
  **"⚠️ ESTADO DE DESPLIEGUE"** al inicio de `PROGRESS.md` para las 3 opciones (plan alto a testers / bypass /
  desplegar recién con Flow).

## Fixes de feedback de tester (mismo día)

Además del trabajo de Flow, se atendió feedback de una tester (nota de voz + mensaje):
- ✅ **Copy del ROI** del plan Pro más claro (commit `085e855`).
- ✅ **Offline iOS**: metas `apple-mobile-web-app-*` + banner "Agregar a inicio" (commit `206d5ab`).
- ⚠️ **Doble email de código**: es config de Clerk (dashboard), no de nuestro código.
- 🕓 **Voz de tutoriales**: pendiente (re-render de clips).

(El detalle del feedback, con datos de la tester, está en un doc **local no versionado** por privacidad.)
