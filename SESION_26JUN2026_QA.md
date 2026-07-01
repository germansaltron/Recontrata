# Sesión 26 jun 2026 — QA de lanzamiento + correcciones

> Registro de todo lo realizado en esta sesión: plan de QA, ejecución de pruebas
> (incl. flujo offline en navegador real), correcciones aplicadas y análisis de lo
> que falta para producción.
>
> Documentos hermanos: [`QA_PLAN_LANZAMIENTO.md`](QA_PLAN_LANZAMIENTO.md) (plan manual, ~140 casos) ·
> [`QA_RESULTADOS.md`](QA_RESULTADOS.md) (resultados automatizados).

---

## 1. Objetivo de la sesión

Asegurar que el sistema funciona bien y que no haya bugs que dañen la reputación en el
lanzamiento. Se pidió: (1) un plan de QA que cubra todas las funcionalidades, (2) ejecutar
las pruebas, (3) resolver hallazgos y (4) probar el flujo offline.

---

## 2. Lo que se hizo

### 2.1 Plan de QA (`QA_PLAN_LANZAMIENTO.md`)
Inventario completo de funcionalidades (11 routers backend + 18 páginas frontend) y ~140
casos de prueba manuales con ID, prioridad (P0/P1/P2), pasos y resultado esperado.
Organizado en 17 secciones (auth, multi-tenancy, workers/RUT/import, proyectos,
evaluaciones/scoring, **offline**, portal/réplica, consentimiento, calibración, dashboard,
fórmula, certificado, landing/marca, PWA, responsive, robustez y smoke test de producción).

### 2.2 Ejecución de pruebas automatizadas — backend (87/87 verdes)
Se corrió la suite con `pytest` contra un **Postgres real efímero (Docker)**:
- Lógica de puntaje, RUT (módulo 11), calibración, validación legal, hardening de seguridad.
- **Aislamiento entre organizaciones (16 tests)**: un usuario de Org A no puede leer ni
  escribir datos de Org B por ningún endpoint (riesgo reputacional #1). Sin fugas.
- **Nuevo: `backend/tests/integration/test_core_flow.py` (10 tests)** escrito en esta sesión:
  - Flujo completo org→proyecto→trabajador→evaluación.
  - Puntaje ponderado correcto vía API (minería 4.2 / general 4.0, verificado a mano) y
    recálculo al cambiar de industria.
  - Evaluación duplicada → 409; RUT duplicado → 409.
  - Ventana de edición vencida (>72h) → 409.
  - Soft-delete permite re-evaluar.
  - Portal: réplica del trabajador, opt-out revoca consentimiento, réplica ajena → 404.

### 2.3 Ejecución — frontend
- `npm run build` (`tsc -b && vite build`): **0 errores** de tipos; PWA generada (57 entradas precacheadas).
- Escaneo estático: **sin secretos hardcodeados** (front ni back), **sin `console.log`/`debugger`**,
  `<title>Recontrata</title>` correcto, **sin "FaenaScore" en texto visible**.

### 2.4 Flujo offline — verificado END-TO-END en navegador real (10/10)
Se montó el stack completo (Postgres efímero + backend con auth mock + frontend vite sin
Clerk + **Chromium headless vía Playwright** con `set_offline()` real). Resultado 10/10:
- Sin señal, al guardar la evaluación → se **encola en IndexedDB** (`recontrata-offline`).
- Sin señal **NO** llega al backend (no se pierde, ni se manda a medias).
- **Al reconectar** → sincroniza automáticamente (evento `online` → flush).
- La cola queda vacía y la evaluación llega con el puntaje correcto (avg 5.0 / weighted 5.0).
- Cero errores de consola.

> Nota de método: en **dev**, Vite carga las rutas como módulos lazy por red (fallan offline);
> en **producción** el service worker las precachea. Se replicó ese precache para probar la
> lógica real de cola/sync.

---

## 3. Correcciones aplicadas

### 3.1 ✅ Texto "faena" (decisión pan-LATAM)
La palabra "faena" (que en AR/UY = matadero) aparecía en texto visible. Corregido a vocabulario neutro:
- `frontend/src/lib/tutorials.ts`: "Crea tu faena" → **"Crea tu obra"**.
- `frontend/src/pages/Landing.tsx`: "¿Sin señal en la faena?" → **"…en terreno"**;
  "en plena faena" → **"en pleno terreno"**.
- Se dejó intencionalmente lo no visible/interno: keyword SEO `faena`, archivo `hero-faena.jpg`,
  y la clave de localStorage `faenascore:draft:` (cambiarla borraría borradores en curso).

### 3.2 ✅ Lint a 0 errores
6 avisos (4 `react-hooks/set-state-in-effect` + 2 `react-refresh/only-export-components`),
todos patrones **intencionales y correctos** (sync con localStorage/caché SWR; HMR-only).
Resueltos con `eslint-disable` puntuales y **justificados** en cada sitio, sin cambiar el
comportamiento en runtime (evita regresiones en la lógica de borrador offline). Archivos:
`org.tsx`, `main.tsx`, `Calibration.tsx`, `Evaluate.tsx`, `EvaluateWorker.tsx`.

---

## 4. Veredicto

La lógica de negocio, la seguridad de datos (multi-tenancy) y el flujo offline están
**sólidos y verificados** contra base de datos real y navegador real. **No se encontró ningún
bug funcional.**

---

## 5. Qué falta para salir a producción

### 5.1 🔴 Bloqueante real
- **Clerk a producción.** El banner "development mode" sigue pendiente (`pk_test` en prod).
  Requiere acceso de German al dashboard de Clerk: crear instancia de producción, copiar
  `pk_live_*`, setear `VITE_CLERK_PUBLISHABLE_KEY` en Railway (build-arg), y agregar
  `recontrata.cl` + `www` a los orígenes permitidos.

### 5.2 🟠 Decisión de negocio importante — monetización
Verificado en el código:
- **No hay integración de pagos** (ni Webpay/Transbank, ni MercadoPago, ni Stripe).
- **No hay enforcement de los límites de plan** (el "Gratis: 15 trabajadores / 1 proyecto"
  que muestra la landing NO está implementado en el backend; hoy se puede cargar ilimitado).
- Los 3 planes con precio de la landing son **solo vitrina**.

→ Decidir: **(a)** lanzar gratis/beta y cobrar manualmente al inicio (válido para validar), o
**(b)** construir pagos + cuotas antes de lanzar con precios visibles.

### 5.3 🟡 Endurecimiento recomendado (reputación)
- **Rate limiting**: no existe. Importa sobre todo en el **portal público del trabajador**
  (`/api/v1/portal/{token}`, réplica, opt-out), que no requiere login → scrapeable/abusable.
- **Monitoreo de errores** (Sentry o similar): no hay. Para detectar errores en producción
  antes que el cliente.

### 5.4 🟡 Operación
- **Backups de la base de datos** (Postgres Railway): confirmar respaldo automático y restauración.
- **Decidir el AccessGate**: el código `recontrata2211` viaja en el bundle (gate "blando").
  Para lanzar, o se apaga (`VITE_ACCESS_GATE=false`, se confía en Clerk) o se asume simbólico.
- **Deploy manual**: sin autodeploy; cada cambio es `railway up --detach`.

### 5.5 🟢 Cosmético / opcional
- El repo y los servicios de Railway siguen llamándose `faenascore-*` (funciona igual).

### Lo que ya está BIEN (verificado, no son pendientes)
- Health check en `/api/health`; Railway ya lo apunta correcto (`railway.toml`).
- Migraciones Alembic corren solas en el deploy (`alembic upgrade head` en el `Dockerfile`).
- En producción frontend y API se sirven en el **mismo dominio** → CORS no es problema.

---

## 6. Cómo reproducir las pruebas

### Backend (suite completa)
```bash
cd backend
# 1) Postgres efímero
docker run -d --name recontrata-qa-pg -e POSTGRES_PASSWORD=qa -e POSTGRES_DB=recontrata_qa -p 55432:5432 postgres:16-alpine
# 2) Correr con DB real (incluye los 16 tests de aislamiento)
TEST_DATABASE_URL="postgresql+asyncpg://postgres:qa@localhost:55432/recontrata_qa" .venv/Scripts/python.exe -m pytest -q
# Sin TEST_DATABASE_URL, los tests de integración se SALTAN y corren solo los unitarios.
docker rm -f recontrata-qa-pg
```

### Flujo offline (E2E navegador)
Requiere `playwright` (ya instalado en el venv del backend) + Chromium.
1. Levantar Postgres efímero (arriba) y crear tablas (`Base.metadata.create_all`).
2. Backend: `DEBUG=true AUTH_MOCK_ENABLED=true DATABASE_URL=...:55432... uvicorn app.main:app --port 8001`
   (el puerto **8001** coincide con el proxy de `vite.config`).
3. Frontend: `.env.local` con `VITE_AUTH_MOCK_ENABLED=true`, `VITE_ACCESS_GATE=false`,
   `VITE_CLERK_PUBLISHABLE_KEY=` (vacío) → `vite` (usa el proxy `/api` → 8001).
4. Sembrar org/proyecto/trabajador por API (mock auth, sin token) y manejar Chromium con
   Playwright usando `context.set_offline(True/False)`. El script usado quedó en el scratchpad
   de la sesión (`offline_e2e.py`).

---

## 7. Estado de artefactos

| Artefacto | Estado |
|-----------|--------|
| `QA_PLAN_LANZAMIENTO.md` | Plan manual de ~140 casos (referencia para QA continuo) |
| `QA_RESULTADOS.md` | Resultados de la ejecución automatizada |
| `backend/tests/integration/test_core_flow.py` | 10 tests nuevos (quedan en el repo, CI) |
| Correcciones en `frontend/src` | Aplicadas (faena + lint) |
| Stack temporal de pruebas (Docker PG, servidores, `.env.local`) | Eliminado, sin residuos |

---

_Próximo paso sugerido: migrar Clerk a producción (único bloqueante real) y decidir la
estrategia de monetización (lanzar gratis vs. construir pagos+cuotas)._
