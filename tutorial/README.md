# Tutoriales en video de Recontrata — guía de producción

Serie de **clips cortos (1–2 min)**, uno por objetivo, que enseñan a usar Recontrata
*tal como está construido hoy*. Cada clip se genera de forma **reproducible** con un
script Python por clip (`scripts/produce_clipN.py`) que orquesta voz IA, captura del
producto, tarjetas de marca y ensamblado con ffmpeg.

> **Estado (22 jun 2026):** Clip 1 **aprobado por Germán**, Clip 2 **producido**.
> Clips 3–7 pendientes. Ver la tabla de [Estado](#estado) al final.

---

## 1. Enfoque pedagógico (principios)

1. **Un clip, un objetivo.** Cada video deja al espectador capaz de hacer **una** cosa.
2. **Mostrar, no contar.** Se graba el flujo **real** del producto; la voz acompaña la
   acción.
3. **Del problema al alivio.** Cada clip arranca con el dolor concreto del usuario y
   muestra cómo Recontrata lo resuelve.
4. **Voz cálida y cercana**, español latino/chileno neutro, **sin tecnicismos** ni
   voseo.
5. **Honestidad.** No se sobre-promete.
6. **Continuidad.** Intro de marca al abrir, outro con CTA al cerrar, y un teaser
   **"Siguiente:"** que enlaza con el próximo clip.
7. **Subtítulos VERBATIM:** el texto en pantalla es **exactamente** lo que dice el
   narrador (lo exige Germán y lo valida el código). Nada de paráfrasis.

---

## 2. La serie (7 clips + 1 opcional)

| # | Clip | Objetivo | Público | Estado |
|---|---|---|---|---|
| 1 | Bienvenida y tu cuenta | Qué resuelve Recontrata + crear la cuenta | Dueño/Admin | ✅ aprobado |
| 2 | Trae tu gente | Cargar trabajadores (uno a uno + importar Excel) | Admin | ✅ producido |
| 3 | Crea tu faena | Crear un proyecto y asignarle trabajadores | Admin | ⬜ pendiente |
| 4 | Evalúa en terreno, en 30 segundos | Evaluar 5 dimensiones + recontratación | Supervisor | ⬜ pendiente |
| 5 | ¿Sin señal? Igual evalúas | Modo terreno offline + sincronización | Supervisor | ⬜ pendiente |
| 6 | Decide con datos | Dashboard, historial, score ponderado, fórmula | Admin | ⬜ pendiente |
| 7 | Transparencia y confianza | Portal del Trabajador (réplica, certificado) | Admin | ⬜ pendiente |
| 8 (opc.) | Evaluaciones más justas | Calibración de evaluadores (anti-sesgo) | Admin | ⬜ opcional |

Arco: **preparar** (1–3) → **usar en terreno** (4–5) → **decidir** (6) →
**confianza** (7) → **avanzado** (8).

Los guiones de los 8 están en `guiones/clipN.md` (formato: objetivo, público, y por
escena `EN PANTALLA` / `CALLOUT` / `NARRACIÓN`).

---

## 3. Arquitectura del pipeline

Todo vive en `tutorial/`:

```
tutorial/
├─ guiones/            clipN.md  (guion narrativo por clip)
├─ scripts/
│  ├─ brand.py         identidad común: colores, fuentes, voz TTS, rutas, ffmpeg, openai_key()
│  ├─ produce_clip1.py productor del Clip 1 (landing pública + B-roll)
│  ├─ produce_clip2.py productor del Clip 2 (dashboard autenticado vía mock)
│  └─ openai_key.txt   clave OpenAI (GITIGNORED, no se sube; recrear tras cambiar de PC)
├─ assets/
│  ├─ broll/           video de stock (Pexels, licencia libre)
│  └─ demo/            Excel demo para la importación del Clip 2
└─ output/             clipN.mp4 + intermedios (raw/, audio/, *.srt) — gitignored
```

Cada `produce_clipN.py` tiene **4 etapas** (se corren con `python produce_clipN.py <etapa>`):

| Etapa | Qué hace | Salidas |
|---|---|---|
| `tts` | Narra cada escena con OpenAI `gpt-4o-mini-tts` (voz *alloy*, acento latino) y mide su duración | `output/audio/clipN_escX.mp3`, `clipN_durations.json` |
| `capture` | Graba el flujo real con Playwright (cursor azul inyectado, gate `recontrata2211` saltado), un `.webm` por escena. Mide el "blanco" de carga de cada escena | `output/raw/clipN_escX.webm`, `clipN_leads.json` |
| `cards` | Genera tarjetas de marca (intro/outro) con Pillow | `output/clipN_intro_title.png`, `clipN_outro.png` |
| `assemble` | Ensambla con ffmpeg: intro animado + escenas (con recorte de blanco) + outro, subtítulos quemados, concat uniforme | `output/clipN.mp4` |
| `all` | Las cuatro en orden | |

> **Importante:** `capture` regraba contra la app, así que requiere que la app esté
> disponible (prod para Clip 1; **dev server local** para los clips de dashboard, ver §6).
> Los intermedios (`raw/`, `audio/`, `*_durations.json`, `*_leads.json`) están
> **gitignored** y **no sobreviven** a un cambio de PC → para regenerar un clip hay que
> correr de nuevo desde `tts`/`capture`.

---

## 4. Requisitos (entorno)

- **Python 3.12** con: `openai`, `playwright` (+ Chromium: `python -m playwright install chromium`),
  `pillow`, `openpyxl`. (`pip install openai playwright pillow openpyxl`)
- **ffmpeg / ffprobe** (vía winget; `brand._find` los localiza solo).
- **Clave OpenAI** en `scripts/openai_key.txt` (solo el valor `sk-...`) o env var
  `OPENAI_API_KEY`. El archivo está gitignored y **no viaja en el repo ni en el respaldo
  de `.env`** → recrearlo tras restaurar/cambiar de PC (se reutiliza la clave de
  Fillanyform/CasiListo, misma cuenta de Germán). Leer `**/.env` es bloqueo duro del
  harness, por eso la clave va en este `.txt` aparte.
- **Node + frontend** instalado (`frontend/node_modules`) para los clips de dashboard.

---

## 5. Técnicas y decisiones de marca (afinadas en el Clip 1)

Estas valen para **todos** los clips:

- **Intro = logo animado CON sonido.** Se usa `branding/logo-animado/output/recontrata_intro_sound.mp4`
  (la flecha de retorno se traza + sonic logo, 4 s). Se superpone sobre una tarjeta de
  título cuyo fondo se iguala a **`#F7F8FB`** (el del video) para que no se vea un
  recuadro. **Sin fade a negro:** la animación termina y el logo queda **estático** hasta
  el corte (un fade causaba un parpadeo oscuro).
- **Subtítulos VERBATIM.** `SUBS` debe concatenar exactamente a `SCENES`; lo verifica
  `_check_subs()` (aborta el render si no coincide). Estilo ffmpeg: `FontSize=16`,
  `MarginV=24` (bajo, rozando el borde), `BackColour=&H66000000` (caja ~60 % opaca para
  leer sobre fondos brillantes), `BorderStyle=4`, `Alignment=2`. Timing por proporción de
  caracteres (aproximado; si llegara a desincronizar, alinear con Whisper).
- **Recorte del "blanco" de carga.** Cada escena mide `lead` (tiempo hasta el primer
  render) y el ensamblado hace `-ss lead` para que la narración **nunca** corra sobre
  pantalla en blanco.
- **B-roll de stock (Pexels) sin API key.** `curl -L "https://www.pexels.com/download/video/<ID>/"`
  redirige al CDN; variante HD: `https://videos.pexels.com/video-files/<ID>/<ID>-hd_1920_1080_<fps>fps.mp4`
  (probar 30/25/24 fps). Licencia libre, uso comercial. Guardar en `assets/broll/`.
  **Cuidado con la autenticidad:** Germán rechaza lo que no parezca minería chilena árida
  o sin EPP. Usado: `mina_drone.mp4` (tajo abierto, Pexels 8382429). Disponible sin usar:
  `trabajador.mp4` (8964296).

---

## 6. El patrón clave: capturar el DASHBOARD AUTENTICADO (clips 2–7)

La landing es pública, pero el producto está tras Clerk (login real) y **no se puede
grabar logueado en producción**. Solución, probada en el Clip 2:

1. **Correr el frontend en modo demo local:**
   ```bash
   cd frontend && npm run dev      # sirve en http://localhost:5173
   ```
   `frontend/.env` ya trae `VITE_AUTH_MOCK_ENABLED=true` → `clerkEnabled=false` y la app
   monta `/app/*` **sin login**.
2. **Interceptar la API con datos demo** desde Playwright:
   `ctx.route("**/api/v1/**", handler)`. El handler es **STATEFUL** (una lista de
   trabajadores en un dict mutable): `GET .../workers` devuelve el estado actual,
   `POST .../workers` agrega uno, `POST .../workers/import` agrega varios. Así el video
   muestra la lista creciendo de verdad (vacía → 1 → 8).
3. **Una escena = un contexto nuevo sembrado** con el estado inicial correcto
   (`SCENE_INITIAL` en `produce_clip2.py`), para que el orden del ensamblado sea limpio.

Endpoints mínimos a mockear: `GET /me` (perfil con `organizations[].org_id/org_name`),
`GET .../dashboard/{stats,top-workers,recent-evaluations,next-evaluation,projects-pending}`,
y los de `workers`. Las formas JSON exactas están en `produce_clip2.py` (`_make_handler`).

**Gotchas aprendidos:**
- La página Trabajadores renderiza **tabla de escritorio + card móvil oculta**. Un
  `wait_for_selector("text=Nombre")` se cuelga esperando que el duplicado oculto sea
  "visible". → Esperar a que el **modal se cierre** (`input[placeholder='12.345.678-9']`
  pase a `detached`), no al texto.
- El **RUT debe ser válido** (la app valida el dígito verificador). `produce_clip2._rut_dv/_rut_fmt`
  lo calculan; las especialidades salen de `src/lib/constants.ts` (`SPECIALTIES`).
- El Excel de importación se genera con openpyxl en `assets/demo/`.

Los clips de **evaluación (4–7)** necesitarán además mockear proyectos + evaluaciones +
scores en el handler (no solo workers).

---

## 7. Cómo producir / regenerar un clip

```bash
# 0. (clips de dashboard) levantar el dev server
cd frontend && npm run dev

# 1. asegurar la clave OpenAI
#    scripts/openai_key.txt  con el valor sk-...   (o export OPENAI_API_KEY=...)

# 2. producir
cd tutorial/scripts
python produce_clip2.py all        # tts + capture + cards + assemble
#   o por etapas para iterar rápido:
python produce_clip2.py assemble   # reusa audio/captura ya en disco

# 3. resultado
#    tutorial/output/clip2.mp4
```

Para **iterar solo el ensamblado** (cambiar subtítulos, intro, ritmo) no hace falta
re-grabar ni re-narrar: basta `assemble` si `output/raw/`, `output/audio/` y los
`*_durations.json`/`*_leads.json` siguen en disco.

---

## 8. Estado

- ✅ **Guiones** de los 7 + opcional — en `guiones/`.
- ✅ **Clip 1** (`output/clip1.mp4`, ~61 s) — **aprobado por Germán** (22 jun 2026).
  Intro animado+sonido, B-roll de mina en el bloque del problema, subtítulos verbatim.
- ✅ **Clip 2** (`output/clip2.mp4`, ~57 s) — producido (22 jun 2026). Dashboard
  autenticado vía dev server mock + interceptación stateful. Org demo "Constructora
  Andes", 8 trabajadores. *Pendiente menor:* en esc4 la importación termina antes que la
  narración; se puede repartir mejor el ritmo.
- ⬜ **Clips 3–7** — pendientes. Reutilizan `produce_clip2.py` como base (mismo patrón de
  dashboard mock); los de evaluación requieren ampliar el mock con proyectos/evaluaciones.

> Antes de abrir los tutoriales al público hay un pendiente humano del producto: probar
> login real en `recontrata.cl/sign-up` y luego quitar el gate `recontrata2211` + el
> `noindex` (ver `PROGRESS.md`).
