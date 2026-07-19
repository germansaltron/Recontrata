# Bot de WhatsApp — captación de prospectos

> **Estado (19-jul-2026): FUNCIONANDO en producción** con el número de **prueba** de Meta.
> Fases 1-3 completas y verificadas en vivo. Falta el número definitivo (Fase 4), que depende
> de que Meta apruebe la verificación de negocio de Saltronic SpA (enviada el 19-jul).

---

## 1. Qué es y qué no es

Recontrata tiene PWA, portal del trabajador y pasarela de pago, pero **ningún canal de
captación**: un prospecto que llegaba a recontrata.cl solo podía mirar. Este bot cubre eso:
responde dudas comerciales por WhatsApp, captura los datos del interesado y avisa por correo.

**No consulta datos del producto.** No busca trabajadores, no muestra puntajes, no toca
`organizations` ni `workers`. Fue una decisión deliberada:

- Los puntajes son **datos personales bajo la Ley 21.719**, y el producto los protege con
  consentimiento, rastro inmutable, derecho a réplica y opt-out. Mandarlos por WhatsApp los
  saca de esa estructura: quedan en el teléfono de un supervisor, se reenvían, se fotografían.
  Sería una puerta lateral que rodea el cuidado que el producto se tomó el trabajo de construir.
- Los clientes RRHH **ya tienen la PWA**, que además funciona sin señal en faena.

**El soporte a clientes va por `atencion@recontrata.cl`.** Un cliente que ya paga *va a*
escribirle al bot ("no puedo entrar"). El bot lo reconoce, entrega esa dirección y cierra.

**Consecuencia arquitectónica:** al no leer datos, el bot **no necesita** autenticación
máquina-a-máquina, ni vínculo teléfono→organización, ni API key por organización. Por eso vive
como un router más dentro del backend, sin superficie de seguridad nueva.

---

## 2. Cómo funciona

```
prospecto (WhatsApp)
   ↓  Meta entrega el mensaje firmado
POST /api/v1/whatsapp/webhook   ── valida firma HMAC ── deduplica por wamid
   ↓  responde 200 al instante; procesa en tarea de fondo
BotEngine (Claude Sonnet 5 + tool-use)
   ├─ registrar_prospecto  → BotLead + correo al equipo (Resend)
   ├─ derivar_a_soporte    → entrega atencion@recontrata.cl y cierra
   └─ escalar_a_humano     → avisa por correo y PAUSA el bot en esa conversación
   ↓
respuesta enviada por Graph API
```

### Dónde vive el código

```
backend/app/
  api/v1/whatsapp.py    # webhook: GET verify + POST; procesa en tarea de fondo
  models/bot.py         # BotConversation, BotMessage, BotLead, BotInboundEvent
  main.py               # 2 líneas: import + include_router
  bot/
    knowledge.py        # base de conocimiento comercial (precios desde billing/plans.py)
    prompts.py          # SYSTEM_PROMPT (persona + KB), estable y cacheable
    tools.py            # 3 tools con descripciones PRESCRIPTIVAS ("llama a esto cuando…")
    conversation.py     # motor: AsyncAnthropic tool-use + máquina de estados
    client.py           # envío a WhatsApp (Graph API)
    notifications.py    # correo de lead y de escalamiento (Resend)
```

Vive **dentro del monolito** porque comparte dominio con el landing que genera los prospectos,
y hereda Postgres, Alembic, el harness de tests y el deploy sin montar infraestructura nueva.
Eso además evita de entrada la herida operativa del bot de Faymex, cuya base SQLite se borra en
cada deploy por no tener volumen. Costo aceptado: comparte proceso con la API del producto;
como no comparte datos ni autenticación, separarlo después sería casi trivial.

### El tono (aprobado con el dueño)

Formal pero cercano y servicial, tratando de **tú**. Mensajes cortos estilo WhatsApp (2-4
líneas), **sin emojis**, se presenta como asistente y nunca finge ser persona. Saludo aprobado:

> ¡Hola! Soy el asistente de Recontrata. Te ayudo con lo que necesites saber: cómo funciona,
> los planes, o cualquier duda para empezar. ¿Qué te gustaría ver?

---

## 3. Las dos garantías del webhook

Ambas son obligatorias, y ambas **faltan** en los bots de Faymex y SoyMaestra.

**Firma HMAC (`X-Hub-Signature-256`).** Cada entrega de Meta viene firmada. Se valida con
`hmac.compare_digest` contra `META_APP_SECRET`, **sobre el cuerpo crudo** (no sobre el JSON
re-serializado: cualquier cambio de bytes rompe el MAC). Falla cerrado. Sin esto, cualquiera
podría inyectar mensajes falsos y hacer que el bot escriba a números arbitrarios, a nuestra costa.

**Idempotencia por `wamid`.** Meta **reintenta** si no recibe un 2xx a tiempo. El árbitro es el
índice `UNIQUE` sobre `bot_inbound_events.wamid`: si el insert choca, ya lo procesamos. Mismo
patrón que `PaymentEvent.flow_token` en billing.

**Regla: el webhook SIEMPRE responde 200.** Un 5xx hace que Meta marque el endpoint como no
saludable y reduzca la entrega. Una firma inválida también responde 200 —para no darle señal a
quien sondea— pero no procesa nada.

---

## 4. Infraestructura

### Meta

Portafolio comercial **Saltronic SpA** (`528027061198782`), bajo el login gsaltron@gmail.com.

| | Valor |
|---|---|
| App | **Recontrata Bot** — App ID `1777753076558682` |
| WABA de prueba | `2799045830476773` |
| Número de prueba | **+1 (555) 181-5450** — Phone Number ID `1145341392005969` |
| Webhook | `https://recontrata.cl/api/v1/whatsapp/webhook`, campo suscrito: `messages` |
| Token | **usuario del sistema** `recontrata-bot` → `SYSTEM_USER`, `expires_at=0` (nunca vence) |

⚠️ Al autorizar la app, Meta ofrece también la cuenta de WhatsApp de **Luddos** (otra empresa
de Germán). Se seleccionó **solo la de prueba**; nunca marcar Luddos ni "todos los actuales y
futuros", porque ese "todos" la incluye.

### Números de WhatsApp

| | Número | Estado |
|---|---|---|
| Pruebas (destinatario) | **+56 9 3565 2743** | El personal de Germán. Está en la lista blanca del número de prueba. |
| Producción (provisorio) | **+56 9 2731 5616** | Chip WOM nuevo (18-jul), **nunca tuvo WhatsApp** y **no debe tenerlo**. A nombre personal: WOM exige 4 meses de empresa para ponerlo a nombre de la sociedad. |

Que la línea esté a nombre personal **no afecta** la verificación de Meta: Meta valida la
*empresa* con documentos, no a nombre de quién está el chip.

⚠️ **El número de producción NUNCA debe tener WhatsApp instalado**, ni siquiera para agregarlo
como destinatario de prueba. Los destinatarios son teléfonos de personas; el número de
producción es la identidad del bot, y al registrarlo en la API pierde WhatsApp normal para
siempre. Migrar al definitivo es barato **mientras no se difunda**: no publicarlo como número
oficial (landing, tarjetas, publicidad) mientras sea provisorio.

### Correo del dominio (Cloudflare Email Routing) — solo RECIBE

| Dirección | Reenvía a | Para qué |
|---|---|---|
| `atencion@recontrata.cl` | gsaltron@gmail.com | El correo que el bot le da a los clientes. **Antes no existía: rebotaba.** |
| `gsaltron@recontrata.cl` | gsaltron@gmail.com | Correo de Saltronic, usado para crear las cuentas de Anthropic y Resend. |

Catch-all **deshabilitado** a propósito: una dirección inexistente rebota en vez de caer en un
pozo silencioso.

### Correo de leads (Resend) — solo ENVÍA

Cuenta **propia de Saltronic** (registrada con `gsaltron@recontrata.cl`; **no** la personal que
usa SoyMaestra, ni la de Faymex). Dominio verificado: **`send.recontrata.cl`**.

**Por qué un subdominio y no `recontrata.cl` a secas:** la raíz ya tiene el SPF de Email
Routing, y un dominio admite **un solo SPF**. Con el subdominio, Resend pone su SPF en
`send.send.recontrata.cl` y **no hay que tocar** el de la raíz — que es justamente la operación
que rompió el correo de Faymex en julio. Verificado después de configurar: los MX y el SPF de
la raíz quedaron intactos.

El DNS se cargó con **Domain Connect** de Cloudflare: autorización de **un solo uso**, acotada a
recontrata.cl, sin dejar token vivo. La API key de Resend está **acotada a ese dominio** y con
permiso **solo de envío**.

### Anthropic

Organización **propia de Saltronic** con su propio medio de pago. La organización anterior
("Germán's Individual Org") tenía cargado el **RUT de Faymex (76.536.742-5)**, así que sus
boletas iban a Faymex. Dentro de la organización hay **espacios separados** para Recontrata y
Casilisto, cada uno con su llave y su límite de gasto. La llave del bot es `recontrata-bot-prod`.

---

## 5. Configuración

Variables en Railway (servicio `faenascore`). **Los secretos se cargan por el PANEL WEB**, nunca
por comando en un chat, y las consultas de variables se hacen pidiendo **solo nombres**.

| Variable | Valor en prod | Nota |
|---|---|---|
| `BOT_ENABLED` | `true` | Default en código es `false` (candado dormido). |
| `META_APP_SECRET` | *(secreto)* | Firma del webhook. Vacío = rechaza todo. **Es el corto (32 hex), NO el `EAA…`**. |
| `WHATSAPP_TOKEN` | *(secreto)* | Token de usuario del sistema, permanente. Es el largo que empieza con `EAA…`. |
| `WHATSAPP_PHONE_ID` | `1145341392005969` | |
| `WHATSAPP_VERIFY_TOKEN` | *(secreto)* | Solo para el `GET` de alta. Vacío = 403. |
| `WHATSAPP_API_URL` | `https://graph.facebook.com/v22.0` | |
| `ANTHROPIC_API_KEY` | *(secreto)* | Llave `recontrata-bot-prod`, org Saltronic. |
| `BOT_MODEL` | `claude-sonnet-5` | Sonnet, no Opus: es un bot comercial. |
| `RESEND_API_KEY` | *(secreto)* | Acotada a `send.recontrata.cl`, solo envío. |
| `BOT_FROM_EMAIL` | `bot@send.recontrata.cl` | **Debe coincidir con el dominio verificado** o Resend rechaza. |
| `BOT_LEAD_EMAILS` | *(default)* `["gsaltron@gmail.com"]` | Destinatarios del lead. |
| `ALERTS_TEST_MODE` | *(default)* `true` | **Marcha blanca:** redirige TODAS las alertas a `ALERTS_TEST_EMAILS`. Apagar para usar destinatarios reales. |
| `ALERTS_TEST_EMAILS` | *(default)* `["gsaltron@gmail.com"]` | |
| `SESSION_TIMEOUT_MINUTES` | *(default)* `30` | Pasado esto, el siguiente mensaje abre conversación nueva. |
| `BLOCKED_NUMBERS` | *(default)* `[]` | JSON o separado por comas. Compara solo dígitos. |

⚠️ **Declaradas pero NO usadas por el código** (ver §9): `MESSAGE_BUFFER_SECONDS`, `MAX_TURNS`,
`BOT_SUPPORT_EMAIL`.

### Configuración del LLM (por qué así)

- **`claude-sonnet-5`**, no `claude-opus-4-8`: decisión explícita, un bot comercial no necesita
  el tier alto. Si el costo apretara, la palanca es bajar a Haiku (una variable), no cambiar de
  proveedor.
- **`thinking: {"type": "disabled"}`** — Sonnet 5 corre thinking adaptativo **si se omite el
  campo** (al revés que Sonnet 4.6). Omitirlo agregaría latencia y tokens en cada "hola".
- **`effort: "low"`** — el default es `high`. Ojo: con thinking apagado Sonnet 5 invoca **menos**
  herramientas, por eso las descripciones de `tools.py` son prescriptivas.
- **Sin `temperature` ni `top_p`** — Sonnet 5 los rechaza con 400. El tono va solo en el prompt.
- **Caché de prompt** sobre el bloque `system`. El mínimo cacheable de Sonnet 5 son 2.048 tokens
  y el nuestro son 3.821, así que **sí cachea**. Verificar con `usage.cache_read_input_tokens`.

---

## 6. Modelo de datos

| Tabla | Para qué |
|---|---|
| `bot_inbound_events` | Auditoría + idempotencia. `wamid` **unique**. |
| `bot_conversations` | Estado por teléfono. `phone` **no** es único: la sesión expira y se abren conversaciones nuevas. |
| `bot_messages` | Turnos. `role` usa el vocabulario de Claude (`user`/`assistant`). |
| `bot_leads` | El entregable del bot. |

Ninguna tabla referencia `organizations` ni `workers`.

`collect_turns` está separado de un contador global **a propósito**: en el bot de Faymex, medir
contra el total hizo que dos saludos agotaran el presupuesto y el lead se derivara sin pedir
datos jamás.

---

## 7. Verificado en vivo (19-jul-2026)

**Circuito completo, extremo a extremo, en 11 segundos:**

```
whatsapp_message_received → bot_tool_call(registrar_prospecto) → bot_email_sent → whatsapp_sent
```

| Prueba | Resultado |
|---|---|
| Saludo | Respondió **textual** el saludo aprobado |
| Segundo "Hola" | **No repitió** el saludo (la regla del prompt funciona) |
| "¿Cuánto cuesta?" | Precios correctos desde `plans.py` + pregunta de seguimiento |
| "Soy Germán de Constructora Andes, 60 trabajadores" | Lead creado; **dedujo** rubro=construccion y banda 16-100 |
| "Soy cliente y no puedo entrar" | Entregó `atencion@recontrata.cl`, estado→`support` |
| Prospecto con correo y 200 trabajadores | Lead + **correo recibido en Gmail** desde `bot@send.recontrata.cl`, sin rebote ni spam; dedujo rubro=mineria y banda 100-500 |

### Costo real medido (con `count_tokens`, no estimado a ojo)

- Prefijo estable (system + tools): **3.821 tokens** → supera el mínimo de caché.
- Conversación típica de 6 turnos: **~USD 0,0021 (~$2 CLP)** con caché, vs ~$35 CLP sin él.
- 1.000 conversaciones ≈ **USD 2**.

> Los **conteos de tokens son reales**; la proyección de costo asume ~120 tokens de salida por
> turno y que los turnos caen dentro de la ventana de caché (5 min). Con conversaciones muy
> espaciadas, el costo real sube hacia el número sin caché.

---

## 8. Gotchas (todos vividos)

**`subscribed_apps` — el que dejó al bot mudo.** Suscribir el campo `messages` en el panel de la
app **NO basta**: la **WABA** tiene que estar suscrita **a la app**. La nuestra venía atada solo
a una app interna de Meta (*WA DevX Webhook Events 1P App*), así que los mensajes nunca llegaban
y no había ningún error visible.

```bash
# ¿qué apps están suscritas?
curl -s "https://graph.facebook.com/v22.0/<WABA_ID>/subscribed_apps" \
  -H "Authorization: Bearer ${WHATSAPP_TOKEN}"
# suscribir la nuestra
curl -s -X POST "https://graph.facebook.com/v22.0/<WABA_ID>/subscribed_apps" \
  -H "Authorization: Bearer ${WHATSAPP_TOKEN}"
```

**El token temporal NO dura 24 h.** Vence a una **hora fija** (vimos "expired on 11:00 PDT"),
así que puede durar minutos. Nos mordió **dos veces el mismo día**. Síntomas:
`OAuthException code 190` (expirado) o `401 Unauthorized`. Solución: token de usuario del
sistema. Verificarlo con:

```bash
curl -s "https://graph.facebook.com/v22.0/debug_token?input_token=${WHATSAPP_TOKEN}&access_token=${WHATSAPP_TOKEN}"
# esperado: "type":"SYSTEM_USER", "expires_at":0, scopes con management Y messaging
```

**`(#131030) Recipient phone number not in allowed list`.** El número de prueba solo puede
**responder** a números en su lista blanca. El mensaje entrante SÍ llega y se procesa; lo que
falla es el envío.

**Confundir el App Secret con el token.** El App Secret es **corto (32 hex), no vence**, y está
en *Configuración de la app → Básica*. El token es el **larguísimo que empieza con `EAA`**. Si
se invierten, el webhook responde 200 pero **descarta todos los mensajes en silencio** (busca
`whatsapp_bad_signature` en los logs).

**`railway variables --set` NO redespliega.** Hay que `railway up` para que el contenedor tome
una variable nueva.

**La migración corre sola al desplegar:** el Dockerfile hace `alembic upgrade head` en cada
arranque.

**El catch-all del SPA** (`main.py`) solo excluye rutas que empiezan con `api`, así que
`/api/v1/whatsapp/*` no colisiona.

---

## 9. Deudas conocidas

**El buffer de mensajes NO está implementado.** `MESSAGE_BUFFER_SECONDS` está declarada en
`config.py` pero **no se usa**: cada mensaje entrante dispara su propia llamada al LLM de
inmediato. Si un prospecto escribe tres mensajes seguidos ("Hola" / "quiero cotizar" / "para 50
personas"), el bot responde tres veces en vez de una. El bot de Faymex sí lo implementa
(acumula y cancela el timer anterior) y es de donde habría que copiarlo.

**`MAX_TURNS` no se usa.** Está declarada pero el motor no limita los turnos de captura; se
apoya en que Claude decide cuándo llamar a `registrar_prospecto`.

**`BOT_SUPPORT_EMAIL` no se usa.** La dirección `atencion@recontrata.cl` está **escrita a mano**
en `prompts.py` y en `tools.py`. Cambiar la variable de entorno no cambia lo que el bot dice.

**El estado del proceso no sobrevive a múltiples réplicas.** Hoy hay una sola, así que está bien.

**Los adjuntos no se descargan.** Una nota de voz o una foto se degradan a `[audio]` / `[image]`
y el modelo responde pidiendo que le escriban. No hay transcripción.

---

## 10. Probar en local

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

**El código HTTP no prueba nada** (todo responde 200 por diseño). La evidencia está en la base:

```sql
SELECT wamid, phone, signature_valid FROM bot_inbound_events;
```

Firma válida → una fila. Firma falsa → cero filas. Mismo `wamid` dos veces → una fila.

---

## 11. Estado por fase

| Fase | Estado |
|---|---|
| **1 — Webhook seguro** | ✅ firma HMAC, idempotencia, modelos, migración. 26 tests. |
| **2 — Conversación** | ✅ `app/bot/`, Sonnet 5 + tool-use. Verificado en vivo. |
| **3 — Leads por correo** | ✅ Resend, dominio propio, correo recibido en Gmail. |
| **4 — Número definitivo** | ⏳ depende de la verificación de negocio de Saltronic (enviada 19-jul, ~2 días laborables). Falta registrar +56 9 2731 5616 y pasar la revisión del nombre para mostrar. |

**152 tests verdes** (`cd backend && pytest -q` con `TEST_DATABASE_URL`).

---

## 12. Cuando le toque a Casilisto

También es de Saltronic, así que **hereda casi todo**:

- **Mismo portafolio de Meta** → la verificación de negocio ya está hecha, no se repite.
- **Misma organización de Anthropic** → ya tiene su espacio de trabajo creado.
- **Misma cuenta de Resend** → solo agrega su dominio y una llave acotada a él.

Lo propio de cada producto: **un número limpio, una WABA, una App de Meta y un webhook**
apuntando a su backend (Fillanyform). El webhook se configura por app, por eso cada producto
necesita la suya.
