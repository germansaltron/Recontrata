# Offline-first en terreno (Recontrata)

> Fase 5 · Apuesta #3 — **completa (3/3) y en producción** desde el 17 jun 2026.
> Solo frontend, sin migración ni cambios de modelo de datos.

Recontrata se usa en faenas de minería/construcción, muchas veces **sin señal**.
Esta funcionalidad permite que la app **abra, navegue y registre evaluaciones sin
conexión**, y que esas evaluaciones se **envíen solas** al recuperar la red.

Se construyó en tres puntos independientes:

1. **Service worker / app shell** — la app abre y navega sin señal.
2. **Cola IndexedDB** — las evaluaciones creadas offline se guardan en vez de perderse.
3. **Sync** — la cola se vacía contra la API al volver la conexión.

---

## 1. Service worker / app shell (PWA)

**Qué hace:** precachea el "shell" de la app (HTML, JS, CSS, iconos) para que cargue
desde caché aunque no haya red. Las rutas SPA caen a `index.html` cacheado.

**Cómo:** [`vite-plugin-pwa`](https://vite-pwa-org.netlify.app/) 1.3.0 (Workbox).

| Aspecto | Decisión |
|---|---|
| Estrategia de actualización | `registerType: 'prompt'` — el usuario decide cuándo actualizar (toast "Actualizar"). **No** se auto-recarga, para no interrumpir una evaluación a medio llenar. |
| Manifest | `manifest: false` — se reusa el `public/manifest.webmanifest` ya existente (no se duplica). |
| Precache | Shell + iconos. Se **excluye** media pesada (`logo-intro.mp4`, `hero-faena.jpg`, `og-image.png`, etc.) para no inflar la instalación. |
| Navegación offline | `navigateFallback: '/index.html'` con `navigateFallbackDenylist: [/^\/api\//]` — las llamadas a la API **no** caen al shell (las maneja la cola). |
| Dev | `devOptions.enabled: false` — SW apagado en `npm run dev` (no interfiere con HMR). |

**Archivos:**
- `frontend/vite.config.ts` — configuración del plugin.
- `frontend/src/lib/pwa.ts` — `setupPWA()`: registra el SW y muestra toasts
  ("Hay una versión nueva… Actualizar" / "Listo para usar sin conexión"). No-op en dev.
- `frontend/src/main.tsx` — llama a `setupPWA()` tras montar.
- `frontend/src/vite-env.d.ts` — tipos `vite/client` + `vite-plugin-pwa/client`.

---

## 2. Cola offline de evaluaciones (IndexedDB)

**Qué hace:** cuando se guarda una evaluación **sin conexión** (o si la red falla),
se persiste en IndexedDB en vez de perderse o mostrar un error.

**Por qué IndexedDB y no localStorage:** persiste datos estructurados, soporta varios
registros y no se borra al limpiar la caché del navegador.

**Esquema:**
- DB `recontrata-offline` (v1), object store `pending-evaluations` (keyPath `id`).
- Registro: `{ id, orgId, payload, label, createdAt, attempts }`
  (`payload` = `CreateEvaluationData`; `label` = "Nombre · Proyecto" para la UI).

**Archivos:**
- `frontend/src/lib/offlineQueue.ts` — wrapper de IndexedDB **vanilla** (sin
  dependencias). API: `enqueueEvaluation`, `getQueuedEvaluations`,
  `removeQueuedEvaluation`, `countQueuedEvaluations`. Cada cambio dispara el evento
  `recontrata:queue-changed` (constante `QUEUE_CHANGED_EVENT`) para que la UI se actualice.
- `frontend/src/lib/api.ts` — se exporta el tipo `CreateEvaluationData`, compartido
  entre `api.createEvaluation` y la cola (sin duplicar el shape).
- `frontend/src/hooks/usePendingSync.ts` — contador reactivo de pendientes (escucha el
  evento + `online`/`offline`).
- `frontend/src/pages/EvaluateWorker.tsx` — en `handleSubmit`:
  - Si `!navigator.onLine` → encola directo (ni intenta la red).
  - Si está online pero la llamada lanza **error de red** (`e instanceof TypeError`) → encola.
  - Si la API responde **error de validación (4xx)** → se muestra el error como antes (no se encola).

---

## 3. Sync de la cola

**Qué hace:** reenvía a la API las evaluaciones encoladas y las saca de la cola.

**Disparadores** (`useOfflineSync`):
- Evento `online` del navegador.
- Al montar el `AppShell` (si hay conexión y pendientes).
- Botón manual **"Sincronizar ahora"** en la barra de pendientes.

**Manejo de errores en `flushQueue()`** (por cada evaluación, en orden de creación):

| Resultado de `createEvaluation` | Acción |
|---|---|
| OK | Se borra de la cola (`sent++`). |
| Error de **red** (`TypeError` / quedó offline) | Se **deja** en la cola y se corta el flush (se reintenta en el próximo disparo). |
| Error del **servidor (4xx)** (ej. "ya evaluado") | Se **saca** de la cola y se reporta en `failed[]` (no va a pasar nunca; evita envenenar la cola). |

Tras enviar con éxito, se invalida la caché `projects-pending:*` (vía `swr.invalidate`)
para que los pendientes por proyecto se refresquen en la próxima visita. Toasts:
"N evaluaciones sincronizadas" / "N no se pudieron enviar" (con el motivo).

**Archivos:**
- `frontend/src/lib/offlineSync.ts` — `flushQueue(): FlushResult` (`{ sent, failed[], remaining }`).
  Guard `flushing` contra ejecuciones concurrentes.
- `frontend/src/lib/swr.ts` — `invalidate(match)` (nuevo): borra claves del cache.
- `frontend/src/hooks/useOfflineSync.ts` — orquesta `sync({ manual? })`, toasts y `syncing`.
- `frontend/src/components/layout/AppShell.tsx` — banners de estado:
  - **Offline:** barra ámbar "Sin conexión — N evaluaciones guardadas…".
  - **Online con pendientes:** barra índigo "N por sincronizar" + botón "Sincronizar ahora".

---

## ⚠️ Gotcha de operaciones: el CDN no debe cachear el service worker

`recontrata.cl` está detrás de **Cloudflare**. Como `/sw.js` termina en `.js`,
Cloudflare lo trató como asset estático y **cacheó la respuesta del fallback SPA
(HTML)** bajo `/sw.js` → el navegador intentaba registrar un HTML como SW y fallaba.

**Solución (en `backend/app/main.py`):** `/sw.js` e `index.html` se sirven con
`Cache-Control: no-cache, no-store, must-revalidate` → Cloudflare responde
`cf-cache-status: BYPASS` y deja de cachearlos. Los assets hasheados (`/assets/*`,
`workbox-*.js`) sí son inmutables y se cachean sin problema.

**Si vuelve a aparecer HTML en `/sw.js`:** purgar esa URL una vez en el panel de
Cloudflare (Caching → Purge → Custom URL: `https://recontrata.cl/sw.js`).

**Verificación rápida:**
```bash
curl -s -o /dev/null -w "%{content_type}\n" https://recontrata.cl/sw.js
# Esperado: text/javascript  (NO text/html)
```

---

## Cómo verificar

### Local (lógica real en navegador)
La cola y el flush se probaron con páginas de test temporales que importan los
**módulos reales** (`offlineQueue.ts`, `offlineSync.ts`), servidas por `vite dev` y
manejadas con Playwright. Escenarios cubiertos: encolar/orden/persistencia/borrado +
flush en éxito / error de red / 4xx / offline. (Las páginas de test no se versionan.)

### Manual en el navegador
1. Abrir la app, DevTools → **Application → Service Workers** (debe estar *activated*).
2. **Network → throttling → Offline**. Guardar una evaluación → toast "guardada en el
   dispositivo"; verla en **Application → IndexedDB → recontrata-offline →
   pending-evaluations**.
3. Volver a **Online** (o botón "Sincronizar ahora") → la evaluación se envía y la cola
   queda vacía; aparece el toast de sincronización.

---

## Deploy

- **Solo frontend, sin migración.** `railway up --detach --service faenascore`.
- El service worker usa `registerType: 'prompt'`: tras un deploy, el SW nuevo queda
  **en espera** y el usuario recibe un toast "Actualizar". Hasta que lo acepte, sigue
  viendo el bundle anterior (comportamiento intencional para no cortar una evaluación).
- Verificación post-deploy: bundle nuevo servido + `/sw.js` con `content_type:
  text/javascript` + DevTools muestra el SW activo e IndexedDB `recontrata-offline`.

---

## Límites conocidos / mejoras futuras (fuera de la apuesta #3)

- **Cold-start sin señal:** si el `orgId` nunca cargó (depende de la API), no se puede
  encolar. En el flujo real el supervisor abre la app con señal en el campamento y el
  `orgId` ya está en memoria. Cachear org/listas para arranque 100% offline es mejora futura.
- **Background Sync API** nativa como complemento al evento `online` (reintento por el SW
  aunque la pestaña esté cerrada).
