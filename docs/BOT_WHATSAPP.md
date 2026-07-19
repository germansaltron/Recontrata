# Bot de WhatsApp — captación de prospectos

> Estado: **FUNCIONANDO en producción con el número de PRUEBA de Meta** (19-jul-2026).
> Fases 1-3 completas y verificadas en vivo. Falta el número definitivo (Fase 4).

## Correo de leads — Resend (19-jul-2026) ✅ FUNCIONANDO

Cuenta **propia de Saltronic** (registrada con `gsaltron@recontrata.cl`, NO la personal que usa
SoyMaestra ni la de Faymex). Dominio verificado: **`send.recontrata.cl`** (subdominio a
propósito).

**Por qué subdominio y no `recontrata.cl` a secas:** el dominio raíz ya tiene el SPF de
Cloudflare Email Routing, y un dominio admite **un solo SPF**. Usando un subdominio, Resend
pone su SPF en `send.send.recontrata.cl` y **no hay que tocar** el de la raíz — que es
justamente la operación que rompió el correo de Faymex en julio. Verificado tras configurar:
los MX y el SPF de la raíz quedaron intactos.

El DNS se cargó con **Domain Connect** de Cloudflare: autorización de **un solo uso**, acotada
a recontrata.cl, sin dejar token vivo. Mejor que entregar una API key de Cloudflare.

La API key de Resend está **acotada al dominio** `send.recontrata.cl` y con permiso solo de
envío: si se filtrara, no podría enviar como ningún otro dominio.

Variables: `RESEND_API_KEY` + `BOT_FROM_EMAIL=bot@send.recontrata.cl` (si el remitente no
coincide con el dominio verificado, Resend rechaza el envío).

## Token de WhatsApp — PERMANENTE (19-jul-2026)

El token temporal **venció dos veces en un mismo día** (expira a hora fija, no a las 24 h),
dejando al bot sin poder responder. Solución definitiva: **usuario del sistema** en el
Business Manager de Saltronic (`recontrata-bot`), con la app y la WABA asignadas en **control
total**. Verificado con `debug_token`:

```
tipo: SYSTEM_USER · válido: True · expira: 0 (nunca)
scopes: whatsapp_business_management, whatsapp_business_messaging, public_profile
```

Los dos scopes son necesarios: `management` para leer configuración, `messaging` para enviar.

## ✅ Verificado en vivo (19-jul-2026)

**Circuito completo, extremo a extremo (22:21):**

```
whatsapp_message_received → bot_tool_call(registrar_prospecto) → bot_email_sent → whatsapp_sent
```

11 segundos desde que el prospecto escribe hasta que recibe respuesta y el lead está en la
bandeja. El correo llegó a Gmail sin rebote ni spam, desde `bot@send.recontrata.cl`, con los
datos extraídos por el modelo (dedujo rubro "mineria" de "faenas mineras" y la banda 100-500
a partir de "unos 200 trabajadores").

Conversación real desde WhatsApp contra el número de prueba, ~5 s de latencia por respuesta:

| Prueba | Resultado |
|---|---|
| Saludo | Respondió **textual** el saludo aprobado |
| Segundo "Hola" | **No repitió** el saludo (la regla del prompt funciona) |
| "¿Cuánto cuesta?" | Precios correctos, generados desde `plans.py`, + pregunta de seguimiento |
| "Soy Germán de Constructora Andes, 60 trabajadores" | `registrar_prospecto` → **lead creado**; dedujo rubro=construccion y banda 16-100 |
| "Soy cliente y no puedo entrar" | `derivar_a_soporte` → entregó `atencion@recontrata.cl`, estado→`support` |

Firma HMAC validando, idempotencia operando, historial y persistencia OK.

### Costo real medido (con `count_tokens`, no estimado a ojo)

- Prefijo estable (system + tools): **3.821 tokens** → **supera** el mínimo de caché de
  Sonnet 5 (2.048), así que **el caché sí aplica**.
- Conversación típica de 6 turnos: **~USD 0,0021 (~$2 CLP)** con caché, vs ~$35 CLP sin él.
- 1.000 conversaciones ≈ **USD 2** (~$2.000 CLP).

> Los **conteos de tokens son reales**; la proyección de costo asume ~120 tokens de salida por
> turno y que los turnos caen dentro de la ventana de caché (5 min). Con conversaciones muy
> espaciadas el costo real sube hacia el número sin caché.

## Qué es y qué no es

Recontrata tiene PWA, portal del trabajador y pasarela de pago, pero **ningún canal de
captación**: un prospecto que llega a recontrata.cl solo puede mirar. Este bot cubre esa
carencia. Responde dudas comerciales por WhatsApp, captura los datos del interesado y
avisa por correo.

**No consulta datos del producto.** No busca trabajadores, no muestra puntajes, no toca
`organizations` ni `workers`. Fue una decisión, no una omisión:

- Los puntajes de desempeño son **datos personales bajo la Ley 21.719**. El producto los
  protege con consentimiento, rastro inmutable, derecho a réplica y opt-out. Mandarlos por
  WhatsApp los saca de esa estructura: quedan en el teléfono personal de un supervisor, se
  reenvían, se fotografían. Sería una puerta lateral que rodea el mismo cuidado que el
  producto se tomó el trabajo de construir.
- Los clientes RRHH **ya tienen la PWA**, que además funciona sin señal en faena. El bot no
  les resolvería ninguna carencia.

**El soporte a clientes va por `atencion@recontrata.cl`.** Un cliente que ya paga *va a*
escribirle al bot ("no puedo entrar", "cómo evalúo"). El bot lo reconoce, entrega esa
dirección y cierra. Mismo gesto que el bot de Faymex usa con los CV, por la misma razón:
el canal correcto es el correo, no WhatsApp.

**Consecuencia arquitectónica:** al no leer datos, el bot no necesita autenticación
máquina-a-máquina, ni vínculo teléfono→organización, ni API key por organización. Por eso
vive como un router más dentro del backend, sin superficie de seguridad nueva.

## Dónde vive

```
backend/app/
  api/v1/whatsapp.py    # webhook: GET verify + POST recepción; procesa en tarea de fondo
  models/bot.py         # BotConversation, BotMessage, BotLead, BotInboundEvent
  main.py               # 2 líneas: import + include_router
  bot/
    knowledge.py        # base de conocimiento comercial (precios desde billing/plans.py)
    prompts.py          # SYSTEM_PROMPT (persona + KB), estable y cacheable
    tools.py            # 3 tools: registrar_prospecto, derivar_a_soporte, escalar_a_humano
    conversation.py     # motor: AsyncAnthropic tool-use + máquina de estados
    client.py           # envío a WhatsApp (Graph API)
    notifications.py    # correo de lead y escalamiento (Resend)
```

Dentro del monolito porque el bot comparte dominio con el landing que genera los
prospectos, y hereda Postgres, Alembic, el harness de tests y el deploy sin montar nada
nuevo. Esto además evita de entrada la herida operativa del bot de Faymex, cuya base
SQLite **se borra en cada deploy** por no tener volumen.

Costo aceptado: comparte proceso con la API del producto. Como no comparte datos ni
autenticación, separarlo después es casi trivial.

## Las dos garantías del webhook

Ambas son obligatorias, y ambas **faltan** en los bots de Faymex y SoyMaestra.

### 1. Firma HMAC (`X-Hub-Signature-256`)

Cada entrega de Meta viene firmada. Se valida con `hmac.compare_digest` contra
`META_APP_SECRET`, **sobre el cuerpo crudo** (no sobre el JSON re-serializado: cualquier
cambio de bytes rompe el MAC). Falla cerrado: sin `META_APP_SECRET` no pasa ni una firma
bien construida.

Sin esto, el endpoint es público y cualquiera puede inyectar mensajes falsos y hacer que
el bot responda por WhatsApp a números arbitrarios, a nuestra costa.

### 2. Idempotencia por `wamid`

Meta **reintenta** la entrega si no recibe un 2xx a tiempo, así que el mismo mensaje llega
más de una vez. El árbitro es el índice `UNIQUE` sobre `bot_inbound_events.wamid`: si el
insert choca, ya lo procesamos y se descarta. Mismo patrón que `PaymentEvent.flow_token`
en billing (`app/billing/service.py`).

Sin esto, un reintento hace que el bot conteste dos veces al mismo mensaje.

### Regla: el webhook SIEMPRE responde 200

Si el endpoint devuelve 5xx, Meta lo marca como no saludable y **reduce o desactiva la
entrega**. En el bot de Faymex eso fue causa raíz de una caída real de `subscribed_apps`.
Un error nuestro no puede costarnos el canal: se loguea y se responde 200 igual. Una firma
inválida también responde 200 — no le damos señal a quien sondea — pero no procesa nada.

## Correo del dominio (Cloudflare Email Routing, 19-jul-2026)

`recontrata.cl` usa **Cloudflare Email Routing** (gratis, solo RECIBE y reenvía):

| Dirección | Reenvía a | Para qué |
|---|---|---|
| `atencion@recontrata.cl` | gsaltron@gmail.com | **El correo que el bot le da a los clientes** (antes no existía: rebotaba). |
| `gsaltron@recontrata.cl` | gsaltron@gmail.com | Correo distinto para crear la organización de **Anthropic a nombre de Saltronic** (la org actual factura a Faymex, RUT 76.536.742-5). |

Catch-all queda **deshabilitado** a propósito: una dirección inexistente rebota en vez de
caer en un pozo silencioso.

⚠️ **SPF — trampa para cuando se configure Resend.** Cloudflare agregó este registro:
`"v=spf1 include:_spf.mx.cloudflare.net ~all"`. Autoriza SOLO a Cloudflare a enviar como
recontrata.cl. Cuando el bot mande los correos de leads por **Resend** (desde
`bot@recontrata.cl`), hay que **agregar Resend a ESE MISMO registro** — NO crear un segundo
SPF: un dominio admite uno solo y tener dos los invalida a ambos. (Es lo que rompió el correo
de Faymex en julio.) Cloudflare deja el SPF "Unlocked" justamente para poder editarlo.

## Infraestructura de Meta (19-jul-2026)

Portafolio comercial: **Saltronic SpA** (`528027061198782`).

| | Valor |
|---|---|
| App | **Recontrata Bot** — App ID `1777753076558682` |
| Cuenta WhatsApp (WABA) de prueba | `2799045830476773` |
| Número de prueba | **+1 (555) 181-5450** — Phone Number ID `1145341392005969` |

Secretos (NO van aquí, van en Railway): `WHATSAPP_TOKEN`, `META_APP_SECRET`,
`WHATSAPP_VERIFY_TOKEN`, `ANTHROPIC_API_KEY`.

⚠️ Al autorizar la app, el diálogo de Meta ofrece también la cuenta de WhatsApp de **Luddos**
(otra empresa). **Se seleccionó SOLO la de prueba** — nunca marcar Luddos ni "todos los
actuales y futuros", porque ese "todos" la incluye.

El número de prueba solo puede escribir a números en su **lista de destinatarios permitidos**
(hasta 5). Ahí va el +56 9 2731 5616 para las pruebas.

## Números de WhatsApp

| | Número | Estado |
|---|---|---|
| **Producción (provisorio)** | **+56 9 2731 5616** | Chip WOM nuevo (activado 18-jul-2026), **nunca tuvo WhatsApp**. A nombre **personal de Germán**, NO de Saltronic: WOM exige 4 meses de empresa funcionando para poner la línea a nombre de la sociedad. |
| Desarrollo | Número de prueba de Meta | Sale al instante con la App, sin verificación. Hasta 5 destinatarios en lista blanca. |

**Que la línea esté a nombre personal NO afecta la verificación de Meta**: Meta valida la
*empresa* con documentos (el portafolio Saltronic SpA), no a nombre de quién está el chip.

⚠️ **Dos cuidados con el número provisorio:**
1. Registrarlo en la API es **permanente**: ese número pierde WhatsApp normal para siempre.
2. Se cambiará al definitivo (a nombre de Saltronic) en ~4 meses. Migrar es barato **mientras
   no se difunda**: quien tenga el número viejo guardado quedaría escribiéndole a un número
   muerto, y el historial no se migra. **No publicarlo como número oficial** (landing,
   tarjetas, publicidad) mientras sea provisorio.

## Configuración

| Variable | Default | Nota |
|---|---|---|
| `BOT_ENABLED` | `false` | **Candado dormido.** Audita la entrada pero no contesta. |
| `META_APP_SECRET` | `""` | Firma del webhook. Vacío = rechaza todo. |
| `WHATSAPP_TOKEN` | `""` | Token de envío (Graph API). |
| `WHATSAPP_PHONE_ID` | `""` | Phone number ID de Meta. |
| `WHATSAPP_VERIFY_TOKEN` | `""` | Solo para el `GET` de alta. Vacío = 403. |
| `WHATSAPP_API_URL` | `https://graph.facebook.com/v22.0` | |
| `ANTHROPIC_API_KEY` | `""` | |
| `BOT_MODEL` | `claude-sonnet-5` | Sonnet, no Opus: es un bot comercial. |
| `RESEND_API_KEY` | `""` | Correo de leads. |
| `BOT_FROM_EMAIL` | `bot@recontrata.cl` | |
| `BOT_LEAD_EMAILS` | `["gsaltron@gmail.com"]` | Destinatarios del lead. |
| `BOT_SUPPORT_EMAIL` | `atencion@recontrata.cl` | El bot lo entrega y cierra. |
| `ALERTS_TEST_MODE` | `true` | Redirige **todas** las alertas a `ALERTS_TEST_EMAILS`. |
| `ALERTS_TEST_EMAILS` | `["gsaltron@gmail.com"]` | |
| `MESSAGE_BUFFER_SECONDS` | `3` | |
| `SESSION_TIMEOUT_MINUTES` | `30` | Pasado esto, el siguiente mensaje abre conversación nueva. |
| `MAX_TURNS` | `3` | Turnos de captura antes de derivar con lo que haya. |
| `BLOCKED_NUMBERS` | `[]` | JSON o separado por comas. Compara solo dígitos. |

## Configuración del LLM (por qué así)

- **`claude-sonnet-5`**, no `claude-opus-4-8`. Decisión explícita: un bot que responde
  dudas comerciales no necesita el tier alto.
- **`thinking: {"type": "disabled"}`.** Sonnet 5 corre thinking adaptativo **si se omite el
  campo** (al revés que Sonnet 4.6). Omitirlo agregaría latencia y tokens en cada "hola,
  ¿cuánto cuesta?".
- **`effort: "low"`.** El default es `high`, caro y lento para este caso. Ojo: con thinking
  apagado Sonnet 5 invoca **menos** herramientas, así que las descripciones deben ser
  prescriptivas ("llama a esto cuando…"), no solo descriptivas. Punto de partida a
  calibrar, no número definitivo.
- **Sin `temperature` ni `top_p`:** Sonnet 5 los rechaza con 400. El tono se controla solo
  desde el prompt.
- **Caché de prompt** sobre el bloque `system`. El mínimo cacheable de Sonnet 5 son 2048
  tokens; bajo eso no cachea **y no avisa** — verificar con `usage.cache_read_input_tokens`.

## Modelo de datos

| Tabla | Para qué |
|---|---|
| `bot_inbound_events` | Auditoría + idempotencia. `wamid` **unique**. |
| `bot_conversations` | Estado por teléfono. `phone` **no** es único: la sesión expira y se abren conversaciones nuevas. |
| `bot_messages` | Turnos. `role` usa el vocabulario de Claude (`user`/`assistant`) para armar el historial sin traducir. |
| `bot_leads` | El entregable del bot. |

`collect_turns` está separado de un contador global **a propósito**: en el bot de Faymex,
medir contra el total hizo que dos saludos agotaran el presupuesto y el lead se derivara
sin pedir datos jamás.

Ninguna tabla referencia `organizations` ni `workers`.

## Probar en local

```bash
docker compose up -d
cd backend

# Suite completa (los de integración necesitan la DB)
TEST_DATABASE_URL="postgresql+asyncpg://faenascore:faenascore_dev@localhost:5434/faenascore_test" \
  ./.venv/Scripts/python.exe -m pytest -q

# Servidor
DATABASE_URL="postgresql+asyncpg://faenascore:faenascore_dev@localhost:5434/faenascore" \
META_APP_SECRET="secreto_local_de_prueba" WHATSAPP_VERIFY_TOKEN="verify_local_123" \
BOT_ENABLED="false" AUTH_MOCK_ENABLED="true" \
  ./.venv/Scripts/python.exe -m uvicorn app.main:app --port 8799
```

Golpear el webhook como lo haría Meta:

```bash
SECRET="secreto_local_de_prueba"
BODY='{"entry":[{"changes":[{"value":{"messages":[{"from":"56911112222","id":"wamid.X","type":"text","text":{"body":"hola"}}]}}]}]}'
SIG="sha256=$(printf '%s' "$BODY" | openssl dgst -sha256 -hmac "$SECRET" | awk '{print $2}')"

curl -X POST http://localhost:8799/api/v1/whatsapp/webhook \
  -H "Content-Type: application/json" -H "X-Hub-Signature-256: $SIG" -d "$BODY"
```

**El código HTTP no prueba nada** (todo responde 200 por diseño). La evidencia está en la
base:

```sql
SELECT wamid, phone, signature_valid FROM bot_inbound_events;
```

Firma válida → una fila. Firma falsa → cero filas. Mismo `wamid` dos veces → una fila.

## Estado y qué falta

- **Fase 1 ✅** — webhook seguro, modelos, migración, settings. 26 tests nuevos.
  Verificado con `curl` contra servidor y Postgres reales.
- **Fase 2 ✅** — conversación: `app/bot/` (knowledge, prompts, tools, conversation, client).
  `AsyncAnthropic` con tool-use, Sonnet 5 (thinking off, effort low, sin temperature, system
  cacheado). KB de precios generada desde `app/billing/plans.py`. El webhook procesa en tarea
  de fondo para responder 200 al toque. 148 tests verdes (7 nuevos del motor, con cliente
  Anthropic falso). **Falta verificar en vivo** (modelo, caché, tokens) — necesita la llave y
  el número de prueba (pasos 3/5/6 de Verificación).
- **Fase 3 ✅** — `app/bot/notifications.py`: correo del lead y del escalamiento por Resend.
  `registrar_prospecto` avisa al equipo con los datos + la conversación; `escalar_a_humano`
  avisa y pausa el bot; `derivar_a_soporte` NO manda correo (solo entrega el correo al
  cliente). **Marcha blanca:** con `ALERTS_TEST_MODE` (default on) las alertas se redirigen a
  `ALERTS_TEST_EMAILS`. Sin `RESEND_API_KEY` → loguea, no manda. 152 tests verdes. **Falta el
  envío real** (necesita `RESEND_API_KEY`); la forma HTTP es la de Resend, igual que Faymex.
- **Fase 4 ⏳** — infra Meta. Verificación de negocio de Saltronic SpA EN REVISIÓN. Falta el
  número de **prueba** (para probar el bot en vivo: modelo, caché, correo real) y luego el
  número **definitivo** bajo la cuenta de **Saltronic** + revisión del nombre para mostrar.

## Gotchas de la puesta en marcha (19-jul, todos vividos)

**1. `subscribed_apps` — el que dejó al bot mudo.** Suscribir el campo `messages` en el panel
de la app **NO basta**: la **WABA** tiene que estar suscrita **a la app**. La WABA de prueba
venía suscrita solo a una app interna de Meta (*WA DevX Webhook Events 1P App*), así que los
mensajes nunca llegaban. Diagnóstico y arreglo (token desde el entorno, nunca en el chat):

```bash
# ¿qué apps están suscritas?
curl -s "https://graph.facebook.com/v22.0/<WABA_ID>/subscribed_apps" \
  -H "Authorization: Bearer ${WHATSAPP_TOKEN}"
# suscribir la nuestra
curl -s -X POST "https://graph.facebook.com/v22.0/<WABA_ID>/subscribed_apps" \
  -H "Authorization: Bearer ${WHATSAPP_TOKEN}"
```

**2. El token temporal NO dura 24 h desde que lo generas.** Vence a una **hora fija** (vimos
"expired on 11:00 PDT"), así que puede durar minutos. Síntoma: `whatsapp_send_failed` con
`OAuthException code 190`. Para producción → **token permanente de usuario del sistema**.

**3. `(#131030) Recipient phone number not in allowed list`.** El número de prueba solo puede
**responder** a números en su lista blanca. El mensaje entrante SÍ llega y se procesa; lo que
falla es el envío. Agregar el número en el panel del número de prueba.

**4. El número de producción NUNCA debe tener WhatsApp instalado**, ni siquiera para agregarlo
como destinatario de prueba. Los destinatarios son teléfonos de personas; el número de
producción es la identidad del bot.

## Gotchas

- **`railway variables --set` NO redespliega.** Para que el contenedor tome una variable
  nueva hay que `railway up`.
- **La migración corre sola al desplegar**: el Dockerfile hace `alembic upgrade head` en
  cada arranque.
- **El buffer de mensajes vive en memoria del proceso** (Fase 2). Con una réplica está
  bien; con varias, no. Documentado en vez de fingir que no existe.
- **El catch-all del SPA** (`main.py`) solo excluye rutas que empiezan con `api`, así que
  `/api/v1/whatsapp/*` no colisiona.
