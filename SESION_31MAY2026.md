# Sesión 31 may 2026 — Recontrata: branding, intro animada, copy y hero

Continuación del rebrand **FaenaScore → Recontrata** (ver `SESION_30MAY2026.md`).
Todo lo de abajo está **deployado y verificado en producción** (https://recontrata.cl).
Último commit master: `3777016`.

---

## Qué se hizo (en orden)

1. **Logo animado — punta de flecha corregida**
   - El video del logo (`branding/logo-animado/animate_logo.py`) dibujaba la flecha a mano y la punta salía "hacia afuera".
   - Fix: rasterizar el SVG real de Lucide `rotate-ccw` con **`resvg-py`** y animar el trazado por barrido angular polar. Punta correcta (retorno).
   - El `index.html` web y `logo-recontrata.svg` ya estaban bien.

2. **Sonic logo** — `branding/logo-animado/add_sound.py`
   - Audio sintetizado (numpy/scipy, sin samples), muxeado con ffmpeg.
   - Whoosh → shimmer → arpegio de campanas → acorde Do mayor + reverb.
   - Ajustado por feedback: balanceado intro/cierre, cola corta (no "trompeta sostenida"), volumen bajado (~−6 dB).
   - Salidas: `output/recontrata_sonic.wav`, `recontrata_intro_sound.mp4` (+ dark).

3. **Set de assets de marca** — `branding/gen_brand_assets.py` (resvg + Pillow, reproducible)
   - Reemplaza el favicon morado viejo por el ícono Recontrata.
   - Genera: `favicon.svg/.ico`, `apple-touch-icon`, `icon-192/512`, `icon-maskable-512`, `og-image.png` (1200×630), `manifest.webmanifest`.
   - `index.html` cableado: favicons, manifest, theme-color, Open Graph + Twitter Card, `lang="es"`.

4. **Intro animada en la landing** (patrón "video splash" de CasiListo)
   - **Splash en `index.html`** (antes de React): `<video id="boot-video" src="/logo-intro.mp4" autoplay muted playsinline>`. Script inline revisa `sessionStorage('recontrata_intro_seen')` + `prefers-reduced-motion`.
   - **`BootIntro`** (`src/components/brand/LogoIntro.tsx`): al terminar el video (o skip click/scroll/tecla, o safety 5s) hace el **magic-move** — clona el logo y lo vuela al `#nav-logo` del navbar con `getBoundingClientRect()` real. Montado en **App root** (no solo Landing) para que el splash se quite en todas las rutas.
   - MP4 web: `branding/logo-animado/make_logo_intro_web.py` (fondo **blanco puro** = rectángulo invisible; mudo; ~70KB).
   - Ajustes por feedback: clon centrado exacto sobre el navbar; splash más chico; teléfono del hero más grande.

5. **Copy de marketing** (`src/pages/Landing.tsx`)
   - **Hero A**: "Deja de recontratar / al que ya te falló" + subhead benefit-led ("equipo A").
   - Bloque problema: nombra el costo del mal trabajador (retrabajo, días, **seguridad/accidente**).
   - Feature cards giradas a beneficio; fuera "mobile-first".
   - **Quitada la palabra "faena"** de todo lo visible → proyecto/terreno/personal. Foco Chile (CLP).

6. **Hero visual**
   - **Mock del celular** con la pantalla de evaluación REAL replicada (sin levantar backend): `branding/landing-hero/eval_mock.html` (Tailwind CDN, datos demo) → `render_mock.py` (captura móvil) → `make_phone.py` (frame de teléfono) → `phone-eval.png`.
   - **Dashboard-preview** debrandeado (decía "FaenaScore" → "Recontrata", editado con PIL) y movido a su sección "Y todo se ordena en un solo panel".
   - **Foto del hero**: terminó en **solo paisaje de mina a cielo abierto** (Pexels ID 2892618), sin persona, tras varias iteraciones de feedback.

---

## Archivos clave

| Qué | Dónde |
|---|---|
| Landing (copy + hero + secciones) | `frontend/src/pages/Landing.tsx` |
| Intro (BootIntro + splash) | `frontend/src/components/brand/LogoIntro.tsx` + `frontend/index.html` |
| BootIntro montado | `frontend/src/App.tsx` (ambos branches) |
| Assets en prod | `frontend/public/` (logo-recontrata.png, logo-intro.mp4, hero-faena.jpg, phone-eval.png, favicon*, icon*, og-image.png, manifest.webmanifest, dashboard-preview.png) |
| Generadores reproducibles | `branding/gen_brand_assets.py`, `branding/logo-animado/*.py`, `branding/landing-hero/*` |

---

## Pendiente

**Clerk a producción** (único real) — quitar el banner "development mode":
- Crear instancia de **producción** en el dashboard de Clerk.
- Copiar prod keys (`pk_live_*`); setear `VITE_CLERK_PUBLISHABLE_KEY` en Railway (es build-arg del Dockerfile).
- Agregar `recontrata.cl` + `www` a orígenes/allowed en Clerk prod; configurar dominio/DNS de Clerk si pide CNAMEs.
- Requiere acceso de Germán al dashboard de Clerk.

Opcional/cosmético: renombrar repo y servicio Railway de `faenascore-*` a `recontrata-*`.

---

## Trampas de deploy (importante)

- **Deploy**: sin autodeploy desde GitHub. `railway up --detach` desde la raíz (ya linkeado a project/service `faenascore`).
- **Bundle hash prod ≠ local**: el Docker compila CON Clerk (build-arg), el build local sin Clerk → hashes/tamaños distintos. Para verificar el deploy, pollear el **origin directo** `faenascore-production.up.railway.app` o un string del código nuevo, NO el hash del build local.
- **Cache de Cloudflare por tipo**:
  - `index.html` = `cf-cache DYNAMIC` → NO se cachea, no requiere purge.
  - Assets estáticos (`.png/.jpg/.svg/.ico`, `max-age=14400`) SÍ se cachean. Al **cambiar uno con el mismo nombre**, purgar esa URL en Cloudflare (Caching → Configuration → Custom Purge → URL) o Purge Everything. Assets nuevos (nombre que no existía) no necesitan purge.
- **Verificación**: Playwright Python headless. Video autoplay headless: `--autoplay-policy=no-user-gesture-required --mute-audio`. Saltar la intro: context `reduced_motion='reduce'`.
