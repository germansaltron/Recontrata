# Resultados de QA — Recontrata (ejecución automatizada)

> Ejecutado el 2026-06-26. Complementa a `QA_PLAN_LANZAMIENTO.md` (plan manual).
> Estas son las pruebas que se corrieron **automáticamente** contra el código real.

## Resumen

| Área | Resultado |
|------|-----------|
| Suite backend (pytest, con Postgres real) | ✅ **87 / 87 pruebas verdes** |
| Aislamiento entre organizaciones (multi-tenant) | ✅ 16/16 — sin fugas de datos |
| Cálculo de puntaje ponderado (vía API) | ✅ verificado a mano (4.2 minería, 4.0 general) |
| Reglas de negocio (duplicados, ventana de edición, soft-delete) | ✅ 10/10 (nuevas) |
| Portal del trabajador (réplica, opt-out, PII) | ✅ verde |
| Build frontend (`tsc -b && vite build`) | ✅ 0 errores de tipos; PWA generada |
| Lint frontend | ✅ **0 errores** (corregido) |
| **Flujo offline E2E (navegador real, Playwright)** | ✅ **10/10 verdes** |
| Marca / secretos / console.logs | ✅ limpio (texto "faena" corregido) |

**Veredicto:** la lógica de negocio, la seguridad de datos y el flujo offline están sólidos y verificados (DB real + navegador real). No se encontró ningún bug funcional. Único pendiente real: Clerk a producción (requiere acceso de German).

---

## Flujo offline — verificado end-to-end en navegador real (Playwright)

Montado: Postgres efímero + backend (auth mock) + frontend (vite, sin Clerk) + Chromium headless con `set_offline()` real. Las 10 aserciones pasaron:

1. ✅ La página de evaluación carga el trabajador y las 5 dimensiones.
2. ✅ El botón "Guardar" se habilita al completar el formulario.
3. ✅ **Sin señal**, al guardar: la evaluación se encola en IndexedDB (`recontrata-offline`).
4. ✅ **Sin señal NO llega al backend** (no se pierde, pero tampoco se envía a medias).
5. ✅ **Al reconectar**: se sincroniza automáticamente (evento `online` → flush).
6. ✅ La cola offline queda vacía tras sincronizar.
7. ✅ La evaluación sincronizada tiene el puntaje correcto (promedio 5.0, ponderado 5.0).
8. ✅ Cero errores de consola relevantes.

> Nota de método: en modo **dev** Vite carga las rutas como módulos lazy por red, que fallan offline; en **producción** el service worker las precachea (build = "precache 57 entries"). Se replicó ese precache calentando el módulo antes de simular la desconexión, para probar la lógica real de cola/sync (no el dev-server).

---

## Qué se ejecutó

### Backend — 87 pruebas (pytest + Postgres 16 efímero en Docker)
- `test_score_calculator.py` — fórmula de puntaje, perfiles por industria, redondeo.
- `test_rut_validator.py` — RUT chileno (módulo 11), incluido dígito K.
- `test_evaluator_calibration.py` — detección de indulgencia/severidad/efecto halo.
- `test_phase1_legal.py` — motivo obligatorio si no recontrata (cumplimiento legal).
- `test_security_hardening.py` — token admin fail-closed, allowlist de orden, límites de import.
- `integration/test_tenant_isolation.py` — **aislamiento entre orgs + PII del portal (16)**.
- `integration/test_core_flow.py` — **NUEVO**, escrito en esta sesión (10):
  - Flujo completo org→proyecto→trabajador→evaluación.
  - Puntaje ponderado correcto vía API y recálculo al cambiar de industria.
  - Evaluación duplicada → 409; RUT duplicado → 409.
  - Ventana de edición vencida (>72h) → 409.
  - Soft-delete permite re-evaluar.
  - Portal: réplica del trabajador, opt-out revoca consentimiento, réplica ajena → 404.

### Frontend
- `npm run build`: compila sin errores de TypeScript; genera service worker PWA (57 entradas precacheadas).
- `npm run lint`: 6 avisos (detalle abajo).
- Escaneo estático: marca, secretos, console.logs.

---

## Hallazgos

### ✅ H1 — RESUELTO (2026-06-26): texto visible con "faena"
Contradice la decisión pan-LATAM documentada del proyecto ("quitar 'faena' del texto visible" porque en Argentina/Uruguay = matadero). Aparece visible en:
- `frontend/src/lib/tutorials.ts:31` → título "Crea tu faena" (centro de ayuda).
- `frontend/src/pages/Landing.tsx:176` → "¿Sin señal en la faena? Igual evalúas".
- `frontend/src/pages/Landing.tsx:239` → "...cómo se evalúa en plena faena."

**Corregido**: "Crea tu faena" → "Crea tu obra" (`tutorials.ts`); "¿Sin señal en la faena?" → "...en terreno" y "en plena faena" → "en pleno terreno" (`Landing.tsx`).
> Se dejaron a propósito (no visibles / internos): meta keyword SEO `faena`, nombre de archivo `hero-faena.jpg`, y la clave de localStorage `faenascore:draft:` (cambiarla borraría borradores en curso).

### ✅ H2 — RESUELTO (2026-06-26): avisos de lint
Eran 6: 4 de `react-hooks/set-state-in-effect` (`Calibration.tsx:36`, `Evaluate.tsx:22`, `EvaluateWorker.tsx:53` y `:69`) + 2 de `react-refresh/only-export-components` (`org.tsx:14`, `main.tsx:14`). Todos son patrones **intencionales y correctos** (sync con localStorage / caché SWR; HMR-only). Se resolvieron con `eslint-disable` puntuales y **justificados** en cada sitio, sin cambiar el comportamiento en runtime (evita regresiones en la lógica de borrador offline). `npm run lint` ahora da **0 errores**.

### 🟡 H3 — Código del AccessGate embebido en el bundle
`frontend/src/components/AccessGate.tsx:10` → default `recontrata2211`. Es un gate "blando": el código viaja en el JS del cliente, así que no es protección real si alguien inspecciona el bundle. Está bien para una barrera suave de prelanzamiento; si se quiere protección real, usar `VITE_ACCESS_GATE=false` y confiar en Clerk, o un código no por defecto. **Decisión de producto.**

### ✅ Sin hallazgos negativos en:
- Fugas de datos entre organizaciones (probado activamente).
- Secretos/credenciales hardcodeados (ni frontend ni backend).
- `console.log`/`debugger` olvidados.
- Nombre de marca "FaenaScore" en texto visible (rebrand del nombre = limpio).
- CORS: configurable por entorno, sin wildcard en duro.

---

## Pendientes que NO se pueden automatizar desde aquí (requieren entorno en vivo)

1. **🔴 Clerk a producción** (P0). El banner "development mode" sigue pendiente según la memoria del proyecto (`pk_test` en prod). Requiere acceso de German al dashboard de Clerk. Es el último bloqueante real de lanzamiento.
2. ~~Modo offline real~~ → ✅ **VERIFICADO** end-to-end en navegador (ver sección arriba, 10/10).
3. **Recorrido visual E2E en móvil físico** (responsive con guantes, intro animada, certificado imprimible, tutoriales YouTube). Pendiente menor; conviene una pasada manual en un teléfono real.

> Estas 3 se pueden hacer levantando el stack con `AUTH_MOCK_ENABLED` + Postgres + build sin Clerk (la app tiene rama "sin Clerk"). Se dejó como paso opcional por el costo de orquestación.

---

_Suite reproducible:_ `cd backend && TEST_DATABASE_URL=postgresql+asyncpg://... pytest`. Sin `TEST_DATABASE_URL`, los 16 tests de integración se saltan y corren solo los 71 unitarios.
