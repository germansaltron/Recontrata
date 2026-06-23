"""Produce el Clip 2 de Recontrata (Trae tu gente).

A diferencia del Clip 1 (landing pública + B-roll), este muestra el DASHBOARD
AUTENTICADO. Estrategia: dev server local en modo mock (VITE_AUTH_MOCK_ENABLED=true,
http://localhost:5173) con las llamadas a /api/v1 interceptadas por Playwright con
datos demo. El mock es STATEFUL por escena: la lista de trabajadores arranca en el
estado correcto para esa escena (vacía / con uno / completa).

Requiere el dev server corriendo:  cd frontend && npm run dev

Pipeline calcado del Clip 1:
  tts | capture | cards | assemble | all
"""
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

import brand

BASE = "http://localhost:5173"
DUR_FILE = brand.OUTPUT_DIR / "clip2_durations.json"
LEAD_FILE = brand.OUTPUT_DIR / "clip2_leads.json"
OUT = brand.OUTPUT_DIR / "clip2.mp4"
INTRO_VIDEO = (brand.REPO_DIR / "branding" / "logo-animado" / "output"
               / "recontrata_intro_sound.mp4")
XLSX = brand.TUTORIAL_DIR / "assets" / "demo" / "equipo_constructora_andes.xlsx"
W, H = brand.VIDEO_W, brand.VIDEO_H

INTRO_SECS = 4.0
OUTRO_SECS = 4.0
ORG_NAME = "Constructora Andes"

# ── Narración (del guion guiones/clip2.md) ───────────────────────────
SCENES = {
    "esc2": "Lo primero es tener a tu gente en Recontrata. En el menú, entra a "
            "'Trabajadores'. Aquí va a vivir tu base: el activo más valioso de tu empresa.",
    "esc3": "Puedes agregarlos uno por uno: nombre, RUT y especialidad. El RUT se "
            "valida y se ordena solo, así no quedan datos mal escritos. Eliges el "
            "oficio de la lista y listo.",
    "esc4": "Pero si ya tienes tu equipo en una planilla —y casi todos la tienen— no "
            "copies nada a mano. Usa 'Importar', sube tu Excel o CSV, y Recontrata "
            "carga a todos de una vez, validando cada RUT. En segundos tienes tu base completa.",
    "esc5": "Tu gente ya está dentro. Ahora vamos a crear tu primera faena para empezar a evaluar.",
}
ORDER = ["esc2", "esc3", "esc4", "esc5"]

# Subtítulos VERBATIM (cada lista, concatenada == SCENES). Lo valida _check_subs().
SUBS = {
    "esc2": [
        "Lo primero es tener a tu gente en Recontrata.",
        "En el menú, entra a 'Trabajadores'.",
        "Aquí va a vivir tu base: el activo más valioso de tu empresa.",
    ],
    "esc3": [
        "Puedes agregarlos uno por uno: nombre, RUT y especialidad.",
        "El RUT se valida y se ordena solo, así no quedan datos mal escritos.",
        "Eliges el oficio de la lista y listo.",
    ],
    "esc4": [
        "Pero si ya tienes tu equipo en una planilla —y casi todos la tienen— no copies nada a mano.",
        "Usa 'Importar', sube tu Excel o CSV, y Recontrata carga a todos de una vez, validando cada RUT.",
        "En segundos tienes tu base completa.",
    ],
    "esc5": [
        "Tu gente ya está dentro.",
        "Ahora vamos a crear tu primera faena para empezar a evaluar.",
    ],
}


def _check_subs():
    squash = lambda s: "".join(s.split())
    for name in ORDER:
        if squash(" ".join(SUBS[name])) != squash(SCENES[name]):
            raise SystemExit(f"SUBS[{name}] no coincide con SCENES[{name}] (verbatim).")


# ── RUT chileno: dígito verificador + formato ────────────────────────
def _rut_dv(body):
    s, m = 0, 2
    for d in reversed(str(body)):
        s += int(d) * m
        m = 2 if m == 7 else m + 1
    r = 11 - (s % 11)
    return {10: "K", 11: "0"}.get(r, str(r))


def _rut_fmt(body):
    dv = _rut_dv(body)
    rev = str(body)[::-1]
    groups = [rev[i:i + 3][::-1] for i in range(0, len(rev), 3)][::-1]
    return ".".join(groups) + "-" + dv


def _rut_digits(body):
    return str(body) + _rut_dv(body)


# ── Roster demo (body RUT, nombre, apellido, especialidad, fono, email) ──
SERGIO = (15333444, "Sergio", "Díaz", "Soldador", "+56 9 8123 4567", "sergio.diaz@andes.cl")
IMPORTED = [
    (16777888, "Marcela", "Rojas", "Supervisor", "+56 9 7222 1100", "m.rojas@andes.cl"),
    (14222333, "Pedro", "Cáceres", "Mecánico", "+56 9 6333 2211", "p.caceres@andes.cl"),
    (17888999, "Luis", "Tapia", "Eléctrico", "+56 9 5444 3322", "l.tapia@andes.cl"),
    (13444555, "Jorge", "Muñoz", "Operador Grúa", "+56 9 4555 4433", "j.munoz@andes.cl"),
    (18555666, "Camila", "Fuentes", "Prevencionista", "+56 9 3666 5544", "c.fuentes@andes.cl"),
    (12666777, "Andrés", "Soto", "Rigger", "+56 9 2777 6655", "a.soto@andes.cl"),
    (19777888, "Patricio", "Vega", "Cañerista", "+56 9 1888 7766", "p.vega@andes.cl"),
]


def _worker(idx, body, first, last, specialty):
    return {"id": f"w{idx}", "rut": _rut_fmt(body), "first_name": first,
            "last_name": last, "specialty": specialty, "phone": None, "email": None,
            "is_active": True, "evaluation_count": 0, "avg_score": None,
            "created_at": "2026-01-01T00:00:00"}


def _all_workers():
    rows = [SERGIO] + IMPORTED
    return [_worker(i + 1, b, f, l, sp) for i, (b, f, l, sp, _, _) in enumerate(rows)]


# ── Mock de /api/v1 (stateful por escena) ────────────────────────────
PROFILE = {"id": "u1", "email": "demo@recontrata.cl", "full_name": "Demo Recontrata",
           "organizations": [{"org_id": "org1", "org_name": ORG_NAME, "role": "admin"}]}


def _make_handler(initial):
    """Devuelve un handler de page.route con estado mutable de trabajadores."""
    state = {"workers": list(initial)}

    def handler(route):
        req = route.request
        url, m = req.url, req.method

        def j(body):
            route.fulfill(status=200, content_type="application/json",
                          body=json.dumps(body))

        if url.rstrip("/").endswith("/me"):
            return j(PROFILE)
        if "/dashboard/stats" in url:
            n = len(state["workers"])
            return j({"project_count": 2, "active_project_count": 1, "worker_count": n,
                      "evaluation_count": 0, "avg_score_overall": None,
                      "rehire_rate": None, "specialty_distribution": []})
        if "/dashboard/next-evaluation" in url:
            return j({"project_id": None, "project_name": None, "worker_id": None,
                      "worker_name": None, "pending_count": 0})
        if "/dashboard/" in url:
            return j([])
        if "/workers/import" in url and m == "POST":
            base = len(state["workers"])
            for i, (b, f, l, sp, _, _) in enumerate(IMPORTED):
                state["workers"].append(_worker(base + i + 1, b, f, l, sp))
            return j({"created": len(IMPORTED), "updated": 0, "errors": []})
        if "/workers" in url and m == "POST":
            try:
                data = req.post_data_json or {}
            except Exception:
                data = {}
            w = _worker(len(state["workers"]) + 1, "0",
                        data.get("first_name", "Nuevo"), data.get("last_name", ""),
                        data.get("specialty", "Otro"))
            w["rut"] = data.get("rut", w["rut"])
            state["workers"].append(w)
            return j(w)
        if "/workers" in url and m == "GET":
            ws = state["workers"]
            return j({"items": ws, "total": len(ws), "page": 1, "size": 20,
                      "pages": max(1, (len(ws) + 19) // 20)})
        if "/organizations" in url and m == "POST":
            return j({"id": "org1", "name": ORG_NAME, "slug": "andes",
                      "industry": "construccion_mineria", "created_at": "2026-01-01T00:00:00"})
        return j({})

    return handler


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


def _move(page, x, y, steps=25):
    page.mouse.move(x, y, steps=steps)
    page.wait_for_timeout(120)


def _move_to(page, locator, steps=25):
    box = locator.bounding_box()
    if box:
        _move(page, box["x"] + box["width"] / 2, box["y"] + box["height"] / 2, steps)
    return box


# ── Excel demo para la importación ───────────────────────────────────
def make_xlsx():
    from openpyxl import Workbook
    XLSX.parent.mkdir(parents=True, exist_ok=True)
    wb = Workbook()
    ws = wb.active
    ws.title = "Trabajadores"
    ws.append(["rut", "first_name", "last_name", "specialty", "phone", "email"])
    for b, f, l, sp, ph, em in IMPORTED:
        ws.append([_rut_fmt(b), f, l, sp, ph, em])
    wb.save(XLSX)
    print(f"  Excel demo -> {XLSX}")


# ───────────────────────────── TTS ─────────────────────────
def tts():
    from openai import OpenAI
    client = OpenAI(api_key=brand.openai_key())
    durations = {}
    for name in ORDER:
        mp3 = brand.AUDIO_DIR / f"clip2_{name}.mp3"
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


# ─────────────────────── CAPTURE ───────────────────────
def _scene2(page, dur, t0):
    """Dashboard -> click 'Trabajadores' en el menú -> lista vacía."""
    page.goto(f"{BASE}/app", wait_until="domcontentloaded")
    page.wait_for_selector("h1", state="visible", timeout=12000)
    lead = time.time() - t0
    page.wait_for_timeout(900)
    link = page.get_by_role("link", name="Trabajadores").first
    _move_to(page, link)
    link.click()
    page.wait_for_selector("text=No se encontraron trabajadores", timeout=8000)
    page.wait_for_timeout(int(dur * 0.30 * 1000))
    return lead


def _scene3(page, dur, t0):
    """Agregar un trabajador uno a uno."""
    page.goto(f"{BASE}/app/workers", wait_until="domcontentloaded")
    page.wait_for_selector("h1", state="visible", timeout=12000)
    lead = time.time() - t0
    page.wait_for_timeout(500)
    nuevo = page.get_by_role("button", name="Nuevo").first
    _move_to(page, nuevo)
    nuevo.click()
    rut_in = page.locator("input[placeholder='12.345.678-9']").first
    rut_in.wait_for(state="visible", timeout=6000)
    _move_to(page, rut_in)
    rut_in.click()
    rut_in.type(_rut_digits(SERGIO[0]), delay=70)
    page.locator("input[placeholder='Juan']").first.click()   # blur -> formatea RUT
    page.wait_for_timeout(400)
    page.locator("input[placeholder='Juan']").first.type(SERGIO[1], delay=55)
    page.locator("input[placeholder='Perez']").first.click()
    page.locator("input[placeholder='Perez']").first.type(SERGIO[2], delay=55)
    page.wait_for_timeout(300)
    page.locator("select").first.select_option(label=SERGIO[3])
    page.wait_for_timeout(500)
    crear = page.get_by_role("button", name="Crear Trabajador").first
    _move_to(page, crear)
    crear.click()
    # éxito = el modal se cierra (desaparece el input del RUT). Evita el duplicado
    # oculto de la card móvil que confunde a wait_for_selector(text=...).
    try:
        rut_in.wait_for(state="detached", timeout=8000)
    except Exception:
        page.wait_for_timeout(1500)
    page.wait_for_timeout(int(dur * 0.20 * 1000))
    return lead


def _scene4(page, dur, t0):
    """Importar desde Excel."""
    page.goto(f"{BASE}/app/workers", wait_until="domcontentloaded")
    page.wait_for_selector("h1", state="visible", timeout=12000)
    lead = time.time() - t0
    page.wait_for_timeout(600)
    imp = page.get_by_role("button", name="Importar").first
    _move_to(page, imp)
    imp.click()
    file_in = page.locator("input[type='file']").first
    file_in.wait_for(state="attached", timeout=6000)
    file_in.set_input_files(str(XLSX))
    page.wait_for_timeout(900)
    submit = page.get_by_role("button", name="Importar").last
    _move_to(page, submit)
    submit.click()
    page.wait_for_selector("text=Importacion completa", timeout=8000)
    page.wait_for_timeout(1400)
    listo = page.get_by_role("button", name="Listo").first
    _move_to(page, listo)
    listo.click()
    page.wait_for_timeout(int(dur * 0.18 * 1000))
    return lead


def _scene5(page, dur, t0):
    """Lista poblada (cierre)."""
    page.goto(f"{BASE}/app/workers", wait_until="domcontentloaded")
    page.wait_for_selector("h1", state="visible", timeout=12000)
    lead = time.time() - t0
    page.wait_for_timeout(int(dur * 0.45 * 1000))
    page.mouse.wheel(0, 240)
    page.wait_for_timeout(int(dur * 0.35 * 1000))
    return lead


# Estado inicial de trabajadores por escena (mock stateful)
SCENE_INITIAL = {
    "esc2": [],
    "esc3": [],
    "esc4": [_worker(1, SERGIO[0], SERGIO[1], SERGIO[2], SERGIO[3])],
    "esc5": _all_workers(),
}
SCENE_FN = {"esc2": _scene2, "esc3": _scene3, "esc4": _scene4, "esc5": _scene5}


def capture():
    from playwright.sync_api import sync_playwright
    durations = json.loads(DUR_FILE.read_text())
    make_xlsx()
    leads = {}
    with sync_playwright() as p:
        for name in ORDER:
            dur = durations[name]
            browser = p.chromium.launch()
            ctx = browser.new_context(
                viewport={"width": W, "height": H},
                record_video_dir=str(brand.RAW_DIR),
                record_video_size={"width": W, "height": H},
            )
            ctx.add_init_script(INIT_JS)
            ctx.route("**/api/v1/**", _make_handler(SCENE_INITIAL[name]))
            page = ctx.new_page()
            print(f"  capturando {name} (~{dur:.1f}s)…")
            t0 = time.time()
            leads[name] = round(SCENE_FN[name](page, dur, t0), 3)
            video = page.video
            ctx.close()
            browser.close()
            src = Path(video.path())
            dst = brand.RAW_DIR / f"clip2_{name}.webm"
            if dst.exists():
                dst.unlink()
            shutil.move(str(src), str(dst))
            print(f"    -> {dst.name} ({dur_of(dst):.1f}s, blanco {leads[name]:.1f}s)")
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

    # Tarjeta de título (fondo = el del video del logo, #F7F8FB) para el intro animado.
    img = Image.new("RGB", (W, H), (247, 248, 251))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 14], fill=brand.BLUE)
    d.rectangle([0, H - 14, W, H], fill=brand.BLUE)
    center_text(d, W / 2, 824, "Trae tu gente", font(58), brand.INK)
    center_text(d, W / 2, 910, "Tutorial 2 de 8", font(32, bold=False), brand.SLATE)
    img.save(brand.OUTPUT_DIR / "clip2_intro_title.png")

    # Outro (estático)
    img = Image.new("RGB", (W, H), brand.WHITE)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 14], fill=brand.BLUE)
    d.rectangle([0, H - 14, W, H], fill=brand.BLUE)
    img.paste(logo, ((W - logo.width) // 2, 300), logo)
    center_text(d, W / 2, 560, brand.CTA, font(48), brand.BLUE)
    center_text(d, W / 2, 660, "Siguiente: Crea tu faena", font(34, bold=False), brand.SLATE)
    img.save(brand.OUTPUT_DIR / "clip2_outro.png")
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
        total = sum(len(c) for c in chunks)
        ct = t
        for c in chunks:
            seg = dur * (len(c) / total)
            lines += [str(idx), f"{_srt_time(ct)} --> {_srt_time(ct + seg)}", c, ""]
            idx += 1
            ct += seg
        t += dur
    path.write_text("\n".join(lines), encoding="utf-8")


def _seg_intro_animated(out, secs):
    base_png = brand.OUTPUT_DIR / "clip2_intro_title.png"
    fc = (f"[1:v]scale={W}:{H},setsar=1[bg];"
          f"[0:v]scale=1280:700:force_original_aspect_ratio=decrease,setsar=1[lg];"
          f"[bg][lg]overlay=(W-w)/2:80[ov];[ov]fps={brand.FPS}[v]")
    sh([brand.FFMPEG, "-y", "-i", str(INTRO_VIDEO), "-loop", "1", "-i", str(base_png),
        "-filter_complex", fc, "-map", "[v]", "-map", "0:a", "-t", f"{secs:.3f}",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", str(brand.FPS),
        "-c:a", "aac", "-ar", "44100", "-ac", "2", str(out)])


def _seg_from_scene(name, dur, out, lead=0.0):
    src = brand.RAW_DIR / f"clip2_{name}.webm"
    audio = brand.AUDIO_DIR / f"clip2_{name}.mp3"
    vf = (f"scale={W}:{H}:force_original_aspect_ratio=decrease,"
          f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2,fps={brand.FPS},setsar=1,"
          f"tpad=stop_mode=clone:stop_duration=12")
    sh([brand.FFMPEG, "-y", "-ss", f"{max(0.0, lead):.3f}", "-i", str(src),
        "-i", str(audio), "-filter_complex", f"[0:v]{vf}[v]", "-map", "[v]", "-map", "1:a",
        "-t", f"{dur:.3f}", "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-r", str(brand.FPS), "-c:a", "aac", "-ar", "44100", "-ac", "2", str(out)])


def _seg_from_card(png, secs, out):
    fade = f"fade=in:0:12,fade=out:{int(secs * brand.FPS) - 12}:12"
    sh([brand.FFMPEG, "-y", "-loop", "1", "-i", str(png),
        "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
        "-filter_complex", f"[0:v]scale={W}:{H},fps={brand.FPS},setsar=1,{fade}[v]",
        "-map", "[v]", "-map", "1:a", "-t", f"{secs:.3f}",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", str(brand.FPS),
        "-c:a", "aac", "-ar", "44100", "-ac", "2", str(out)])


def assemble():
    _check_subs()
    durations = json.loads(DUR_FILE.read_text())
    leads = json.loads(LEAD_FILE.read_text()) if LEAD_FILE.exists() else {}
    tmp = brand.OUTPUT_DIR / "_tmp2"
    tmp.mkdir(exist_ok=True)
    segs = []

    intro = tmp / "00_intro.mp4"
    _seg_intro_animated(intro, INTRO_SECS)
    segs.append(intro)

    for i, name in enumerate(ORDER):
        seg = tmp / f"{i+1:02d}_{name}.mp4"
        _seg_from_scene(name, durations[name], seg, lead=leads.get(name, 0.0))
        segs.append(seg)

    outro = tmp / "99_outro.mp4"
    _seg_from_card(brand.OUTPUT_DIR / "clip2_outro.png", OUTRO_SECS, outro)
    segs.append(outro)

    inputs = []
    for s in segs:
        inputs += ["-i", str(s)]
    n = len(segs)
    fc = "".join(f"[{i}:v][{i}:a]" for i in range(n)) + f"concat=n={n}:v=1:a=1[v][a]"
    pre = brand.OUTPUT_DIR / "clip2_pre.mp4"
    sh([brand.FFMPEG, "-y", *inputs, "-filter_complex", fc, "-map", "[v]", "-map", "[a]",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac",
        "-movflags", "+faststart", str(pre)])

    srt = brand.OUTPUT_DIR / "clip2.srt"
    _build_srt(durations, srt)
    style = ("FontName=Arial,FontSize=16,PrimaryColour=&H00FFFFFF,"
             "BackColour=&H66000000,BorderStyle=4,Outline=0,Shadow=0,"
             "Alignment=2,MarginV=24")
    subprocess.run([brand.FFMPEG, "-y", "-i", "clip2_pre.mp4",
                    "-vf", f"subtitles=clip2.srt:force_style='{style}'",
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "copy",
                    "clip2.mp4"], check=True, cwd=str(brand.OUTPUT_DIR))
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
