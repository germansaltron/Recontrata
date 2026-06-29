# Sesión 29 jun 2026 — Lanzamiento del beta + inventario de cuentas

> Continuación de `SESION_28JUN2026_ESTUDIO_PRECIOS.md`. Producto: **Recontrata**.
> Del estudio de precios se pasó a: corregir datos heredados → desplegar a prod → habilitar el beta cerrado → revisar cuentas y costos.

---

## 1. Prerrequisitos del beta — implementados en código (commit 7bfcd2a)

- **Sentry**: backend (FastAPI, `SENTRY_DSN`) + frontend (`@sentry/react`, `VITE_SENTRY_DSN`), ambos **no-op si no hay DSN**. `send_default_pii=False` para no filtrar datos de trabajadores.
- **Botón de feedback** flotante (`VITE_FEEDBACK_URL`), oculto si no está seteado.
- **Dockerfile**: declara los nuevos `VITE_*` como build args (Railway los inyecta).
- `.env.example` (backend + frontend nuevo) + **`BETA_SETUP.md`** (guía de pasos manuales).
- **Gotcha clave**: con las `VITE_*` de Sentry/feedback vacías, Vite hace **tree-shaking** y elimina ese código → el bundle queda **idéntico** (mismo hash). No es un deploy fallido; el bundle cambia recién cuando se setean las env vars. Verificado.

## 2. Clerk → producción (pk_live) — ✅ HECHO Y VERIFICADO

- Instancia **Production** creada; dominio **`clerk.recontrata.cl`** verificado por DNS (estado "Connected").
- Variables en Railway: `VITE_CLERK_PUBLISHABLE_KEY=pk_live`, `CLERK_SECRET_KEY=sk_live`, `CLERK_JWKS_URL=https://clerk.recontrata.cl/.well-known/jwks.json`, `CLERK_ISSUER=https://clerk.recontrata.cl` (las 2 URLs las cargué por CLI con `--skip-deploys`), `CLERK_AUDIENCE` vacía. `AUTH_MOCK_ENABLED=False`.
- **Primer usuario en prod creado** y login E2E verificado (el backend valida el token contra el JWKS de prod).

## 3. Sentry — ✅ HECHO

- Cuenta Sentry `personal-g34` (la misma que tiene `casilisto-*`). Proyectos creados: **`recontrata-backend`** (FastAPI) y **`recontrata-frontend`** (React).
- DSN en Railway (`SENTRY_DSN`, `VITE_SENTRY_DSN`). Verificado: log de arranque del backend dice `Sentry inicializado · environment=production`; el código de Sentry aparece en el bundle del frontend.

## 4. Canal de feedback — ✅ HECHO (opción WhatsApp)

- El usuario optó por que el botón abra WhatsApp en vez de un formulario. `VITE_FEEDBACK_URL=https://wa.me/56935652743?text=...` en Railway. Verificado: la URL quedó horneada en el bundle.

## 5. Estado del beta: **LISTO PARA INVITAR**

| Prerrequisito | Estado |
|---|---|
| Clerk pk_live | ✅ |
| Sentry (observabilidad) | ✅ |
| Canal de feedback | ✅ |
| AccessGate (código `recontrata2211`) | ✅ |

Para invitar: compartir `recontrata.cl` + código `recontrata2211`; registrarse con correo real; botón "Feedback" abajo a la derecha → WhatsApp del fundador. Recordatorio legal: al cargar trabajadores reales se tratan datos de terceros (Ley 19.628/21.719); intra-org con consentimiento es legítimo (el flujo de consentimiento + Portal del Trabajador ya está construido).

## 6. Cómo se despliega (operativo)

- **`railway up`** desde la raíz (sube el working dir). **NO** hay auto-deploy desde GitHub (`source.repo = null`).
- **Trampa de variables**: setear una variable en el panel web **dispara un redeploy** del último *source* (que puede ser viejo). Por eso se usó `railway variable set ... --skip-deploys` y un único `railway up` al final.
- Las `VITE_*` son **build-time**: requieren rebuild (`railway up`) para tomar efecto.

## 7. Inventario de cuentas e infraestructura (verificado 29 jun)

| Plataforma | Cuenta | Verificación |
|---|---|---|
| **Railway** (hosting) | **bodegaquilp01@gmail.com** (Faymex), workspace `german-faymex` | `railway whoami` ✅ |
| **GitHub** (repo `German-Faymex/FaenaScore`) | **German-Faymex** (= bodegaquilp01) | git remote ✅ |
| **Supabase** (base de datos, `aws-1-sa-east-1.pooler.supabase.com`) | ⚠️ **por verificar** | host confirmado; cuenta no |
| **Clerk** (auth) | "Personal workspace" (Hobby) — ⚠️ qué Google account, por verificar | — |
| **Sentry** (errores) | org `personal-g34` (tiene `casilisto-*`) — ⚠️ email por verificar | — |
| **OpenAI** (TTS de videos) | la de `openai_key.txt` — ⚠️ por verificar | — |
| **YouTube** (videos tutoriales) | ⚠️ por verificar qué cuenta Google | — |
| **DNS / dominio `recontrata.cl`** | ⚠️ por verificar registrador/proveedor | — |

## 8. ¿Quién paga el consumo? (verificado)

- **El sistema corriendo NO consume ninguna API de IA de pago.** El backend no tiene `openai/anthropic/gemini` en dependencias; su única llamada saliente es a Clerk por el JWKS (gratis). El score es promedio ponderado, no IA.
- **Cobro real hoy → Railway → bodegaquilp01 (Faymex)** (Hobby ~US$5/mes + uso; para beta de bajo tráfico, pocos dólares/mes).
- **Free tier (no cobran aún)**: Clerk (Hobby), Sentry (Developer).
- **Supabase**: por verificar si es free o de pago.
- **OpenAI**: costo **puntual** del TTS de los videos, a la cuenta de `openai_key.txt`. NO es costo de operación de la app.

## 9. Tema abierto: mover Recontrata a cuenta personal (gsaltron)

Recontrata es un proyecto **personal** pero vive en cuentas de **Faymex** (Railway + GitHub), y **Faymex paga la operación** (Railway). Para personalizarlo:
- **Railway** → se puede transferir vía Dashboard → proyecto → Settings → **Transfer project** a un workspace de gsaltron (la cuenta destino acepta). Tras transferir: `railway login` (gsaltron) + `railway link`. La DB **no** está en Railway (está en Supabase), así que la transferencia es liviana.
- **El par clave a mover es Railway + Supabase** (hosting + datos). GitHub, Clerk y Sentry son decisiones aparte (Clerk/Sentry no tienen traspaso limpio entre cuentas; se recrearían si se quiere todo prolijo).

## 10. Pendientes

- **Verificar cuenta + plan de Supabase** (siguiente dato clave de costos).
- Decidir destino de cada plataforma de la tabla §7.
- (Beta) invitar a los primeros testers de confianza.
- (Backlog del estudio) monetización con Flow, validación legal del dato compartido, refinar SAM con `.xlsx` del SII + Barómetro SICEP.

---

*Documento generado el 29 de junio de 2026.*
