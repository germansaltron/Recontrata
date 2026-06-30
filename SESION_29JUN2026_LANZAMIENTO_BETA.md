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

> ⚠️ **Nota (actualización del mismo día):** la tabla de abajo refleja el estado **ANTES** de la migración de cuentas. Más tarde ese 29 jun se **migró todo a gsaltron/germansaltron** (Railway, GitHub `germansaltron/Recontrata`, Supabase org Saltronic, Clerk/Sentry/Cloudflare). Operatividad verificada intacta. Estado actual y detalle en `Desktop\Independencia_gsaltron_BITACORA_2026-06-29.md`.

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

## 11. Migración de cuentas a gsaltron + verificación post-migración (29 jun, cierre)

Ese mismo día (en otra sesión) se ejecutó la **independencia de cuentas**: Casilisto, Recontrata y SoyMaestra se sacaron de Faymex (bodegaquilp01) y quedaron bajo **gsaltron/germansaltron**, con facturación separada por entidad. Detalle completo en `Desktop\Independencia_gsaltron_BITACORA_2026-06-29.md` y en la memoria `independencia-gsaltron-migracion`.

**Lo que toca a Recontrata:**
- **Railway** `faenascore` → transferido a gsaltron (CLI local ya logueado como gsaltron). Plan Pro este ciclo (bajar a Hobby ~27 jul).
- **GitHub** `FaenaScore` → renombrado y transferido a **`germansaltron/Recontrata`**; el `origin` del repo local (carpeta sigue siendo `Claude Code German\FaenaScore`) ya apunta ahí.
- **Supabase** → proyecto movido a la org **Saltronic** (gsaltron, Pro, Spend Cap ON); ref y API keys conservados → connection string sin cambios.
- **Clerk / Sentry / Cloudflare** → ya estaban en gsaltron.

**Verificación de operatividad independiente (post-migración) — todo 🟢:**
- `recontrata.cl` → HTTP 200, frontend carga (bundle `Dk-YUE0U`).
- `/api/health` → `{"status":"ok","database":"connected"}` → backend arriba y conectado a Supabase (Saltronic).
- Clerk `pk_live` presente en el bundle.
- `git remote` local → `germansaltron/Recontrata`. Railway CLI → `gsaltron@gmail.com`.
- **Conclusión: sin downtime, Recontrata 100% operativo bajo las cuentas nuevas.**

**Memoria reconciliada:** se actualizó `recontrata-cuentas-infraestructura` (que había quedado con el estado viejo "bajo Faymex") al estado post-migración, + el índice `MEMORY.md`, + esta nota.

---

## 12. Revisión del flujo móvil + hardening + fixes (29 jun, tarde)

Antes de invitar testers, se revisó a fondo el flujo de registro en celular (preocupaba el "magic link" en PWA iOS).

### 12.1 Hallazgo clave: Clerk ya usa código OTP, no enlace mágico
Consultando la config real de Clerk (`https://clerk.recontrata.cl/v1/environment`): `email_address_verification_strategies: ["email_code"]`. O sea, al registrarse llega un **código de 6 dígitos que se escribe en la misma app**, NO un enlace que abre otro navegador. → **El riesgo grave de iOS (magic link + contexto/cookies separados de la PWA) NO aplica.** El tutorial decía "enlace" por error (ver 12.4).

### 12.2 Hardening aplicado: usuario autenticado salta el AccessGate
`App.tsx` (commit `8d14e81`, en prod): si el usuario ya está autenticado (Clerk `SignedIn`), **no ve el gate del código**, sin importar el contexto/navegador. Evita el re-prompt del código si la sesión existe pero el flag local no. Guardado por `clerkEnabled` (no afecta mock/dev). Se decidió NO sacar `/sign-up` del gate (innecesario con OTP y dejaría registrarse a cualquiera).

### 12.3 ⚠️ Gotcha resuelto: proyecto Railway DUPLICADO
Al desplegar, el `railway up` fue a un proyecto **equivocado**: en la cuenta gsaltron hay **dos** proyectos parecidos — **`faenascore`** (minúscula, ID `7ec526bb`, service `a5ff98e5`) = **PRODUCCIÓN** (recontrata.cl), y **`FaenaScore`** (mayúscula, ID `1d85d02e`) = duplicado/extraviado sin dominio. El link local había quedado en el duplicado tras la migración. **Fix:** `railway link -p 7ec526bb-74bc-4796-bac4-4c89bde2d6bd` (siempre re-linkear por ID). Producción nunca se vio afectada. Anotado en memoria `recontrata-cuentas-infraestructura`. (El duplicado `FaenaScore` quedó con un deploy errado + un subdominio autogenerado; pendiente que el usuario decida si lo elimina.)

### 12.4 Fix de copy "enlace → código" + re-render de clip1
- Corregido el copy del registro (decía "te llega un enlace, haces clic") → **"te llega un código, lo escribes y entras"** en: guion `clip1.md` + narración/subtítulos `produce_clip1.py`. (Las menciones a "enlace" del Portal del Trabajador NO se tocaron: ahí sí es un link real.)
- **Clip1 re-renderizado** (TTS + captura + ensamblado), subido por el usuario a YouTube → **nuevo ID `Dd4jEE_6vLQ`**; `tutorials.ts` actualizado, desplegado y verificado en vivo. El video anterior (`X0NaBzalW8Y`) lo eliminó el usuario (sin impacto: la app ya apuntaba al nuevo).
- El frontend NO describe el registro como "enlace" (usa la UI de Clerk, que ya muestra el código).

### 12.5 Pendientes al cerrar
- **Ensayo en teléfono real** (Android + iPhone): instalar PWA → registrarse con el código → 1 evaluación. Riesgo ahora bajo (OTP confirmado), pero conviene antes de invitar.
- Corregir la línea del **correo** a las testers ("enlace" → "código") — la versión corregida se entregó en el chat.
- Decidir si se elimina el proyecto Railway duplicado `FaenaScore` (mayúscula).
- Invitar a Daniela, Vanessa y Joanna al beta.
- Backlog del estudio: monetización (Flow), validación legal del dato compartido, refinar SAM.
- Costos: bajar Railway Pro→Hobby (~27 jul); vigilar Spend Cap de Saltronic (Supabase).

---

*Documento generado el 29 de junio de 2026.*
