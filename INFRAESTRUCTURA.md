# Infraestructura — Recontrata

> Estado de la infraestructura de Recontrata (recontrata.cl) y bitácora de cambios.
> Este repo es el de Recontrata (nombre técnico histórico: FaenaScore).

## Cuentas y hosting (bajo gsaltron, post-migración 29 jun 2026)

- **Railway** (cuenta `germansaltron` / gsaltron@gmail.com). Proyecto de producción =
  **`Recontrata`** (renombrado desde `faenascore` el 1 jul 2026; el rename NO cambia el ID).
  - **Project ID:** `7ec526bb-74bc-4796-bac4-4c89bde2d6bd` · **Service:** `a5ff98e5`.
  - Sirve **recontrata.cl**. **Deploy = AUTO desde GitHub** (desde 20-jul-2026): el proyecto
    tiene conectado el source repo `germansaltron/Recontrata`, branch `master`. **Cada push a
    master despliega solo.** ⚠️ `git push` a master = deploy a producción.
  - **Plan B de deploy** (si el auto-deploy falla): `./deploy.sh` en la raíz usa un **project
    token** (`RAILWAY_TOKEN` en `.railway-token`, gitignored), porque el Railway CLI de este
    equipo está logueado en la cuenta de **Faymex** (bodegaquilp01), NO en gsaltron → un
    `railway up` normal apunta al workspace equivocado. Ver cabecera de `deploy.sh`.
  - Plan Railway en **Pro** → bajar a **Hobby** antes del ~27-29 jul.
- **GitHub** = `germansaltron/Recontrata` (repo renombrado desde `FaenaScore`). El repo local
  vive en `C:\Users\JEF_INT\Claude Code German\FaenaScore` con `origin` a `germansaltron/Recontrata`.
- **DB** = **Supabase**, org **Saltronic** (Pro, Spend Cap ON). Pooler transaction mode
  (puerto 6543, host `aws-1-sa-east-1.pooler.supabase.com`).
- **Dominio** = `recontrata.cl` — DNS en **Cloudflare** (gsaltron), **proxied** (nube naranja).
  `clerk.recontrata.cl` (auth) verificado.
- **Clerk** (auth, pk_live) · **Sentry** (proyectos `recontrata-backend` / `recontrata-frontend`,
  org `personal-g34`) · **Cloudflare Web Analytics** (activo, proxied → modo automático mide).
- El backend **no consume APIs de IA de pago** (score = promedio ponderado).

## Bitácora de cambios de infraestructura

### 20 jul 2026 — Auto-deploy desde GitHub
- Se conectó el **Source Repo `germansaltron/Recontrata`** (branch `master`) al proyecto
  Railway. **El deploy pasó de manual (`railway up`) a automático en cada push a master.**
- Motivo: el Railway CLI de este equipo está logueado en la cuenta de **Faymex**
  (`bodegaquilp01`); Recontrata vive en **gsaltron@gmail.com** → `railway up` apuntaba al
  workspace equivocado. El auto-deploy desde GitHub evita el problema de cuenta cruzada.
- Se recomendó activar **"Wait for CI"** (solo desplegar con el CI en verde). El dashboard
  mostraba "Auto deploy unavailable" — si los push no disparan deploy, revisar permisos de la
  GitHub App de Railway sobre el repo.
- Fallback: `deploy.sh` + project token (`.railway-token`, gitignored).

### 1 jul 2026 — Limpieza y rename en Railway
- **Duplicado BORRADO:** `FaenaScore` (mayúscula, ID `1d85d02e`) era un proyecto huérfano
  (sin dominio, build fallido, sin variables) que generaba confusión. Eliminado. Producción
  quedó intacta (recontrata.cl 200). Ver memoria global `railway-limpieza-proyectos-duplicados`.
- **Rename:** `faenascore` → **`Recontrata`** (cosmético; ID/dominios/variables sin cambios).

### 1 jul 2026 — Feedback de Joanna (beta)
Ver `SESION_01JUL2026_FEEDBACK_JOANNA.md`: 6 ajustes desplegados (bug del portal en blanco,
reorden de nav, perf del selector de industria, copy de la landing) + canal de marca de
YouTube con los 9 tutoriales resubidos.

## Herramienta relacionada — Dashboard KPIs Recontrata

Dashboard **local** (carpeta `Proyectos Claude Code\Dashboard Recontrata`, **NO** vive en este
repo). Lee en **solo lectura** la DB de prod (Supabase, pooler) + Cloudflare Web Analytics
(con filtro de bots) + Sentry (errores). Tiene selector de período (7/30/90/365/Todo). Puerto
8791, acceso directo en el Escritorio. Ver su `README.md`/`PROGRESS.md` y la memoria global
`dashboard-kpis-recontrata`.

## Relación con memoria global

Temas en la memoria de Claude: `recontrata-cuentas-infraestructura`,
`railway-limpieza-proyectos-duplicados`, `recontrata-feedback-joanna-beta`,
`dashboard-kpis-recontrata`, `recontrata-qa-lanzamiento`.
