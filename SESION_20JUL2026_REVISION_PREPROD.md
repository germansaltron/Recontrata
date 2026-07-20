# Sesión 20-jul-2026 — Revisión exhaustiva pre-producción + fix A1 + auto-deploy

> Objetivo de la sesión: revisión exhaustiva de Recontrata en víspera de salir a
> producción, arreglar lo bloqueante, y dejar el deploy automatizado.

---

## 1. Estado de los dos bloqueadores externos

**🟡 Verificación de Saltronic en Meta → sigue "En revisión".** Confirmado hoy en el
Centro de Seguridad del portafolio Meta (`528027061198782`): *"~2 días laborables… En
revisión"*. Enviada el 19-jul; como el 19-20 fue fin de semana, la fecha realista de
respuesta es **~miércoles 22-jul**. No ha llegado correo de Meta. Hasta que apruebe, el
bot sigue con `BOT_ENABLED=false` y número de PRUEBA (correcto).

**🟠 Cuenta empresa → Flow → pasarela: falta MÁS que pegar credenciales.**
- ✅ Construido y testeado: cliente Flow (firma HMAC), webhook con re-consulta de estado
  autoritativo e idempotencia por `flow_token`, modelo de suscripción, enforcement de
  límites (candado freemium con `BILLING_ENFORCEMENT_ENABLED=false`).
- ❌ **NO construido — la Fase 5:** endpoints de checkout (crear customer, registrar
  tarjeta, crear suscripción) + conectar el botón "Mejorar" (hoy `Billing.tsx` muestra un
  toast honesto "el pago se habilita muy pronto"). También falta correr
  `scripts/flow_bootstrap_plans.py` y el QA E2E en sandbox.
- ⚠️ Conclusión: cuando llegue la cuenta empresa, la pasarela es **~1 sesión de trabajo**,
  no "10 minutos de pegar la API key".

---

## 2. Revisión exhaustiva — hallazgos

Revisión hecha con lectura dirigida del backend + 2 agentes (frontend / infra+tests).
Resultado global: **producto sólido y bien construido, sin bloqueadores críticos de
código.** El único hallazgo que se arregló antes de lanzar fue A1 (pérdida de datos).

### 🔴 ALTO — ✅ RESUELTO esta sesión

**A1. Pérdida permanente de evaluaciones offline** — `frontend/src/lib/offlineSync.ts` +
`api.ts`. El flush de la cola solo trataba como reintentable el error de red (`TypeError`);
**cualquier otro error (401 por token lento, 5xx transitorio, 402) borraba la evaluación de
la cola para siempre** → chocaba con la propuesta de valor offline-first.
- **Fix:** solo los errores definitivos de un item (`400/409/422` = validación/duplicado) lo
  descartan; auth/servidor/rate-limit se conservan en cola y se reintentan (`classifyFlushError`).
- **Fix 2:** `apiFetch` ya no manda requests sin `Authorization` cuando el race del token
  (5 s) vence — falla con 401 explícito, así la evaluación sobrevive en la cola.
- **Tests:** se agregó **Vitest** (antes el frontend no tenía runner) + 17 tests que cubren
  la política de reintento/descarte. `npm test` verde, `npm run build` verde, lint limpio.
- Commit `9952025`. **Verificado en producción** (firma `new Set([400,409,422])` presente en
  el bundle real `index-IngxCRuU.js`).

### 🟠 MEDIO — ⏳ PENDIENTES (retomar mañana)

- **M1. Bot: `asyncio.create_task` fire-and-forget** — `app/api/v1/whatsapp.py:201`. La
  respuesta del bot corre en una task sin referencia retenida → Python solo guarda refs
  débiles → bajo carga el GC puede matarla y **la respuesta nunca se envía**, sin error.
  Fix: retener la task en un `set` a nivel módulo (o `BackgroundTasks`).
- **M2. Evaluaciones no validan pertenencia a la org** — `app/api/v1/evaluations.py`
  (`_create_single`, usado por create y batch). Toma `worker_id`/`project_id` del body sin
  verificar que sean de `org_id` (inconsistente con `assign_workers`, que sí valida).
  Explotabilidad práctica baja (UUIDs inadivinables, workers por-org), pero rompe el
  invariante de aislamiento y puede ensuciar el portal de un worker. Fix trivial.
- **M3. Sin rate limiting en endpoints públicos** — webhook de Flow (dispara una llamada
  saliente por request) y portal. Considerar `slowapi`.
- **M4. Bot: buffer de mensajes nunca implementado** — `MESSAGE_BUFFER_SECONDS` declarada
  sin uso. 3 mensajes seguidos = 3 llamadas al LLM = 3 respuestas. UX de WhatsApp. El bot de
  Faymex ya tiene el patrón (acumular + cancelar timer) para copiar.
- **M5. Frontend: sin handler global de 401** (sesión que expira sin navegar). Considerar
  uno análogo a `setPlanLimitHandler` (402) que redirija a `/sign-in`.
- **M6. Frontend: detección de 403 por string matching frágil** — `Calibration.tsx:32`
  usa `String(e).includes('403')`; debería ser `e instanceof ApiError && e.status === 403`.
- **M7. Infra — endurecimiento:** contenedor corre como **root** (falta `USER` en
  Dockerfile); `alembic upgrade head` en el CMD de arranque (carrera si se escala a >1
  réplica); `requirements.txt` con rangos `>=` sin lockfile; `python-jose` con CVEs
  conocidas (mitigadas por fijar `algorithms=["RS256"]`, pero está poco mantenida — evaluar PyJWT).

### 🟡 BAJO — ⏳ pendientes

- **Email de usuario se guarda vacío** desde el provisioning de Clerk (`dependencies.py:48`)
  → hoy no se puede identificar usuarios por correo. Se arregla configurando el JWT template
  de Clerk para incluir `email`.
- `BOT_SUPPORT_EMAIL` / `MAX_TURNS` declaradas sin efecto (deuda ya documentada en BOT_WHATSAPP.md).
- Prefijo legacy `faenascore:draft:` en localStorage (`EvaluateWorker.tsx:13`); cosmético.

### ✅ Lo que está BIEN (confianza para lanzar)

- Webhooks: WhatsApp con HMAC + idempotencia por `wamid`, siempre 200; Flow re-consulta el
  estado autoritativo + idempotencia por `flow_token`.
- Secure-by-default: `BOT_ENABLED`, `BILLING_ENFORCEMENT_ENABLED`, `AUTH_MOCK_ENABLED` en
  `false`, fallan cerrado; `main.py` rehúsa arrancar con mock auth en prod.
- Aislamiento multi-tenant consistente (`get_org_member`) con test de aislamiento como CI
  gate (salvo el gap M2).
- Lógica de negocio: el score calculator valida integridad de pesos al importar; RUT
  validator correcto; time-lock de evaluaciones (Ley 21.719).
- Portal público: no expone identidad del evaluador, fuera de Clerk, token de 256 bits.
- Higiene de repo: sin secretos commiteados, sin `dist/` ni `.env` trackeados, migraciones
  lineales (1 head), buenos índices.
- Tests: **88 backend passed** (+64 integración que corren en CI con Postgres), build de
  frontend OK.

---

## 3. Cambio de infraestructura: DEPLOY AHORA ES AUTOMÁTICO (GitHub → Railway)

**Antes:** deploy manual con `railway up` (sin source GitHub). Problema descubierto hoy: el
Railway CLI de este equipo está logueado en la cuenta de **Faymex (bodegaquilp01)**, y
Recontrata vive en **gsaltron@gmail.com** → `railway up` apuntaba al workspace equivocado
("german-faymex's Projects", que NO contiene Recontrata).

**Ahora:** Germán conectó el **Source Repo `germansaltron/Recontrata`** (branch `master`) al
proyecto Railway desde el dashboard. **Cada push a `master` despliega solo.** Se recomendó y
(idealmente) activó **"Wait for CI"** para que solo despliegue con el CI en verde.

> ⚠️ **CAMBIO DE FLUJO IMPORTANTE:** de ahora en adelante, **`git push` a master = deploy a
> producción.** Antes el push era seguro (no desplegaba). Tenerlo presente siempre.

**Plan B (por si el auto-deploy falla):** hay un `deploy.sh` en la raíz que despliega con un
**project token** de Railway (`RAILWAY_TOKEN`), sin depender del login del CLI ni tocar la
sesión de Faymex. Requiere pegar el token en `.railway-token` (gitignored). Setup documentado
en la cabecera de `deploy.sh`.

---

## 4. Estado de producción al cierre (verificado)

- `https://recontrata.cl/api/health` → **200**, `database: connected`.
- SPA sirve 200; fix A1 confirmado en el bundle real de prod.
- Nota: Cloudflare cachea el `index.html` unos minutos tras cada deploy (el shell va con
  `no-cache`, pero el CDN tarda en soltar la copia). El build real es el que lista el
  service worker. Ctrl+Shift+R fuerza la versión nueva.

---

## 5. Próximos pasos (orden sugerido para mañana)

1. **Confirmar auto-deploy en push:** el próximo `git push` a master debe disparar un deploy
   solo. Si no, revisar permisos de la GitHub App de Railway sobre el repo (el dashboard
   mostraba "Auto deploy unavailable").
2. Cuando Meta apruebe (~22-jul): dar de alta el número definitivo +56 9 2731 5616 y prender
   `BOT_ENABLED=true` (Fase 4 del bot). Ver `docs/BOT_WHATSAPP.md`.
3. Cuando llegue la cuenta empresa: **codificar la Fase 5 de Flow** (checkout) + bootstrap de
   planes + QA E2E en sandbox. Ver `docs/PASARELA_PAGO_FLOW.md`.
4. Backlog de calidad (no bloqueante): M1 (bot fire-and-forget) y M2 (aislamiento en
   evaluaciones) son cambios chicos de bajo riesgo — buenos candidatos para la próxima pasada.
