# Tutoriales en video de Recontrata — plan pedagógico y producción

Serie de **clips cortos (1–2 min)**, uno por objetivo, que enseñan a usar Recontrata
*tal como está construido hoy*. Diseño y pipeline calcados del tutorial de CasiListo
(`Proyectos Claude Code/Fillanyform/tutorial/`), que ya está probado y aprobado.

## Enfoque pedagógico (principios)

1. **Un clip, un objetivo.** Cada video deja al espectador capaz de hacer **una** cosa.
2. **Mostrar, no contar.** Se graba el flujo **real** en `recontrata.cl`; la voz
   acompaña la acción (sincronía narración↔pantalla ≈ 1:1).
3. **Del problema al alivio.** Cada clip arranca con el dolor concreto del usuario
   (faena, terreno, recontratar a quien ya falló) y muestra cómo Recontrata lo resuelve.
4. **Voz cálida y cercana**, español latino/chileno neutro, **sin tecnicismos** ni
   jerga. Sin voseo.
5. **Honestidad.** No se sobre-promete ("te ayuda a decidir", no "elige por ti";
   "la mayoría de los campos", no "siempre perfecto").
6. **Continuidad.** Intro de marca al abrir, outro con CTA al cerrar, y un teaser
   **"Siguiente:"** que enlaza con el próximo clip (la serie cuenta una historia).
7. **Pensado para el público real:** el supervisor de terreno (clips de uso) y el
   dueño/administrador del contrato (clips de decisión y confianza).

## Estructura de cada guion (`guiones/clipN.md`)

```
# Clip N — Título
- Duración objetivo / Objetivo pedagógico / Voz / Público
## Escena X — nombre (rango de tiempo)
**EN PANTALLA**: qué se ve / qué hace el cursor.
**CALLOUT**: texto sobreimpreso (si aplica).
**NARRACIÓN**: el texto exacto de la voz en off.
```

## La serie (7 clips + 1 opcional)

| # | Clip | Objetivo | Público |
|---|---|---|---|
| 1 | Bienvenida y tu cuenta | Entender qué resuelve Recontrata y crear la cuenta | Dueño/Admin |
| 2 | Trae tu gente | Cargar trabajadores (uno a uno e importando Excel/CSV) | Admin |
| 3 | Crea tu faena | Crear un proyecto y asignarle trabajadores | Admin |
| 4 | Evalúa en terreno, en 30 segundos | Evaluar 5 dimensiones + recontratación, encadenar | Supervisor |
| 5 | ¿Sin señal? Igual evalúas | Usar el modo terreno offline y la sincronización | Supervisor |
| 6 | Decide con datos | Dashboard, historial, score ponderado y la fórmula | Admin |
| 7 | Transparencia y confianza | Portal del Trabajador (réplica, certificado) | Admin |
| 8 (opc.) | Evaluaciones más justas | Calibración de evaluadores (anti-sesgo) | Admin |

Arco narrativo: **preparar** (1–3) → **usar en terreno** (4–5) → **decidir** (6) →
**confianza/transparencia** (7) → **avanzado** (8).

## Cómo producirlos (pipeline reutilizable de CasiListo)

El tutorial de CasiListo automatiza: **captura** del flujo real con Playwright →
**narración** con voz IA (OpenAI `gpt-4o-mini-tts`, voz *alloy* con acento latino) →
**ensamblado** con ffmpeg (intro/outro de marca, cursor resaltado, zoom, callouts o
subtítulos). Scripts: `00_login.py` (sesión), `01_capture.py` (screencast por escena,
dict `CLIPS`), `02_tts.py` (audio por escena), `03_assemble.py` (mezcla + subtítulos).

Para Recontrata se reutiliza ese pipeline adaptando:
- **Marca:** logo/colores de Recontrata (azul `#2563eb`), no violeta CasiListo.
- **Sesión/seed:** `recontrata.cl` está tras gate `recontrata2211` + Clerk; los clips
  necesitan una **organización demo con datos** (trabajadores, un proyecto, alguna
  evaluación) para grabar un flujo realista. Sembrar antes de capturar.
- **Checklist (heredado, respetar en cada clip):** esperar render antes de grabar (sin
  spinner "Cargando…"); limpiar campos autocompletados antes de tipear; callouts que no
  tapen botones; narración honesta; grabar contra la app en producción.
- **Móvil:** los clips 4 y 5 (terreno) se ven mejor en **viewport de teléfono (375px)**,
  que es como se usa de verdad; los de oficina (1, 6, 7) en escritorio.

## Estado

- ✅ **Guiones** de los 7 clips + el opcional — en `guiones/`. (Esta entrega.)
- ⬜ Producción de los MP4 — pendiente: requiere marca aplicada + organización demo
  sembrada + correr el pipeline. (Trabajo siguiente, reutiliza los scripts de CasiListo.)
