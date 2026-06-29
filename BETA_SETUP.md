# Recontrata — Preparar el beta cerrado

> Guía de los pasos **manuales** para dejar el sistema listo para pasárselo a personas de confianza.
> El código ya está preparado (Sentry, botón de feedback y AccessGate están wired); aquí solo se configuran las claves y el panel de Clerk.
> Fecha: 29 de junio de 2026.

---

## Checklist

| # | Tarea | Tipo | Estado |
|---|---|---|---|
| 1 | Migrar Clerk a producción (pk_live) | Panel + env | ✅ **Hecho (29 jun)** — DNS verificado, claves en Railway, primer usuario creado y login E2E OK |
| 2 | Crear proyectos Sentry y pegar los DSN | Panel + env | ✅ **Hecho (29 jun)** — proyectos `recontrata-backend`/`recontrata-frontend`, DSN en Railway, código activo en prod |
| 3 | Crear canal de feedback y pegar la URL | Panel + env | ✅ **Hecho (29 jun)** — botón flotante → WhatsApp (`VITE_FEEDBACK_URL=wa.me/56935652743`) |
| 4 | Fijar el código de acceso del beta | env | ✅ por defecto `recontrata2211` (cambiar con `VITE_ACCESS_CODE` si se quiere) |
| 5 | Redeploy (`railway up`) y verificar | Deploy | ✅ **Hecho** — Clerk pk_live, Sentry y feedback verificados en prod |

> **Estado: beta LISTO para invitar.** Comparte `recontrata.cl` + el código de acceso. Los tres ajustes "duros" (auth de prod, observabilidad, feedback) están cerrados.

Las variables `VITE_*` son **build-time**: se hornean al construir el frontend, así que **cualquier cambio en ellas requiere un nuevo deploy** (`railway up`). El Dockerfile ya las declara como build args y Railway las inyecta automáticamente desde las variables del servicio.

---

## 1. Clerk → producción (pk_live)

Hoy corre en `pk_test` (instancia de **desarrollo**: tope ~100 usuarios, banners de dev, no apta para usuarios reales). Para testers reales:

1. En el **dashboard de Clerk** → crea/activa la **Production instance** del proyecto Recontrata.
2. Configura el **dominio de producción** `recontrata.cl`. Clerk te pedirá agregar unos **registros DNS** (CNAME tipo `clerk.recontrata.cl`, `accounts.recontrata.cl`, etc.) en tu proveedor de DNS. Espera a que Clerk los verifique (puede tardar).
3. Copia las claves de la instancia **Production**:
   - `pk_live_...` (publishable key)
   - `sk_live_...` (secret key)
   - El **JWKS URL**, **issuer** y **audience** de la instancia de producción (los da Clerk en la sección de API/JWT).
4. En **Railway** (servicio `faenascore`, env production) → **Variables**, fija:
   - `VITE_CLERK_PUBLISHABLE_KEY = pk_live_...`
   - `CLERK_SECRET_KEY = sk_live_...`
   - `CLERK_JWKS_URL = <jwks de producción>`
   - `CLERK_ISSUER = <issuer de producción>`
   - `CLERK_AUDIENCE = <audience, si aplica>`
5. `railway up` para reconstruir con la clave nueva. Verifica que el registro/login funcione sin banners de "development".

> ⚠️ Asegúrate de que `AUTH_MOCK_ENABLED` y `ALLOW_MOCK_IN_PROD` estén en `false`/vacío en prod (el backend ya falla cerrado si no).

---

## 2. Sentry (tracking de errores)

El código ya inicializa Sentry **solo si hay DSN** (no-op si está vacío). Falta crear los proyectos y pegar los DSN.

1. Crea una cuenta/organización en **sentry.io** (plan gratis sirve para el beta).
2. Crea **2 proyectos**:
   - Plataforma **Python / FastAPI** → para el backend.
   - Plataforma **React** → para el frontend.
3. Copia el **DSN** de cada proyecto (formato `https://xxx@oyyy.ingest.sentry.io/zzz`).
4. En **Railway** → Variables:
   - `SENTRY_DSN = <DSN del proyecto FastAPI>`
   - `VITE_SENTRY_DSN = <DSN del proyecto React>`
   - (opcional) `SENTRY_ENVIRONMENT = production` y `VITE_SENTRY_ENVIRONMENT = production` ya vienen por defecto.
5. `railway up`. Para verificar, fuerza un error de prueba (p. ej. una ruta inexistente del backend o lanzar una excepción) y revisa que aparezca en Sentry.

> El backend usa `send_default_pii=False` para **no** filtrar datos personales de trabajadores en los eventos de error.

---

## 3. Canal de feedback

El botón flotante **"Feedback"** aparece solo si `VITE_FEEDBACK_URL` está configurado.

1. Crea el destino más cómodo:
   - Un **formulario de Google** (recomendado: preguntas tipo "¿qué intentabas hacer?", "¿qué pasó?", "¿en qué pantalla?"), **o**
   - Un enlace de **WhatsApp**: `https://wa.me/569XXXXXXXX?text=Feedback%20Recontrata`.
2. En **Railway** → `VITE_FEEDBACK_URL = <la URL>`.
3. `railway up`. El botón aparece abajo a la derecha en toda la app.

---

## 4. Código de acceso del beta (AccessGate)

La app está detrás de un gate con clave. Por defecto el código es **`recontrata2211`**.

- Para usar un código propio del beta: en Railway fija `VITE_ACCESS_CODE = <tu-codigo>` y `railway up`.
- Reparte ese código solo a los testers de confianza.
- Para desactivar el gate al lanzar de verdad: `VITE_ACCESS_GATE = false`.

---

## 5. Cómo setear variables en Railway + redeploy

1. `railway variables` (o el panel web del servicio) para ver/editar.
2. Fija las variables de arriba.
3. `railway up` desde la raíz del repo para reconstruir y desplegar (Railway inyecta las `VITE_*` como build args automáticamente).
4. Verifica en https://recontrata.cl.

---

## Lo que NO hace falta para el beta

Pagos (Flow), enforcement de límites de plan, factura electrónica y rate limiting **no** son necesarios para un beta cerrado: los testers entran como "design partner" con acceso gratuito e ilimitado. Eso se construye después, al validar disposición a pagar (ver `ESTUDIO_PRECIOS_INVERSOR.md`).

## Recordatorio legal (datos reales)

En cuanto un tester cargue **trabajadores reales** se tratan datos personales de terceros (Ley 19.628 / 21.719). Mientras cada empresa use **su propia data aislada** (caso del beta), es legítimo; el flujo de **consentimiento + Portal del Trabajador + opt-out** ya está construido. El riesgo de "listas negras" solo aparece si se comparte desempeño **entre** empresas — eso no ocurre en el beta y queda pendiente de validación legal antes del plan Enterprise.
