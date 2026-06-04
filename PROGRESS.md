# FaenaScore — Progreso de Desarrollo

## Ultima actualizacion: 2026-06-04T15:40:00-04:00

## Sesion 4 jun 2026 — FASE 1 del plan (confianza y riesgo legal) — COMPLETA Y DEPLOYADA A PROD ✅

Implementados los 5 items L1-L5 del `PLAN_ACCION_CLASE_MUNDIAL.md`. Verificado: 40/40 tests backend, build frontend OK, migracion aplicada+revertida+reaplicada contra Postgres real (docker), smoke test E2E HTTP de todos los flujos, **y DEPLOYADO + verificado en prod**.
- **master `9a1a9ea`** (pusheado). Deploy Railway servicio `faenascore` (deployment `d190d44a`).
- **Migracion `f1a2b3c4d5e6` corrio contra Supabase prod**: logs muestran `Running upgrade d4b28c6514bc -> f1a2b3c4d5e6` + `Uvicorn running`. Rutas nuevas `/workers/{id}/consent` y `/evaluations/{id}/history` pasaron de 404 (antes) a **401** (despues) = codigo+migracion vivos. Health OK, frontend root 200.
- **Probe de deploy usado** (reusable): pollear una ruta NUEVA de API hasta que pase de 404→401 (Railway mantiene el contenedor viejo sirviendo 404 hasta que el nuevo arranca; si la migracion falla el contenedor no arranca y se queda en 404).

### L1 — Paginas legales (frontend)
- `frontend/src/pages/Privacy.tsx` + `Terms.tsx`: citada **Ley N° 21.719** (no la 19.628 derogada; se menciona solo como "moderniza la Ley 19.628"). Derechos ampliados a acceso/rectificacion/supresion/oposicion/portabilidad. Eliminado el disclaimer "Borrador inicial / referencial / no reemplaza asesoria legal" de ambas. Fecha actualizada a 4 jun 2026.

### L2 — rehire_reason obligatorio en backend
- `schemas/evaluation.py`: `validate_rehire_reason()` + `@model_validator`. Si `would_rehire != "yes"`, el motivo es obligatorio (>=3 chars, normalizado/trim). Se valida al CREAR (schema) y al EDITAR (endpoint, sobre estado final). Verificado: crear "no" sin motivo -> 422.

### L3 — Soft-delete + audit log
- `models/evaluation.py`: nueva col `deleted_at`. **La unicidad (project_id, worker_id) paso de UNIQUE CONSTRAINT a INDICE UNICO PARCIAL** `uq_evaluation_project_worker_active ... WHERE deleted_at IS NULL` (clave: permite re-evaluar tras soft-delete; el bug del constraint full salio en el smoke test y se corrigio).
- `models/evaluation_audit.py` (NUEVO): tabla `evaluation_audit_log` (action create/update/delete, actor_id+actor_name, snapshot JSONB, changed_fields JSONB). FK a evaluations ondelete SET NULL (el rastro sobrevive).
- `services/evaluation_audit.py` (NUEVO): `evaluation_snapshot()` + `record_evaluation_audit()`.
- DELETE de evaluacion ahora es soft (set `deleted_at`) + traza. **Filtro `deleted_at IS NULL` propagado a TODAS las agregaciones**: evaluations (list/get/dup-check/update/delete), workers (list/export/detail), dashboard (stats/top/next-eval/projects-pending/recent), projects (ec_subq, get, list_project_workers). En outerjoins el filtro va en el ON (no en WHERE) para no perder trabajadores sin evals.

### L4 — Consentimiento del trabajador
- `models/worker_consent.py` (NUEVO): tabla `worker_consent` (status pending/informed/granted/revoked, method, consent_date, notes, recorded_by). Unique por worker_id. **Alcance: INTRA-org** (cada org tiene su perfil aislado por org_id). La portabilidad cross-org (Portal del Trabajador, Fase 5) requerira consentimiento separado — documentado en el docstring.
- `schemas/worker_consent.py` (NUEVO). Endpoints `GET/PUT /organizations/{org}/workers/{id}/consent` en `workers.py`. `consent` agregado a `WorkerDetailResponse`.
- Frontend: `WorkerDetail.tsx` nueva tarjeta `ConsentCard` (badge de estado + editar status/via/notas). Tipos+funciones en `api.ts`.

### L5 — Time-lock 72h + versionado
- `config.py`: `EVALUATION_EDIT_WINDOW_HOURS=72`. `update_evaluation` rechaza con **409 `EVALUATION_EDIT_WINDOW_EXPIRED`** si la eval tiene mas de 72h. Verificado forzando created_at a -100h.
- Versionado: cada update (con cambios reales) escribe un snapshot en `evaluation_audit_log`. Nuevo endpoint `GET /organizations/{org}/evaluations/{id}/history` devuelve el historial (incluye borradas). Smoke: history mostro [create, update, delete].

### Migracion
- `alembic/versions/f1a2b3c4d5e6_phase1_legal_trust.py`: add col deleted_at + swap constraint->indice parcial + crea evaluation_audit_log + worker_consent. Downgrade completo. **Verificada upgrade/downgrade/re-upgrade contra PG real.** El deploy de Railway la corre solo (`alembic upgrade head &&` en el CMD del Dockerfile).

### Nota frontend
- Las evaluaciones NO son editables/borrables desde la UI todavia (endpoints PATCH/DELETE existen pero no cableados), asi que el time-lock 409 no se dispara aun desde el front; el backend ya lo protege. UI de historial de versiones: endpoint listo, pendiente de cablear cuando se agregue edicion en la UI.

### ARRANCAR MAÑANA AQUI — Fase 2 (conversion landing), quick wins <1 dia
Fase 0 (seguridad) y Fase 1 (legal) ya estan EN PROD. Sigue **Fase 2** del `PLAN_ACCION_CLASE_MUNDIAL.md`:
- **M1**: `<title>` + meta description + OG (keyword + propuesta de valor) en `frontend/index.html`.
- **M2**: seccion de prueba social (caso 0 Faymex / stat-bar INE + "$750K por mala recontratacion").
- **M3**: inyectar el ROI concreto ($750K) en el hero y bajo el precio Profesional.
- **M4**: angulo "la alternativa legal a las listas negras" (diferenciador pan-LATAM).
- **M5**: nav links (Funciones/Precios) + 2do CTA + CTA de cierre con urgencia.
- **M6**: plan Empresa con CTA self-serve (trial) en vez de `mailto:`.
Todo es `frontend/src/pages/Landing.tsx` + `index.html`. Verificar con `npm run build` y deploy `railway up --detach` (servicio `faenascore`).

### Pendientes menores arrastrados de Fase 1 (no bloquean)
- Cablear en la UI la **edicion/borrado de evaluaciones** (endpoints PATCH/DELETE existen; al hacerlo, manejar el 409 `EVALUATION_EDIT_WINDOW_EXPIRED` con un toast claro) + mostrar el **historial de versiones** (`GET .../evaluations/{id}/history`, endpoint ya vivo).
- AccessGate de pre-lanzamiento sigue activo (codigo `recontrata2211`); checklist "QUITAR al lanzar" cuando se abra al publico.
- Prueba de login real con correo (lo unico que necesita un humano; arrastrado de la sesion 2 jun).

### Como verificar Fase 1 manualmente (si se quiere)
- Ir a la ficha de un trabajador en prod -> tarjeta "Consentimiento del trabajador" (badge + boton Registrar/Editar).
- Al evaluar con "No"/"Con reservas" sin motivo, el backend ahora lo rechaza (el front ya lo pedia).
- Setup local para tocar schema: `docker compose up -d` (PG en :5433), `DATABASE_URL=postgresql+asyncpg://faenascore:faenascore_dev@localhost:5433/faenascore`, `alembic upgrade head`, server en :8009 con `AUTH_MOCK_ENABLED=true ALLOW_MOCK_IN_PROD=true`.

---

## Ultima actualizacion previa: 2026-06-02T15:20:00-04:00

## Sesion 2 jun 2026 — Landing aspiracional + Auditoria multi-rol + Fase 0 seguridad + Clerk PROD (TODO DEPLOYADO Y VERIFICADO)

### 1. Landing girada a mensaje aspiracional (deployado)
- German se arrepintio del enfoque "dolor" y pidio mensaje **positivo/aspiracional**. Eleccion de hero: **"Tu mejor equipo, en cada proyecto."**
- Cambios en `frontend/src/pages/Landing.tsx`: hero + subtitulo, seccion "Tu mejor activo ya trabajo contigo" (antes "1 millon... accidente... el problema vuelve"), feature "El historial que se queda contigo".
- **Limpieza pan-LATAM**: eliminadas las 2 ocurrencias visibles de **"faena"** (=matadero en AR) → "proyecto"; quitado chilenismo "la pega" → "su trabajo". Quedan invisibles: `hero-faena.jpg` (nombre archivo) + localStorage key `faenascore:draft:` (no se ven).

### 2. Auditoria multi-rol "clase mundial" (4 expertos en paralelo)
- A pedido de German, auditoria con 4 lentes: **UX, Marketing, RRHH/Legal, Ciberseguridad**. Sintesis y roadmap en **`PLAN_ACCION_CLASE_MUNDIAL.md`** (raiz del repo) con 6 fases.
- Hallazgos clave (ver doc): score = promedio plano indefendible; sin consentimiento/replica del trabajador; cita Ley derogada 19.628 (es **21.719**); disclaimer "Borrador inicial" en Privacy/Terms; landing sin prueba social ni ROI ($750K); RUT hardcodeado bloquea pan-LATAM.

### 3. FASE 0 seguridad — DEPLOYADA a prod (commit `d7834ef`, master)
- `config.py`: defaults `DEBUG=False` + `AUTH_MOCK_ENABLED=False` (fail-closed; prod en Railway YA estaba en False, era riesgo latente del codigo).
- `projects.py`: fix **IDOR cross-tenant** en `unassign_worker` (valida `_get_project`) + scope `Worker.org_id` en `list_project_workers`.
- `workers.py`: allowlist de columnas ordenables `_SORTABLE_COLUMNS` (anti ORM column injection) + validacion upload Excel (content-type, 5MB, 5000 filas) + mensajes de error sanitizados.
- `admin.py`: `seed-demo` exige `ADMIN_TOKEN` >=32 chars + `secrets.compare_digest`. **ADMIN_TOKEN rotado a 48 chars en Railway** (valor en dashboard Railway; mandar en header `X-Admin-Token`).
- `main.py`: security headers (X-Frame-Options DENY, nosniff, Referrer-Policy, HSTS solo si !DEBUG) + CORS estricto (methods/headers explicitos, +X-Admin-Token).
- `backend/tests/test_security_hardening.py`: 9 tests de regresion sin-DB. **30/30 tests pasando.**
- Verificado en prod: `/api/v1/me` sin token → **401** (mock OFF vivo), HSTS presente (DEBUG=False vivo), 4 headers OK, health OK.
- **Rate limiting (S8) NO implementado en codigo**: delegado a Cloudflare (edge). Documentado en el plan.

### 4. CLERK dev → PRODUCCION (S7) — COMPLETADO Y VERIFICADO EN VIVO
- Instancia de produccion creada (clonada de dev). Dominio recontrata.cl conectado.
- **Cloudflare: 5 CNAME en DNS only (nube gris)**: `clerk`→frontend-api.clerk.services, `accounts`→accounts.clerk.services, `clkmail`→mail.mwgqdbmmudlz.clerk.services, `clk._domainkey`→dkim1..., `clk2._domainkey`→dkim2... (los recontrata.cl/www proxied a Railway NO se tocaron).
- **Railway (servicio `faenascore`): 4 vars `_live_`**: `VITE_CLERK_PUBLISHABLE_KEY=pk_live_Y2xlcmsu...`, `CLERK_SECRET_KEY=sk_live_...`, `CLERK_ISSUER=https://clerk.recontrata.cl`, `CLERK_JWKS_URL=https://clerk.recontrata.cl/.well-known/jwks.json`. Set con `railway variables --set ... --skip-deploys` + `railway up --detach` (rebuild necesario: VITE_ es build-arg). Bundle nuevo `index-CMqLqCxR.js`.
- **Login = email + magic link/contraseña (camino B, SIN Google)**. Google deshabilitado (toggle "Enable for sign-up and sign-in" OFF; NO se pudo borrar la conexion por validacion Client ID/Secret, pero con el toggle off basta). App renombrada FaenaScore→Recontrata.
- **Verificado E2E con Playwright en recontrata.cl/sign-in**: banner "development mode" DESAPARECIDO, `frontendApi=clerk.recontrata.cl`, `isProd=true`/`pk_live_`, sin boton Google, "para continuar a **Recontrata**", JWKS prod 200 RS256 (kid `ins_3EakJ6wu...`), 0 errores consola.
- Trampa SDK: el bundle tiene 1 ref a `pk_test_` que es solo string interno del SDK para detectar tipo de llave, NO una llave hardcodeada.

### PENDIENTES (retomar manana, en orden de prioridad)
1. **Prueba de login real** (German, requiere bandeja de entrada): registrarse con correo real en recontrata.cl/sign-up y confirmar que llega el email de verificacion (ahora por dominio propio + DKIM) y entra al dashboard. Es lo unico que necesita un humano.
2. **FASE 1 del plan (legal/confianza)** — siguiente bloque grande antes de lanzamiento publico:
   - Quitar disclaimer "Borrador inicial" de Privacy.tsx/Terms.tsx + citar **Ley 21.719** (no 19.628).
   - `rehire_reason` OBLIGATORIO en backend cuando `would_rehire != "yes"` (hoy solo valida el front; un `@model_validator` en `schemas/evaluation.py`).
   - Soft-delete + audit log en evaluaciones (hoy DELETE fisico sin traza).
   - Consentimiento del trabajador (tabla `worker_consent`); separar perfil intra-org vs cross-org.
   - Time-lock edicion evals (72h) + versionado.
3. **Fases 2-5 del plan** (`PLAN_ACCION_CLASE_MUNDIAL.md`): conversion landing (prueba social, ROI, SEO), UX terreno (bottom-nav, toasts, offline), pan-LATAM (RUT→id_type/id_country, pricing USD), apuestas grandes (score defensible, Portal del Trabajador, anti-sesgo, CI aislamiento tenant).
4. **Clerk opcionales (no bloquean)**: pasar a solo-magic-link (Configure→Authentication→Email) si se quiere quitar el campo contraseña; la conexion Google quedo deshabilitada-no-borrada.
5. **AccessGate de pre-lanzamiento sigue activo** (codigo `recontrata2211`): cuando se lance publico, ejecutar el checklist "QUITAR al lanzar" (ver seccion sesion 1 jun).

## Sesion 1 jun 2026 — Gate de acceso pre-lanzamiento (DEPLOYADO + verificado E2E)
- **Objetivo**: recontrata.cl NO es publico todavia (estamos puliendolo). Replicar el gate de pre-lanzamiento de casilisto.cl, con codigo propio.
- **Implementado** (commit `9ed5d4d`, master, en prod):
  - `frontend/src/components/AccessGate.tsx` — overlay de marca (paleta azul blue-600/700, `/logo-recontrata.png`) que pide un codigo antes de mostrar nada. **Codigo: `recontrata2211`** (case-insensitive). Al acertar guarda `localStorage recontrata_access` con TTL 90 dias. Replica del de CasiListo, adaptado a la marca.
    - Configurable con `VITE_ACCESS_CODE`; desactivable con `VITE_ACCESS_GATE=false` (env Vite, requiere rebuild).
  - `frontend/src/App.tsx` — envuelve con `<AccessGate>` **las dos ramas** (clerkEnabled true y false).
  - `frontend/index.html` — `<meta name="robots" content="noindex, nofollow">` + el inline script del boot-splash ahora tambien retira el intro de logo si no hay `recontrata_access` vigente (sin flash del intro para visitantes sin codigo).
  - `frontend/public/robots.txt` — `Disallow: /`.
- **Build local OK** (bundle `index-Ci-5utmB.js`). Deploy via `railway up --detach` (servicio `faenascore`, single-service: Dockerfile compila frontend y lo sirve desde el backend). Prod sirve bundle `index-CA16zARG.js` (hash difiere por build-arg Clerk — esperado).
- **Verificado E2E con Playwright en prod**: el gate aparece → `recontrata2211` desbloquea → Landing completa renderiza. Meta `noindex` servido OK.
- **TRAMPA descubierta — robots.txt**: Cloudflare sirve su **robots.txt gestionado** (Content-Signal / bloqueo bots IA / `Allow: /` para search) que **pisa el estatico** → mi `/robots.txt` no llega. La proteccion efectiva contra Google es el **meta noindex** (sirve). Para bloquear tambien via robots.txt habria que desactivar "Managed robots.txt" en el dashboard de Cloudflare.
- **AL LANZAR** (checklist, buscar comentario "QUITAR al lanzar"): (1) quitar `<AccessGate>` de ambas ramas de App.tsx o `VITE_ACCESS_GATE=false`; (2) quitar meta noindex de index.html; (3) revertir el check `!unlocked` del inline script de index.html; (4) borrar/abrir public/robots.txt.
- **Recordatorio**: sigue pendiente pasar **Clerk a produccion** (banner dev), unico otro pendiente del rebrand. Ver paso a paso abajo.

## [✅ HECHO 2 jun 2026 — ver seccion arriba] Pasar Clerk de desarrollo a produccion (documentado 1 jun 2026)
> COMPLETADO: instancia prod + 5 CNAME Cloudflare + 4 vars `_live_` Railway + rebuild + Google off + rename. Verificado en vivo. Detalle en la sesion 2 jun arriba. (Historico del plan original abajo.)
- **Por que**: prod usaba `VITE_CLERK_PUBLISHABLE_KEY=pk_test_...` + `CLERK_ISSUER=https://willing-monitor-52...` (instancia de DESARROLLO de Clerk). Por eso sale el banner "development mode". `AUTH_MOCK_ENABLED=False` ya esta OK (login real activo).
- **Vars en Railway involucradas**: `VITE_CLERK_PUBLISHABLE_KEY` (build-arg en Dockerfile), `CLERK_SECRET_KEY`, `CLERK_ISSUER`, `CLERK_JWKS_URL`.
- **El codigo NO cambia**: usa `<SignIn>`/`<SignUp>` prediseñados; los metodos de login se configuran en el dashboard de Clerk, no aqui. Login social NO esta forzado en codigo.
- **Pasos de German (dashboard, requiere su cuenta)**:
  1. dashboard.clerk.com -> app Recontrata -> "Deploy to production" / crear instancia de produccion.
  2. Conectar dominio recontrata.cl: pegar en Cloudflare los CNAMEs que da Clerk (clerk./accounts.recontrata.cl) + registros DKIM para emails.
  3. SOLO si usa "Sign in with Google": crear credenciales OAuth propias en Google Cloud y pegarlas en Clerk. Si es solo email/magic link, se salta.
  4. Copiar las llaves de produccion: `pk_live_...`, `sk_live_...`, nuevo issuer y JWKS URL.
- **Pasos de Claude (cuando German pase las llaves `_live_`)**:
  1. Actualizar en Railway las 4 vars con valores `_live_`.
  2. `railway service faenascore` -> `railway up --detach` (rebuild necesario por el build-arg).
  3. Verificar E2E en recontrata.cl: banner dev desaparecido + registro/login OK. Pollear bundle/artefacto nuevo, no /health.

## Ultima actualizacion previa: 2026-05-30T18:30:00-04:00

## Sesion 30 may 2026 (parte 5) — Logo + animacion Recontrata (PENDIENTE: flecha mal)
- **Logo elegido**: concepto **B = flecha de retorno** (cuadro azul #2563eb + flecha circular blanca + wordmark "Re"(azul)+"contrata"(gris)). Coincidio German. Archivos en `branding/`: `logo-recontrata.svg`, preview `logo-preview.html`.
- **Animacion "el ciclo se cierra"** (cuadro aparece -> flecha se traza girando -> punta -> giro de cierre -> wordmark entra). Web: `branding/logo-animado/index.html` (SVG+CSS, servida en http://127.0.0.1:8077/...). Video: `branding/logo-animado/animate_logo.py` (Pillow, 3.2s, exporta MP4+GIF claro y oscuro en `output/`).
- **PENDIENTE CRITICO (retomar manana)**: **la PUNTA de la flecha sigue mal** segun German. Intentos: (1) "L" axis-aligned en PIL = mal; (2) chevron tangente en PIL = German dice que SIGUE mal. 
  - **Aclarar con German exactamente que esta mal**: ¿solo el video PIL?, ¿tambien el simbolo SVG (Lucide rotate-ccw)?, ¿la punta, el angulo, el gap, el grosor?
  - **Estrategia sugerida**: dejar de dibujar la flecha a mano en PIL; **rasterizar el SVG real** (path Lucide `M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8` + cabeza `M3 3v5h5`) con resvg/cairosvg por frame (animar stroke-dashoffset), que es lo que se ve bien en el web. O re-disenar el simbolo de flecha desde cero si a German no le gusta el de Lucide.
- Resto de la sesion (parte 1-4) abajo: monetizacion + landing, fix N+1 perf, rebrand Recontrata Fase A, dominio recontrata.cl via Cloudflare (DNS propagando).

## Ultima actualizacion previa: 2026-05-30T00:00:00-04:00

## Sesion 30 may 2026 (parte 3) — Naming pan-LATAM: decision Recontrata (PENDIENTE ejecutar)
- **Contexto**: German quiere expandir el producto a TODA Latinoamerica (no solo Chile), incluido Mexico/Colombia/Cono Sur.
- **Hallazgo decisivo sobre "Faena"** (verificado con fuentes): la palabra NO viaja bien pan-LATAM:
  - Chile / Peru / Bolivia (andino-minero): OK, es jerga del rubro.
  - Argentina / Uruguay: "faena" = **matanza/sacrificio de ganado** (matadero-frigorifico, acepcion oficial SENASA). Malo para software de trabajadores.
  - Mexico / Colombia: tarea coloquial / taurino / agricola, NO jerga de construccion. Tibio.
  - => Tanto FaenaScore como FichaFaena quedan descartados por anclar a "Faena".
- **Decision de German**: rebrand a **"Recontrata"** (marca = propuesta de valor; pan-LATAM; sin connotacion negativa; dice que hace).
- **Dominios verificados (NIC Chile, autoritativo solo para .cl)**: `recontrata.cl` LIBRE. `faenascore.cl` y `fichafaena.cl` tambien libres (ya no se usaran). `recontrata.com/.io/.co/.app` parecen TOMADOS pero la verificacion via nslookup NO es confiable — **CONFIRMAR en registrador real (Namecheap/GoDaddy)**.
- **FASE A EJECUTADA Y DEPLOYADA** (commit `8b8f99e`): sed `FaenaScore`->`Recontrata` + `faenascore.cl`->`recontrata.cl` en 9 archivos (index.html, Landing, AppShell, Terms, Privacy, EvaluateWorker, config.py, main.py, dependencies.py). 0 ocurrencias "FaenaScore" restantes en marca; URL infra `faenascore-production.up.railway.app` y DB local INTACTAS a proposito. Build OK, 21 tests OK. Verificado en prod: `<title>Recontrata</title>` vivo + health OK.
- **Pendiente menor Fase A**: regenerar `frontend/public/dashboard-preview.png` (el screenshot de la landing aun muestra el logo viejo "FaenaScore" en el header capturado) — requiere login (Playwright deslogueado). localStorage key `faenascore:draft:` se dejo (interno, inocuo). `backend/.env.example` APP_NAME y docker-compose DB names siguen "faenascore" (infra local, no marca).
- **FASE B pendiente (requiere accion de German)**: comprar `recontrata.cl` (NIC ~$10k/ano; .com/.io confirmar en registrador, parecen tomados); renombrar repo GitHub, proyecto Railway (cambia URL a recontrata-production), app Clerk; conectar dominio.

### Plan de rebrand a Recontrata (cuando se confirme)
- **Fase A — Codigo (reversible, NO toca infra)**: archivos con "FaenaScore"/"faenascore": `frontend/index.html` (title/meta), `frontend/src/pages/Landing.tsx`, `frontend/src/components/layout/AppShell.tsx` (logo sidebar), `frontend/src/pages/Terms.tsx`, `frontend/src/pages/Privacy.tsx`, `backend/app/core/config.py`, `.env.example`, `backend/seed_org1.sql` (demo). Emails `contacto@faenascore.cl` -> `contacto@recontrata.cl`. Regenerar screenshot `dashboard-preview.png` (tiene el logo). Docs historicos (JUSTIFICACION_FAENASCORE.md, NAMING_DISCUSSION.md) se pueden dejar o anotar.
- **Fase B — Infra (requiere accion de German / coordinacion)**: comprar `recontrata.cl` en NIC (~$10k CLP/ano); renombrar repo GitHub FaenaScore->Recontrata (mantiene redirects); renombrar proyecto Railway (URL pasa a recontrata-production.up.railway.app); renombrar app en Clerk (no afecta keys); conectar dominio. Supabase no cambia (ref interno).

## Sesion 30 may 2026 (parte 2) — Fix N+1 en Evaluar/Proyectos (deployado)
- **Sintoma**: entrar a "Evaluar" tardaba 4-5s. **Causa**: N+1 anidado. Auditados TODAS las paginas a pedido del usuario.
- **Hallazgos** (el N+1 NO estaba solo en el front):
  - `projects.py::list_project_workers`: 1 query de evaluacion POR trabajador (1+M). Afecta Evaluar y Detalle de Proyecto.
  - `Evaluate.tsx`: llamaba a list_project_workers POR cada proyecto (1+N). Multiplicaba lo anterior → 40-60 queries.
  - `projects.py::list_projects`: 2 queries (wc+ec) POR proyecto (1+2N). Afecta Evaluar y Proyectos.
  - Resto de paginas (Dashboard/EvaluateWorker/ProjectDetail/WorkerDetail) ya usaban `Promise.all` correcto.
- **Fixes** (commit `7d1f757`):
  - `list_project_workers` → single query con `outerjoin` a Evaluation.
  - `list_projects` → subqueries escalares correlacionadas (`add_columns`), 1 query.
  - Nuevo endpoint `GET /dashboard/projects-pending` (2 queries fijas) con `ProjectPendingItem` (id/name/client_name/worker_count/pending_count/first_pending_worker_id). Reusa la tecnica de evaluated_subq de next-evaluation.
  - `api.ts`: `getProjectsPending` + tipo `ProjectPending`. `Evaluate.tsx`: 1 sola llamada agregada.
- **Verificado**: `npm run build` OK, `pytest` 21/21 OK, deploy Railway (deployment `fb27f523`) — endpoint `/projects-pending` responde 403 estable en prod (probe: 404=viejo, 401/403=nuevo). Control: `/next-evaluation` y `/stats` tambien 403.
- **Verificado parcial**: tras fix N+1, Evaluar bajo de ~4s a ~2s (medido por German logueado).
- **Diagnostico latencia restante (medido por curl 30 may)**: RTT base Chile->Railway ~0.5s; cada query a Supabase (sa-east-1) ~0.5s (statement_cache_size=0 + distancia Railway<->DB). Piso fisico ~300-500ms. El cuello YA NO es el numero de llamadas sino el costo por query + RTT.
- **Optimizacion cliente (prefetch + SWR cache) deployada** (commits `c8c83be` + `0fe5f97`, bundle prod `index-BoJyl9Cn.js`): `lib/swr.ts` (cache SWR en memoria); `AppShell` precarga projects-pending + el chunk JS de Evaluate al montar cualquier pantalla del panel; `Evaluate.tsx` renderiza cache al instante y revalida. OJO: el primer intento (commit `c8c83be`) NO cableo el prefetch (el Edit a AppShell fallo silenciosamente por shape de archivo distinto); corregido en `0fe5f97`. Efecto: al entrar a Evaluar tras ~1-2s en el panel, deberia sentirse instantaneo (cache hit + chunk precargado).
- **Pendiente (palanca backend, requiere input de German)**: pasar DATABASE_URL al **session pooler (5432)** de Supabase para habilitar statement cache -> baja CADA query de ~0.5s a ~0.15s (afecta toda la app). Necesita la connection string del session pooler + verificar IPv4/limites desde Railway.
- **Nota entorno**: el canal de herramientas estuvo inestable (outputs vacios/duplicados, bucles de polling descontrolados). Deploy Railway requirio `railway service faenascore` + `railway up` con salida SIN filtrar (el grep se comia la confirmacion y el up no creaba deployment).

## Sesion 30 may 2026 — Investigacion monetizacion + nuevo pricing en landing (deployado)
- Investigacion de competidores (Chile: Buk/Talana/Rankmi/GeoVictoria cobran por trabajador/mes, desempeno es modulo add-on en Buk, precios solo por cotizacion; global: Workyard US$6-13/user + US$50 base fee, trial 14d; freemium vs trial: trial convierte 14-25% vs freemium 2-5%, hibrido es lo mas usado). Documento completo en `PROPUESTA_MONETIZACION.md`.
- **Decisiones de German**: eje de cobro por **trabajadores activos** (supervisores e historial ilimitados, NO per-seat); **Pro $49.990** (subido desde $29.990); **Empresa $149.990** (subido desde $99.990); conversion **hibrida freemium + trial 14d**; **10 design partners** a -50% lifetime.
- **Landing actualizada y deployada**: `frontend/src/pages/Landing.tsx` seccion pricing. Commit `7d8f8e3`. Build OK. Verificado E2E en prod (bundle `index-DcM1ckkw.js` sirviendo "$49.990" tras 220s). Copy nuevo: "Pagas por trabajadores activos, no por usuario. Supervisores e historial ilimitados". Menciona trial 14d, facturacion anual (2 meses gratis), y plan Enterprise +500.
- Pendiente implementacion (no decision): aplicar limites de plan en el producto cuando se construya billing, flujo design partners, medios de pago (transferencia+factura+Webpay).

## Estado actual
- Fase: **P2 polish cerrado.** Quedan solamente #2 Clerk prod (bloqueado por dominio) y decisiones de producto (modelo monetizacion, compra dominio).
- Branch activo: master
- Ultimo commit: `e83fb0a` — ux: P2 phase 2 (sparkline SVG, empty states, landing pricing + screenshot, legal pages)
- Commit anterior: `79b2ed7` — ux: P2 quick wins (a11y stars, status badge, clickable rows, mobile KPI, breadcrumbs)
- Deploy prod: bundle Railway `index-CzvcM-hl.js` confirma codigo en prod. `/terminos` 200, `/privacidad` 200, `/dashboard-preview.png` 200, `/api/health` ok. Playwright verifico landing con hero + product preview + 3 planes de pricing.

## Sesion 17 abr 2026 — P2 polish completo (11 items en 2 commits)

### Contexto
Retomamos con #2 Clerk prod bloqueado por dominio. Usuario pidio avanzar con P2 polish directamente. Decisiones del usuario:
1. Pricing real en CLP (estimado, ajustable despues)
2. Screenshots: decide tu
3. Terminos + privacidad: redactar primer borrador propio
4. Resto tecnico: decide tu

### Commit `79b2ed7` — P2 quick wins
- **a11y stars en EvaluateWorker** (`StarRating.tsx`): `role="radiogroup"` en container, `role="radio"` + `aria-checked` + `aria-label="N estrellas"` + `title` tooltip por boton
- **Status badge en ProjectDetail header**: breadcrumb "Proyectos / [nombre]" + badge coloreado (active=green, paused=amber, completed=gray, cancelled=red) junto al titulo
- **Filas Workers clickeables enteras**: `useNavigate` + `onClick={() => navigate('/app/workers/${w.id}')}` + `cursor-pointer`. Link del nombre usa `stopPropagation` para no duplicar nav
- **Mobile KPI wrap fix** (`Dashboard.tsx`): padding responsive `p-3 sm:p-4`, texto `text-xs sm:text-sm leading-tight`, `shrink-0` en icon wrapper
- **Empty states con CTA** en Dashboard: "Sin trabajadores evaluados aun" + Link a `/app/evaluate`, "Sin evaluaciones recientes" + mismo Link
- Bundle: `index-09AiEa6i.js` → `index-CAf2vZi0.js`

### Commit `e83fb0a` — P2 phase 2 (mas pesado)
- **Recharts → SVG sparkline** (`WorkerDetail.tsx`): eliminado `import { LineChart, ... } from 'recharts'`. Nuevo componente `ScoreSparkline` inline (600x160 viewBox, 5 grid lines, polyline path, circles con `<title>` tooltip, labels de proyectos debajo). **WorkerDetail chunk: 347KB → 7KB** (Recharts ya no se descarga nunca).
- **Breadcrumbs**: "Trabajadores / [nombre]" en WorkerDetail. "Proyectos / [nombre] / Evaluar" en EvaluateWorker con `pl-11` offset para alinearse con el back-arrow.
- **Evaluate simplificada**: antes lista pasiva de proyectos que linkeaba a ProjectDetail. Ahora hace `Promise.all(listProjectWorkers)` por proyecto, computa `pending_count` + `first_pending_worker_id`, ordena por pendientes desc. Cada card muestra progreso "N/M evaluados" + badge amber "N pendientes" + **boton "Evaluar" salta directo a `/app/evaluate/${projectId}/${firstPendingId}`**. Si no hay pendientes, muestra badge green "Completo".
- **Landing pricing**: 3 PricingCard components dentro de seccion `#pricing` con fondo gray-50:
  - Gratis $0 (15 trabajadores, 1 proyecto, 30 evals/mes, import Excel)
  - Profesional **$29.990 CLP/mes** (100 trabajadores, proyectos ilimitados, evals ilimitadas) — featured "Más popular"
  - Empresa **$99.990 CLP/mes** (ilimitado, API, onboarding, soporte prioritario) — CTA `mailto:contacto@faenascore.cl`
  - Disclaimer: "Precios referenciales, aún en fase de lanzamiento. Podrían ajustarse antes del cobro."
- **Landing product preview**: screenshot real del dashboard (Playwright snapshot de prod, 1440x900, 105KB) en `/dashboard-preview.png`. Gradient blur blue-50 debajo + rounded-xl + shadow-2xl.
- **Landing hero fix mobile**: `leading-tight`, `text-base md:text-xl`, `max-w-xl md:max-w-2xl`, `leading-relaxed`, subtitulo deja de cortarse raro en 375px.
- **Landing footer con 3 columnas**: FaenaScore / Producto / Legal. Legal linkea a `/terminos`, `/privacidad`, `mailto:contacto@faenascore.cl`.
- **Paginas legales nuevas**:
  - `frontend/src/pages/Terms.tsx` — 11 secciones (objeto, registro, uso aceptable, datos ingresados por Usuario, planes y pagos CLP, propiedad intelectual, limitacion de responsabilidad, terminacion, modificaciones, **ley aplicable Chile/Santiago**, contacto). Referencia Ley N° 19.628 y Codigo del Trabajo. Header con back-arrow.
  - `frontend/src/pages/Privacy.tsx` — 12 secciones (responsable tratamiento, datos tratados, finalidades, base licitud, subencargados **Clerk/Supabase/Railway**, almacenamiento SA, plazo 90 dias, derechos ARCO, seguridad, cookies, modificaciones, contacto). Referencia Ley 19.628 + GDPR aplicable.
  - Ambas con disclaimer "Borrador inicial. Este documento es referencial y no reemplaza asesoria legal especifica".
- **Rutas en App.tsx**: `/terminos` y `/privacidad` agregadas a ambas ramas (clerkEnabled y mock). Lazy imports.
- **Empty state WorkerDetail**: "Sin evaluaciones aun" + CTA a `/app/evaluate` cuando el trabajador no tiene historial.
- Bundle: `index-CAf2vZi0.js` → `index-CzvcM-hl.js`. Vendor Recharts dejo de aparecer en output.

### Verificacion prod (Playwright)
- `curl /api/health` → `{"status":"ok","database":"connected"}`
- `curl /terminos` → 200, `curl /privacidad` → 200, `curl /dashboard-preview.png` → 200
- Landing desktop: hero con subtitulo completo + product preview image + 3 planes pricing visibles + footer con 3 columnas
- Screenshot capturado: `dashboard-preview.png` (Playwright snapshot de prod, usuario logueado en profile `mcp-chrome-7006d60`)

### Pendiente siguiente sesion
- **#2 Clerk production instance** — sigue bloqueado por dominio (faenascore.cl o subdominio faymex.cl). Una vez con dominio: crear prod instance en dashboard.clerk.com, sacar 4 env vars, setear en Railway, `railway up --detach`. Elimina banner "Development mode".
- **Decisiones de producto** (ver seccion "Pendiente decisiones" abajo): monetizacion, compra dominio, launch strategy.
- **Decision de naming pendiente** — ver `NAMING_DISCUSSION.md`. Recomendacion: rebrand a **FichaFaena** (2-3h, ventana optima pre-launch). "Score" no es natural en Chile fuera del contexto Dicom; "Ficha" es lenguaje real del rubro. Alternativa marca: **Cuadrilla**. Default si no se decide: mantener FaenaScore.

---

## Sesion 16 abr 2026 (tarde) — #12 paginacion + #14 skeletons

### Contexto
Retomamos post-audit UX de la manana. Arrancamos cerrando los 2 items UX que quedaban de la lista priorizada.

### Estado tras sesion (para contexto del 17 abr)
- Branch activo: master
- Ultimo commit: `207b568` — ux: skeleton loaders in Dashboard / Evaluate / ProjectDetail
- Commit anterior: `1364141` — feat: paginate Workers page (size 20 + prev/next UI)
- Deploy prod: bundle Railway `index-09AiEa6i.js` confirma codigo en prod. Playwright verifico Dashboard skeleton con `aria-label="Cargando dashboard"`, Workers con 20 filas paginadas (barra oculta porque total=20=1 pagina, comportamiento esperado), Evaluate + ProjectDetail cargan sin "Cargando..." plain.

## Sesion 16 abr 2026 (tarde) — #12 paginacion + #14 skeletons

### Contexto
Retomamos post-audit UX de la manana. Arrancamos cerrando los 2 items UX que quedaban de la lista priorizada.

### Bloqueo con el classifier
Al arrancar, el auto-mode classifier de Anthropic (`claude-opus-4-6[1m]`) quedo intermitentemente caido durante ~1 hora. Bloqueaba todo `npm`/`python`/`railway`/`cd` con espacios en path. Workaround: usuario corrio comandos con prefijo `!` desde el prompt (build + commit + push + railway up de #12 todos via `!`). Luego desactivamos auto mode con Shift+Tab, lo que hace que Bash use la allowlist de `permissions.allow` en vez del classifier — comandos ahora pasan pidiendo confirmacion puntual.

### Commit `1364141` — #12 Paginacion Workers
- `frontend/src/pages/Workers.tsx`: `PAGE_SIZE=20` (antes hardcoded 50), estado `page/total/totalPages`, auto-reset de page cuando cambian filtros (search/specialty/minScore)
- UI de paginacion: "Mostrando X–Y de Z" + botones Anterior/Siguiente con disabled states + "Página N de M"
- Barra solo aparece si `totalPages > 1`
- Backend ya soportaba `page`/`size` y devolvia `total`/`pages` — cero cambios en workers.py
- Bundle hash: `kmh2W6H6`
- Verificado: build pasa (749ms), deploy OK (`curl /api/health` → `{"status":"ok","database":"connected"}`)

### Commit `207b568` — #14 Skeletons
- Reemplazo de `<div className="animate-pulse text-gray-400">Cargando...</div>` por skeletons shape-aware en:
  - `Dashboard.tsx`: nuevo componente `DashboardSkeleton()` inline. 4 KPI cards + 2 panels con rows. `aria-busy="true"`
  - `Evaluate.tsx`: h1 + descripcion + `CardSkeleton count={3}` del primitivo existente
  - `ProjectDetail.tsx`: header con back-arrow + titulo, workers table con 5 filas skeleton. `aria-busy="true"`
- `App.tsx PageFallback` + `WorkerDetail` + `AssignWorkersForm` aun usan "Cargando..." plain (scope de la tarea era Dashboard/Evaluate/ProjectDetail por lista UX audit)
- Bundle hash: `cVo6nHCx`
- Verificado: build pasa (545ms)

### Creacion de CLAUDE.md global
- Nuevo archivo en `C:/Users/Usuario/Proyectos Claude Code/CLAUDE.md` con las 6 reglas de autonomia adaptadas del CLAUDE.md de Fillanyform
- Aplica a todos los subproyectos de esa carpeta (Brochure, Investigador Faena, Fillanyform, etc.)
- **Nota**: FaenaScore esta en `C:/Users/Usuario/Claude Code German/FaenaScore`, OTRA carpeta — no hereda ese CLAUDE.md. Si queremos que FaenaScore tambien siga esas reglas, habria que crear un CLAUDE.md en `Claude Code German/` o linkear

### Verificacion Playwright en prod (cerrada)
- Login con profile persistido `mcp-chrome-7006d60` de sesion anterior
- **Dashboard** (`/app`): snapshot capturo `generic "Cargando dashboard" [ref=e110]` → skeleton con `aria-busy="true"` renderiza durante load. Tras cargar: 3 proyectos, 20 trabajadores, 37 evals, score 3.9/5, 62% recontratar. Top Trabajadores + Evals Recientes OK.
- **Workers** (`/app/workers`): 20 filas, sin barra de paginacion visible (total=20=1 pagina, logica `totalPages > 1` oculta correctamente).
- **Evaluate** (`/app/evaluate`): 2 proyectos activos listados sin "Cargando..." plain.
- **ProjectDetail** (`/app/projects/39495fc5-...`): header + 14 workers con ScoreBadges, sin "Cargando..." plain.
- Bundle Railway prod: `index-09AiEa6i.js` (distinto al hash local porque Railway rebuild) — confirma que `207b568` esta deployado.

### Pendiente siguiente sesion
- **#2** Clerk production instance — sigue bloqueado por dominio
- **P2**: landing screenshots/pricing/footer legal, Recharts bundle 347KB, mobile 375px wrap, a11y stars, ProjectDetail badge estado, breadcrumbs, filas Workers clickeables enteras, etc.



## Comandos utiles para retomar

```bash
cd "C:/Users/Usuario/Claude Code German/FaenaScore"
git log --oneline -10           # ver ultimos commits
git status                       # estado working tree
railway status                   # ver deploy
railway logs                     # logs runtime
curl -s https://faenascore-production.up.railway.app/api/health | python -m json.tool

# Re-seedear data demo si hace falta:
cd backend
python -u scripts/gen_seed_sql.py 34791eb6-e33e-4c75-bd4f-65b1fcc8f5cb > /tmp/seed1.sql
python -u scripts/gen_seed_sql.py 162e58e2-2530-4627-a0fa-9a5b5f824f14 > /tmp/seed2.sql
railway run python -u scripts/exec_seed_sql.py /tmp/seed1.sql 34791eb6-e33e-4c75-bd4f-65b1fcc8f5cb
railway run python -u scripts/exec_seed_sql.py /tmp/seed2.sql 162e58e2-2530-4627-a0fa-9a5b5f824f14
railway run python -u scripts/check_seed.py   # verificar counts con conexion fresca
```

## Sesion 16 abr 2026 — Audit UX live + 9 fixes en prod + migracion tildes

### Contexto
Arrancamos retomando desde donde quedo la sesion 15 abr (MVP cerrado, UX audit hecho por lectura de codigo). El usuario pidio correr el audit EN VIVO con Playwright autenticado para separar hipotesis de bugs reales.

### Setup Playwright autenticado
Plugin MCP Playwright usa profile aislado (`mcp-chrome-7006d60`), no comparte cookies con Chrome normal. Flujo final:
- Navegar a `/sign-in` desde Claude Code
- Usuario se loguea manualmente en la ventana del Playwright-chrome
- Sesion Clerk persiste en ese profile hasta que se cierre
- Todo el audit se hizo con cuenta real `gsaltron@gmail.com`, org `162e58e2-...`

### Audit findings (28 items priorizados)
Completa lista en orden de impacto en seccion "UX audit — post-Playwright" abajo. Highlights:
- **#1** EvaluateWorker sin nombre/RUT/proyecto -> data safety (supervisor puede evaluar al equivocado)
- **#4** Workers endpoint 8.7s N+1 -> query por worker en loop
- **#2-3** Clerk "Development mode" visible + menu en ingles
- **#5** /sign-up rompia funnel (signUpUrl apuntaba a /sign-in)
- **#8** Typos masivos UI + seed data sin tildes (Mantencion, Electrico, etc.)

### Fixes deployados (5 commits)

**Commit `ac50527` — 4 bloqueadores**
- `EvaluateWorker.tsx`: fetch worker + project en mount, header muestra "Sergio Diaz · Calderero · RUT 10.087.109-2 · Proyecto: Mantencion Mayor Concentradora · Codelco Andina"
- `workers.py`: list_workers consolidado a un solo query con `outerjoin + group_by` en vez de loop N+1. `min_score` ahora es `HAVING`. Verificado: 8694ms -> 1850ms (4.7x speedup)
- `App.tsx`: ruta `/sign-up/*` con `<SignUp>` de Clerk, `signUpUrl="/sign-up"` en SignIn
- `main.tsx`: `localization={esES}` via `@clerk/localizations` (instalado). "Administrar cuenta", "Cerrar sesion" en espanol

**Commit `02de8a3` — Typos + scores /5 + fechas**
- Strings UI acentuados: "Evaluacion"->"Evaluación", "Recontratarias"->"¿Recontratarías", "Habilidad Tecnica"->"Habilidad Técnica", "Telefono"->"Teléfono", "Ubicacion"->"Ubicación", "Planificacion"->"Planificación", "Score minimo"->"Score mínimo", "RUT invalido"->"RUT inválido", "Si"->"Sí", "aun"->"aún"
- `constants.ts` PROJECT_STATUSES + SCORE_LABELS + REHIRE_OPTIONS sync
- `Dashboard.tsx`: "62% recontrataria" -> "62% recomienda recontratar", Evaluaciones Recientes ahora son Links al WorkerDetail
- `ScoreBadge.tsx`: prop `showScale`; md size default shows "X.X / 5" inline; sm size keeps compact + title tooltip
- `WorkerDetail.tsx`: hero badge fuerza `showScale`, cada dimension muestra "X.X / 5" junto a las estrellas
- `Workers.tsx`: columna "Evals"->"Evaluaciones"
- Plural correcto: "1 evaluacion" / "N evaluaciones" (antes "N evals")
- `lib/dates.ts`: helper `formatRelative(iso)` que devuelve "hace 2 dias", "hace 21 h", "ayer", etc.
- Dashboard Evaluaciones Recientes muestra `· hace 21 h` despues del proyecto
- Backend `RecentEvaluationItem` ahora incluye `worker_id` para que el Link funcione

**Commit `fb0e3b7` + `953c090` — Migracion tildes en DB**
- Script nuevo `backend/scripts/fix_tildes.py` (idempotente, asyncpg direct via `statement_cache_size=0`): UPDATE workers.first_name/last_name/specialty, projects.name/location/client_name
- Corrido via `railway run python -u scripts/fix_tildes.py` contra prod Supabase sa-east-1. 52 + 4 = 56 rows updated
- Datos acentuados: Diaz->Díaz, Gonzalez->González, Munoz->Muñoz, Lopez->López, Sepulveda->Sepúlveda, Matias->Matías, Raul->Raúl, Sebastian->Sebastián, Hector->Héctor, Jose->José, Electrico->Eléctrico, Mecanico->Mecánico, Canierista->Cañerista, Operador Grua->Operador Grúa, Mantencion->Mantención, Ampliacion->Ampliación, Region->Región, Valparaiso->Valparaíso, Copiapo->Copiapó, Tarapaca->Tarapacá, Puchuncavi->Puchuncaví, Colbun->Colbún, Generacion->Generación
- `frontend/constants.ts` SPECIALTIES sync con valores acentuados (sino filtro de dropdown no matchea con DB)
- Seed scripts (`gen_seed_sql.py`, `seed_demo.py`, `admin.py`) sync -> futuros seeds nacen limpios

**Commit `8fa8bbd` — Autosave + disabled hint (EvaluateWorker)**
- Draft a localStorage key `faenascore:draft:{projectId}:{workerId}` en cada cambio
- Restaura en mount via `useEffect`. Limpia con `removeItem` al guardar exito
- Indicador "Borrador guardado hace X" bajo el boton cuando esta completo
- Si el boton esta disabled: helper text visible + `title` tooltip explica que falta:
  - "Completa los 5 puntajes" / "Falta 1 puntaje" / "Falta N puntajes"
  - "Indica si recontratarias"
  - "Escribe el motivo (minimo 3 caracteres)"
- Autosave deployado pero NO verificado interactivamente en Playwright (codigo straightforward, verificacion manual recomendada con recarga de pagina)

### Railway deploy notes
- **No hay autodeploy desde GitHub** en faenascore (confirmado por el usuario via screenshot del dashboard). Cada release requiere `railway up --detach` manual desde el CWD del proyecto
- Session del CLI expira. Si falla `Unauthorized`, correr `railway login` en terminal normal (no `!railway login` en prompt de Claude - el `!` es para comandos ejecutados desde el prompt interno)
- Bundle hashes verificados post-deploy para confirmar llego nuevo codigo: `eYslB05P` -> `DGYDkdEb` -> `DsKu3uAx` -> `OJ0Dr81T` -> `CcGOklUG` -> `DkzRyZF4`

### Pendiente implementar (orden sugerido)
1. **#12** Paginacion Workers — hoy hardcoded `size=50`, sin UI de paginacion. ~30 min
2. **#14** Skeletons en Dashboard + Evaluate + ProjectDetail — hoy muestran "Cargando..." plain text. Workers y EvaluateWorker YA usan Skeleton. ~15 min
3. **#2** Clerk production instance — bloqueado hasta comprar dominio (faenascore.cl o subdominio de faymex.cl). Una vez con dominio: crear prod instance en dashboard.clerk.com, sacar 4 env vars (`CLERK_SECRET_KEY`, `CLERK_JWKS_URL`, `CLERK_ISSUER`, `VITE_CLERK_PUBLISHABLE_KEY`), setear en Railway, re-deploy. Elimina banner "Development mode"

### P2 (pulido)
- Landing sin screenshots / pricing / footer legal
- WorkerDetail bundle 339KB (Recharts lazy pero pesado cuando hay poco data) — considerar spark SVG
- Evaluate page intermedia redundante (links a ProjectDetail, no a flujo de evaluacion)
- Mobile 375px: "Score Promedio" wrapea raro a 2 lineas
- Stars en EvaluateWorker sin `aria-label` (a11y)
- ProjectDetail sin badge de estado en header (solo en lista)
- Sin breadcrumbs
- Filas de tabla Workers no-clickeables enteras (solo nombre es Link)

### Deuda tecnica nueva descubierta en audit
- Dashboard hace 4 calls al backend en paralelo, max 2.5s c/u en sa-east-1 -> first paint ~3.5s. Palancas: HTTP cache `stale-while-revalidate`, session pooler 5432 (eliminaria overhead de `statement_cache_size=0`)
- Evaluaciones Recientes tienen fecha `created_at` que es la fecha de creacion del Evaluation. Si la sesion se alarga, "hace 21 h" queda desactualizado. Sin impacto real mientras no se refresque la pagina

---

## Sesion 15 abr 2026 — Seed, perf, UX audit

### Bloque 1: Seed demo data resuelto (commits 07ffb29, a13d683)
**Problema pendiente de ayer**: seed no funcionaba via Supabase transaction pooler (timeouts).

**Solucion**: `backend/scripts/exec_seed_sql.py` (nuevo) — asyncpg connect con `statement_cache_size=0` + `server_settings={'statement_timeout':'0'}`, ejecuta archivo SQL completo como UN solo `conn.execute(sql)`. El pooler no parsea statement por statement -> no hay timeouts per-row.

**Bug adicional encontrado en `gen_seed_sql.py`**: loop infinito cuando unique (project_id, worker_id) pairs disponibles < target=40. El while loop spinnea con `rng.choice` retries en duplicados, producia archivo SQL sin `COMMIT;` al final, y asyncpg hacia rollback silencioso al cerrar conexion.

**Fix**: pre-calcular todos los pares asignados, `rng.shuffle`, iterar hasta `min(40, len(all_pairs))`. Rompe cuando target alcanzado o pares agotados, COMMIT siempre se imprime.

**Datos seedeados finales (verificado con conexion fresca `scripts/check_seed.py`):**
- `mi-empresa` (34791eb6-e33e-4c75-bd4f-65b1fcc8f5cb): 3 proyectos, 20 workers, 37 evaluaciones
- `mi-empresa-23c437` (162e58e2-2530-4627-a0fa-9a5b5f824f14): 3 proyectos, 20 workers, 37 evaluaciones

**Nuevo archivo util**: `backend/scripts/check_seed.py` — verifica counts por org via asyncpg directo (bypassea SQLAlchemy session cache).

### Bloque 2: Incidente servidor wedged (resuelto con redeploy)
Al empezar la sesion, `https://faenascore-production.up.railway.app/` no cargaba (timeout 30s). Logs del container mostraban ultimo registro 2026-04-14 20:09:36 — el Uvicorn quedo wedged desde ayer por uno de los intentos fallidos del admin endpoint (loop de INSERTs largo bloqueo el event loop). Fix: `railway up --detach` levanto container nuevo y volvio a responder.

**Leccion**: endpoints HTTP no son buen lugar para batch largos. Si hace falta en el futuro -> Celery task o script standalone, nunca sincrono en request handler.

### Bloque 3: UserButton con logout en AppShell (commit 0d4c929)
Usuario reporto no ver opcion de logout. Agregado `<UserButton showName afterSignOutUrl="/">` en header de `frontend/src/components/layout/AppShell.tsx`. Muestra avatar + nombre + menu con profile y sign-out.

Usuario tambien pidio ver "creditos restantes". **Decision**: FaenaScore NO tiene sistema de creditos hoy. Pendiente definir modelo de negocio antes de implementar (ver seccion "Pendiente decisiones de producto").

### Bloque 4: Performance del Dashboard (commit 08e34b6)
Usuario reporto dashboard lento (5-6s). Root cause:
- `/stats`: 7 queries secuenciales (cada una await la anterior).
- `/top-workers`: 1 query + N+1 (un query rehire_yes por cada top worker, hasta 11 total).
- Total: 18+ round-trips al pooler de Supabase en sa-east-1 (~150-200ms c/u) + `statement_cache_size=0` fuerza re-parse cada vez.
- Ademas: Clerk JWKS verification + lazy-load del chunk Dashboard.

**Fix**: consolidar con `func.count(case(...))` para agregar conteos condicionales en la misma query.
- `/stats`: 7 -> 4 queries.
- `/top-workers`: 11 -> 1 query.
- `backend/app/api/v1/dashboard.py`: imports agregados `case`, removido loop N+1.
- Tests backend siguen pasando (21 OK).

**Resultado verificado por usuario**: dashboard ahora carga en ~3s (antes 5-6s).

**Palancas futuras si hace falta mas velocidad**:
1. Prefetch del chunk Dashboard al montar AppShell (~200-400ms).
2. HTTP cache `stale-while-revalidate` en `/stats` y `/top-workers`.
3. Pasar DATABASE_URL al session pooler (5432) para eliminar `statement_cache_size=0` overhead (mayor ganancia, requiere verificar IPv4 desde Railway).

### Bloque 5: Auditoria UX con Playwright (pendiente implementar)
Usuario pidio auditoria UX completa. Navegue landing (desktop 1440 + mobile 375), sign-in, y revise codigo de todas las paginas autenticadas (Dashboard, Workers, ProjectDetail, EvaluateWorker, Evaluate, Projects, WorkerDetail).

**NO se pudo probar flujo autenticado en vivo**: Playwright arranca sin sesion Clerk, no tengo credenciales. El analisis post-login es por lectura de codigo.

**Hallazgos organizados por prioridad** (lista completa abajo en seccion "UX audit — pendiente implementar").

**Top 5 recomendados para atacar primero (segun mi juicio UX)**:
1. **Clerk production instance + localizar sign-in a espanol**. Hoy hay banner "Development mode" y toda la UI del login en ingles. Mata credibilidad.
2. **EvaluateWorker debe mostrar nombre del trabajador y proyecto**. Hoy solo dice "Evaluar Trabajador". Riesgo de evaluar al equivocado en terreno.
3. **Toasts de error en lugar de `catch {}` silencioso** en Dashboard, Workers, Evaluate, ProjectDetail.
4. **Usar los Skeleton components (ya existen) en vez de "Cargando..." plain text** en Dashboard, Evaluate, ProjectDetail.
5. **Autosave a localStorage en EvaluateWorker** — supervisor pierde todo si se cae la senal en faena remota.

---

## UX audit — pendiente implementar (priorizado)

### P0 (matan credibilidad / bloquean uso)
1. **Clerk Development mode** visible en sign-in + UI en ingles. -> Upgrade a production instance, localizar con `localization={esES}`.
2. **EvaluateWorker.tsx sin nombre/proyecto del trabajador** en header. -> Mostrar nombre completo, RUT, especialidad, proyecto.
3. **`/sign-up` redirige al landing** — rompe funnel. -> Ruta `<SignUp>` de Clerk explicita + link desde sign-in.
4. **Errores silenciados con `catch {}`** en Dashboard, Workers, Evaluate, ProjectDetail. -> Toast de error + retry.

### P1 (friccion importante)
5. **Landing sin screenshots del producto** — solo texto + feature cards genericas con iconos lucide. -> Mockup hero + 2-3 capturas.
6. **Landing sin pricing** — duda sobre si es gratis para siempre. -> Seccion pricing o "Gratis / Pro proximamente".
7. **Skeleton.tsx existe pero NO se usa** en Dashboard, Evaluate, ProjectDetail. Muestra "Cargando..." texto plano. -> Reemplazar por Skeleton components.
8. **Scores sin escala explicita** ("3.9" sin /5). -> Mostrar "3.9 / 5" en KPIs y tooltip en stars.
9. **"62% recontrataria"** texto poco claro. -> "62% recomendaria recontratar" + tooltip con conteo absoluto.
10. **Evaluaciones recientes sin fecha/timestamp** en Dashboard. -> Mostrar "hace 2 dias".
11. **EvaluateWorker con typos**: "Recontratarias" (falta tilde + ¿?), "Evaluacion" (falta tilde). Boton disabled sin explicacion de por que. -> Tildes correctas + tooltip "Completa los 5 puntajes para guardar".
12. **Sin toast de exito al guardar evaluacion** — redirige silenciosamente. -> Toast "Evaluacion guardada — Sergio Diaz" con undo opcional.
13. **Workers sin paginacion visible** — hardcoded `size: 50`. -> Paginacion o "mostrando 50 de 127".
14. **Filtros activos sin chip/limpiar** — usuario olvida que filtro. -> Chips "Soldador ✕" arriba de resultados.
15. **EvaluateWorker: 5 dimensiones sin tooltip explicativo** — que significa "3 estrellas en Seguridad". -> Tooltip/leyenda "1=Muy malo, 5=Excelente".
16. **Sin guardar borrador** en EvaluateWorker. Supervisor pierde todo si se cae senal en mineria remota. -> Autosave a localStorage en cada cambio.

### P2 (pulido)
17. Landing mobile: hero subtitulo se corta raro en 3 lineas.
18. Footer sin links a terminos/privacidad/contacto.
19. ProjectDetail sin badge de estado (active/completed/cancelled).
20. WorkerDetail (347KB con Recharts) chunk grande. Reemplazar por spark SVG.
21. Evaluate page intermedia innecesaria (proyecto -> project detail -> evaluar).
22. Empty states sin CTA secundario (ej. "Sin evaluaciones" no linkea a Evaluar).
23. Sin breadcrumb navigation.
24. UserButton de Clerk sin localizar a espanol ("Manage account", "Sign out").

---

## Pendiente decisiones de producto (Gustavo/German)

1. **Modelo de monetizacion**: plan Free (limite evaluaciones/mes) vs Pro (ilimitadas). Precio. Creditos vs suscripcion. -> Sin esto no se implementa billing.
2. **Comprar dominio `faenascore.cl`** en NIC Chile (~$10k CLP/ano) — decision si reemplaza subdominio Railway.
3. **Landing page**: ¿pedir mockups/capturas del producto a disenador o usar screenshots reales?
4. **Launch strategy**: ¿demo 1:1 con contratistas conocidos de Gustavo, o landing publica + ads?
5. **Clerk production upgrade**: requiere configurar dominio propio para evitar el banner dev. ¿Esperamos a tener faenascore.cl o configurar en subdominio Railway?

---

## Archivos nuevos/modificados hoy

| Archivo | Cambio |
|---------|--------|
| `backend/scripts/exec_seed_sql.py` | NUEVO - ejecuta SQL seed via asyncpg con timeout=0 |
| `backend/scripts/check_seed.py` | NUEVO - verifica counts con conexion fresca asyncpg |
| `backend/scripts/gen_seed_sql.py` | FIX - loop infinito cuando pares insuficientes, ahora shuffle+iterate con break |
| `backend/app/api/v1/dashboard.py` | PERF - consolidacion queries via `func.count(case(...))` |
| `frontend/src/components/layout/AppShell.tsx` | FEAT - UserButton de Clerk con showName + afterSignOutUrl |
| `PROGRESS.md` | DOC - esta actualizacion |

## Commits del dia
- `07ffb29` feat: seed demo data script that bypasses pgbouncer timeouts
- `a13d683` fix: gen_seed_sql infinite loop when unique (project,worker) pairs < target
- `0d4c929` feat: add Clerk UserButton with name in AppShell header
- `08e34b6` perf: reduce dashboard backend queries from 18+ to 4

## Sesion 14 abr 2026 — Landing + features + quality
- **Landing page publica** en `/`, dashboard movido a `/app/*`, Clerk sign-in en `/sign-in`
  - `frontend/src/pages/Landing.tsx` con hero, problem, 6 features, CTA, footer
  - App.tsx reestructurado con SignedIn/SignedOut gate en `/app/*`
  - AppShell + todos los Link/navigate actualizados a `/app/*`
- **Seed demo script**: `backend/scripts/seed_demo.py` — 3 proyectos + 20 workers (RUTs validos) + ~40 evals
  - Uso: `python -m scripts.seed_demo --org-slug <slug>` o `--org-id <uuid>` + `--wipe` opcional
- **Edit forms**: NewProjectForm/NewWorkerForm aceptan `initial` -> modo edit. Boton Pencil en ProjectDetail y WorkerDetail
- **Evaluate next pending**: GET `/dashboard/next-evaluation` (pick proyecto activo con mas pendientes + primer worker). Banner en Dashboard con CTA
- **Export CSV workers**: GET `/workers/export.csv` (RUT, nombre, especialidad, telefono, email, activo, evaluaciones, score). Boton Download en Workers page
- **Fix apiFetch**: formatApiError aplana FastAPI detail=array a mensaje legible con campo
- **Code splitting**: lazy load paginas -> bundle inicial 722KB -> 281KB. Recharts (347KB) queda solo en WorkerDetail
- **Backend tests**: `tests/` con 21 tests unit (rut_validator + score_calculator) — `pytest -q` pasa

## Sesion 13 abr 2026 — Clerk auth real en produccion
- Clerk Development instance creada (willing-monitor-52.clerk.accounts.dev)
- 4 env vars seteadas en Railway: CLERK_SECRET_KEY, CLERK_JWKS_URL, CLERK_ISSUER, VITE_CLERK_PUBLISHABLE_KEY
- AUTH_MOCK_ENABLED=False, ALLOW_MOCK_IN_PROD=False
- CORS_ORIGINS restringido al dominio prod
- DATABASE_URL rotado (password nuevo Supabase)
- Dockerfile: ARG/ENV para pasar VITE_CLERK_PUBLISHABLE_KEY al build stage
- alembic/env.py: connect_args statement_cache_size=0 para pgbouncer
- App.tsx: SignedIn/SignedOut gate + setAuthTokenGetter sincrono (bug: useEffect corre despues de OrgProvider)
- Verificado end-to-end: login con Clerk, dashboard carga con Bearer token
- Repo: https://github.com/German-Faymex/FaenaScore
- **Produccion**: https://faenascore-production.up.railway.app
- **Railway project**: https://railway.com/project/7ec526bb-74bc-4796-bac4-4c89bde2d6bd
- **Supabase project ref**: sudhcjpiixkkwywapvpe (region sa-east-1)

## Resumen sesion 12 de abril 2026

### Bloque 1: Formularios CRUD (commit 7259787)
- Modal reutilizable (ui/Modal.tsx, mobile sheet + desktop center)
- NewProjectForm + NewWorkerForm (RUT validacion mod-11 cliente)
- ImportWorkersForm (dropzone Excel/CSV usando endpoint existente)
- AssignWorkersForm (multi-select con buscador)
- Wired en Projects.tsx, Workers.tsx, ProjectDetail.tsx
- Verificado end-to-end con Playwright local

### Bloque 2: Polish UI (commit 3e82a73)
- index.html title -> FaenaScore + meta description
- Skeleton.tsx (Card + Row variants) reemplaza "Cargando..."
- Empty states con CTAs a crear/importar
- EvaluateWorker: rehire reason required (>=3 chars) cuando != yes
- EvaluateWorker mobile: label stack sobre stars (no overflow a 375px)
- Verificado screenshots mobile 375px: Dashboard, Workers, Evaluate, ProjectDetail

### Bloque 3: Deploy produccion (commits 53d8e9b, faf46cd)
- ALLOW_MOCK_IN_PROD flag para testing sin Clerk todavia
- SPA fallback en main.py (sirve index.html para rutas no-/api)
- Dockerfile CMD: alembic upgrade head && uvicorn
- .env.example documentado
- Fix asyncpg statement_cache_size=0 para Supabase transaction pooler
- Supabase PostgreSQL creada (region sa-east-1, IPv4 shared pooler)
- Railway project faenascore creado, env vars seteadas, deploy OK
- Dominio: faenascore-production.up.railway.app
- DATABASE_URL rotado post-deploy (el primero quedo en chat)
- Smoke test: /api/health 200 + database connected, SPA routes 200, /api/v1/me OK

## Archivos nuevos hoy

| Archivo | Descripcion |
|---------|-------------|
| `frontend/src/components/ui/Modal.tsx` | Modal reutilizable responsive |
| `frontend/src/components/ui/Skeleton.tsx` | Skeleton + CardSkeleton + RowSkeleton |
| `frontend/src/components/forms/NewProjectForm.tsx` | Form crear proyecto |
| `frontend/src/components/forms/NewWorkerForm.tsx` | Form crear trabajador con RUT validado |
| `frontend/src/components/forms/ImportWorkersForm.tsx` | Modal upload Excel/CSV |
| `frontend/src/components/forms/AssignWorkersForm.tsx` | Multi-select asignar workers |
| `frontend/src/lib/rut.ts` | Validador RUT cliente (mod 11) |
| `.env.example` | Doc env vars |

## Env vars produccion (Railway)

- DATABASE_URL: Supabase pooler IPv4 (rotado 12 abr)
- DEBUG: False
- AUTH_MOCK_ENABLED: True
- ALLOW_MOCK_IN_PROD: True **(inseguro, solo testing)**
- CORS_ORIGINS: ["*"]

## Proximos pasos (para la proxima sesion)

### Prioridad 1: Seguridad (URGENTE antes de compartir con alguien real)
1. **Crear app Clerk produccion** — 4 vars: CLERK_SECRET_KEY, CLERK_JWKS_URL, CLERK_ISSUER, CLERK_AUDIENCE + VITE_CLERK_PUBLISHABLE_KEY en build
2. **Desactivar ALLOW_MOCK_IN_PROD** una vez Clerk funcione
3. **Restringir CORS_ORIGINS** al dominio real (hoy esta en "*")

### Prioridad 2: Decisiones de negocio
4. **Comprar dominio** faenascore.cl en NIC Chile (~$10k CLP/ano) — opcional, hoy funciona el subdominio Railway
5. **Landing page** — la home actual va directo al dashboard. Para mostrar a prospectos necesitamos una landing publica con pitch.

### Prioridad 3: Features para demo
6. **Seed data realista** para mostrar a potenciales clientes (3 proyectos, 20 workers, 40 evaluaciones distribuidas)
7. **Edit project + edit worker** — hoy solo se pueden crear, no editar
8. **Evaluate flow desde Dashboard** — boton "Evaluar siguiente pendiente" que salta al primer worker sin evaluar del proyecto mas activo
9. **Export CSV de trabajadores con scores** — util para gerentes de contratistas

### Prioridad 4: Quality
10. **Tests backend** — pytest fixtures + tests de RUT validator, score_calculator, endpoints criticos
11. **Error handling** — el apiFetch cliente deja "[object Object]" cuando backend devuelve array de errores (FastAPI validation). Aplanar a string legible.
12. **Code splitting frontend** — bundle 708KB, Vite warning. Lazy load Recharts, router, formularios.

## Problemas conocidos
- `CORS_ORIGINS=["*"]` en prod (inseguro pero no critico con auth mock)
- `AUTH_MOCK_ENABLED=True` en prod: cualquiera es "Dev User" con acceso total
- Bundle frontend 708KB (Recharts + lucide + Clerk) — sin code splitting
- apiFetch no maneja bien detail=array de FastAPI (muestra "[object Object]")
- Backend sin tests (baseline sprint 1 era E2E manual)

## Comandos utiles

```bash
# Backend local
cd backend && python -m uvicorn app.main:app --port 8001 --reload

# Frontend local
cd frontend && npx vite --port 5180

# PostgreSQL local
docker compose up -d  # puerto 5433

# Deploy (auto al hacer push, pero tambien)
railway up --detach

# Logs prod
railway logs

# Ver env vars prod
railway variables

# Health check prod
curl -s https://faenascore-production.up.railway.app/api/health
```
