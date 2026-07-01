# Infraestructura — Recontrata

> Estado de la infraestructura de Recontrata (recontrata.cl) y bitácora de cambios.
> Este repo es el de Recontrata (nombre técnico histórico: FaenaScore).

## Cuentas y hosting (bajo gsaltron, post-migración 29 jun 2026)

- **Railway** (cuenta `germansaltron` / gsaltron@gmail.com). Proyecto de producción =
  **`Recontrata`** (renombrado desde `faenascore` el 1 jul 2026; el rename NO cambia el ID).
  - **Project ID:** `7ec526bb-74bc-4796-bac4-4c89bde2d6bd` · **Service:** `a5ff98e5`.
  - Sirve **recontrata.cl**. **Deploy = `railway up`** (sin source GitHub, NO auto-deploy).
    Re-linkear siempre por ID: `railway link -p 7ec526bb-74bc-4796-bac4-4c89bde2d6bd`.
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
