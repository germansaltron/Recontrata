# FaenaScore — Progreso de Desarrollo

## Ultima actualizacion: 2026-07-19 (🎉 BOT FUNCIONANDO en vivo con el número de prueba de Meta)

---

## 🎉 SESIÓN 19-JUL — EL BOT FUNCIONA EN VIVO (número de PRUEBA)

Doc completa: **`docs/BOT_WHATSAPP.md`** (incluye los 4 gotchas de puesta en marcha y el costo medido).

**Conversación real por WhatsApp, verificada de punta a punta:** saludo textual, no repite saludo,
precios correctos desde `plans.py`, `registrar_prospecto` creó un **lead** (dedujo rubro y banda de
trabajadores solo), y `derivar_a_soporte` entregó `atencion@recontrata.cl`. ~5 s de latencia.

**Costo medido con `count_tokens`** (no estimado): prefijo estable 3.821 tokens (⇒ el caché aplica),
**~$2 CLP por conversación** de 6 turnos con caché; 1.000 conversaciones ≈ USD 2.

**Infra montada hoy:** App de Meta "Recontrata Bot" (`1777753076558682`) bajo el portafolio
Saltronic; número de prueba +1 555 181-5450; **correo del dominio** con Cloudflare Email Routing
(`atencion@recontrata.cl` ya EXISTE — antes el bot daba una dirección que rebotaba); organización
de **Anthropic a nombre de Saltronic** (la anterior facturaba a Faymex, RUT 76.536.742-5) con
espacios separados para Recontrata y Casilisto.

**Verificación de negocio de Meta:** ENVIADA el 19-jul, "En revisión" (~2 días laborables).

### ⚠️ Pendientes de esta sesión

1. **Rotar credenciales expuestas — falta SOLO `ADMIN_TOKEN`.** ✅ `DATABASE_URL` (Supabase),
   ✅ `CLERK_SECRET_KEY` (que además NO se usa en el código: la auth va por JWKS) y ✅ el token de
   WhatsApp ya fueron rotados. El `ADMIN_TOKEN` necesita **≥32 caracteres** (si es más corto, el
   endpoint de admin queda bloqueado por diseño). **Cargarlo por el PANEL WEB de Railway**, nunca
   por comando — el valor no debe pasar por el chat.
2. **Token de WhatsApp**: es temporal y vence a **hora fija**. Montar **token permanente de
   usuario del sistema** antes de producción, para no depender de regenerarlo a mano.
3. **`RESEND_API_KEY`**: sin ella los correos de leads solo se loguean. Al configurarla, **EDITAR**
   el SPF de Cloudflare (no crear un segundo) para incluir a Resend.
4. **Número definitivo** +56 9 2731 5616 (chip WOM nuevo, sin WhatsApp, a nombre personal por ahora):
   registrar cuando apruebe la verificación de negocio.

---

## 📌 SESIÓN 17-JUL — RESUMEN Y CÓMO RETOMAR MAÑANA

Doc completa del bot: **`docs/BOT_WHATSAPP.md`**. Todo pusheado a `master`.

**Lo que se hizo hoy:**
1. **Bot de WhatsApp de ventas — Fases 1, 2 y 3 HECHAS** (código completo, 152 tests verdes,
   bot DORMIDO con `BOT_ENABLED=false`). Vive en `backend/app/bot/` + `app/api/v1/whatsapp.py`.
   - F1 (`edce465`): webhook con firma HMAC + idempotencia por `wamid`.
   - F2 (`c213077`): motor de conversación, Sonnet 5 + tool-use (registrar_prospecto,
     derivar_a_soporte, escalar_a_humano). Tono formal-cercano, tú, saludo aprobado.
   - F3 (`ab516d0`): correo de lead y escalamiento por Resend, con marcha blanca (ALERTS_TEST_MODE).
2. **Landing público desplegado** (`8f4706a`): recontrata.cl se ve sin código; la app sigue
   con `recontrata2211`. **Saltronic SpA nombrado** en sitio/términos/privacidad (`d40566c`).
3. **Trámite Meta** (ver sección de abajo): portafolio **Saltronic SpA** creado, **dominio
   recontrata.cl VERIFICADO**. La verificación de negocio se creyó enviada el 17-jul pero
   **había quedado como borrador**; se ENVIÓ de verdad el **19-jul** y ahora sí está
   **"En revisión"** (~2 días laborables ⇒ ~mié 22-jul). Ver la corrección más abajo.
4. **Datos demo sembrados** en la org del tester Eric (erojas): 20 trabajadores, 3 faenas,
   37 evaluaciones (org slug `mi-empresa-a72e5f`, id `aede6fb3-...`).

**Qué falta / próximo paso (por dónde seguir mañana):**
- **Fase 4 del bot — infra Meta.** Se puede AVANZAR YA sin esperar la verificación: crear la
  **App de Meta** (en developers.facebook.com, vinculada al portafolio Saltronic) + producto
  WhatsApp → da un **número de PRUEBA** al instante. Con eso + una `ANTHROPIC_API_KEY` se
  prueba el bot EN VIVO (que Sonnet 5 responda bien, que el caché funcione, que llegue el
  correo real por Resend). Necesito 3 datos de esa App: **App Secret, Phone Number ID, token**.
- **Verificación en vivo del bot** (pasos 3/5/6 del plan): pendiente hasta tener llave + número.
- **Envío real de correo:** falta `RESEND_API_KEY` (cuenta Resend de Recontrata).
- **Número definitivo:** chip WOM de PLAN (no prepago) a nombre de Saltronic, sin instalarle
  WhatsApp, para cuando apruebe la verificación de negocio.

**⚠️ Bug descubierto (anotado, no urgente):** los correos de los usuarios se guardan VACÍOS en
la base (el provisioning desde Clerk no captura el email). Hoy no se puede identificar usuarios
por correo. Revisar cuando toque.

---

## 🟢 META WHATSAPP — trámite en curso (17-jul)

Portafolio comercial de Meta para el bot: **"Saltronic SpA"** (id 528027061198782), bajo el
login **gsaltron@gmail.com**. Doc del bot: `docs/BOT_WHATSAPP.md`.

**Cómo se llegó:** los 3 portafolios de gsaltron estaban al tope (límite 3). Se reutilizó el
portafolio **VACÍO** "Germán Saltron Mellado" (0 activos, sin verificar) → renombrado a
Saltronic SpA + info legal (RUT 78.462.524-9, dirección Quilpué). **NO se borró Luddos**
(tiene página FB de 1.400 seg + IG que se quieren conservar; además es otra sociedad, EIRL
76.933.353-3). **NO se tocó "joannasoymaestra"** (portafolio de SoyMaestra SpA, 78.393.119-2).

**Estado del trámite:**
- ✅ **Dominio recontrata.cl VERIFICADO** (metaetiqueta `facebook-domain-verification` en el
  `index.html` estático, commit del 17-jul; el crawler lee HTML crudo, no pasa por el SW).
- ⏳ **Verificación de negocio EN REVISIÓN — enviada el DOM 19-jul** (~2 días laborables ⇒
  respuesta esperable ~mié 22-jul, porque el 19 es domingo). Se subió la **constitución** +
  el **e-RUT** (por la dirección). Tipo de negocio: **"Empresa privada"** (un SpA NO es las
  opciones "Sociedad" de Meta, que son bolsa/partnership).

  > ⚠️ **CORRECCIÓN (19-jul).** Esta bitácora decía desde el 17-jul que la verificación estaba
  > "en revisión". **Era FALSO**: el 17 se subieron los documentos pero se salió del flujo
  > (para ir a verificar el dominio) **sin llegar al paso final de envío**. La solicitud quedó
  > como BORRADOR — el Centro de seguridad mostraba *"Retoma el proceso de verificación donde
  > lo dejaste · Solicitud pendiente · [Continuar]"*, y por eso nunca llegó correo de Meta ni
  > corrió el plazo. Se detectó el 19-jul al revisar y se completó ese día.
  >
  > **Lección (aplica a todo trámite web):** la confirmación real es el ESTADO en la pantalla
  > tras recargar, no lo que uno cree que envió ni el cuadro de "gracias". Estado bueno =
  > **"En revisión"** (sin botón "Continuar"). Verificar SIEMPRE recargando la página.
- Para reforzar la revisión, recontrata.cl ahora **nombra a Saltronic SpA** (pie + términos +
  privacidad, commit `d40566c`), porque es el sitio declarado como web del negocio.

**Reglas aprendidas (para Casilisto después):**
- Número WhatsApp: **1 portafolio (Saltronic) → 1 verificación**, y adentro **1 WABA + 1 App +
  1 webhook + 1 número por producto**. Casilisto hereda la verificación (mismo SpA); solo suma
  su número + App apuntando al backend de Fillanyform.
- Cada número debe estar **limpio** (sin WhatsApp), recibir SMS una vez, registrado con RUT
  Saltronic, y **nunca instalarle WhatsApp**. Chips de plan barato WOM (no prepago: se muere a
  los 180 días sin recarga y el bot no avisa).
- El nombre del portafolio/negocio NO puede ir en mayúsculas (Meta lo rechaza salvo siglas):
  usar "Saltronic SpA", no "SALTRONIC SPA".

**Pendiente del trámite:** esperar la verificación de negocio. En paralelo se puede crear la App
de Meta + número de PRUEBA (no requiere verificación) para probar el bot.

---


---

## ✅ DESPLIEGUE 17-jul-2026 — landing PÚBLICO + Fase 1 del bot (dormida)

`railway up --service faenascore`. Commits `edce465` (bot fase 1), `81143d6` (doc), `8f4706a` (landing).

**Qué cambió para el visitante:** `recontrata.cl` ahora muestra el **landing sin pedir código**.
`/terminos` y `/privacidad` también. La app (`/app`), el registro y todos los datos siguen detrás de
`recontrata2211`, y el `noindex` se mantiene → **no es el lanzamiento**, solo se destapó la vitrina.

**Por qué:** la revisión de Meta para el bot de WhatsApp valida que el negocio existe visitando el
sitio; un muro de contraseña es causa probable de rechazo (días perdidos por cada reintento). Y el
bot de ventas necesita un landing al cual derivar. Ver `docs/BOT_WHATSAPP.md`.

**Verificado post-deploy (en prod, no en local):**
- `/api/health` → 200 `database: connected` (⇒ la migración `019426b0cd06` corrió: 4 tablas del bot).
- `recontrata.cl/` → landing público ✅ · `recontrata.cl/app` → gate pidiendo código ✅
- `POST /api/v1/whatsapp/webhook` sin firma → 200 sin procesar ✅
- `GET /api/v1/whatsapp/webhook` sin verify token → 403 (falla cerrado) ✅
- **Bot DORMIDO**: no hay ninguna var del bot en Railway ⇒ `BOT_ENABLED=False` por default del código.

### ⚠️ Dos trampas de verificación que casi me engañan (anotar para la próxima)

1. **El service worker sirve el bundle viejo.** Tras el deploy, `recontrata.cl` me seguía mostrando el
   gate con el aviso "Hay una versión nueva". Un visitante NUEVO (sin SW) sí ve el landing. Para
   verificar de verdad hay que desregistrar el SW y borrar `caches` antes de recargar. **Los testers
   con la PWA instalada verán la versión vieja hasta que toquen "Actualizar"** (comportamiento normal).
2. **`localStorage.recontrata_access` dura 90 días.** Si tu navegador ya pasó el gate alguna vez, la app
   te abre sin pedir código y parece que el gate está roto. Hay que borrar esa marca para probar.

También: el `.env` local tiene `VITE_ACCESS_GATE=false` (intencional, para dev) → **el gate NUNCA se ve
en local**. Para probarlo hay que construir sin `.env`, como hace el Dockerfile.

---

## 🤖 BOT DE WHATSAPP (ventas) — Fase 1 HECHA, dormido en prod

Doc completa: **`docs/BOT_WHATSAPP.md`**. Commit `edce465`. **NO desplegado aún.**

### Alcance: SOLO ventas (decisión del 16-jul)

El bot capta **prospectos**. **NO consulta datos del producto** (no busca trabajadores, no
muestra puntajes, no toca `organizations` ni `workers`). Razones:

- Los puntajes son **datos personales (Ley 21.719)** y el producto los protege con
  consentimiento, rastro inmutable, derecho a réplica y opt-out. Mandarlos por WhatsApp los
  saca de esa estructura (quedan en teléfonos personales, se reenvían, se fotografían).
- Los clientes RRHH **ya tienen la PWA** offline: el bot no les resuelve ninguna carencia.
- **Soporte a clientes → `atencion@recontrata.cl`**. El bot lo entrega y cierra (mismo gesto
  que el bot de Faymex usa con los CV).

**Consecuencia:** sin lectura de datos, NO hace falta auth máquina-a-máquina, ni vínculo
teléfono→org, ni API key por org. Por eso vive como **router dentro del backend**
(`app/api/v1/whatsapp.py` + 2 líneas en `main.py`), sin superficie de seguridad nueva.

### Fase 1 — hecho y verificado

- Webhook Meta: `GET` de alta (`hub.verify_token`) + `POST` con **firma HMAC
  `X-Hub-Signature-256` obligatoria** sobre el cuerpo crudo (`compare_digest`, falla cerrado
  sin `META_APP_SECRET`). **Ni el bot de Faymex ni el de SoyMaestra validan firma.**
- **Idempotencia por `wamid`** (índice unique en `bot_inbound_events`) — Meta reintenta las
  entregas. Mismo patrón que `PaymentEvent.flow_token` en billing.
- **Siempre responde 200**: un 5xx hace que Meta degrade/desactive la entrega (fue causa raíz
  de una caída real en el bot de Faymex).
- **`BOT_ENABLED` (default `false`)** — candado dormido, calcado de `BILLING_ENFORCEMENT_ENABLED`.
- Modelos + migración `019426b0cd06`. Ninguna tabla del bot referencia tablas del producto.
- **Verificación:** 141 tests verdes (115 previos + 26 nuevos) **y** prueba real con `curl`
  contra servidor + Postgres: la base queda con **1 sola fila** — firma falsa rechazada,
  reintento de Meta deduplicado, candado dormido respetado.

### LLM: `claude-sonnet-5` (NO Opus — decisión explícita)

Gotchas de Sonnet 5 ya considerados: corre thinking **adaptativo si se omite el campo**
(al revés que 4.6) → se pone `thinking: disabled` explícito; `effort` default es `high` → se
baja a `low`; **`temperature`/`top_p` dan 400** → el tono va solo en el prompt.

### Próximos pasos del bot

1. ✅ **Fase 2 HECHA** (commit `c213077`) — motor de conversación en `backend/app/bot/`:
   `AsyncAnthropic` + tool-use, Sonnet 5 (thinking off, effort low, sin temperature, system
   cacheado). 3 herramientas: `registrar_prospecto`, `derivar_a_soporte`, `escalar_a_humano`.
   KB de precios generada desde `app/billing/plans.py`. Webhook procesa en tarea de fondo.
   148 tests verdes (7 nuevos con cliente Anthropic falso). **Falta prueba EN VIVO** (modelo,
   caché, tokens) — necesita `ANTHROPIC_API_KEY` + número de prueba de Meta.
2. ✅ **Fase 3 HECHA** (commit `ab516d0`) — `app/bot/notifications.py`: correo de lead y de
   escalamiento por Resend, con redirección por `ALERTS_TEST_MODE` (marcha blanca). Avisos se
   mandan tras el commit (mejor esfuerzo). 152 tests verdes. **Falta el envío real** (`RESEND_API_KEY`).
3. **Fase 4** — infra Meta: **verificación de negocio de Saltronic SpA EN REVISIÓN** (arriba).
   Falta crear la App de Meta + número de PRUEBA (no requiere verificación) para probar el bot
   en vivo, y luego el número definitivo + revisión del nombre para mostrar.

### ⚠️ Deuda anotada (fuera del alcance del bot)

Prod corre con **`AUTH_MOCK_ENABLED=True` + `ALLOW_MOCK_IN_PROD=True`** en Railway: la
verificación de Clerk está puenteada y todo request entra como `dev_user_001` sin mirar el
token. El código está bien (`config.py` deja ambos en `False` por defecto); son las env vars.
Hoy lo tapa el código de acceso del prelanzamiento, y **este bot no depende de eso** porque no
lee datos del producto. **Hay que apagarlo antes de abrir el beta.**

---

## ✅ DESPLIEGUE 15-jul-2026 — HECHO (con el candado DORMIDO)

- **Desplegado a producción** (`railway up`, servicio `faenascore`) con **`BILLING_ENFORCEMENT_ENABLED=false`**
  en Railway → el candado de planes queda **dormido**, los testers **NO** tienen límites. Verificado post-deploy:
  health 200 (`database: connected` → migraciones corrieron), recontrata.cl 200, `/api/v1/webhooks/flow` 422
  (ruta viva), billing 401 (auth), `/me` 401 (auth de testers intacta). Sin downtime.
- **Para activar el cobro (con Flow):** poner `BILLING_ENFORCEMENT_ENABLED=true` en Railway + credenciales Flow
  (Fase 5). ANTES de prenderlo, subir las orgs de testers a un plan alto o cerrar el beta.
- Fixes de feedback (copy ROI, aviso offline iOS) **ya en producción** con este deploy.
- **⛔ CUIDADO al desplegar el enforcement de planes durante el beta:** la migración `1ac66b2f6de5`
  backfillea **todas** las orgs a `free`, y el candado limita a **15 trabajadores activos / 1 proyecto
  activo**. Los testers son **design partners con acceso libre** (`BETA_SETUP.md`). Si se despliega tal cual,
  **los testers con >15 trabajadores o >1 proyecto activo chocarán con el paywall**. Antes de desplegar, elegir:
  - **A)** subir las orgs de testers a un plan alto (enterprise/ilimitado) o un "plan beta";
  - **B)** una bandera/bypass del enforcement mientras dure el beta;
  - **C)** no desplegar el enforcement todavía (mantenerlo en `master` y desplegarlo junto con Flow al cerrar el beta).
  - **✅ ELEGIDO 15-jul (opción B):** flag `BILLING_ENFORCEMENT_ENABLED` (default **False**). El candado queda
    **dormido** en prod → testers sin límites. Para activar el cobro con Flow, poner la env var en `True`.
- Los fixes de feedback del 15-jul (copy ROI, aviso offline iOS) **tampoco** están en prod aún; van en el próximo `railway up`.

## Fixes de feedback de tester (15-jul)

- ✅ **#1 Copy del ROI** del plan Pro reescrito (se quitó "ROI sobre 7x", que confundía). commit `085e855`.
- ⚠️ **#2 Doble email de código de verificación**: **NO es bug de nuestro código** (solo se usan los
  componentes hospedados de Clerk; StrictMode es inerte en el build de prod). Es **configuración de Clerk**
  (dashboard): probablemente "Email verification code" **y** "link" ambos activos → apagar uno. Requiere acceso
  de Germán al dashboard de Clerk.
- ✅ **#3 Offline en iOS Safari**: en iOS el modo sin señal solo funciona con la app instalada. Se agregaron
  los metas `apple-mobile-web-app-*` + un banner que guía a "Agregar a inicio" (auto-oculto en desktop/Android
  y si ya está instalada). commit `206d5ab`. Confirmar final en un iPhone real.
- 🕓 **#4 Voz de los tutoriales** (muy lenta): pendiente; requiere re-render de los clips (TTS en
  `tutorial/scripts/clipkit.py`) y re-subir a YouTube.

---

## 💳 PASARELA DE PAGO (Flow) — EN CONSTRUCCIÓN

Diseño completo en **`docs/PASARELA_PAGO_FLOW.md`** (8 fases, decisiones de negocio cerradas 15-jul).

**✅ Fase 1 — Modelo de suscripción (hecho, verificado):**
- Tablas nuevas `subscriptions` (1:1 con org) y `payment_events` (auditoría de webhooks). Migración `1ac66b2f6de5` con backfill: toda org existente → plan `free`. Org nueva nace `free` en `create_organization`.
- Catálogo de planes en código: `app/billing/plans.py` (límites, precios CLP, trial 14d).

**✅ Fase 2 — Enforcement de límites (hecho, verificado):**
- `app/billing/enforcement.py`: cuenta trabajadores activos (distinct, asignados a proyectos `status='active'`) y proyectos activos. Al exceder → **HTTP 402 `PLAN_LIMIT`** con cuerpo estructurado (limit/current/plan/resource) para el paywall.
- Enganchado en `create_project` (tope de proyectos activos) y `assign_workers` (tope de trabajadores activos, todo-o-nada). Fuera de `trialing`/`active` la suscripción degrada a límites free (historial NUNCA se borra).
- `GET /organizations/{id}/billing/subscription` (solo lectura): plan + uso. Router `app/api/v1/billing.py`.
- Tests: `tests/integration/test_billing_enforcement.py` (8 casos). **Suite completa: 95/95 verde.**

**✅ Frontend del candado freemium (hecho 15-jul, verificado en navegador):**
- Página **Suscripción** (`/app/suscripcion`, `pages/Billing.tsx`): plan actual + estado + barras de uso (X/límite, ámbar ≥80%) + tarjetas de planes.
- **Paywall modal global** (`components/billing/PaywallProvider.tsx`): cualquier `402 PLAN_LIMIT` abre el modal ("no pierdas el historial…") vía handler global en `apiFetch` (`ApiError` + `setPlanLimitHandler`). Los form-modals se cierran para no apilar.
- **Chip de plan/uso** en el pie del sidebar (`AppShell`) enlazando a Suscripción; hook `useSubscription`.
- CTAs de precios de la Landing → `/app/suscripcion` para usuarios logueados.
- Botón "Mejorar" muestra toast honesto ("el pago se habilita muy pronto") hasta conectar Flow.
- Verificado E2E en navegador: crear 2º proyecto activo en free → paywall; "Ver planes" → Suscripción; uso 1/1. Build + lint limpios.

**✅ Cliente Flow + Webhook (hecho 15-jul, tests offline):**
- `app/billing/flow_client.py`: firma HMAC-SHA256 **calcada del cliente oficial de Flow** (params ordenados, `key+value`, apiKey firmado, `s` aparte). Wrappers: customer/plan/subscription/payment. Config `FLOW_*` en `config.py` + `.env.example`. 9 tests unitarios (vector conocido + requests con transporte mock httpx).
- `app/billing/service.py`: normaliza el pago de Flow y lo aplica a la suscripción, **idempotente por `flow_token`** (pagado→active+período; rechazado/anulado→past_due). `payment_events.org_id` ahora nullable (migración `22502bd4cbd9`).
- `app/api/v1/webhooks.py` → `POST /api/v1/webhooks/flow` (público). Flow **no firma** el webhook: solo manda `token` y se re-consulta `payment/getStatus` para confirmar. 503 si no se puede verificar (Flow reintenta). 8 tests de integración.
- `scripts/flow_bootstrap_plans.py`: crea los 4 planes en Flow e imprime los `planId` (`--dry-run` verificado; falta EJECUTARLO con creds).
- **Suite completa: 114/114 verde.**

**⏭️ Próximo (necesita credenciales sandbox de Flow):** ejecutar el bootstrap de planes, endpoints checkout/return/cancel (Fase 5), conectar el botón "Mejorar" del frontend, y QA E2E en sandbox con tarjetas de prueba. Solo la EJECUCIÓN contra Flow queda pendiente; el código y su lógica ya están construidos y probados.

**Correr los tests de billing localmente:**
```bash
docker compose up -d   # Postgres (override local: puerto 5434)
# crear DB de test una vez: CREATE DATABASE faenascore_test;
cd backend && TEST_DATABASE_URL="postgresql+asyncpg://faenascore:faenascore_dev@localhost:5434/faenascore_test" python -m pytest tests/integration/test_billing_enforcement.py -v
```

---

## 🔖 RETOMAR AQUI (próxima sesión)

**Estado al cierre del 23 jun 2026:**
- **Producto: Fase 5 = 5/5 EN PROD** (sin cambios desde el 17 jun). Bundle prod `index-DZRQQpla.js`. Trampa `/sw.js` resuelta (verificada el 22 jun).
- **Tutoriales en video** — guía completa en `tutorial/README.md`. **Serie REORDENADA a 8 clips + 1 opcional; 5 de 8 listos:**
  - ✅ **Clip 1 APROBADO** (`clip1.mp4`): "Bienvenida y tu cuenta".
  - ✅ **Clip 2** (`clip2.mp4`): "Trae tu gente" (dashboard mock, vacío→1→8).
  - ✅ **Clip 3** (`clip3.mp4`): "Crea tu faena" (crea proyecto + asigna 5).
  - ✅ **Clip 4** (`clip4.mp4`, ~65 s): **"La fórmula del puntaje"** 🆕 — recorre `/app/formula`, pesos por industria (Seguridad 30% > Puntualidad 10%), cambia perfil a Logística y vuelve. Mock `clipkit.scoring_formula` + PATCH org.
  - ✅ **Clip 5** (`clip5.mp4`, ~85 s): "Evalúa en terreno" (MÓVIL 390px) — era el Clip 4; reensamblado con título "Tutorial 5 de 8".
  - ✅ **Clip 6** (`clip6.mp4`, ~62 s): **"¿Sin señal? Igual evalúas"** (MÓVIL) — modo offline: se cae la red (`set_offline`), banner ámbar, evalúa y encola (IndexedDB), vuelve la señal y sincroniza sola. **Truco dev:** precargar el chunk lazy de la ruta destino antes de cortar la red (en prod lo precachea el SW); delay opcional `post_eval_delay` en el mock para ver "Sincronizando…".
  - ✅ **Clip 7** (`clip7.mp4`, ~58 s): **"Decide con datos"** (escritorio) — dashboard poblado (KPIs, Top Trabajadores, Recientes) + ficha de trabajador (promedio por dimensión, tendencia, historial, CSV) + cierre sobre el ranking ponderado. Mock sembrado: `stats`/`top_workers`/`recent`/`worker_details` + `eval_summary()`/`worker_detail()`.
  - ✅ **Clip 8** (`clip8.mp4`, ~76 s): **"Transparencia y confianza"** (escritorio) — genera el enlace del portal → portal público `/p/{token}` (puntajes + fórmula, nunca el evaluador) → réplica + botón de baja + certificado imprimible. Mock: `portal_profile()`/`portal_eval()` + ramas `portal-link`/`GET /portal/{token}`/`reply`/`opt-out`.
  - ✅ **Clip 9 (opcional)** (`clip9.mp4`, ~57 s): **"Evaluaciones más justas"** (escritorio) — calibración de evaluadores en `/app/calibracion`: tabla con promedio, delta vs media de la org y señales (Indulgente/Severo/Halo/Pocos datos). Mock: `calibration` en el estado.
  - 🎉 **LOS 9 CLIPS PRODUCIDOS.** Aprobados por Germán: **Clips 1, 8 y 9**; resto (2–7) a su revisión. Entregados en Downloads como "Recontrata - Tutorial N - Título.mp4".
  - 🔧 Kit común **`tutorial/scripts/clipkit.py`** (mock stateful workers/proyectos/evaluaciones **+ fórmula + dashboard/historial + portal + calibración**, TTS, captura, tarjetas, ensamblado, `deliver()`).

**Reorden (23 jun, pedido de Germán):** se separó "La fórmula del puntaje" como **Clip 4** (antes era parte de "Decide con datos") y va ANTES de evaluar; "Evalúa en terreno" pasó de 4 a **5**; todo lo posterior corrió +1 (6 ¿Sin señal?, 7 Decide con datos, 8 Transparencia, 9 opc. Calibración). Guiones renumerados.

**Ubicación de los tutoriales en la app — ✅ EN PRODUCCIÓN (25 jun, bundle `index-EYfsGaTZ.js`):**
- Los **9 IDs de YouTube** pegados y **deployados** (`railway up --service faenascore`). Verificado E2E en recontrata.cl: la sección "Míralo en acción" y el Centro de Ayuda abren el embed real de YouTube y reproducen.
- Catálogo central `frontend/src/lib/tutorials.ts` (9 clips por etapa). **IDs de YouTube pegados: 8 de 9** (Clips 1-8). **Falta el Clip 9** (Germán topó el límite de subida de YouTube el 24 jun; lo sube el 25 jun). Mientras un `youtubeId` esté vacío, ese reproductor muestra "disponible muy pronto" (no rompe nada).
- `frontend/src/components/ui/TutorialModal.tsx`: reproductor (embed YouTube 16:9) + `<WatchButton clip="clipN" />`.
- **Centro de Ayuda** `/app/ayuda` (`pages/Ayuda.tsx`) + ítem "Ayuda" en sidebar y en la barra superior (AppShell).
- **CTAs contextuales** en estados vacíos/páginas: Trabajadores→clip2, Proyectos→clip3, Dashboard→clip7, Evaluar→clip5, Fórmula→clip4, Calibración→clip9, ficha/Portal→clip8.
- **Landing pública**: sección "Míralo en acción" con clip1 + clip5.
- **IDs de YouTube (sin listar) en `tutorials.ts`, los 9:** Clip1 `RjVftlQZZiI` · Clip2 `z63Y6LO5Etc` · Clip3 `W4cubV-fANM` · Clip4 `nZYOXJFPpC0` · Clip5 `FNMvaMhJrw4` · Clip6 `cR_LtE0r7IY` · Clip7 `q46tg0Lge5A` · Clip8 `YypZtLhPT8U` · Clip9 `lxZiDtaR3KA`.
- Railway re-linkeado tras restauración: `railway link -p faenascore -e production -s faenascore` (project ID `7ec526bb-74bc-4796-bac4-4c89bde2d6bd`).

**Próximos pasos (RETOMAR):**
1. **Pendiente humano del producto — único bloqueante para abrir al público:** probar login real en recontrata.cl/sign-up; luego quitar el gate `recontrata2211` + el `noindex` (ver [[recontrata-prelaunch-gate]]). Recién ahí los tutoriales y el sitio quedan visibles para todos (hoy siguen tras el gate).
2. (opcional) Revisión final de Germán de los clips 2-7.
2. **Pendiente humano (para abrir al público)**: probar login real en recontrata.cl/sign-up; quitar gate `recontrata2211` + `noindex`. Recién ahí publicar los tutoriales.
2. (menor, a criterio de Germán) ritmo de la importación en Clip 2 esc4.
3. **Pendiente humano (para abrir al público)**: probar login real con correo en recontrata.cl/sign-up; luego quitar gate `recontrata2211` + `noindex`.

**⚠️ Lección de captura (no repetir):** correr `produce_clipN.py capture` en **primer plano, `PYTHONUNBUFFERED=1`, timeout estricto y atendido**. Si se corre en background y el equipo se suspende, la sesión de Playwright se rompe y el proceso queda colgado indefinidamente (le pasó al Clip 3: 10 h colgado tras suspensión nocturna).

**Notas para producir tutoriales (resumen; detalle en `tutorial/README.md`):**
- Clave OpenAI en `tutorial/scripts/openai_key.txt` (gitignored; **recrear tras cambiar de PC**, reusa la de Fillanyform). Deps Python: `openai playwright pillow openpyxl` + Chromium.
- Clips de dashboard: levantar `cd frontend && npm run dev` (modo mock, `localhost:5173`) antes de `capture`.
- Producir/regenerar: `cd tutorial/scripts && python produce_clipN.py all` (o `assemble` para iterar solo el montaje).
- Deploy de frontend del producto: `railway up --detach --service faenascore`.

---

## Sesion 23 jun 2026 (tarde) — Reorden de la serie + nuevo Clip 4 "La fórmula del puntaje" ✅

Germán pidió que la fórmula del puntaje (los pesos por dimensión) sea su propio clip, ANTES de evaluar.
- **Nuevo Clip 4 "La fórmula del puntaje"** (`clip4.mp4`, ~65 s): recorre `/app/formula` — perfil Construcción/Minería (Seguridad 30% > Puntualidad 10%), fórmula `Σ(dimensión × peso)`, cambia a Logística (puntualidad sube, toast) y vuelve. Mock nuevo en `clipkit`: `scoring_formula()` (5 perfiles que calcan `backend/.../score_calculator.py`) + `GET /scoring/formula` + `PATCH /organizations/{id}` (updateOrg).
- **"Evalúa en terreno" pasó a Clip 5**: `produce_clip4.py` (Evalúa) → `produce_clip5.py`, intermedios `clip4_*`→`clip5_*` renombrados (sin re-capturar), reensamblado con "Tutorial 5 de 8".
- **Renumber +1**: 6 ¿Sin señal?, 7 Decide con datos (pierde la fórmula), 8 Transparencia, 9 opc. Calibración. Guiones `clipN.md` renumerados + nuevo `clip4.md`.
- **Re-rotulados** clips 1-3 a "Tutorial N de 8" y teaser del Clip 3 → "Siguiente: La fórmula del puntaje" (solo `cards`+`assemble`, barato porque los intermedios siguen en disco).

---

## Sesion 23 jun 2026 — Tutoriales: Clips 3 y 4 producidos + kit común ✅

- **`clipkit.py`** (kit común): RUT chileno, roster demo, INIT_JS (cursor+gate), `draft_js` (pre-carga borrador de evaluación), **mock STATEFUL genérico** de `/api/v1` (workers, proyectos, project-workers, evaluaciones; deriva `dashboard/projects-pending` del estado y marca `evaluated` al hacer POST), TTS, captura por escena, tarjetas, ensamblado con subtítulos verbatim. `produce_clip3.py` y `produce_clip4.py` quedan delgados encima.
- **Clip 3 "Crea tu faena"** (`clip3.mp4`, ~49 s, escritorio): Proyectos vacío → crear "Parada de Planta de Ácido N°2" (Codelco/Calama) → Activo → asignar 5 trabajadores → "5 trabajadores sin evaluar".
- **Clip 4 "Evalúa en terreno"** (`clip4.mp4`, ~85 s, móvil 390px): bottom-nav Evaluar → trabajador (Sergio Díaz) → 5 estrellas con anclas → "Con Reservas" + motivo → Guardar → "Evaluar siguiente" encadena a Marcela Rojas → contador a "3 pendientes".
- **Trampas de interacción resueltas** (detalle en `tutorial/README.md` §6): en modales usar `.fill()` (inputs) / `.click(force=True)` (botones) / click en `<label>` (checkboxes); en páginas usar `.click()` normal (no force, que exige viewport); móvil → apuntar al bottom-nav (`nav[aria-label='Navegación principal']`), no al sidebar oculto; sembrar `workers` en el mock aunque la escena no los liste (si no, `getWorker` → cabecera "undefined undefined").
- **Incidente**: el Clip 3 se corrió en background y quedó 10 h colgado tras suspenderse el equipo (rompe la sesión de Playwright). Recuperado: TaskStop + re-captura en primer plano. Regla nueva arriba en RETOMAR.

---

## Sesion 22 jun 2026 — Tutoriales: Clip 1 pulido+aprobado, Clip 2 producido ✅

Sesión enfocada 100 % en los tutoriales (el producto no se tocó). Guía completa nueva en **`tutorial/README.md`**.

### Verificación de trampas pendientes
- **Cloudflare `/sw.js`**: verificada en vivo como **RESUELTA** (`curl` → `Content-Type: text/javascript`, `Cache-Control: no-store`, `Cf-Cache-Status: BYPASS`, cuerpo = Workbox SW real). El purge manual ya no hace falta.
- **Clave OpenAI**: `tutorial/scripts/openai_key.txt` se había perdido en la restauración de PC (está gitignored). **Recreada** reutilizando la clave de Fillanyform/CasiListo y validada viva contra `GET /v1/models` (gpt-4o-mini-tts disponible).

### Clip 1 — pulido y APROBADO por Germán
Tres rondas de feedback, todas aplicadas y verificadas frame a frame:
1. **Subtítulos** más chicos y bajados (`FontSize 20→16`, `MarginV 70→24`).
2. **Intro** = ahora el **logo animado con sonido** (`recontrata_intro_sound.mp4`) sobre fondo `#F7F8FB`, **sin fade a negro** (el logo queda estático). Se eliminó el "blanco" con que arrancaban las capturas (se mide `lead` por escena y se recorta con `-ss`).
3. **B-roll**: el bloque del problema dejó de ser captura de pantalla; ahora es un dron de **mina a tajo abierto** (Pexels 8382429, descarga directa sin API key). Se descartó una planta de áridos por no parecer minería chilena.
4. **Subtítulos VERBATIM**: eran parafraseados; ahora son texto exacto de la narración, con `_check_subs()` que aborta el render si dejan de coincidir.

### Clip 2 "Trae tu gente" — PRODUCIDO (`tutorial/output/clip2.mp4`, ~57 s)
Primer clip del **dashboard autenticado**. Como prod usa Clerk real, se grabó el **frontend en modo mock** (`npm run dev`, `VITE_AUTH_MOCK_ENABLED=true`, `localhost:5173`) interceptando `/api/v1` con Playwright (`ctx.route`). El handler es **STATEFUL**: la lista de trabajadores crece (vacía → Sergio Díaz con toast → 8 tras importar el Excel). Org demo "Constructora Andes". Productor: **`produce_clip2.py`**. Gotcha resuelto: la tabla de escritorio + la card móvil oculta confunden a `wait_for_selector(text=…)` → se espera el cierre del modal. RUTs válidos calculados en el script; Excel demo generado con openpyxl. *Pendiente menor:* en esc4 la importación termina antes que la narración (afinar ritmo).

---

## Sesion 17 jun 2026 (parte 7) — CLIP 1 DEL TUTORIAL PRODUCIDO (video real) ✅

Producido el **piloto en video** del Clip 1 ("Bienvenida y tu cuenta") reutilizando el pipeline de CasiListo, adaptado a Recontrata. **`tutorial/output/clip1.mp4`** (62.5s, 1920x1080, h264+aac, 8.1 MB).

### Pipeline (en `tutorial/scripts/`)
- **`brand.py`**: identidad azul, rutas, ffmpeg, voz TTS. **Clave OpenAI**: SOLO de `OPENAI_API_KEY` (entorno) o de `tutorial/scripts/openai_key.txt` (gitignored). Leer `**/.env` es **bloqueo duro** del harness (no se puede ni con permiso del chat) → por eso el archivo aparte.
- **`produce_clip1.py`**: etapas `tts` (OpenAI gpt-4o-mini-tts, voz alloy, acento latino) · `capture` (Playwright: 1 webm/escena, cursor azul inyectado, gate `recontrata2211` por add_init_script) · `cards` (PIL: intro/outro de marca) · `assemble` (ffmpeg: escenas recortadas al largo del audio + subtítulos quemados + concat).

### Como se verifico (REAL)
- ffprobe: 62.5s, video 1920x1080 h264 + audio aac (ambos streams OK).
- Frames extraídos: esc2 = landing real con subtítulo; esc4 = formulario Clerk real con **cursor azul visible** sobre el campo correo + subtítulo; outro = logo + "Pruébalo en recontrata.cl" + "Siguiente: Trae tu gente". Intro de marca OK.

### Notas de pulido (para revisión de German, menores)
- El CTA "Empezar gratis" lleva a **/sign-in** ("Entrar"), no a registro; la narración dice "regístrate". Honesto (es el flujo real) pero se puede afinar haciendo clic en "Regístrese".
- Subtítulos algo grandes; en esc4 la caja roza el pie "Secured by Clerk". Ajustable (FontSize/MarginV en `_build_srt`/style).
- Captura hecha con duraciones estimadas y recortada al audio real en el ensamblado (sincronía OK).

### Próximo
- Revisión de German del `clip1.mp4` (aprobar estilo, como el piloto de CasiListo). Tras aprobación, producir clips 2–7 (los 4–5 necesitan **organización demo sembrada** con datos).

---

## Sesion 17 jun 2026 (parte 6) — DOCUMENTACION CONSOLIDADA + SERIE DE TUTORIALES EN VIDEO (guiones) ✅

A pedido de German: documentar todo lo construido + crear, como pedagogo, una serie de tutoriales en video calcando el patron del tutorial de CasiListo (`Proyectos Claude Code/Fillanyform/tutorial/`).

### Que se hizo (solo docs, sin tocar codigo)
- **`docs/SISTEMA.md`**: documentacion consolidada del producto tal como esta (que es, stack, todas las funcionalidades, mapa de rutas del frontend, estado y pendientes).
- **`tutorial/README.md`**: plan pedagogico + pipeline de produccion, espejo del de CasiListo (captura Playwright + voz IA gpt-4o-mini-tts + ffmpeg; principios: 1 clip=1 objetivo, mostrar-no-contar, del problema al alivio, voz latina sin tecnicismos, honestidad, continuidad con teaser "Siguiente:"). Tabla de la serie + como producir los MP4 reutilizando los scripts de CasiListo (adaptar marca azul + sembrar org demo + gate recontrata2211).
- **`tutorial/guiones/clip1..7.md` + `clip8_opcional.md`**: guiones completos (estructura Escena → EN PANTALLA / CALLOUT / NARRACION), fieles al UI real (nav, 5 dimensiones con anclas BARS, Si/Con Reservas/No, importar Excel, offline, fórmula, portal, calibración). Arco: preparar (1-3) → terreno (4-5) → decidir (6) → confianza (7) → avanzado (8).

### Estado
- ✅ Guiones de los 8 clips listos. ⬜ Produccion de los MP4 pendiente (reutiliza pipeline CasiListo; requiere marca + org demo sembrada).

---

## Sesion 17 jun 2026 (parte 5) — COMUNICAR OFFLINE EN LANDING + PASADA MÓVIL 375px — COMPLETO Y VERIFICADO ✅ (commit+push; deploy junto al próximo cambio)

Aprovechar comercialmente el offline (que construimos en #3 pero la landing no comunicaba) + asegurar que los banners nuevos no rompan en móvil. Solo frontend.

### Que se hizo
- **Landing (`Landing.tsx`)**: la feature card "Hecho para el celular del supervisor" (icono Zap) se reescribio para **liderar con el offline**: icono **WifiOff**, titular **"¿Sin señal en la faena? Igual evalúas"**, cuerpo "En la mina muchas veces no hay internet… sigue funcionando sin conexión y envía las evaluaciones solo cuando vuelve la señal — no se pierde nada. …con una mano y guantes puestos." (variante de copy "dolor", elegida por German). Subtitulo del hero ahora dice "…en terreno y hasta sin señal…".
- **AppShell**: los 2 banners offline (ambar "sin conexión" + indigo "N por sincronizar / Sincronizar ahora") ahora usan `flex-wrap` + `text-center` + `gap-y` para que no desborden en pantallas chicas.

### Como se verifico (REAL, 375px en navegador)
- `tsc -b` + build OK.
- **Landing a 375px (Playwright + screenshot)**: la card de offline renderiza limpia (icono, titular, cuerpo bien ajustado); el subtitulo del hero incluye "sin señal". (Gate de pre-lanzamiento desbloqueado por localStorage para la prueba.)
- **Banners a 375px (medicion DOM, peor caso de texto)**: inyectado el markup real con clases Tailwind, **overflow horizontal = 0** en ambos (ambar 74px alto, indigo 59px) → envuelven bien, no se desbordan.
- Nota: el StarRating de evaluar ya tenia targets **68px** para guantes (de Fase 3), confirmado en codigo.

### DEPLOY — HECHO (17 jun) ✅
- Deployado (`railway up --detach --service faenascore`). Bundle prod nuevo **`index-DZRQQpla.js`**. Verificado: copy de offline en el bundle ("Sin señal en la faena", "hasta sin señal", "sigue funcionando sin conexión"); API health 200, recontrata.cl 200, /sw.js sigue `text/javascript` (sin regresion). (Usuarios con SW viejo lo ven al aceptar "Actualizar"; nuevos visitantes, directo.)

---

## Sesion 17 jun 2026 (parte 4) — DEPLOY 2+3 + APUESTA #3 COMPLETA → **FASE 5 = 5/5, EN PROD** ✅✅

Deployados los puntos 2+3 juntos (`railway up --detach --service faenascore`). Bundle prod nuevo **`index-D9bRanN3.js`**. Con esto la apuesta #3 (offline-first) queda **3/3** y **Fase 5 completa (5/5), toda en produccion**.

### Verificado en prod (en vivo, 17 jun)
- API health 200, recontrata.cl 200. `/sw.js` GET -> `text/javascript` 200 (Workbox real). (HEAD da 405/json: la ruta solo maneja GET; los navegadores hacen GET, no afecta.)
- **Codigo offline desplegado**: "Sincronizar ahora"/"por sincronizar" en el bundle principal; "guardada en el dispositivo" en el chunk `EvaluateWorker-*.js`.
- **Navegador prod (Playwright)**: SW activo y controlando; **IndexedDB `recontrata-offline` se crea OK en prod**. El **flujo de actualizacion PWA funciona**: tras el deploy habia un SW nuevo `waiting` (registerType:'prompt'), se forzo SKIP_WAITING + reload y el bundle paso del viejo `Dp1Bd8f1` al nuevo `D9bRanN3` → los puntos 2+3 ya se sirven a usuarios al aceptar "Actualizar".
- La logica de cola (punto 2) y flush (punto 3) se verifico E2E localmente contra los modulos REALES en Chromium (ver partes 2 y 3); es el mismo codigo que viaja en el bundle.

### Pendientes (no son de #3)
1. Pendiente humano (unico para abrir al publico): prueba de login real con correo en recontrata.cl/sign-up.
2. Mejora futura: cachear org/listas para cold-start sin señal; Background Sync API nativa como complemento al evento `online`.

---

## Sesion 17 jun 2026 (parte 3) — FASE 5 apuesta #3, PUNTO 3: SYNC DE LA COLA OFFLINE — COMPLETO Y VERIFICADO ✅ → con esto **APUESTA #3 COMPLETA (3/3)**; deploy 2+3 juntos a continuacion

Tercer y ultimo punto de offline-first: enviar a la API las evaluaciones que quedaron en la cola (punto 2) y vaciarla. Solo frontend, sin migracion.

### Que se hizo
- **`src/lib/offlineSync.ts`** `flushQueue(): FlushResult`: recorre la cola (orden por createdAt) y por cada item `api.createEvaluation(orgId, payload)`; **OK -> removeQueuedEvaluation + sent++**; **error de RED (`e instanceof TypeError` o `!navigator.onLine`) -> break** (se deja en cola para reintentar); **error 4xx del servidor -> se saca de la cola y se reporta en `failed[]`** (item que no va a pasar nunca, p. ej. "ya evaluado"; evita que envenene la cola). Guard `flushing` contra ejecuciones concurrentes. Si offline al entrar, no intenta.
- **`src/lib/swr.ts`**: nueva `invalidate(match)` que borra claves del cache (para refrescar `projects-pending:*` tras sincronizar).
- **`src/hooks/useOfflineSync.ts`**: orquesta `sync({manual?})`. Triggers: **evento `online`** + **al montar** (si online y hay pendientes) + **boton manual**. Toasts: "N evaluaciones sincronizadas" (+ "quedan M" si la red se corta a mitad), "N no se pudieron enviar" (con motivo). Tras enviar invalida `projects-pending:*`. Expone `syncing` para feedback. Guard `running` ref.
- **`AppShell.tsx`**: la barra indigo "N por sincronizar" ahora trae boton **"Sincronizar ahora"** (deshabilitado + icono pulsando mientras `syncing`).

### Como se verifico (REAL, logica de flush en navegador)
- `tsc -b` + lint nuevos limpios; `npm run build` OK.
- **Test del flush real en Chromium** (pagina temporal `offline-sync-test.html/.ts`, borrada despues; monkeypatch del singleton `api.createEvaluation` para controlar respuestas; `navigator.onLine` override via defineProperty; Playwright lee `window.__results`):
  - **Exito**: 2 encoladas -> sent=2, remaining=0, llamadas en orden [w-1,w-2], cola vacia. ✓
  - **Error de RED (TypeError)**: sent=0, remaining=2 (se quedan), failed=0 (no se descartan). ✓
  - **Error 4xx servidor**: sent=0, remaining=0 (descartada), failed=1 con el motivo preservado. ✓
  - **Offline**: ni intenta (apiCalled=false), remaining=1. ✓

### Estado: APUESTA #3 (offline-first) COMPLETA — 3/3 puntos. Con esto **Fase 5 queda 5/5**.
### ARRANCAR AQUI — proximo
1. **DEPLOY 2+3 juntos** (`railway up --detach --service faenascore`, solo frontend, sin migracion). Verificar post-deploy: bundle nuevo + DevTools Application (IndexedDB `recontrata-offline`). El SW (#1) ya esta en prod; el no-store de /sw.js evita la trampa Cloudflare.
2. Pendiente humano (unico para abrir al publico): prueba de login real con correo en recontrata.cl/sign-up.
3. Mejora futura (fuera de #3): cachear org/listas para cold-start sin señal; Background Sync API nativa como complemento al evento `online`.

---

## Sesion 17 jun 2026 (parte 2) — FASE 5 apuesta #3, PUNTO 2: COLA OFFLINE DE EVALUACIONES (IndexedDB) — COMPLETO Y VERIFICADO ✅ (commit+push, deploy junto al punto 3)

Segundo de los 3 puntos de offline-first. Cuando no hay señal (o la red falla), la evaluacion se guarda en **IndexedDB** en vez de perderse; el envio automatico es el **punto 3**. Solo frontend, sin migracion, sin backend.

### Que se hizo
- **`src/lib/offlineQueue.ts`**: wrapper de IndexedDB VANILLA (sin dependencias nuevas). DB `recontrata-offline` v1, store `pending-evaluations` (keyPath `id`). API: `enqueueEvaluation(orgId, payload, label)` (genera uuid via crypto.randomUUID), `getQueuedEvaluations()` (ordenadas por createdAt), `removeQueuedEvaluation(id)`, `countQueuedEvaluations()`. Dispara `window` event `recontrata:queue-changed` en cada cambio. Record = {id, orgId, payload, label, createdAt, attempts}.
- **`src/lib/api.ts`**: se extrajo el tipo `CreateEvaluationData` (export) para compartirlo entre `createEvaluation` y la cola (sin duplicar el shape).
- **`src/hooks/usePendingSync.ts`**: cuenta de la cola, reactiva al evento + online/offline.
- **`EvaluateWorker.tsx` handleSubmit**: arma el `payload`, y (a) si `!navigator.onLine` -> `queueOffline()` directo; (b) si esta online pero la llamada lanza error de RED (`e instanceof TypeError`, no un 4xx de validacion) -> tambien encola. `queueOffline` guarda en IndexedDB, limpia el borrador de localStorage, toast "Evaluacion guardada en el dispositivo… se enviara cuando recuperes señal", y navega al proyecto. Los errores de validacion del servidor siguen mostrandose como antes.
- **`AppShell.tsx`**: banner offline ahora dice cuantas hay guardadas; ademas, **online con pendientes** muestra una barra indigo "N evaluaciones por sincronizar" (icono UploadCloud).

### Como se verifico (REAL, modulo en navegador)
- `tsc -b` limpio; `npm run build` OK (55 entradas precache).
- **Test del modulo real en Chromium** (pagina temporal `offline-queue-test.html/.ts` servida por `vite dev`, borrada despues, manejada por Playwright): enqueue x2 -> count=2; orden por createdAt OK; **payload + orgId + label preservados** tras round-trip por IndexedDB; remove del 1.º -> count=1 y queda el worker correcto (w-2); **3 eventos `queue-changed`** (2 add + 1 remove); finalCount=0 tras limpieza. Todas las aserciones verdes.
- Los 2 warnings eslint `react-hooks/set-state-in-effect` en EvaluateWorker son **preexistentes** (efecto de autosave de borrador, lineas 60-76; mis hunks tocan 7/116/181). CI corre `npm run build`, no eslint.

### Limite conocido / decision de deploy
- **NO desplegar el punto 2 solo**: el toast promete "se enviara automaticamente", pero el envio es el punto 3. Si se sube sin sync, las evaluaciones quedan en la cola sin salir. **Plan: implementar el punto 3 (sync) y desplegar 2+3 juntos.** (Acordado con German.)
- Cold-start sin señal: si el `orgId` nunca cargo (useOrg depende de la API), no se puede encolar; en el flujo real el supervisor abre la app con señal en el campamento y el orgId ya esta en memoria. Cachear org/listas offline es mejora futura (no parte de #3).

### ARRANCAR AQUI — proximo: PUNTO 3 (sync)
1. `flushQueue()` en offlineQueue: por cada `QueuedEvaluation` -> `api.createEvaluation(orgId, payload)`; si OK -> `removeQueuedEvaluation`; si falla red -> dejar y reintentar luego; si 4xx (ej. eval duplicada/validacion) -> decidir (descartar con aviso o marcar). Incrementar `attempts`.
2. Disparadores: evento `online` (window) + al montar AppShell si hay pendientes + boton manual "Sincronizar ahora" en la barra indigo. (Background Sync API opcional, fallback al evento online.)
3. Feedback: toasts "Sincronizando N…" / "N evaluaciones enviadas". Refrescar SWR de proyectos/dashboard tras sync.
4. Verificar E2E con backend real + mock auth (encolar offline -> volver online -> confirmar POST y vaciado de cola).
5. **Deploy 2+3 juntos** (`railway up`, requiere autorizacion de German). Sin migracion.

---

## Sesion 17 jun 2026 (parte 1) — FASE 5 apuesta #3, PUNTO 1: SERVICE WORKER / APP SHELL OFFLINE (PWA) — COMPLETO Y VERIFICADO ✅ (EN PROD)

Primer punto de la unica apuesta pendiente de Fase 5 (offline-first en terreno). La apuesta se desglosa en **1) service worker / app shell offline (ESTE)**, 2) cola IndexedDB de evaluaciones, 3) sync al recuperar señal. Solo **frontend**, sin migracion, sin tocar backend.

### Que se hizo
- **`vite-plugin-pwa` 1.3.0** (Workbox 7.4.1, devDep). `vite.config.ts`: `registerType: 'prompt'` (actualizacion controlada por el usuario, no auto-recarga en medio de una evaluacion), `injectRegister: false`, `manifest: false` (se reusa el `public/manifest.webmanifest` ya enlazado en index.html, sin duplicar). Workbox: precache del **app shell** (js/css/html/svg/ico/woff2 + iconos + logo-recontrata.png + manifest), `globIgnores` de media pesada (logo-intro.mp4, hero-faena.jpg, og-image.png, dashboard-preview.png, phone-eval.png), `navigateFallback: '/index.html'` con `navigateFallbackDenylist: [/^\/api\//]` (las llamadas a la API NO caen al shell), `cleanupOutdatedCaches` + `clientsClaim`. `devOptions.enabled:false` (SW off en dev, no rompe HMR).
- **`src/lib/pwa.ts`** `setupPWA()`: registra el SW via `virtual:pwa-register`. Toasts sonner: "Hay una version nueva… Actualizar" (onNeedRefresh, duracion infinita, accion que llama updateSW(true)) y "Listo para usar sin conexion" (onOfflineReady). No-op en dev.
- **`src/hooks/useOnlineStatus.ts`**: hook sobre eventos online/offline del navegador (base del modo terreno; lo consumira la cola en el punto 2).
- **`AppShell.tsx`**: banner ambar "Sin conexion — modo terreno. Tu trabajo se sincronizara al recuperar señal." cuando `!online` (icono WifiOff), sobre el `<main>`.
- **`src/vite-env.d.ts`**: refs de tipos `vite/client` + `vite-plugin-pwa/client`. **`main.tsx`**: llama `setupPWA()` tras montar.

### Como se verifico (REAL, no asumido)
- `npx tsc -b` limpio. `npm run build` OK -> genera `dist/sw.js` + `dist/workbox-*.js`, **55 entradas precache (733 KiB)**. Confirmado por grep que la media pesada NO esta en el precache y que `navigateFallback`/index.html SI estan.
- **Prueba offline genuina (Playwright)**: `vite preview` :4317 -> SW queda **active**, scope raiz `/`, controller = `/sw.js`, 54→55 entradas, `index.html` cacheado (match ignoreSearch). Luego **se MATO el servidor de preview** (curl -> HTTP 000) y se navego a **`/app/workers`**: **la app cargo igual** (React monto el AccessGate "Estamos afinando los ultimos detalles…", root con contenido, controller activo). Unicos 2 errores de consola = `logo-intro.mp4` + `logo-recontrata.png` ERR_CONNECTION_REFUSED (media excluida a proposito); tras agregar el logo al precache quedan en 1 (solo el mp4 decorativo). **=> el app shell se sirve offline, confirmado en vivo.**

### Notas / limites
- El banner offline depende de `navigator.onLine` (en la prueba seguia true porque matar el server no apaga la interfaz de red; en terreno sin señal `navigator.onLine` pasa a false). Logica simple y correcta; verificada por codigo.
- El lint `react-refresh/only-export-components` en main.tsx es **preexistente** (componente Root ya estaba), no introducido aqui.

### DEPLOY — HECHO (17 jun), con 1 pendiente manual de Cloudflare
- **Deployado a prod** (`railway up --detach`, service faenascore). Commits `9be282f` (SW) + `1c59ffd` (fix headers). Bundle prod nuevo `index-Dp1Bd8f1.js`, `workbox-9c191d2f.js` servido 200 JS.
- **TRAMPA CLOUDFLARE (resuelta a futuro, pendiente puntual)**: al consultar `https://recontrata.cl/sw.js` ANTES del deploy, Cloudflare cacheo la respuesta del `spa_fallback` (HTML) bajo `/sw.js` (la extension .js hace que CF la trate como asset estatico). Quedo `cf-cache-status: HIT`, `Cache-Control: max-age=14400` (4h) sirviendo HTML => el navegador no puede registrar el SW (intenta registrar un HTML).
  - **Fix de fondo deployado** (`1c59ffd`, backend `main.py`): `/sw.js` y el shell `index.html` ahora se sirven con `Cache-Control: no-cache, no-store, must-revalidate`. Verificado: por cache-buster `https://recontrata.cl/sw.js?cb=x` -> **200 `text/javascript`, `cf-cache-status: BYPASS`**, body = SW Workbox real (NavigationRoute + createHandlerBoundToURL + precache). CF ya NO cachea /sw.js a futuro.
  - **PENDIENTE (requiere panel Cloudflare de German, no hay token en el repo)**: **purgar la URL `https://recontrata.cl/sw.js`** (Caching -> Configuration -> Purge Cached Content -> Custom Purge -> pegar la URL). Sin purge, el `/sw.js` canonico sigue sirviendo el HTML viejo hasta que expire (~3.3h desde el deploy) y el SW no se registra para usuarios reales. Tras purgar (o expirar), el no-store evita que vuelva a pasar.
  - Verificar tras purge: `curl -I https://recontrata.cl/sw.js` -> `content-type: text/javascript` + `cf-cache-status: BYPASS/MISS` (no HIT con HTML).
2. **Punto 2 de apuesta #3: cola IndexedDB** de evaluaciones creadas offline (POST a EvaluateWorker entra a cola si `!online`). Reusa `useOnlineStatus`.
3. **Punto 3: sync** — vaciar la cola al volver online (background sync / al detectar evento `online`), con feedback de toasts.

---

## Sesion 17 jun 2026 (parte 0) — VERIFICACION DE PROD: las notas "DEPLOY PENDIENTE" de las partes 2/3/4 (14 jun) YA ESTAN DESPLEGADAS ✅

Las entradas de abajo (Portal del Trabajador, certificado descargable, modulo de calibracion) decian "DEPLOY PENDIENTE". Se verifico en vivo que **SI estan en produccion** — esas notas quedaron desactualizadas. Estado real de prod confirmado hoy:
- **API** `https://faenascore-production.up.railway.app/api/health` -> 200.
- **Frontend** `https://recontrata.cl` -> 200 (bundle `index-0WkJy1YH.js`).
- **Portal del Trabajador (backend)**: `/api/v1/portal/{token}` vivo (token invalido -> 404). En `openapi.json`: `portal-link`, `/portal/{token}`, `/reply`, `/opt-out`.
- **Calibracion (backend)**: `/organizations/{org_id}/calibration` en `openapi.json`.
- **Frontend Fase 5**: el bundle de prod contiene `calibracion`, `certificado`, ruta `/p/` y `WorkerPortal`.
- **CI gate** aislamiento multi-tenant: verde en GitHub.

=> Fase 5: 4/5 apuestas EN PROD. Falta solo **#3 offline-first**, que se arranca en esta sesion.

---

## Ultima actualizacion previa: 2026-06-14T15:35:00-04:00

## Sesion 14 jun 2026 (parte 5) — FASE 5 apuesta #5: AISLAMIENTO MULTI-TENANT COMO CI GATE + AUDITORIA PII — COMPLETO Y VERIFICADO ✅ (CI verde en GitHub)

Apuesta #5 de Fase 5 (seguridad): tests que garantizan aislamiento entre organizaciones + auditoria de PII, corriendo como **CI gate** en GitHub Actions. **master `7efe538`**. **NO requiere deploy a prod** (son tests/CI, no tocan el runtime).

### Que se hizo
- **Harness de integracion con DB real** (lo que faltaba: todos los tests previos eran puros): `tests/integration/conftest.py` — engine a `TEST_DATABASE_URL` con `create_all`/`drop_all` por test, `AsyncClient` (ASGITransport) sobre la app real, **override de `get_db`** (sesion de test) **y de `get_current_user`** (actuar como cualquier usuario via `hx.act_as(user)`). Si `TEST_DATABASE_URL` no esta, los tests de integracion se **SALTAN** (los unitarios siguen sin DB). `pytest.ini` con `asyncio_mode=auto`. `pytest`/`pytest-asyncio` agregados a requirements.
- **`tests/integration/test_tenant_isolation.py`** (16 tests): usuario de org A NO puede LEER (GET org, dashboard/stats, top-workers, workers, evaluations, scoring/formula, calibration) ni ESCRIBIR (crear worker, PATCH industria, generar portal-link) en org B -> **403**; IDOR (worker de B bajo el path de A) -> **404**; control positivo (el dueño SI accede, 200). **PII del Portal**: la respuesta publica NO incluye `evaluator_name`/`evaluator_id`, el token solo devuelve su propio worker, token falso -> 404.
- **`.github/workflows/ci.yml`**: gate en push/PR a master. Job **backend** con servicio `postgres:16` + `TEST_DATABASE_URL` corre `pytest -q` (unit + aislamiento). Job **frontend** `npm ci` + `npm run build`. Si alguien rompe el scoping por org_id, el CI falla y bloquea el merge.

### Como se verifico (real)
- Local contra PG (DB de test `faenascore_test`): **77 passed CON DB** (61 unit + 16 integracion); **61 passed + 16 skipped SIN DB** (degrada limpio).
- **CI en GitHub VERDE** (run 27508913799, 1m2s): Backend (tests + aislamiento) 37s ✓ + Frontend (build) 59s ✓. (Solo aviso de deprecacion Node20 en runners; las acciones ya son ultima version, GitHub maneja el runtime.)

### Estado Fase 5: 4 de 5 apuestas hechas. Falta solo #3 offline-first.
### ARRANCAR AQUI — proximo
1. **#3 offline-first en terreno** (unica apuesta pendiente): service worker + cola IndexedDB + sync. Es la mas pesada; merece sesion propia y es la mas dificil de verificar aqui.
2. Pendiente humano: prueba de login real con correo en recontrata.cl/sign-up.
3. Opcional CI: bump de actions a Node24 cuando GitHub lo exija (16 jun 2026).

---

## Ultima actualizacion previa: 2026-06-14T15:05:00-04:00

## Sesion 14 jun 2026 (parte 4) — FASE 5 apuesta #4: MODULO ANTI-SESGO / CALIBRACION DE EVALUADORES — COMPLETO Y VERIFICADO ✅ (commit+push, deploy PENDIENTE)

Apuesta #4 de Fase 5: detecta sesgos sistematicos de quien evalua, para que el puntaje sea mas justo/defendible. **Analitica pura, SIN migracion**. **master `b867f9d`**. **61/61 tests backend OK**, build OK, E2E verificado.
- Refuerza la narrativa de "score defendible": no cambia los puntajes, es herramienta de consistencia para hablar con supervisores.

### Que se hizo
- **`services/evaluator_calibration.py`** (puro, testeable sin DB): por evaluador computa promedio, `leniency_delta` vs media de la org (indulgencia/severidad), `dimension_spread` = dispersion interna promedio entre las 5 dims (efecto halo). Flags: `lenient` (Δ ≥ +0.5), `severe` (Δ ≤ -0.5), `halo` (spread < 0.5), `low_sample` (< 5 evals, no se marca sesgo). 8 tests deterministas.
- **`GET /organizations/{org}/calibration`** (solo admin via get_org_admin): agrupa evals por evaluator_id (outerjoin a users), llama al servicio, devuelve org_mean + umbrales + lista. `schemas/calibration.py`. Router en main.py.
- **Frontend** `/app/calibracion` (+ nav secundario en sidebar, junto a Formula): tabla de evaluadores (promedio, Δ vs org coloreado, dispersion, badges de señales con tooltip), tarjetas org_mean + #evaluadores, leyenda explicativa, estado vacio, guard de solo-admin, enlace a la formula. `api.getCalibration`.

### Como se verifico (E2E real)
- 8 unit tests del servicio (lenient/severe/halo/low_sample/orden por |Δ|).
- **Endpoint con datos reales** (PG local, sembre 2 evaluadores via SQL DO block en org "Calibracion Demo"): Dev User 6 evals mean 4.6 Δ+1.3 -> lenient+halo; Ana Severa 6 evals mean 2.0 Δ-1.3 -> severe. **Agrupacion SQL por evaluator_id correcta** (lo que los unit tests NO cubren).
- **Playwright**: la pagina renderiza 3 evaluadores con sus señales (badges Indulgente/Halo/Severo/Pocos datos), org_mean 3.30, leyenda. 0 errores consola. (Se uso interceptacion de fetch para forzar la org con datos, ya que el OrgProvider toma organizations[0].)

### ARRANCAR AQUI — proximo
1. **DEPLOY PENDIENTE** (backend + frontend, SIN migracion, bajo riesgo): `railway up --detach`. Verificar `/openapi.json` contiene `/calibration` + bundle nuevo. Requiere autorizacion de German.
2. Resto Fase 5: **offline-first (#3)** — la mas pesada (service worker + cola IndexedDB + sync); merece sesion propia. **Tests aislamiento multi-tenant CI (#5)** — contenida.
3. Pendiente humano: prueba de login real con correo en recontrata.cl/sign-up.

---

## Ultima actualizacion previa: 2026-06-14T14:40:00-04:00

## Sesion 14 jun 2026 (parte 3) — Certificado descargable del portal — COMPLETO Y VERIFICADO ✅ (commit+push, deploy PENDIENTE)

Follow-up de la apuesta #2: el "CV de faena" descargable. **master `1defbf9`**. **Solo frontend (sin migracion)**, build OK, E2E Playwright OK.
- Ruta publica **`/p/:token/certificado`** (fuera del AccessGate), `WorkerCertificate.tsx`: documento imprimible via `window.print()` (Guardar como PDF del navegador) con encabezado + fecha de emision, identidad, score ponderado, resumen de recontratacion, **tabla** de evaluaciones (5 dims + ponderado + recontratacion), formula ordenada por peso y nota legal. **CSS `@media print` oculta la barra de acciones** (.no-print) → al imprimir solo sale el documento limpio. Sin nombre del evaluador.
- Boton "Descargar mi certificado" en `WorkerPortal`. 100% client-side, reutiliza `getPortal` (sin libreria PDF, sin backend nuevo).
- Verificado: Playwright renderiza el certificado (identidad, tabla, formula, pie legal) + se confirmo por CSSOM que la regla `@media print { .no-print { display:none } }` esta activa sobre la barra de acciones. 0 errores consola.
- **DEPLOY PENDIENTE** (solo frontend, bajo riesgo, sin migracion): `railway up --detach`, verificar bundle nuevo. Requiere autorizacion de German.

---

## Ultima actualizacion previa: 2026-06-14T14:10:00-04:00

## Sesion 14 jun 2026 (parte 2) — FASE 5 apuesta #2: PORTAL DEL TRABAJADOR — COMPLETA Y VERIFICADA ✅ (commit+push, deploy PENDIENTE)

Implementada la apuesta #2 de Fase 5: el **Portal del Trabajador** (transparencia + derecho a replica + opt-out), intra-organizacion, acceso por **token sin login**. Convierte la herramienta del contratista en un activo del trabajador y neutraliza el mayor riesgo legal.
- **master `df6a9d4`** (pusheado). **53/53 tests backend OK**, build OK, migracion verificada contra PG real, **E2E real (HTTP + Playwright)**.

### Decisiones (recomendadas por Claude, aprobadas por German)
- **Acceso por link con token unico** (sin login; el contratista lo comparte; revocable/regenerable).
- **Privacidad**: el trabajador ve sus puntajes (5 dims + ponderado), recontratacion, motivo/comentario y la formula; **NUNCA el nombre del evaluador**.
- **Replica permanente y visible para ambas partes**.
- **Cross-org sigue fuera** (Fase 1 lo difirio; requiere consentimiento separado). Certificado descargable **diferido** a follow-up.

### Que se hizo
- **DB**: `workers.portal_token` (unico, lazy, String(64)) + `evaluations.worker_reply` + `worker_reply_at`. Migracion **`b8d4f0a2c6e1`** (down_revision a7c3e9f1b2d4). Verificada upgrade/downgrade/re-upgrade contra PG real.
- **Backend router PUBLICO** `app/api/v1/portal.py` montado en `/api/v1/portal/{token}` (NO usa Clerk ni get_org_member): `GET /{token}` (perfil + evals con 5 dims + ponderado + motivo/comentario + formula activa + consent + rehire stats, **sin evaluator_name**), `POST /{token}/evaluations/{id}/reply` (derecho a replica), `POST /{token}/opt-out` (worker_consent -> revoked, method=platform). Contratista: `POST /organizations/{org}/workers/{id}/portal-link?regenerate=` (genera/rota token, reusa get_org_member). `schemas/portal.py`. WorkerDetail expone `portal_token` + `worker_reply`/`worker_reply_at` por eval.
- **Frontend**: ruta publica **`/p/:token` FUERA del AccessGate** — App.tsx reestructurado con layout-route `GateLayout` (AccessGate+BootIntro via Outlet) que envuelve TODO menos el portal. `WorkerPortal.tsx` (branded, score ponderado, resumen recontratacion, formula con barras, responder por eval, solicitar baja, aviso si revocado). WorkerDetail: card "Portal del trabajador" (generar/copiar/regenerar enlace, copia al clipboard) + replicas visibles en el historial. api.ts: tipos PortalProfile/PortalEvaluation/PortalLink + getPortal/portalReply/portalOptOut/createPortalLink + portal_token en WorkerDetail + worker_reply en EvaluationSummary.

### Como se verifico (E2E real)
- Migracion round-trip OK; columnas + `uq_workers_portal_token` creados.
- HTTP (PG real, :8011): generar portal-link OK; **GET portal publico SIN auth** -> worker + org + avg ponderado 3.3 (q4 s2 p5 t4 tec3, perfil construccion) + motivo visible + **evaluator_name ausente**; reply -> worker_reply guardado; opt-out -> 204 + consent_status=revoked; token invalido -> 404; contratista worker-detail ve portal_token + consent revoked + worker_reply (replica visible ambos lados).
- **Playwright** (`/p/<token>` con gate desactivado): la pagina publica renderiza FUERA del gate — identidad, score 3.3, formula con pesos, evaluacion con motivo + "Tu respuesta", aviso de opt-out, sin nombre de evaluador. 0 errores de consola.

### ARRANCAR AQUI — proximo
1. **DEPLOY A PROD pendiente** (apuestas #1 score ponderado YA esta en prod; #2 portal NO): `railway service faenascore` -> `railway up --detach`. Migracion `b8d4f0a2c6e1` corre sola en el CMD (additiva). Verificar pollendo `/api/v1/portal/xxx` (404 token invalido = ruta viva) + bundle nuevo. **REQUIERE AUTORIZACION de German (deploy a prod / migracion en Supabase).**
2. Follow-up corto: **certificado descargable** del portal (pagina imprimible / "CV de faena").
3. Resto Fase 5: offline-first (#3), modulo anti-sesgo (#4), tests aislamiento multi-tenant CI (#5).
4. Pendiente humano: prueba de login real con correo en recontrata.cl/sign-up.

---

## Sesion 14 jun 2026 — FASE 5 apuesta #1: MOTOR DE SCORE PONDERADO DEFENSIBLE — COMPLETA, VERIFICADA Y EN PROD ✅

> Actualizacion: el motor de score ponderado **SE DEPLOYO A PROD** (railway up, migracion a7c3e9f1b2d4 corrio en Supabase prod; ruta /scoring/formula 404->401; health OK). Detalle abajo.

## Ultima actualizacion previa: 2026-06-14T12:35:00-04:00

## Sesion 14 jun 2026 — FASE 5 apuesta #1: MOTOR DE SCORE PONDERADO DEFENSIBLE — COMPLETA Y VERIFICADA ✅ (commit+push, deploy PENDIENTE)

Implementada la apuesta #1 de Fase 5 del `PLAN_ACCION_CLASE_MUNDIAL.md`: el score deja de ser un promedio plano (lo que la auditoria llamo "indefendible") y pasa a ser un **promedio ponderado por industria** con **formula publica**. Alcance acordado con German: ponderado + formula publica, industria a nivel de organizacion.
- **master `4c8138e`** (pusheado a origin). **53/53 tests backend OK**, build frontend OK, migracion verificada contra PG real (docker), y **E2E real con Playwright** (dev mock + backend local + PG real).
- **OJO Recontrata != Faymex** (proyecto personal de German Saltron Mellado).

### Que se hizo
- **`services/score_calculator.py`**: registro `WEIGHT_PROFILES` por industria. Default `construccion_mineria`: **Seguridad 30% > Calidad 25% > Tecnica 20% > Equipo 15% > Puntualidad 10%** (Seguridad pesa mas que Puntualidad = el corazon de la defensa legal). Tambien `energia`, `logistica` (Puntualidad sube a 25%), `manufactura` (Calidad 30%), `general` (promedio simple). `compute_weighted()` + validacion al import de que cada perfil suma 1.0. `compute_average()` se conserva como referencia.
- **DB**: `organizations.industry` (default construccion_mineria) + `evaluations.score_weighted` (+ indice `ix_evaluations_score_weighted`). Migracion **`a7c3e9f1b2d4`** (down_revision f1a2b3c4d5e6): add columns + backfill score_weighted con el perfil default (correcto porque toda org existente nace construccion_mineria) + NOT NULL. **Verificada upgrade/downgrade/re-upgrade contra Postgres local real.**
- **Backend**: el puntaje "oficial" (ranking + headline) pasa a **ponderado** en dashboard (stats avg, top-workers order+value, recent), workers (list, export csv, detail headline via linealidad sobre los promedios por dimension), projects (list_project_workers). `score_average` se sigue calculando y exponiendo como referencia. `evaluations.py` create/update calculan score_weighted con el perfil de la org (helper `_get_org_industry`). admin seed + 3 scripts de seed sincronizados. **Endpoint `GET /organizations/{org}/scoring/formula`** (perfil activo + catalogo, transparencia art. 16 Ley 21.719) y **`PATCH /organizations/{org}`** para fijar industria (solo admin, valida contra WEIGHT_PROFILES -> 422 si invalida).
- **Frontend**: nueva pagina **`/app/formula`** (`ScoreFormula.tsx`): barras de peso por dimension ordenadas desc, formula `puntaje = Σ(dimension × peso)`, selector de industria (5 perfiles) que hace PATCH + recarga, nota legal Ley 21.719. Link "Fórmula del puntaje" en el sidebar (NO en la bottom-nav movil, que se queda en 4 para no romper grid-cols-4). `api.ts`: tipos score_weighted, industry en Organization, ScoringFormula, getScoringFormula/getOrg/updateOrg. Dashboard KPI "Score Ponderado" + badges de evals recientes ponderados. WorkerDetail: headline ponderado, card "Promedio por dimension" con nota + link "Cómo se pondera", badge ponderado por eval, columna "Ponderado" en CSV.

### Como se verifico (E2E real, NO imaginado)
- Docker estaba caido al inicio; **se levanto Docker Desktop** (engine up ~18s) -> PG en :5433.
- Backend en :8011 con PG real + mock auth. Smoke HTTP: org nace `industry=construccion_mineria`; eval (q4 s5 p2 t3 tec4) -> **score_average=3.6, score_weighted=3.95** (exacto al test unitario). Formula endpoint OK (5 perfiles). Worker-detail headline=3.95 weighted vs avg_scores.overall=3.6 simple. Dashboard avg=3.95. PATCH industry->logistica OK; industria invalida->422. Nueva eval (q5 s1 p5 t1 tec1) tras el cambio -> **weighted=2.8 (logistica)** vs 2.4 que daria construccion = el perfil por-org se aplica dinamicamente.
- **Playwright** (dev :5173 mock + backend :8011): `/app/formula` renderiza perfil activo + pesos ordenados + selector + nota legal; click "Energia/Electrico" -> perfil activo cambia a Energia (Tecnica sube a 25%). WorkerDetail muestra headline ponderado + link "Cómo se pondera" + nota. 0 errores de consola.

### Decisiones tomadas
- **Industria a nivel de organizacion** (no proyecto): cubre el caso real hoy, un solo campo/selector. El score ponderado se guarda por-eval con el perfil vigente al evaluar; cambiar la industria afecta evals NUEVAS (las viejas conservan su peso historico = defendible).
- **Headline = ponderado, se conserva el promedio simple** como referencia visible (transparencia).

### ARRANCAR AQUI — proximo
1. **DEPLOY A PROD pendiente**: `railway service faenascore` -> `railway up --detach`. La migracion `a7c3e9f1b2d4` corre sola en el CMD del Dockerfile contra Supabase prod (additiva + backfill, no destructiva). Verificar pollendo ruta nueva `/scoring/formula` (404 viejo -> 401/403 nuevo) y bundle nuevo. **NO se alcanzo a deployar esta sesion.**
2. Resto de Fase 5 (roadmap): Portal del Trabajador (#2), offline-first (#3), modulo anti-sesgo (#4), tests aislamiento multi-tenant CI (#5).
3. Pendiente humano arrastrado: **prueba de login real con correo** en recontrata.cl/sign-up.
4. Menor: cablear edicion/borrado de evals en UI (endpoints existen; manejar 409 EVALUATION_EDIT_WINDOW_EXPIRED).

---

## Ultima actualizacion previa: 2026-06-07T12:50:00-04:00

## Sesion 7 jun 2026 (parte 2) — FASE 3 del plan (UX de terreno U1-U9) — COMPLETA Y VERIFICADA ✅

Implementados los 9 items U1-U9 del `PLAN_ACCION_CLASE_MUNDIAL.md` (UX de terreno). Build frontend OK + **40/40 tests backend** + **verificacion visual E2E real** (Playwright, modo mock + fetch interceptado con datos). Commits en master, pusheados.
- **OJO Recontrata != Faymex** (proyecto personal de German Saltron Mellado).

### Items (todos verificados con screenshot o DOM)
- **U1 — bottom-nav movil**: `AppShell.tsx`, nav fija inferior (Dashboard/Proyectos/Trabajadores/Evaluar) en `md:hidden`, `pb-20` en main para no tapar contenido. Verificado.
- **U2 — toasts (Sonner)**: instalado `sonner`, `<Toaster>` montado en `main.tsx` (top-center, richColors), wrapper `lib/toast.ts` (success/error/info/fromError + action). Reemplazado el unico `alert()` (export Workers). Toasts en export, alta de trabajador, consentimiento, guardado de eval. Verificado (DOM).
- **U3 — targets tactiles**: `StarRating.tsx` interactivo a min 68px (lg) para guantes. Verificado (screenshot).
- **U4 — dead-end de org**: `org.tsx` ahora expone `error` + `retry`; `AppShell` muestra tarjeta de error con boton **Reintentar** en vez de pantalla en blanco cuando `getProfile` falla. Verificado (screenshot, con backend caido).
- **U5 — cards moviles de trabajadores**: `Workers.tsx`, cards en `md:hidden` + tabla en `hidden md:block`. Verificado (screenshot).
- **U6 — post-eval "evaluar siguiente"**: `EvaluateWorker.handleSubmit` busca el siguiente pendiente del proyecto (getProjectsPending) y muestra toast de exito con accion **"Evaluar siguiente"** si lo hay. Verificado (DOM: toast + boton de accion presentes).
- **U7 — 5 dimensiones en historial + CSV**: backend `EvaluationSummary` ahora incluye las 5 dims + `rehire_reason` (schema + endpoint worker-detail). Frontend: grilla CAL/SEG/PUN/EQ/TEC por eval + estado de recontratacion + motivo + boton export CSV (client-side). Verificado (screenshot). **Prerequisito natural de la Fase 5 (score ponderado).**
- **U8 — anclas de comportamiento (BARS)**: `constants.ts` nuevo `SCORE_DIMENSIONS` con hint + ancla por nivel 1-5 por dimension. El form muestra el hint bajo cada dimension y el descriptor del nivel seleccionado ("3/5 · Maneja su especialidad con autonomia"). Mas objetivo/defendible. Verificado (screenshot).
- **U9 — skeletons/a11y**: skeleton de carga en `WorkerDetail`; aria-labels en botones de menu de `AppShell`. (Modal y StarRating ya tenian a11y basica.)

### Fix colateral (necesario para poder verificar en local)
- **`AppShell` crasheaba en modo mock**: renderizaba `<UserButton>` de Clerk sin `ClerkProvider`. Guard `clerkEnabled` → en mock muestra "Modo demo". Bug PREEXISTENTE (no de Fase 3). Commit aparte.

### Como se verifico (Docker inutilizable en este entorno)
Docker estaba colgado (no levantaba PG). Se verifico con **dev server en modo mock** (`VITE_AUTH_MOCK_ENABLED=true npm run dev`, puerto 5180) + **interceptacion de `window.fetch` en el navegador** con datos mock (workers, worker-detail con 5 dims, proyecto, pending) y disparando "Reintentar". Asi se renderizaron los componentes reales con datos controlados, sin backend. **Truco reusable** para futuras verificaciones de pantallas autenticadas sin DB (prod usa Clerk real, no se puede E2E con login).

### Pendiente de Fase 3 que NO se cableo (menor)
- Edicion/borrado de evals en la UI (endpoints PATCH/DELETE existen desde Fase 1; al cablear, manejar 409 `EVALUATION_EDIT_WINDOW_EXPIRED` con toast + mostrar historial de versiones).

### ARRANCAR AQUI — proximo
Fases 0+1+2+3 listas (0/1/2 en prod; 3 commiteada, deploy en curso). Opciones: **Fase 4 (pan-LATAM)** o **Fase 5 / "Fase 5-lite" (score ponderado: Seguridad pesa mas que Puntualidad)** — U7 ya dejo las 5 dims visibles, prerequisito cumplido. Pendiente humano: **prueba de login real con correo** en recontrata.cl/sign-up.

---

## Sesion 7 jun 2026 — FASE 2 del plan (conversion de landing M1-M6) — COMPLETA Y DEPLOYADA A PROD ✅

Implementados los 6 items M1-M6 del `PLAN_ACCION_CLASE_MUNDIAL.md` (Fase 2). Solo frontend (`Landing.tsx` + `index.html`). Build OK, verificado local (Playwright desktop+mobile 375px) y **DEPLOYADO + verificado en prod** (recontrata.cl).
- **master `db32480`** (pusheado). Deploy Railway servicio `faenascore` (build `03911dae`).
- **Probe de deploy**: pollear el `<title>` nuevo en el HTML servido por prod (cambio M1 en index.html, va en el dist). Pasó al intento 12 (~4 min). Luego E2E Playwright cruzando el gate confirmó las 5 secciones nuevas vivas (legal/stat/roi/cierre/nav = todos true).

### Cifras usadas (todas reales y citables, de `JUSTIFICACION_FAENASCORE.md`)
- 1.071.128 trabajadores subcontratados en Chile (INE 2024) · 50% rotacion construccion (INE) · ~$750.000 reemplazar un operario (≈50% sueldo anual) · 2.854+ nombres en listas negras ilegales (Federacion Minera / DT). ROI Profesional: evitar 5 malas recontrataciones/año ahorra ~$3,75M vs ~$600K/año del plan = ROI 6x.

### M1 — SEO (`index.html`)
- `<title>` keyword-rich ("Evaluación de desempeño para contratistas | A quién recontratar"), meta description con keyword+propuesta, meta keywords, OG/Twitter description alineadas a la voz del hero.

### M2 — Prueba social / stat-bar (`Landing.tsx`)
- Seccion nueva tras el hero: banda "El problema, en cifras reales" + 4 stats (componente `Stat` con value/label/source) con las cifras de arriba. Sin testimonios falsos (pre-lanzamiento).
- **CORRECCION (7 jun, commit `e266dde`)**: la banda decia "creado por Faymex" — **ERROR**. **Recontrata NO tiene relacion con Faymex; es proyecto PERSONAL de German Saltron Mellado.** Quitada toda atribucion a Faymex de la landing (grep `[Ff]aymex` en frontend = 0). Las cifras del stat-bar siguen siendo validas (vienen de fuentes publicas INE/DT, no de Faymex). NO atribuir Recontrata a Faymex en copy, docs ni memoria.

### M3 — ROI concreto ($750K)
- Hero: linea "Reemplazar a un mal operario cuesta ~$750.000". PricingCard extendido con prop `roi` (caja destacada bajo la descripcion): Profesional muestra "ROI de 6x", Empresa muestra "14 dias de prueba, sin tarjeta".

### M4 — Alternativa legal a las listas negras
- Banda oscura (gray-900) nueva antes de Pricing: titular "La alternativa legal a las listas negras." + parrafo (DT, criterios objetivos, consentimiento, derecho a replica) + 3 chips con ShieldCheck. Diferenciador pan-LATAM, convierte el riesgo legal en feature.

### M5 — Nav + 2do CTA + cierre con urgencia
- Header: `<nav>` con links Funciones/Precios (md:inline) + "Iniciar sesion" (sm:inline, solo si !signedIn) + CTA primario. CTA de cierre reescrito a urgencia ("Tu proxima cuadrilla se arma esta semana") + sub-linea de garantias (listo en minutos / import Excel / 14 dias prueba).

### M6 — Empresa self-serve
- Plan Empresa: CTA pasó de `mailto:` a trial self-serve (primaryCta → /sign-in o /app). El mailto de Enterprise (>500) sigue en el footnote.

### Notas / pendientes que NO toca Fase 2
- El heading de Pricing sigue "Precios en pesos chilenos" y los precios solo CLP → es **Fase 4 (pan-LATAM, P2)**, intencional dejarlo.
- `dashboard-preview.png` es `loading="lazy"`; en screenshots rapidos sale en blanco pero carga bien (verificado, archivo existe).

### ARRANCAR AQUI — proximo: Fase 3 (UX de terreno) o prueba de login real
Fases 0+1+2 EN PROD. Sigue **Fase 3** (UX terreno: bottom-nav, toasts Sonner, targets tactiles 68px, dead-end org, cards moviles, post-eval "siguiente pendiente", 5 dimensiones en historial). Pendiente humano arrastrado: **prueba de login real con correo** en recontrata.cl/sign-up. AccessGate sigue activo (`recontrata2211`); checklist "QUITAR al lanzar" al abrir publico.

---

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
