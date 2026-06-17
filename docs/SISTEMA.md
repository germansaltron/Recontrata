# Recontrata — El sistema, tal como está construido

> Documento de referencia del producto al **17 jun 2026**. Resume qué hace el
> sistema, cómo está organizado y su estado. Base para los tutoriales (`tutorial/`).

## Qué es

**Recontrata** ayuda a contratistas de minería y construcción a **registrar quién
rindió en cada faena y decidir a quién recontratar con datos reales** — no con memoria
ni cadenas de WhatsApp. Se usa desde el celular en terreno, incluso sin señal.

- **Producción:** https://recontrata.cl (frontend) · API en Railway (`faenascore-*`).
- **Stack:** React 19 + TS + Vite + Tailwind v4 (frontend) · FastAPI + SQLAlchemy
  async + Alembic (backend) · PostgreSQL (Supabase) · Clerk (auth) · Railway (deploy,
  single-service: el backend sirve el frontend) · Cloudflare (CDN).
- **Estado:** Fases 0–5 del `PLAN_ACCION_CLASE_MUNDIAL.md` completas y en producción.
- **Pre-lanzamiento:** sitio aún con muro de acceso (`AccessGate`) + `noindex`
  (quitar al abrir al público). Proyecto **personal de Germán Saltrón** (no Faymex).

---

## Funcionalidades (lo que un usuario puede hacer hoy)

### Cuenta y organización
- Registro/login con **Clerk** (correo + magic link). Cada usuario tiene su
  **organización**; sus datos están **aislados** de otros contratistas (multi-tenant,
  verificado con tests de aislamiento como CI gate).

### Trabajadores
- Crear trabajadores (nombre, RUT, especialidad). **RUT validado** automáticamente.
- **Importar desde Excel/CSV** la planilla completa de trabajadores.
- Especialidades predefinidas (Soldador, Mecánico, Eléctrico, Instrumentista, Rigger,
  Operador Grúa, Prevencionista, Supervisor, etc.).

### Proyectos (faenas)
- Crear proyectos con estado (Planificación / Activo / Completado / Cancelado), cliente, fechas.
- Asignar trabajadores al proyecto. La vista de pendientes muestra a quién falta evaluar.

### Evaluación en terreno
- Evaluación en **~30 segundos desde el celular**, sobre **5 dimensiones** con
  **anclas de comportamiento (BARS)** que describen qué significa cada nivel 1–5:
  1. **Calidad del Trabajo** — terminaciones, retrabajos, estándar.
  2. **Seguridad** — EPP, procedimientos, reporte de riesgos.
  3. **Puntualidad** — asistencia, horarios, plazos.
  4. **Trabajo en Equipo** — colaboración, comunicación, actitud.
  5. **Habilidad Técnica** — dominio del oficio, autonomía, resolución.
- **¿Recontratarías?** Sí / Con Reservas / No (motivo obligatorio si no es "Sí").
- Comentario opcional. Guarda borrador automáticamente. Al guardar, ofrece
  **"Evaluar siguiente"** pendiente del mismo proyecto (encadena el trabajo).
- Targets táctiles de **68px**: pensado para usarse con **una mano y guantes**.

### Funciona sin conexión (offline-first) — diferenciador
- **PWA con service worker**: la app abre y navega **sin señal** (app shell cacheado).
- Si se evalúa sin internet, la evaluación se **guarda en el dispositivo** (IndexedDB)
  en vez de perderse; banner "Sin conexión — modo terreno".
- Al volver la señal (o con el botón **"Sincronizar ahora"**) las evaluaciones se
  **envían solas** y la cola se vacía. Errores de red reintentan; rechazos del servidor se informan.

### Decidir con datos
- **Score ponderado por industria** (no promedio plano): en minería/construcción la
  Seguridad pesa más (Seguridad 30% > Calidad 25% > Técnica 20% > Equipo 15% > Puntualidad 10%).
- **Fórmula del puntaje** pública y visible (transparencia, art. 16 Ley 21.719).
- **Dashboard**: top trabajadores por score, evaluaciones recientes, totales.
- **Historial del trabajador**: sus 5 dimensiones a través de proyectos + exportar **CSV**.
- **Calibración de evaluadores** (admin): detecta sesgos — indulgencia/severidad vs la
  media y efecto halo — para que el puntaje sea más justo y defendible. No altera puntajes.

### Transparencia con el trabajador
- **Portal del Trabajador**: link con token **sin login** que el contratista comparte.
  El trabajador ve sus puntajes, el ponderado y la fórmula —**nunca el nombre del
  evaluador**—, puede **responder** (derecho a réplica) y **pedir baja** (opt-out), y
  **descargar un certificado** imprimible ("CV de faena").
- Posicionamiento: una **alternativa legal y transparente a las listas negras**.

---

## Mapa del frontend (rutas)

| Ruta | Pantalla |
|---|---|
| `/` | Landing pública (marketing) |
| `/app` | Dashboard |
| `/app/projects` · `/app/projects/:id` | Proyectos y detalle |
| `/app/workers` · `/app/workers/:id` | Trabajadores e historial |
| `/app/evaluate` · `/app/evaluate/:projectId/:workerId` | Evaluar |
| `/app/formula` | Fórmula del puntaje |
| `/app/calibracion` | Calibración de evaluadores (admin) |
| `/p/:token` · `/p/:token/certificado` | Portal del Trabajador (público, sin login) |

Navegación: sidebar (escritorio) + **bottom-nav** (móvil): Dashboard · Proyectos ·
Trabajadores · Evaluar. Secundario: Fórmula del puntaje · Calibración.

---

## Documentación relacionada

- `docs/OFFLINE_FIRST.md` — guía técnica del offline (service worker, cola, sync, CDN).
- `PROGRESS.md` — bitácora cronológica de desarrollo (autoritativa).
- `PLAN_ACCION_CLASE_MUNDIAL.md` — plan de fases 0–5.
- `tutorial/` — serie de tutoriales en video (guiones + pipeline de producción).

---

## Pendientes (no bloquean el uso; sí para abrir al público)

1. **Login real** verificado con correo en `recontrata.cl/sign-up` (pendiente humano).
2. Quitar el muro `AccessGate` (`recontrata2211`) + `noindex` al lanzar.
3. Opcional: hint "Agregar a pantalla de inicio" (PWA instalable); cold-start 100%
   offline (cachear organización/listas); Background Sync API nativa.
