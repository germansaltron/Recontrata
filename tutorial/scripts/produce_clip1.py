"""Produce el Clip 1 de Recontrata (Bienvenida y tu cuenta).

Pipeline autocontenido calcado del de CasiListo:
  tts      -> narra escenas 2,3,4 (OpenAI gpt-4o-mini-tts) + mide duraciones
  capture  -> graba un webm por escena con Playwright (cursor inyectado, gate)
  cards    -> tarjetas de intro/outro de marca (PIL)
  assemble -> ensambla con ffmpeg (escenas sincronizadas + subtítulos + cards)
  all      -> todo en orden

Uso:  python produce_clip1.py [tts|capture|cards|assemble|all]
"""
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

import brand

SITE = f"https://{brand.SITE}/"
DUR_FILE = brand.OUTPUT_DIR / "clip1_durations.json"
LEAD_FILE = brand.OUTPUT_DIR / "clip1_leads.json"   # blanco a recortar por escena de UI
OUT = brand.OUTPUT_DIR / "clip1.mp4"
# Intro = logo animado con sonido (el ciclo se cierra), generado en branding/logo-animado.
INTRO_VIDEO = (brand.REPO_DIR / "branding" / "logo-animado" / "output"
               / "recontrata_intro_sound.mp4")
# B-roll de stock (Pexels, licencia libre) para el bloque del problema (esc2).
BROLL_DIR = brand.TUTORIAL_DIR / "assets" / "broll"
BROLL_SCENES = {"esc2": "mina_drone.mp4"}   # esc2 = B-roll en vez de captura de pantalla
W, H = brand.VIDEO_W, brand.VIDEO_H

# Narración por escena (del guion guiones/clip1.md). Esc 1 y 5 son tarjetas de marca.
SCENES = {
    "esc2": "En cada faena hay gente que marca la diferencia… y gente que no debería "
            "volver. Pero cuando arranca el próximo proyecto, esa información vive en la "
            "memoria del supervisor y en cadenas de WhatsApp. Y reemplazar a un mal "
            "operario cuesta más de un millón y medio de pesos.",
    "esc3": "Recontrata convierte ese conocimiento en datos. Evalúas a tu gente en "
            "terreno, en segundos, y cada trabajador acumula un historial real a través "
            "de tus proyectos. Así, la próxima vez, recontratas a tus mejores con datos, "
            "no con memoria.",
    "esc4": "Para empezar solo necesitas una cuenta. Regístrate con tu correo: te llega "
            "un enlace, haces clic y entras. No hay que instalar nada. Recontrata "
            "funciona desde el navegador del celular o del computador.",
}
ORDER = ["esc2", "esc3", "esc4"]

# Subtítulos: trozos VERBATIM de SCENES (cada lista, concatenada, == lo narrado).
# Solo se parte en líneas legibles; NO se parafrasea. Lo valida _check_subs().
SUBS = {
    "esc2": [
        "En cada faena hay gente que marca la diferencia… y gente que no debería volver.",
        "Pero cuando arranca el próximo proyecto, esa información vive en la memoria del supervisor y en cadenas de WhatsApp.",
        "Y reemplazar a un mal operario cuesta más de un millón y medio de pesos.",
    ],
    "esc3": [
        "Recontrata convierte ese conocimiento en datos.",
        "Evalúas a tu gente en terreno, en segundos,",
        "y cada trabajador acumula un historial real a través de tus proyectos.",
        "Así, la próxima vez, recontratas a tus mejores con datos, no con memoria.",
    ],
    "esc4": [
        "Para empezar solo necesitas una cuenta.",
        "Regístrate con tu correo: te llega un enlace, haces clic y entras.",
        "No hay que instalar nada.",
        "Recontrata funciona desde el navegador del celular o del computador.",
    ],
}


def _check_subs():
    """Garantiza que los subtítulos sean EXACTAMENTE lo narrado (verbatim)."""
    squash = lambda s: "".join(s.split())
    for name in ORDER:
        if squash(" ".join(SUBS[name])) != squash(SCENES[name]):
            raise SystemExit(
                f"SUBS[{name}] no coincide con SCENES[{name}] (deben ser verbatim).")

INTRO_SECS = 4.0   # = duración del intro animado con sonido
OUTRO_SECS = 6.0

# add_init_script: desbloquea el gate de pre-lanzamiento + dibuja un cursor visible
# (Playwright no graba el cursor real del mouse).
INIT_JS = """
try {
  localStorage.setItem('recontrata_access', String(Date.now() + 7776000000));
  sessionStorage.setItem('recontrata_intro_seen','1');
} catch(e){}
window.addEventListener('DOMContentLoaded', () => {
  const c = document.createElement('div');
  c.id = '__cur';
  c.style.cssText = 'position:fixed;width:24px;height:24px;border-radius:50%;'+
    'background:rgba(37,99,235,.45);border:2px solid #fff;box-shadow:0 0 8px rgba(0,0,0,.45);'+
    'z-index:2147483647;pointer-events:none;transform:translate(-50%,-50%);left:0;top:0;display:none';
  document.documentElement.appendChild(c);
  addEventListener('mousemove', e => {
    c.style.display='block'; c.style.left=e.clientX+'px'; c.style.top=e.clientY+'px';
  }, true);
});
"""


def sh(cmd):
    subprocess.run(cmd, check=True)


def dur_of(path):
    out = subprocess.check_output([
        brand.FFPROBE, "-v", "error", "-show_entries", "format=duration",
        "-of", "default=nk=1:nw=1", str(path)])
    return float(out.strip())


# ───────────────────────── TTS ─────────────────────────
def tts():
    from openai import OpenAI
    client = OpenAI(api_key=brand.openai_key())
    durations = {}
    for name in ORDER:
        mp3 = brand.AUDIO_DIR / f"clip1_{name}.mp3"
        with client.audio.speech.with_streaming_response.create(
            model=brand.TTS_MODEL, voice=brand.TTS_VOICE,
            input=SCENES[name], instructions=brand.TTS_INSTRUCTIONS,
            response_format="mp3",
        ) as resp:
            resp.stream_to_file(mp3)
        d = dur_of(mp3)
        durations[name] = d
        print(f"  {name}: {d:.1f}s -> {mp3.name}")
    DUR_FILE.write_text(json.dumps(durations, indent=2))
    print(f"durations -> {DUR_FILE}")


# ─────────────────────── CAPTURE ───────────────────────
def _smooth_scroll(page, to_y, secs):
    cur = page.evaluate("window.scrollY")
    steps = max(1, int(secs * 30))
    for i in range(steps):
        y = cur + (to_y - cur) * (i + 1) / steps
        page.evaluate(f"window.scrollTo(0,{y})")
        page.wait_for_timeout(int(secs * 1000 / steps))


def _scroll_to_text(page, text, secs, offset=110):
    y = page.evaluate(
        """(t) => {
          const norm = s => (s||'').toLowerCase().normalize('NFD').replace(/[\\u0300-\\u036f]/g,'');
          const q = norm(t);
          const els = [...document.querySelectorAll('h1,h2,h3,h4,p,span,a,button')];
          let best=null, bl=Infinity;
          for (const e of els){ if(e.offsetParent===null) continue;
            const tx=norm(e.textContent); if(tx.includes(q)&&tx.length<bl){best=e;bl=tx.length;} }
          return best ? best.getBoundingClientRect().top+window.scrollY : null;
        }""", text)
    if y is None:
        y = page.evaluate("window.scrollY") + 600
    _smooth_scroll(page, max(0, y - offset), secs)


def _move(page, x, y, steps=30):
    page.mouse.move(x, y, steps=steps)
    page.wait_for_timeout(150)


def _scene3(page, dur, t0):
    page.goto(SITE, wait_until="domcontentloaded")
    # esperar a que el hero esté pintado antes de empezar la coreografía
    try:
        page.wait_for_selector("h1, h2", state="visible", timeout=12000)
    except Exception:
        page.wait_for_timeout(1200)
    lead = time.time() - t0      # todo lo anterior es "blanco"/carga -> se recorta
    page.wait_for_timeout(700)
    _scroll_to_text(page, "El problema, en cifras", dur * 0.42)
    page.wait_for_timeout(int(dur * 0.16 * 1000))
    _scroll_to_text(page, "Evalúa en terreno. Decide con datos", dur * 0.36)
    page.wait_for_timeout(int(dur * 0.06 * 1000))
    return lead


def _scene4(page, dur, t0):
    page.goto(SITE, wait_until="domcontentloaded")
    # CTA "Empezar gratis" (usuario anónimo) -> /sign-in
    cta = page.get_by_role("link", name="Empezar gratis").first
    try:
        box = cta.bounding_box()
        if box:
            _move(page, box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
        cta.click()
    except Exception:
        page.goto(SITE + "sign-in", wait_until="domcontentloaded")
    # esperar a que Clerk renderice el formulario (esto es lo que antes salía en blanco)
    try:
        page.wait_for_selector("input[type='email'], input[name='identifier']", timeout=12000)
    except Exception:
        page.wait_for_timeout(2500)
    lead = time.time() - t0      # navegación + carga de Clerk -> se recorta
    page.wait_for_timeout(700)
    field = page.locator("input[type='email'], input[name='identifier']").first
    try:
        b = field.bounding_box()
        if b:
            _move(page, b["x"] + b["width"] / 2, b["y"] + b["height"] / 2)
    except Exception:
        pass
    page.wait_for_timeout(int(dur * 0.45 * 1000))
    return lead


def capture():
    from playwright.sync_api import sync_playwright
    durations = json.loads(DUR_FILE.read_text())
    fns = {"esc3": _scene3, "esc4": _scene4}   # esc2 ya no se captura (es B-roll)
    leads = {}
    with sync_playwright() as p:
        for name in [s for s in ORDER if s in fns]:
            dur = durations[name]
            browser = p.chromium.launch()
            ctx = browser.new_context(
                viewport={"width": W, "height": H},
                record_video_dir=str(brand.RAW_DIR),
                record_video_size={"width": W, "height": H},
            )
            ctx.add_init_script(INIT_JS)
            page = ctx.new_page()
            print(f"  capturando {name} (~{dur:.1f}s)…")
            t0 = time.time()
            leads[name] = round(fns[name](page, dur, t0), 3)
            video = page.video
            ctx.close()
            browser.close()
            src = Path(video.path())
            dst = brand.RAW_DIR / f"clip1_{name}.webm"
            if dst.exists():
                dst.unlink()
            shutil.move(str(src), str(dst))
            print(f"    -> {dst.name} ({dur_of(dst):.1f}s grabados, blanco recortado {leads[name]:.1f}s)")
    LEAD_FILE.write_text(json.dumps(leads, indent=2))


# ──────────────────────── CARDS ────────────────────────
def cards():
    from PIL import Image, ImageDraw, ImageFont

    def font(sz, bold=True):
        return ImageFont.truetype(brand.FONT_BOLD if bold else brand.FONT_REG, sz)

    def center_text(d, cx, y, text, f, fill):
        w = d.textlength(text, font=f)
        d.text((cx - w / 2, y), text, font=f, fill=fill)

    logo = Image.open(brand.LOGO).convert("RGBA")
    lw = 720
    logo = logo.resize((lw, int(logo.height * lw / logo.width)))

    def base():
        img = Image.new("RGB", (W, H), brand.WHITE)
        d = ImageDraw.Draw(img)
        d.rectangle([0, 0, W, 14], fill=brand.BLUE)          # franja superior
        d.rectangle([0, H - 14, W, H], fill=brand.BLUE)       # franja inferior
        return img, d

    # Intro animada: tarjeta con SOLO el título (el logo animado con sonido se
    # superpone encima en assemble). Fondo = MISMO que el video del logo (#F7F8FB),
    # para que no se vea un rectángulo al superponerlo sobre la tarjeta.
    intro_bg = (247, 248, 251)
    img = Image.new("RGB", (W, H), intro_bg)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 14], fill=brand.BLUE)
    d.rectangle([0, H - 14, W, H], fill=brand.BLUE)
    center_text(d, W / 2, 824, "Bienvenida y tu cuenta", font(58), brand.INK)
    center_text(d, W / 2, 910, "Tutorial 1 de 8", font(32, bold=False), brand.SLATE)
    img.save(brand.OUTPUT_DIR / "clip1_intro_title.png")

    # Outro
    img, d = base()
    img.paste(logo, ((W - logo.width) // 2, 300), logo)
    center_text(d, W / 2, 560, brand.CTA, font(48), brand.BLUE)
    center_text(d, W / 2, 660, "Siguiente: Trae tu gente", font(34, bold=False), brand.SLATE)
    img.save(brand.OUTPUT_DIR / "clip1_outro.png")
    print("  tarjetas intro/outro generadas")


# ─────────────────────── ASSEMBLE ──────────────────────
def _srt_time(t):
    h = int(t // 3600); m = int((t % 3600) // 60); s = int(t % 60); ms = int((t - int(t)) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def _build_srt(durations, path):
    lines = []
    idx = 1
    t = INTRO_SECS
    for name in ORDER:
        dur = durations[name]
        chunks = SUBS[name]
        total_chars = sum(len(c) for c in chunks)
        ct = t
        for c in chunks:
            seg = dur * (len(c) / total_chars)
            lines.append(str(idx))
            lines.append(f"{_srt_time(ct)} --> {_srt_time(ct + seg)}")
            lines.append(c)
            lines.append("")
            idx += 1
            ct += seg
        t += dur
    path.write_text("\n".join(lines), encoding="utf-8")


def _seg_from_scene(name, dur, out, lead=0.0):
    src = brand.RAW_DIR / f"clip1_{name}.webm"
    audio = brand.AUDIO_DIR / f"clip1_{name}.mp3"
    vf = (f"scale={W}:{H}:force_original_aspect_ratio=decrease,"
          f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2,fps={brand.FPS},setsar=1,"
          f"tpad=stop_mode=clone:stop_duration=12")
    # -ss antes de -i recorta el blanco inicial (carga de página) del webm grabado
    sh([brand.FFMPEG, "-y", "-ss", f"{max(0.0, lead):.3f}", "-i", str(src),
        "-i", str(audio),
        "-filter_complex", f"[0:v]{vf}[v]", "-map", "[v]", "-map", "1:a",
        "-t", f"{dur:.3f}", "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-r", str(brand.FPS), "-c:a", "aac", "-ar", "44100", "-ac", "2", str(out)])


def _seg_broll(clip, dur, out, audio, start=2.0):
    """Segmento de B-roll de stock (cover a 1920x1080) con la narración encima."""
    src = BROLL_DIR / clip
    vf = (f"scale={W}:{H}:force_original_aspect_ratio=increase,"
          f"crop={W}:{H},fps={brand.FPS},setsar=1")
    sh([brand.FFMPEG, "-y", "-ss", f"{start}", "-i", str(src), "-i", str(audio),
        "-filter_complex", f"[0:v]{vf}[v]", "-map", "[v]", "-map", "1:a",
        "-t", f"{dur:.3f}", "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-r", str(brand.FPS), "-c:a", "aac", "-ar", "44100", "-ac", "2", str(out)])


def _seg_from_card(png, secs, out, fade_out=False):
    fade = "fade=in:0:12"
    if fade_out:
        fade += f",fade=out:{int(secs * brand.FPS) - 12}:12"
    sh([brand.FFMPEG, "-y", "-loop", "1", "-i", str(png),
        "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
        "-filter_complex", f"[0:v]scale={W}:{H},fps={brand.FPS},setsar=1,{fade}[v]",
        "-map", "[v]", "-map", "1:a", "-t", f"{secs:.3f}",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", str(brand.FPS),
        "-c:a", "aac", "-ar", "44100", "-ac", "2", str(out)])


def _seg_intro_animated(out, secs):
    """Intro = logo animado con sonido (`recontrata_intro_sound.mp4`) sobre fondo
    blanco, con el título del tutorial debajo. Conserva el audio del logo (sonic)."""
    base_png = brand.OUTPUT_DIR / "clip1_intro_title.png"
    # Sin fade a negro: la animación termina y el logo queda ESTÁTICO hasta el corte.
    fc = (
        f"[1:v]scale={W}:{H},setsar=1[bg];"
        f"[0:v]scale=1280:700:force_original_aspect_ratio=decrease,setsar=1[lg];"
        f"[bg][lg]overlay=(W-w)/2:80[ov];"
        f"[ov]fps={brand.FPS}[v]"
    )
    sh([brand.FFMPEG, "-y",
        "-i", str(INTRO_VIDEO),            # 0: logo animado (video + audio)
        "-loop", "1", "-i", str(base_png), # 1: tarjeta de título (fondo + texto)
        "-filter_complex", fc,
        "-map", "[v]", "-map", "0:a",
        "-t", f"{secs:.3f}", "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-r", str(brand.FPS), "-c:a", "aac", "-ar", "44100", "-ac", "2", str(out)])


def assemble():
    _check_subs()
    durations = json.loads(DUR_FILE.read_text())
    leads = json.loads(LEAD_FILE.read_text()) if LEAD_FILE.exists() else {}
    tmp = brand.OUTPUT_DIR / "_tmp"
    tmp.mkdir(exist_ok=True)
    segs = []

    intro = tmp / "00_intro.mp4"
    _seg_intro_animated(intro, INTRO_SECS)
    segs.append(intro)

    for i, name in enumerate(ORDER):
        seg = tmp / f"{i+1:02d}_{name}.mp4"
        audio = brand.AUDIO_DIR / f"clip1_{name}.mp3"
        if name in BROLL_SCENES:
            _seg_broll(BROLL_SCENES[name], durations[name], seg, audio)
        else:
            _seg_from_scene(name, durations[name], seg, lead=leads.get(name, 0.0))
        segs.append(seg)

    outro = tmp / "99_outro.mp4"
    _seg_from_card(brand.OUTPUT_DIR / "clip1_outro.png", OUTRO_SECS, outro, fade_out=True)
    segs.append(outro)

    # concat por filtro (re-encode uniforme)
    pre = brand.OUTPUT_DIR / "clip1_pre.mp4"
    inputs = []
    for s in segs:
        inputs += ["-i", str(s)]
    n = len(segs)
    fc = "".join(f"[{i}:v][{i}:a]" for i in range(n)) + f"concat=n={n}:v=1:a=1[v][a]"
    sh([brand.FFMPEG, "-y", *inputs, "-filter_complex", fc,
        "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-movflags", "+faststart", str(pre)])

    # subtítulos quemados (cwd = output para evitar el problema del ':' en rutas Windows)
    srt = brand.OUTPUT_DIR / "clip1.srt"
    _build_srt(durations, srt)
    style = ("FontName=Arial,FontSize=16,PrimaryColour=&H00FFFFFF,"
             "BackColour=&H66000000,BorderStyle=4,Outline=0,Shadow=0,"
             "Alignment=2,MarginV=24")
    subprocess.run([brand.FFMPEG, "-y", "-i", "clip1_pre.mp4",
                    "-vf", f"subtitles=clip1.srt:force_style='{style}'",
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "copy",
                    "clip1.mp4"], check=True, cwd=str(brand.OUTPUT_DIR))
    print(f"  -> {OUT}  ({dur_of(OUT):.1f}s)")


def main():
    stage = sys.argv[1] if len(sys.argv) > 1 else "all"
    if stage in ("tts", "all"):
        print("[1/4] TTS…"); tts()
    if stage in ("capture", "all"):
        print("[2/4] Captura…"); capture()
    if stage in ("cards", "all"):
        print("[3/4] Tarjetas…"); cards()
    if stage in ("assemble", "all"):
        print("[4/4] Ensamblado…"); assemble()
    print("OK")


if __name__ == "__main__":
    main()
