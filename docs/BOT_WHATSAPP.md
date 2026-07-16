# Bot de WhatsApp — captación de prospectos

> Estado: **Fase 1 completa** (webhook seguro). El bot está **dormido** en producción
> (`BOT_ENABLED=false`) y todavía no contesta nada.

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
  api/v1/whatsapp.py    # webhook: GET verify + POST recepción
  models/bot.py         # BotConversation, BotMessage, BotLead, BotInboundEvent
  main.py               # 2 líneas: import + include_router
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

- **Fase 1 ✅** — webhook seguro, modelos, migración, settings. 26 tests nuevos; 141 en
  total verdes. Verificado con `curl` contra servidor y Postgres reales.
- **Fase 2 ⏳** — conversación: prompts, máquina de estados, `AsyncAnthropic` con tool-use,
  base de conocimiento comercial (planes y precios desde `app/billing/plans.py`, que es la
  fuente de verdad; argumentos desde `JUSTIFICACION_FAENASCORE.md`).
- **Fase 3 ⏳** — leads por Resend, `derivar_a_soporte`, `escalar_a_humano`.
- **Fase 4 ⏳** — infra Meta. Desarrollo contra el **número de prueba** de Meta para no
  quedar bloqueados. El número definitivo va bajo la cuenta de **Saltronic**, no la de
  Faymex: Recontrata es de Saltronic y mezclarlo con el WABA de otra empresa es un enredo
  de propiedad. La verificación de negocio de Meta toma días — se inicia temprano.

## Gotchas

- **`railway variables --set` NO redespliega.** Para que el contenedor tome una variable
  nueva hay que `railway up`.
- **La migración corre sola al desplegar**: el Dockerfile hace `alembic upgrade head` en
  cada arranque.
- **El buffer de mensajes vive en memoria del proceso** (Fase 2). Con una réplica está
  bien; con varias, no. Documentado en vez de fingir que no existe.
- **El catch-all del SPA** (`main.py`) solo excluye rutas que empiezan con `api`, así que
  `/api/v1/whatsapp/*` no colisiona.
