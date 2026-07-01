# Sesión 1 jul 2026 — Feedback de Joanna (tester beta) + canal de marca en YouTube

Resolución completa del feedback de **Joanna** sobre el beta de Recontrata. Se
cerraron los **6 ajustes** pedidos y todo quedó **desplegado en producción**
(recontrata.cl). Además se creó el canal de marca de YouTube "Recontrata" y se
resubieron los 9 tutoriales.

Ver también: `SESION_26JUN2026_QA.md`, `QA_RESULTADOS.md`, `ESTUDIO_PRECIOS_INVERSOR.md`.

---

## 1. Feedback recibido

**Positivo (8):** visual limpio/ordenado · claridad del pitch antes de entrar ·
todos los botones OK · videos reproducen bien y a buena velocidad · cada paso se
entiende (muy amigable) · el correo con el código llega al instante · restablecer
contraseña sin problemas · descarga el Excel correctamente.

**Ajustes pedidos (6):**
1. Redacción de la landing: (a) "repetir a tus mejores" → especificar
   trabajadores; (b) mejorar "con datos reales, no memoria ni WhatsApp".
2. La sección "Sin señal" habla de la mina → suena a app solo de minería; ampliar.
3. Los videos cuelgan del YouTube personal de Germán; debería haber un canal de
   Recontrata con su logo.
4. Reordenar las pestañas del sidebar en el orden del proceso.
5. Tras evaluar, el botón "generar enlace" del portal lleva a una página con el
   logo de Recontrata y nada más.
6. En "Fórmula del puntaje", cambiar el tipo de industria carga lento.

---

## 2. Qué se hizo (por punto)

### Punto 5 — BUG del portal en blanco (causa raíz)
**Síntoma:** el enlace del Portal del Trabajador (`/p/:token`) mostraba solo el logo.
**Causa:** el `#boot-splash` de `frontend/index.html` (video del logo, `z-index:60`,
`position:fixed inset-0`) se auto-retira por el script inline **solo si el usuario
NO tiene el código de acceso**. Si lo tiene (un tester que desbloqueó con
`recontrata2211`), se espera que **React/BootIntro** lo retire — pero el portal está
**fuera del `GateLayout`** y no renderiza `BootIntro`, así que nadie quitaba el
splash y quedaba tapando la página para siempre.
**Fix:** en `frontend/index.html`, el script inline ahora también retira el splash
cuando `window.location.pathname` empieza con `/p/` (el portal es público y nunca
muestra el intro de marca).

### Punto 4 — Reorden de pestañas por flujo
`frontend/src/components/layout/AppShell.tsx` → `navItems` reordenado a
**Trabajadores → Proyectos → Evaluar → Dashboard** (Dashboard al final). Afecta el
sidebar de escritorio y la bottom-nav móvil. La landing tras login sigue siendo
Dashboard (`/app`, ruta index).

### Punto 6 — Transición lenta al cambiar industria
`frontend/src/pages/ScoreFormula.tsx` → `changeIndustry` hacía `updateOrg` + `load()`,
que reponía `loading=true` (parpadeo del esqueleto) y re-consultaba todo. Ahora es
**optimista**: como los pesos de cada perfil ya están en el cliente
(`formula.profiles`), el cambio se refleja al instante y el servidor se confirma con
un **refresco silencioso** en segundo plano (sin esqueleto), con **revert** si el
servidor rechaza el cambio.

### Puntos 1 y 2 — Copy de la landing
`frontend/src/pages/Landing.tsx`:
- Hero: "…repetir a tus **mejores trabajadores**…" y "…con datos reales, **no con
  recuerdos ni mensajes de WhatsApp**".
- Card offline: "En faena **—una obra, una mina o cualquier lugar remoto—**…"
  (antes "En la mina…"), consistente con la decisión pan-LATAM.

### Punto 3 — Canal de marca en YouTube
No se puede quitar la atribución "German Saltrón" de un video ya subido (el video
pertenece al canal que lo subió). Solución aplicada: **canal de marca (Brand
Account) "Recontrata"** (@Recontrata, foto = isotipo azul) bajo gsaltron@gmail.com;
se resubieron los 9 clips como "No listado" y se actualizó `tutorials.ts`.

---

## 3. Archivos modificados

| Archivo | Cambio |
|---|---|
| `frontend/index.html` | retira el splash en rutas `/p/` (fix portal) |
| `frontend/src/components/layout/AppShell.tsx` | reorden de `navItems` por flujo |
| `frontend/src/pages/ScoreFormula.tsx` | cambio de industria optimista + refresco silencioso |
| `frontend/src/pages/Landing.tsx` | copy hero + card offline |
| `frontend/src/lib/tutorials.ts` | 9 `youtubeId` → canal de marca Recontrata |

---

## 4. Commits (rama `master`, repo `germansaltron/Recontrata`)

- `3fc05c9` docs(qa): add launch QA plan, results and core-flow integration tests
- `246e993` fix(beta): address Joanna's tester feedback (5 items)
- `895cee6` chore(tutorials): point all 9 clips to the Recontrata brand channel

---

## 5. Deploy y verificación

- Deploy: `railway up --detach` al proyecto **`faenascore`**
  (ID `7ec526bb-74bc-4796-bac4-4c89bde2d6bd`, service `a5ff98e5`), sirve recontrata.cl.
- `npx tsc --noEmit` verde en cada tanda.
- Verificado en prod: `index.html` con el guard `isPortal`; root HTTP 200;
  `/api/health` = `database: connected`; ID nuevo `M4AhheIygzY` presente en el chunk
  `TutorialModal-*.js`.
- Los 9 IDs de YouTube verificados vía oEmbed (títulos correctos, embebibles).

**IDs nuevos (canal Recontrata):**
1 `M4AhheIygzY` · 2 `B4ilbXCJWFY` · 3 `mWKc2o1gumY` · 4 `alQxbKS1SyA` ·
5 `wky0-cgphlo` · 6 `MaSrm595J_g` · 7 `RUxK-zv5CbE` · 8 `XOJkZ_KeXnI` · 9 `Q1wwOXHARVQ`

---

## 6. Recursos generados (fuera del repo)

- `Desktop\Recontrata_YouTube_perfil_800.png` — foto de perfil (isotipo azul, 800×800, a sangre).
- `Desktop\Recontrata_YouTube_banner_2048x1152.png` — banner (logo + bajada "Evalúa el desempeño. Recontrata con datos.").
- `Desktop\Recontrata_YouTube_titulos_descripciones.txt` — títulos y descripciones de los 9 tutoriales.
- `Downloads\Videos Recontrata\` — los 9 videos ordenados (01–09) usados para resubir.

---

## 7. Pendientes / notas

- El **Tutorial 3** en pantalla/audio aún puede decir "faena" (se grabó antes del
  cambio pan-LATAM a "obra"); el título y el nombre de archivo ya dicen "obra".
  Opcional: re-renderizar el clip.
- Los clips **viejos** siguen en el canal personal de Germán; se pueden dejar
  privados o borrar.
- Banner del canal: subir en YouTube Studio → Personalización → Marca.
- Réplica del mismo paquete para **Casilisto** (canal de marca + assets + 6
  tutoriales del repo Fillanyform) queda como siguiente tarea.
