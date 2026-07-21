# Sesión 21-jul-2026 — Pendientes de calidad (post revisión pre-prod)

> Se resolvieron los hallazgos MEDIO/BAJO de `SESION_20JUL2026_REVISION_PREPROD.md`.
> Todo verificado y **desplegado a producción** (auto-deploy GitHub confirmado).

## Resumen

| Hallazgo | Qué se hizo | Archivos | Tests |
|---|---|---|---|
| **M1** bot fire-and-forget | La task de `_process_bot_message` se retiene (dict de timers); el GC ya no la mata a medias | `api/v1/whatsapp.py` | — |
| **M2** aislamiento en evaluaciones | `_create_single` valida que `worker_id`/`project_id` sean de la org (como `assign_workers`) | `api/v1/evaluations.py` | +2 (integración) |
| **M3** rate limiting | slowapi en webhook Flow (60/min) + portal (GET 120, POST 20), clave = IP real (`CF-Connecting-IP`→`X-Forwarded-For`→remote). WhatsApp/Meta NO se limita (HMAC + reintentos) | `ratelimit.py`, `main.py`, `webhooks.py`, `portal.py`, `requirements.txt` | +3 |
| **M4** buffer del bot | Debounce por teléfono: agrupa la ráfaga fragmentada en 1 respuesta. `MESSAGE_BUFFER_SECONDS` ahora se usa. Solo activo con `BOT_ENABLED=true` | `api/v1/whatsapp.py` | +3 |
| **M5** 401 global | Un 401 del servidor cierra sesión → login. **Salvaguarda A1:** el 401 por token ausente y las llamadas `silent` (flush offline) NO deslogean | `lib/api.ts`, `lib/offlineSync.ts`, `App.tsx` | +4 |
| **M6** 403 frágil | `e instanceof ApiError && e.status === 403` en vez de `String(e).includes('403')` | `pages/Calibration.tsx` | — |
| **M7-a** contenedor root | Usuario no-root (uid 10001) en runtime | `Dockerfile` | Docker OK |
| **Limpieza** | Deps a versión exacta (`==`), `BOT_SUPPORT_EMAIL` cableado (prompts/tools/conversation), `MAX_TURNS` eliminado | `requirements.txt`, `config.py`, `bot/*.py` | — |

**Backend 160 tests verdes · Frontend 21 tests verdes · 2 Docker builds OK (no-root + pins).**

## Commits (todos en `master`, desplegados)
- `97e2076` M1 + M2 + M6 + M7-no-root
- `fba7411` M5 (401 global)
- `940f34c` M3 (rate limiting)
- `8fdc88f` M4 (buffer del bot)
- `fa0dd5c` limpieza (pins + BOT_SUPPORT_EMAIL + MAX_TURNS)

## Verificación de producción (post-deploy)
- Auto-deploy GitHub **confirmado funcionando** (bundle nuevo `index-D30QG6tY.js`, ~160 s).
- `/api/health` → 200 `database: connected` (arrancó con slowapi sin problema).
- `/api/v1/portal/<token-inválido>` → 404 (no 500): router + rate limiting sanos.

## Decisiones de diseño clave
- **M5 sin romper A1:** el fix de ayer (A1) depende de que un 401 durante la sync offline
  NO borre la evaluación ni saque al usuario. Por eso: (a) el 401 que lanza `apiFetch` por
  token ausente NO llama al handler; (b) `createEvaluation` acepta `{ silent: true }` y el
  flush lo pasa. Tests en `lib/api.test.ts` cubren los tres casos.
- **M3 detrás de Cloudflare:** `request.client.host` sería el proxy (todos compartirían
  clave). Se usa `CF-Connecting-IP`. Storage in-memory: correcto con 1 réplica.

## Pendientes dejados a propósito (con razón)
1. **alembic en release phase (resto de M7):** único cambio con riesgo de *downtime*, y
   beneficio nulo hoy (1 réplica; la carrera solo aparece con ≥2). Hacer al escalar:
   `[deploy] preDeployCommand = "alembic upgrade head"` en `railway.toml` + quitarlo del
   CMD del Dockerfile. Ventaja extra: si la migración falla, Railway no promueve el deploy.
2. **Prefijo `faenascore:draft:` en localStorage:** cambiarlo a `recontrata:` descarta los
   borradores a medio llenar existentes. Cosmético con efecto secundario → requiere migrar
   las claves viejas si se hace.
3. **Email de usuario vacío (Clerk):** el provisioning guarda `email=""` porque el JWT de
   Clerk no trae el claim. Se arregla en el **dashboard de Clerk** (JWT template → incluir
   `email`), no en el código.
4. **Lock transitivo de deps:** se fijaron las directas (`==`). El lock del árbol completo
   conviene generarlo con uv/pip-tools **en Linux** (no en el .venv Windows, que metería
   paquetes específicos de SO).
## Adición — python-jose → PyJWT: MIGRADO (commit `c3ceb4b`)

Germán dio el visto bueno y se migró. `app/auth.py` y `app/dependencies.py` ahora usan
**PyJWT[crypto] 2.10.1** en vez de python-jose (poco mantenida, con CVEs). Se conserva el
fetch async del JWKS con httpx (PyJWKClient es síncrono y bloquearía el event loop); PyJWT
solo selecciona la clave por `kid` y valida firma/exp/issuer/audience con `algorithms=
["RS256"]`. Mismas garantías. `requirements.txt`: fuera `python-jose[cryptography]`, dentro
`PyJWT[crypto]==2.10.1`.

- **Tests:** `tests/test_auth_jwt.py` — 6 casos con tokens RSA reales (válido / expirado /
  issuer malo / audience malo / kid desconocido / firma de otra clave). Backend 166 verdes.
- **Docker Linux:** build OK, PyJWT presente, `import jose` → ModuleNotFoundError.
- **Prod:** todo token inválido → 401, nunca 500 (firma falsa incluida). Happy path (login
  real) a confirmar por Germán abriendo la app.
