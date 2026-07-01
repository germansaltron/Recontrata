# Plan de QA — Lanzamiento Recontrata

> Lista de pruebas manuales para verificar que todas las funcionalidades operan correctamente y que no existen bugs que dañen la reputación de la plataforma en el lanzamiento.
>
> **Proyecto:** Recontrata (ex-FaenaScore) — evaluación de desempeño y recontratación de trabajadores.
> **Stack:** FastAPI + React/Vite/Tailwind + Clerk + PostgreSQL. PWA con modo offline.
> **Prod:** https://recontrata.cl

---

## Cómo usar este documento

- Cada prueba tiene un **ID**, **prioridad**, **pasos** y **resultado esperado**. Marca `[x]` al pasar.
- **Prioridades:**
  - **P0 — Bloqueante de lanzamiento.** Falla = bug visible al cliente, fuga de datos o riesgo legal. No se lanza con P0 abiertos.
  - **P1 — Importante.** Degrada la experiencia o la confianza, pero no bloquea si se documenta.
  - **P2 — Pulido.** Cosmético o caso borde poco probable.
- **Entornos sugeridos:**
  - **Staging/local** para pruebas destructivas (crear/borrar masivo, import).
  - **Prod** solo para smoke test final (sección 17), sin contaminar con datos basura.
- **Dispositivos mínimos:** 1 desktop (Chrome), 1 móvil Android real (Chrome) — la app está pensada para uso en terreno con guantes y mala señal.
- **Cuentas necesarias:** al menos 2 usuarios en 2 organizaciones distintas (para multi-tenancy), y 1 admin + 1 supervisor en la misma org (para roles/calibración).

---

## 0. Preparación del entorno (pre-requisitos)

| ID | Prio | Verificación |
|----|------|--------------|
| ENV-01 | P0 | `GET /health` responde `{status:"ok", database:"connected"}`. |
| ENV-02 | P0 | Frontend carga sin errores en consola (F12 → Console limpio en la primera carga). |
| ENV-03 | P0 | Variables de entorno de **producción** correctas: Clerk con `pk_live_*` (NO `pk_test_*` — el banner "development mode" no debe aparecer). |
| ENV-04 | P1 | `VITE_ACCESS_CODE` definido y conocido por el equipo; o `VITE_ACCESS_GATE=false` si se decide abrir. |
| ENV-05 | P0 | `ADMIN_TOKEN` configurado (≥32 chars) y NO expuesto en el cliente. El endpoint `/admin/seed-demo` debe estar **inaccesible** sin ese token. |
| ENV-06 | P1 | Datos de demo sembrados (`/admin/seed-demo`) en staging para tener proyectos/trabajadores/evaluaciones realistas. |

---

## 1. Autenticación y control de acceso (Clerk + AccessGate)

| ID | Prio | Pasos | Resultado esperado |
|----|------|-------|--------------------|
| AUTH-01 | P0 | Registro nuevo (Sign-up) con email válido. | Cuenta creada, verificación de email funciona, redirige a la app. |
| AUTH-02 | P0 | Iniciar sesión (Sign-in) con credenciales válidas. | Entra al dashboard. Token Bearer se envía en cada request (revisar Network → header `Authorization`). |
| AUTH-03 | P0 | Acceder a una ruta privada (`/app`, `/app/workers`) sin sesión. | Redirige a Sign-in; nunca muestra datos. |
| AUTH-04 | P0 | Cerrar sesión (UserButton → Salir). | Sesión termina; rutas privadas vuelven a pedir login. |
| AUTH-05 | P0 | **NO debe aparecer el banner de "development mode" de Clerk** en prod. | Sin banner. Si aparece → falta migrar a `pk_live`. |
| AUTH-06 | P1 | AccessGate: ingresar código incorrecto. | No deja pasar; mensaje claro. |
| AUTH-07 | P1 | AccessGate: código correcto. | Desbloquea; persiste 90 días (localStorage). Recargar no vuelve a pedirlo. |
| AUTH-08 | P1 | Token expira / sesión vieja (esperar expiración o borrar token). | Manejo limpio: pide re-login, no pantalla en blanco ni error técnico crudo. |
| AUTH-09 | P1 | Primer login auto-provisiona usuario en DB (GET /me). | El usuario aparece con su email/nombre; se crea su organización o se le pide crearla. |
| AUTH-10 | P2 | Login en red lenta (token tarda). | Hay timeout de 5s en obtención de token; muestra estado de carga, no se cuelga. |

---

## 2. Multi-tenancy y seguridad de datos (REPUTACIÓN CRÍTICA)

> Una fuga de datos entre organizaciones (ver trabajadores/evaluaciones de otra empresa) sería el peor bug posible al lanzamiento. Probar con **2 organizaciones distintas (Org A y Org B)**.

| ID | Prio | Pasos | Resultado esperado |
|----|------|-------|--------------------|
| SEC-01 | P0 | Como usuario de Org A, copiar el `org_id` de Org B (de la otra sesión) y pedir `GET /organizations/{orgB_id}/workers` con el token de A. | **403 NOT_ORG_MEMBER**. Nunca devuelve datos de B. |
| SEC-02 | P0 | Igual con `/projects`, `/evaluations`, `/dashboard/stats`, `/calibration` apuntando a Org B. | 403 en todos. |
| SEC-03 | P0 | IDOR: como Org A, intentar `GET .../workers/{worker_de_B_id}` usando el org_id de A en la ruta. | 404 WORKER_NOT_FOUND (no se filtra el dato). |
| SEC-04 | P0 | IDOR en evaluación: editar/borrar `/evaluations/{eval_de_B}` desde Org A. | 404, sin afectar datos de B. |
| SEC-05 | P0 | Desasignar trabajador de un proyecto cruzando IDs de otra org. | 404/403, sin borrar nada ajeno. |
| SEC-06 | P1 | Inyección en búsqueda: en `search` de Workers escribir `' OR 1=1 --`, `%`, `_`. | Búsqueda segura (queries parametrizadas); no error 500, no resultados de más. |
| SEC-07 | P1 | XSS almacenado: crear evaluación con comentario `<script>alert(1)</script>` y verlo en WorkerDetail, Portal y Certificado. | Se muestra como texto, NO se ejecuta. |
| SEC-08 | P0 | Endpoint admin: `POST /admin/seed-demo/{org}` sin header `X-Admin-Token` o con token incorrecto. | 403 (fail-closed). Nunca borra/siembra datos. |
| SEC-09 | P1 | Portal token: adivinar/alterar un token en `/p/{token}`. | 404 si no existe; el token es de 32 bytes (no adivinable). |
| SEC-10 | P1 | Regenerar portal-link de un trabajador. | El token viejo deja de funcionar; el nuevo sí. |
| SEC-11 | P1 | Export CSV de trabajadores contiene PII (RUT, teléfono, email). | Solo accesible autenticado y de la propia org. |

---

## 3. Trabajadores (Workers) — CRUD, RUT, import/export

| ID | Prio | Pasos | Resultado esperado |
|----|------|-------|--------------------|
| WRK-01 | P0 | Crear trabajador con RUT válido (ej. `12.345.678-5`), nombre, apellido, especialidad. | Se crea; aparece en la lista. RUT se auto-formatea al salir del campo. |
| WRK-02 | P0 | Crear con RUT inválido (dígito verificador incorrecto, ej. `12.345.678-9`). | Rechaza con mensaje claro; borde rojo en el campo. |
| WRK-03 | P0 | Crear con RUT duplicado en la misma org. | **409 WORKER_DUPLICATE_RUT**, mensaje legible (no error crudo). |
| WRK-04 | P1 | Mismo RUT en **otra org** (Org B). | Permitido (unicidad es por org). |
| WRK-05 | P1 | Validación RUT cliente vs servidor: probar `1-9`, `11.111.111-1`, RUT con K (`12.345.670-K`). | Cliente y servidor coinciden en aceptar/rechazar. |
| WRK-06 | P0 | Editar trabajador. | RUT aparece **deshabilitado** ("no se puede modificar"); el resto se guarda. |
| WRK-07 | P1 | Eliminar trabajador. | Soft-delete (is_active=false); desaparece de la lista activa pero su historial se conserva. |
| WRK-08 | P1 | Búsqueda por nombre y por RUT (con debounce 300ms). | Filtra correcto; no dispara una request por tecla. |
| WRK-09 | P1 | Filtros: especialidad + score mínimo. | Resultados coherentes; combinables. |
| WRK-10 | P1 | Paginación (>20 trabajadores). | Páginas correctas; no se repiten ni faltan registros. |
| WRK-11 | P1 | Orden por columna (apellido, nombre, especialidad, fecha). | Orden asc/desc correcto. |
| WRK-12 | P0 | **Importar Excel** con formato válido (rut, nombre, apellido, especialidad, teléfono, email, certificaciones). | Reporta `creados / actualizados`; los crea bien. |
| WRK-13 | P0 | Importar archivo con filas inválidas (RUT malo, especialidad rara, celdas vacías). | NO falla todo el lote; reporta lista de errores por fila; las filas buenas sí entran. |
| WRK-14 | P1 | Re-importar el mismo archivo (mismos RUT). | Actualiza, no duplica. |
| WRK-15 | P1 | Importar archivo no-Excel (.pdf, .txt), >5 MB, o >5000 filas. | Rechaza con mensaje claro (MIME / tamaño / límite de filas). |
| WRK-16 | P2 | Lista de errores de import muy larga. | UI no se rompe (muestra primeros ~20, scroll). |
| WRK-17 | P1 | Exportar CSV. | Descarga `trabajadores-*.csv` con headers y datos correctos (incluye conteo y promedio de evaluaciones). |
| WRK-18 | P2 | Caracteres especiales (ñ, tildes, apellidos compuestos) en import/export. | Encoding correcto (UTF-8), sin caracteres rotos. |

---

## 4. Proyectos (Projects) y asignación de trabajadores

| ID | Prio | Pasos | Resultado esperado |
|----|------|-------|--------------------|
| PRJ-01 | P0 | Crear proyecto solo con nombre. | Se crea (estado por defecto "active"); demás campos opcionales. |
| PRJ-02 | P1 | Crear con cliente, ubicación, fechas inicio/fin, notas. | Todo se guarda y se muestra. |
| PRJ-03 | P2 | Fecha fin anterior a inicio. | (Verificar comportamiento: idealmente avisa; si lo permite, documentar.) |
| PRJ-04 | P1 | Filtrar por estado (planning/active/completed/cancelled). | Filtro correcto; badge de color coherente. |
| PRJ-05 | P0 | Editar proyecto: cambiar estado. | Se actualiza; el selector de estado solo aparece en edición. |
| PRJ-06 | P0 | Asignar trabajadores al proyecto (multi-select con búsqueda). | Se asignan; aparecen en la tabla del proyecto. Devuelve cuántos se agregaron. |
| PRJ-07 | P1 | Re-asignar un trabajador ya asignado. | No duplica (se omite silenciosamente). |
| PRJ-08 | P1 | Asignar solo muestra trabajadores **activos** y excluye los ya asignados. | Lista filtrada correcta. |
| PRJ-09 | P1 | Desasignar trabajador del proyecto. | Se quita de la tabla; el trabajador sigue existiendo. |
| PRJ-10 | P0 | Contadores del proyecto (worker_count, evaluation_count). | Cuadran con la realidad (las evaluaciones borradas NO cuentan). |
| PRJ-11 | P1 | CTA "N trabajadores sin evaluar" lleva al primer pendiente. | Link correcto a `/app/evaluate/:projectId/:workerId`. |

---

## 5. Evaluaciones y fórmula de puntaje (NÚCLEO DEL PRODUCTO)

> Si el puntaje está mal calculado, el producto pierde toda credibilidad. Verificar la aritmética a mano en al menos un caso.

| ID | Prio | Pasos | Resultado esperado |
|----|------|-------|--------------------|
| EVAL-01 | P0 | Evaluar un trabajador: 5 dimensiones (calidad, seguridad, puntualidad, equipo, técnica) de 1 a 5 + recontratación. | Se guarda; aparece en historial del trabajador y del proyecto. |
| EVAL-02 | P0 | Verificar `score_average` = promedio simple de las 5 (÷5), redondeado a 2 decimales. | Coincide con cálculo manual. |
| EVAL-03 | P0 | Verificar `score_weighted` = suma ponderada según la **industria** de la org. Ej. minería: calidad .25, seguridad .30, puntualidad .10, equipo .15, técnica .20. | Coincide con cálculo manual; pesos suman 1.0. |
| EVAL-04 | P0 | Recontratación = "Con reservas" o "No" **sin** motivo. | Bloquea: motivo obligatorio (≥3 caracteres). |
| EVAL-05 | P0 | Recontratación = "Sí". | Motivo no obligatorio; guarda bien. |
| EVAL-06 | P0 | Botón "Guardar" deshabilitado hasta completar los 5 scores + recontratación (+ motivo si aplica). | Etiqueta dinámica indica qué falta. |
| EVAL-07 | P0 | Evaluar dos veces el mismo trabajador en el mismo proyecto. | **409 EVALUATION_DUPLICATE** (una evaluación activa por par proyecto-trabajador). |
| EVAL-08 | P1 | Borrar una evaluación y volver a evaluar al mismo par. | Permitido (la borrada es soft-delete; se puede re-crear). |
| EVAL-09 | P0 | **Draft autoguardado**: empezar evaluación, salir sin enviar, volver. | El borrador se restaura (localStorage); muestra hora de guardado. |
| EVAL-10 | P0 | Enviar evaluación. | El draft se elimina tras envío exitoso. |
| EVAL-11 | P1 | Editar una evaluación dentro de la ventana permitida. | Se actualiza; recalcula average/weighted; queda registro en historial (audit). |
| EVAL-12 | P0 | Editar una evaluación **después** de la ventana de edición (EVALUATION_EDIT_WINDOW_HOURS). | **409 EVALUATION_EDIT_WINDOW_EXPIRED** (inmutabilidad/trazabilidad). |
| EVAL-13 | P1 | Historial de cambios (`/history`) de una evaluación editada/borrada. | Muestra create/update/delete con autor, fecha, campos cambiados y snapshot. |
| EVAL-14 | P1 | Cambiar la **industria** de la org y abrir un trabajador con evaluaciones. | El score ponderado se recalcula con los nuevos pesos de forma coherente. |
| EVAL-15 | P0 | StarRating en móvil con dedo/guante. | Tap targets grandes (68px en lg); fácil de tocar; accesible (radiogroup). |
| EVAL-16 | P1 | Evaluación por lote (`/evaluations/batch`) con algún ítem inválido. | Crea los válidos; reporta errores por índice; no aborta todo. |
| EVAL-17 | P1 | "Evaluar siguiente pendiente" tras enviar. | Lleva al próximo trabajador sin evaluar del mismo proyecto; toast con CTA. |
| EVAL-18 | P2 | Anclas de comportamiento (BARS) por nivel en cada dimensión. | Texto de ayuda visible y correcto por cada estrella. |

---

## 6. Modo offline (CRÍTICO — uso en terreno sin señal)

> Es una de las apuestas centrales del producto. Probar en móvil real activando "Modo avión" o DevTools → Network → Offline.

| ID | Prio | Pasos | Resultado esperado |
|----|------|-------|--------------------|
| OFF-01 | P0 | Con la app cargada, activar modo avión. Evaluar un trabajador y guardar. | Se encola en IndexedDB; toast "guardada en el dispositivo"; **no** error de red. |
| OFF-02 | P0 | AppShell estando offline. | Banner ámbar "Sin conexión" + contador de evaluaciones en cola. |
| OFF-03 | P0 | Hacer 3 evaluaciones offline seguidas. | Las 3 quedan en cola; contador = 3. |
| OFF-04 | P0 | Volver a tener conexión (desactivar modo avión). | Sincroniza automáticamente; toast "X evaluaciones sincronizadas"; banner desaparece. |
| OFF-05 | P0 | Tras sincronizar, verificar en backend/UI. | Las evaluaciones existen, con los datos correctos, sin duplicados. |
| OFF-06 | P1 | Botón "Sincronizar ahora" manual (estando online con pendientes). | Fuerza el flush; feedback visual (icono pulsando). |
| OFF-07 | P1 | Sincronizar manual estando offline. | Toast "Sin conexión, conéctate para sincronizar"; nada se pierde. |
| OFF-08 | P1 | Sincronizar sin pendientes. | Toast "Todo al día". |
| OFF-09 | P1 | Item que falla por **error de servidor** (4xx, ej. duplicado al sincronizar). | Se reporta como fallido y se quita de la cola (no reintenta infinito); el resto sí entra. |
| OFF-10 | P1 | Item que falla por **error de red** durante el flush. | Permanece en cola para reintento posterior. |
| OFF-11 | P1 | Cerrar y reabrir la app/pestaña con evaluaciones en cola. | La cola persiste (IndexedDB), no se pierde. |
| OFF-12 | P0 | Recargar la app **estando offline** (PWA). | La app abre desde caché (service worker), no pantalla de dinosaurio. |
| OFF-13 | P2 | Navegador sin IndexedDB / almacenamiento lleno. | Degrada con elegancia (no crash; contador en 0 si no puede). |
| OFF-14 | P1 | Aviso de versión nueva del PWA. | Toast "Hay una versión nueva" + botón Actualizar; no interrumpe una evaluación en curso. |

---

## 7. Portal del trabajador y derecho a réplica (LEGAL + REPUTACIÓN)

> Acceso público por token. Aquí se juega la transparencia legal (Ley 21.719). Errores aquí = riesgo legal y reputacional.

| ID | Prio | Pasos | Resultado esperado |
|----|------|-------|--------------------|
| POR-01 | P0 | Abrir `/p/{token}` válido **sin estar logueado**. | Muestra perfil: nombre, RUT, especialidad, org, evaluaciones, score, fórmula. |
| POR-02 | P0 | Token inválido/inexistente. | 404 / pantalla "no encontrado" limpia; no filtra datos. |
| POR-03 | P0 | El portal muestra solo las evaluaciones de **ese** trabajador. | Sin datos de otros; sin evaluaciones borradas. |
| POR-04 | P0 | Derecho a réplica: responder una evaluación. | Se guarda con timestamp; queda visible para el trabajador y para el supervisor (WorkerDetail). |
| POR-05 | P1 | Réplica vacía. | Bloquea (texto requerido). |
| POR-06 | P1 | Evaluación ya respondida. | Muestra la respuesta en solo lectura; no permite duplicar. |
| POR-07 | P0 | Opt-out: "No autorizo evaluaciones". | Registra consentimiento como `revoked` (method=platform); recarga perfil; queda constancia. |
| POR-08 | P1 | La fórmula de puntaje mostrada en el portal coincide con la industria de la org. | Pesos correctos y transparentes. |
| POR-09 | P0 | Réplica con XSS en el texto. | Se almacena como texto y se muestra escapado (ver SEC-07). |

---

## 8. Certificado de desempeño

| ID | Prio | Pasos | Resultado esperado |
|----|------|-------|--------------------|
| CRT-01 | P1 | Abrir `/p/{token}/certificado`. | Certificado con nombre, especialidad, RUT, score ponderado, conteos de recontratación y tabla de evaluaciones. |
| CRT-02 | P1 | Botón "Imprimir / Guardar PDF". | Genera PDF limpio (CSS @media print): sin barra sticky, layout correcto, logo visible. |
| CRT-03 | P2 | Fecha de emisión. | Es la fecha actual. |
| CRT-04 | P2 | Certificado de trabajador sin evaluaciones. | No se rompe; muestra estado vacío razonable. |

---

## 9. Consentimiento del trabajador (cumplimiento legal)

| ID | Prio | Pasos | Resultado esperado |
|----|------|-------|--------------------|
| CON-01 | P1 | Trabajador nuevo. | Estado de consentimiento por defecto = "pending". |
| CON-02 | P1 | Registrar consentimiento (estado + vía: verbal/escrito/email/contrato/plataforma + notas). | Se guarda; muestra quién lo registró y cuándo. |
| CON-03 | P1 | Cambiar estado (pending → informed → granted → revoked). | Upsert correcto; refleja último estado. |
| CON-04 | P1 | Opt-out desde el portal (POR-07) se refleja aquí. | Estado pasa a "revoked", method "platform". |

---

## 10. Calibración de evaluadores (solo admin)

| ID | Prio | Pasos | Resultado esperado |
|----|------|-------|--------------------|
| CAL-01 | P0 | Acceder a `/app/calibracion` como **no-admin** (supervisor). | 403 / mensaje "solo admin"; no muestra datos. |
| CAL-02 | P1 | Como admin con ≥5 evaluaciones por evaluador. | Muestra promedio de la org y tabla de evaluadores. |
| CAL-03 | P1 | Verificar banderas: "Indulgente" (Δ≥+0.5), "Severo" (Δ≤−0.5), "Efecto halo" (dispersión<0.5), "Pocos datos" (<5). | Cada bandera aparece en el caso correcto; colores coherentes. |
| CAL-04 | P2 | Org con pocas evaluaciones (<min_sample). | Mensaje de "datos insuficientes", sin tabla rota. |
| CAL-05 | P2 | Evaluaciones sin evaluador identificado. | Maneja "Sin identificar" sin crash. |

---

## 11. Dashboard

| ID | Prio | Pasos | Resultado esperado |
|----|------|-------|--------------------|
| DSH-01 | P0 | Cargar dashboard con datos. | KPIs correctos: proyectos (total/activos), trabajadores, evaluaciones, score ponderado promedio, % recontratación. |
| DSH-02 | P1 | Skeletons durante la carga. | Se ven loaders, no saltos bruscos ni pantalla en blanco. |
| DSH-03 | P1 | "Evaluar siguiente pendiente". | Aparece solo si hay pendientes; lleva al trabajador correcto. |
| DSH-04 | P1 | Top trabajadores y evaluaciones recientes. | Datos coherentes; links correctos; respeta soft-deletes. |
| DSH-05 | P0 | Dashboard de una **org sin datos** (recién creada). | Estado vacío amigable (no errores, no NaN, no "null"). |
| DSH-06 | P2 | % recontratación / promedio cuando no hay evaluaciones. | Muestra "—" o vacío, nunca `NaN` ni división por cero. |

---

## 12. Fórmula de puntaje (página /app/formula)

| ID | Prio | Pasos | Resultado esperado |
|----|------|-------|--------------------|
| FOR-01 | P1 | Ver perfil activo según industria de la org. | Barras de pesos correctas; suman 100%. |
| FOR-02 | P1 | Cambiar de industria como **admin**. | Se actualiza el perfil activo; afecta el cálculo ponderado. |
| FOR-03 | P0 | Cambiar de industria como **no-admin**. | Bloqueado con mensaje (403); no cambia nada. |
| FOR-04 | P2 | Nota legal (Ley 21.719) visible. | Texto presente. |

---

## 13. Páginas públicas y marketing (primera impresión)

| ID | Prio | Pasos | Resultado esperado |
|----|------|-------|--------------------|
| LND-01 | P0 | Landing `/` carga (logueado y sin loguear). | Sin errores; CTA cambia según estado de sesión. |
| LND-02 | P0 | **Cero menciones a "FaenaScore" o "faena"** en texto visible. | Todo dice "Recontrata"; revisar hero, features, footer, título de pestaña (`<title>Recontrata</title>`). |
| LND-03 | P1 | Imágenes del hero y screenshots cargan. | Sin imágenes rotas; el dashboard-preview dice "Recontrata". |
| LND-04 | P1 | Tutoriales embebidos en la landing. | Reproducen (o muestran "muy pronto" si sin ID). |
| LND-05 | P1 | Links de planes/precios y CTAs. | Llevan a sign-up / app correctamente. |
| LND-06 | P1 | `/terminos` y `/privacidad`. | Cargan; texto legible; sin "faena"/"FaenaScore". |
| LND-07 | P2 | Open Graph / compartir en redes (`og:image`). | Previsualización con logo Recontrata y tagline (probar en validador OG o WhatsApp). |
| LND-08 | P2 | Favicon e ícono PWA. | Ícono Recontrata (cuadro azul + flecha), no el morado viejo. |

---

## 14. PWA, intro animada e instalación

| ID | Prio | Pasos | Resultado esperado |
|----|------|-------|--------------------|
| PWA-01 | P1 | Intro animada (LogoIntro) en primera visita. | Splash con logo armándose → vuela al navbar; saltable con click/scroll/tecla. |
| PWA-02 | P1 | Recargar dentro de la misma sesión. | La intro NO se repite (sessionStorage). |
| PWA-03 | P1 | `prefers-reduced-motion` activado. | La intro se omite. |
| PWA-04 | P1 | Instalar PWA en móvil ("Agregar a pantalla de inicio"). | Se instala con ícono Recontrata; abre en modo standalone. |
| PWA-05 | P2 | Splash no queda "pegado" al entrar directo a `/app`, `/sign-in`, `/terminos`. | Se remueve en todas las rutas. |
| PWA-06 | P2 | El morph del logo al navbar queda alineado. | Sin clon residual ni descalce. |

---

## 15. Responsividad, accesibilidad y UX transversal

| ID | Prio | Pasos | Resultado esperado |
|----|------|-------|--------------------|
| UX-01 | P0 | Recorrer todas las páginas en móvil (360px de ancho). | Sin overflow horizontal; bottom-nav visible; sidebar colapsa. |
| UX-02 | P1 | Tablas anchas (WorkerDetail historial) en móvil. | Scroll horizontal contenido, no rompe el layout. |
| UX-03 | P1 | Modales (nuevo proyecto/trabajador, asignar, importar). | Cierran con Esc y con click fuera; scroll interno si son largos; bottom-sheet en móvil. |
| UX-04 | P1 | Tap targets de botones/inputs ≥44px en móvil. | Cómodos de tocar. |
| UX-05 | P1 | Estados de carga y vacío en cada listado. | Skeleton al cargar; mensaje claro si no hay datos. |
| UX-06 | P1 | Mensajes de error de API. | Legibles en español (no JSON crudo ni stack traces). |
| UX-07 | P2 | Notch / safe-area en móviles con muesca. | Contenido no tapado por la barra del sistema. |
| UX-08 | P2 | Toasts (Sonner) no se apilan infinitamente ni tapan acciones. | Se ven y desaparecen bien. |

---

## 16. Robustez, rendimiento y casos borde

| ID | Prio | Pasos | Resultado esperado |
|----|------|-------|--------------------|
| RBT-01 | P1 | Página inexistente (`/app/ruta-rara`). | 404 amigable o redirección, no pantalla en blanco. |
| RBT-02 | P1 | Comentarios/notas muy largos (varios miles de caracteres). | Se guardan y muestran sin romper el layout. |
| RBT-03 | P1 | Org con muchos trabajadores (≥500) y evaluaciones. | Listas paginadas responden en tiempo razonable; sin congelamientos. |
| RBT-04 | P1 | Doble click rápido en "Guardar" (proyecto/trabajador/evaluación). | No crea registros duplicados (botón se deshabilita al enviar). |
| RBT-05 | P1 | Pérdida de conexión a mitad de una request normal (no offline-eval). | Error manejado; permite reintentar; no deja la UI en estado inconsistente. |
| RBT-06 | P2 | Zona horaria / fechas relativas ("hace 2 horas"). | Coherentes con la hora local del usuario. |
| RBT-07 | P2 | Números/decimales con locale (coma vs punto). | Consistentes en toda la app. |
| RBT-08 | P1 | Recargar (F5) en rutas profundas (`/app/workers/:id`, `/p/:token`). | Carga directa funciona (deep-link), no 404 del servidor. |

---

## 17. Smoke test final en PRODUCCIÓN (antes de anunciar)

> Recorrido rápido end-to-end en `https://recontrata.cl`. Todo debe pasar.

| ID | Prio | Verificación |
|----|------|--------------|
| SMK-01 | P0 | `https://recontrata.cl` y `https://www.recontrata.cl` cargan con HTTPS válido y `<title>Recontrata</title>`. |
| SMK-02 | P0 | Sign-up + Sign-in reales funcionan; **sin banner dev de Clerk**. |
| SMK-03 | P0 | Crear org → crear proyecto → crear trabajador → asignar → evaluar → ver en dashboard. Flujo completo sin errores. |
| SMK-04 | P0 | Generar portal-link → abrir `/p/{token}` en ventana incógnito → ver perfil → responder una evaluación. |
| SMK-05 | P0 | Modo offline en móvil real: evaluar sin señal → reconectar → sincroniza. |
| SMK-06 | P0 | Consola del navegador sin errores rojos en el recorrido. |
| SMK-07 | P0 | No hay rastros de "FaenaScore"/"faena" en ninguna pantalla visible. |
| SMK-08 | P1 | `GET /health` = ok. Endpoint `/admin/seed-demo` protegido. |
| SMK-09 | P1 | Borrar los datos de prueba creados en prod durante el smoke (no dejar basura). |

---

## Resumen de áreas de mayor riesgo reputacional (foco P0)

1. **Fuga de datos entre organizaciones** (sección 2) — lo más grave posible.
2. **Cálculo de puntaje incorrecto** (sección 5) — destruye la credibilidad del producto.
3. **Banner "development mode" de Clerk visible en prod** (AUTH-05) — se ve poco serio.
4. **Pérdida de evaluaciones hechas offline** (sección 6) — rompe la promesa central de "evalúa sin señal".
5. **Portal del trabajador / derecho a réplica fallando** (sección 7) — riesgo legal (Ley 21.719) y de reputación.
6. **Restos de marca "FaenaScore"/"faena" visibles** (LND-02, SMK-07) — inconsistencia de marca en el lanzamiento.

---

_Generado para QA de lanzamiento. Marca cada prueba al ejecutarla y registra los bugs encontrados (ID de prueba + descripción + severidad)._
