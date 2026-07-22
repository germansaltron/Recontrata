# Sesión 22-jul-2026 — Pasarela de pago Flow: de 0 a producción

> Sesión enorme. Se completó: contrato B2B + aceptación, sinceramiento del landing,
> dominio `saltronic.cl` + correo `@saltronic.cl`, y **toda la pasarela de pago Flow
> desplegada a producción**. Falta la prueba real y afinar el webhook.

---

## 1. Estado de la pasarela: EN PRODUCCIÓN ✅ (falta prueba real + webhook)

**Código desplegado a master/prod** (rama `feature/flow-checkout` mergeada, commits
`453ab3f`→`527e8a0`). Endpoints de checkout montados y verificados en prod (401 con auth).

### Lo construido (Fase 5)
- **Backend** `app/billing/checkout.py`: `start_checkout` (customer + registro de tarjeta),
  `complete_return` (crea la suscripción con trial 14d + cupón fundador), `cancel_subscription`.
- **Endpoints** `app/api/v1/billing.py`: `POST …/billing/checkout`, `POST …/billing/cancel`
  (admin), `GET /billing/return` (público, retorno de Flow).
- **Modelo**: `Subscription.pending_plan/pending_period` (migración `d3f8b1a6c9e4`, ya aplicada
  en prod).
- **Frontend** `Billing.tsx`: el botón "Mejorar" inicia el checkout real (mensual) y maneja el
  retorno (`?checkout=success|error`). `api.checkout()` / `api.cancelSubscription()`.
- **Tests**: 3 de checkout con cliente Flow simulado (172 backend + 21 frontend en total).

### QA E2E validado contra sandbox (los campos de Flow, confirmados)
Se corrió el flujo completo real (`scripts/flow_qa_probe.py`). Campos confirmados y ya en el
código:
- `create_customer` → **`customerId`**
- `register_card` → **`token`**, **`url`**
- `get_register_status` → **`status: "1"`** (tarjeta OK) + `customerId`
- `create_subscription` → **`subscriptionId`**

### Bootstrap de planes
- **Sandbox**: 4 planes creados.
- **Producción**: 4 planes creados (mismos IDs determinísticos):
  `recontrata-pro-monthly`, `recontrata-pro-annual`, `recontrata-empresa-monthly`,
  `recontrata-empresa-annual`.

### Variables en Railway (producción) — configuradas por Germán
`FLOW_API_KEY`, `FLOW_API_SECRET` (prod), `FLOW_API_BASE=https://www.flow.cl/api`,
los 4 `FLOW_PLAN_ID_*`, `BILLING_RETURN_URL=https://recontrata.cl/api/v1/billing/return`,
`FLOW_WEBHOOK_URL=https://recontrata.cl/api/v1/webhooks/flow`.

---

## 2. PENDIENTES para mañana (en orden)

### 2.1 Prueba real (valida que las credenciales prod funcionan) — PRIMERO
Entrar a la app (cuenta **gsaltron@faymex.cl**) → Suscripción → "Mejorar a Pro" → registrar
**tarjeta real** en Flow → verificar que queda en **"trialing"**. NO cobra al instante (trial
14 días; se puede cancelar antes). Al hacerlo, verificar en la DB (`subscriptions`) y en Flow
que la suscripción quedó bien.

### 2.2 ⚠️ Webhook de renovaciones (los planes prod se crearon SIN url_callback)
Cuando se corrió el bootstrap de producción, `FLOW_WEBHOOK_URL` NO estaba en el `.env`, así que
los planes de Flow prod quedaron **sin URL de notificación**. Esto NO afecta la contratación
inicial, pero sí las **notificaciones de cobro/renovación** (Flow no avisaría a la app cuando
cobre a los 14 días). **Arreglo (hay tiempo antes del primer cobro):**
- Poner `FLOW_WEBHOOK_URL=https://recontrata.cl/api/v1/webhooks/flow` en el entorno.
- Actualizar los planes con esa `urlCallback`. El `flow_client` NO tiene `edit_plan`; opciones:
  (a) agregar `plans/edit` al cliente y un script de update, o (b) eliminar y recrear los planes
  con el callback (cuidado si ya hay suscripciones vivas), o (c) revisar si Flow permite un
  webhook global en el panel.
- El endpoint `POST /api/v1/webhooks/flow` YA existe en prod (re-consulta el estado a Flow,
  idempotente por `flow_token`).

### 2.3 🧹 Restaurar el `.env` local a SANDBOX
Ahora mismo `backend/.env` tiene las credenciales de **producción** de Flow (se pusieron para el
bootstrap prod). Restaurar las de **sandbox** para que cualquier prueba local NO cobre de verdad.
Las de producción viven solo en Railway.

---

## 3. Otros hitos de hoy (ya desplegados)

- **Contrato de Suscripción B2B** en `/terminos` + gate de aceptación obligatorio al primer
  ingreso (tabla `contract_acceptances`, guarda quién/versión/cuándo/IP). Word para el abogado en
  `Downloads\CONTRATO_SUSCRIPCION_RECONTRATA_v0.1_BORRADOR.docx`. Ver `legal/` (local, no
  commiteado por el RUT personal). `CONTRACT_VERSION` en `backend/app/legal.py` y `Terms.tsx`.
- **Landing sincerado**: fuera features inexistentes (IA/API/alertas), reencuadre "listas
  negras"→"decisiones a dedo", precios netos **+ IVA** aclarados.
- **Dominio `saltronic.cl`**: registrado en NIC (titular Saltronic SpA) → Cloudflare (NS
  `romina`/`cash`) → correo **Email Routing**: `contacto@` y `facturacion@` + catch-all →
  gsaltron@gmail.com. Verificado E2E.

## 4. Cómo retomar
1. Leer este doc + `PROGRESS.md`.
2. Restaurar `.env` a sandbox (2.3).
3. Hacer la prueba real (2.1).
4. Arreglar el webhook de los planes (2.2).
5. Con eso, la pasarela queda 100% operativa (cobrando + notificando).
