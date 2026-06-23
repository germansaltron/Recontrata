"""Kit común para los tutoriales de Recontrata (clips 3+).

Reúne lo que los Clips 1 y 2 dejaron probado: voz IA (OpenAI TTS), captura con
Playwright contra el dev server en modo mock con /api/v1 interceptado de forma
STATEFUL, tarjetas de marca, y ensamblado con ffmpeg (intro animado + escenas con
recorte de blanco + outro + subtítulos VERBATIM). Los `produce_clipN.py` importan de
aquí y solo definen SCENES/SUBS/escenas/orden.

Requiere el dev server:  cd frontend && npm run dev   (http://localhost:5173)
"""
import json
import re
import shutil
import subprocess
import time
from pathlib import Path

import brand

BASE = "http://localhost:5173"
W, H = brand.VIDEO_W, brand.VIDEO_H
INTRO_VIDEO = (brand.REPO_DIR / "branding" / "logo-animado" / "output"
               / "recontrata_intro_sound.mp4")
ORG_ID = "org1"
ORG_NAME = "Constructora Andes"
PROFILE = {"id": "u1", "email": "demo@recontrata.cl", "full_name": "Demo Recontrata",
           "organizations": [{"org_id": ORG_ID, "org_name": ORG_NAME, "role": "admin"}]}

# ── RUT chileno ──────────────────────────────────────────────────────
def rut_dv(body):
    s, m = 0, 2
    for d in reversed(str(body)):
        s += int(d) * m
        m = 2 if m == 7 else m + 1
    r = 11 - (s % 11)
    return {10: "K", 11: "0"}.get(r, str(r))


def rut_fmt(body):
    rev = str(body)[::-1]
    groups = [rev[i:i + 3][::-1] for i in range(0, len(str(body)), 3)][::-1]
    return ".".join(groups) + "-" + rut_dv(body)


def rut_digits(body):
    return str(body) + rut_dv(body)


# ── Roster demo (mismo que el Clip 2) ────────────────────────────────
ROSTER = [
    (15333444, "Sergio", "Díaz", "Soldador"),
    (16777888, "Marcela", "Rojas", "Supervisor"),
    (14222333, "Pedro", "Cáceres", "Mecánico"),
    (17888999, "Luis", "Tapia", "Eléctrico"),
    (13444555, "Jorge", "Muñoz", "Operador Grúa"),
    (18555666, "Camila", "Fuentes", "Prevencionista"),
    (12666777, "Andrés", "Soto", "Rigger"),
    (19777888, "Patricio", "Vega", "Cañerista"),
]


def worker(idx, body, first, last, specialty, evals=0, avg=None):
    return {"id": f"w{idx}", "rut": rut_fmt(body), "first_name": first,
            "last_name": last, "specialty": specialty, "phone": None, "email": None,
            "is_active": True, "evaluation_count": evals, "avg_score": avg,
            "created_at": "2026-01-01T00:00:00"}


def all_workers():
    return [worker(i + 1, *r) for i, r in enumerate(ROSTER)]


def pworker(idx, body, first, last, specialty, evaluated=False, score=None):
    """ProjectWorkerItem (lista de trabajadores dentro de un proyecto)."""
    return {"id": f"w{idx}", "rut": rut_fmt(body), "first_name": first,
            "last_name": last, "specialty": specialty, "role_in_project": None,
            "assigned_at": "2026-01-02T00:00:00", "evaluated": evaluated,
            "score_in_project": score}


# ── Inyección en el navegador (cursor visible + gate saltado) ────────
INIT_JS = """
try {
  localStorage.setItem('recontrata_access', String(Date.now() + 7776000000));
  sessionStorage.setItem('recontrata_intro_seen','1');
} catch(e){}
window.addEventListener('DOMContentLoaded', () => {
  const c = document.createElement('div');
  c.id = '__cur';
  c.style.cssText = 'position:fixed;width:22px;height:22px;border-radius:50%;'+
    'background:rgba(37,99,235,.45);border:2px solid #fff;box-shadow:0 0 8px rgba(0,0,0,.45);'+
    'z-index:2147483647;pointer-events:none;transform:translate(-50%,-50%);left:0;top:0;display:none';
  document.documentElement.appendChild(c);
  addEventListener('mousemove', e => {
    c.style.display='block'; c.style.left=e.clientX+'px'; c.style.top=e.clientY+'px';
  }, true);
});
"""


def draft_js(project_id, worker_id, scores, would_rehire="", reason="", comment=""):
    """Pre-carga el borrador de una evaluación en localStorage (para escenas que ya
    muestran el formulario lleno). ts fijo (Date.now no está disponible en scripts)."""
    payload = {"scores": scores, "wouldRehire": would_rehire,
               "rehireReason": reason, "comment": comment, "ts": 1750000000000}
    key = f"faenascore:draft:{project_id}:{worker_id}"
    return f"try{{localStorage.setItem({json.dumps(key)}, {json.dumps(json.dumps(payload))});}}catch(e){{}}"


# ── Mock STATEFUL de /api/v1 ─────────────────────────────────────────
def make_handler(state):
    """state: dict mutable con claves opcionales:
       workers[], projects[], project_workers{projId:[pworker]}, evaluated(set de wid),
       import_extra[] (workers que agrega POST /workers/import)."""
    st = {
        "workers": list(state.get("workers", [])),
        "projects": list(state.get("projects", [])),
        "project_workers": {k: list(v) for k, v in state.get("project_workers", {}).items()},
        "evaluated": set(state.get("evaluated", set())),
        "import_extra": list(state.get("import_extra", [])),
    }

    def pending_list():
        out = []
        for p in st["projects"]:
            pw = st["project_workers"].get(p["id"], [])
            pend = [w for w in pw if not w["evaluated"] and w["id"] not in st["evaluated"]]
            first = pend[0]["id"] if pend else None
            out.append({"id": p["id"], "name": p["name"],
                        "client_name": p.get("client_name"),
                        "worker_count": len(pw), "pending_count": len(pend),
                        "first_pending_worker_id": first})
        return out

    def handler(route):
        req = route.request
        url, m = req.url, req.method
        path = url.split("?", 1)[0]

        def j(body, status=200):
            route.fulfill(status=status, content_type="application/json",
                          body=json.dumps(body))

        if path.rstrip("/").endswith("/me"):
            return j(PROFILE)
        if "/dashboard/stats" in path:
            return j({"project_count": len(st["projects"]),
                      "active_project_count": len(st["projects"]),
                      "worker_count": len(st["workers"]), "evaluation_count": len(st["evaluated"]),
                      "avg_score_overall": None, "rehire_rate": None,
                      "specialty_distribution": []})
        if "/dashboard/projects-pending" in path:
            return j(pending_list())
        if "/dashboard/next-evaluation" in path:
            pl = [p for p in pending_list() if p["pending_count"] > 0]
            if pl:
                p = pl[0]
                return j({"project_id": p["id"], "project_name": p["name"],
                          "worker_id": p["first_pending_worker_id"], "worker_name": None,
                          "pending_count": p["pending_count"]})
            return j({"project_id": None, "project_name": None, "worker_id": None,
                      "worker_name": None, "pending_count": 0})
        if "/dashboard/" in path:
            return j([])

        # Evaluaciones
        if path.endswith("/evaluations") and m == "POST":
            try:
                d = req.post_data_json or {}
            except Exception:
                d = {}
            wid = d.get("worker_id")
            st["evaluated"].add(wid)
            for pw in st["project_workers"].get(d.get("project_id"), []):
                if pw["id"] == wid:
                    pw["evaluated"] = True
            return j({"id": "ev1", "project_id": d.get("project_id"), "project_name": "",
                      "worker_id": wid, "worker_name": "", "evaluator_name": None,
                      "score_quality": d.get("score_quality"), "score_safety": d.get("score_safety"),
                      "score_punctuality": d.get("score_punctuality"),
                      "score_teamwork": d.get("score_teamwork"),
                      "score_technical": d.get("score_technical"),
                      "score_average": 4.0, "score_weighted": 4.0,
                      "would_rehire": d.get("would_rehire"),
                      "rehire_reason": d.get("rehire_reason"), "comment": d.get("comment"),
                      "created_at": "2026-01-03T00:00:00"}, status=201)

        # Proyectos
        mpw = re.search(r"/projects/([^/]+)/workers", path)
        if mpw:
            pid = mpw.group(1)
            if m == "GET":
                return j(st["project_workers"].get(pid, []))
            if m == "POST":
                try:
                    d = req.post_data_json or {}
                except Exception:
                    d = {}
                ids = d.get("worker_ids", [])
                cur = st["project_workers"].setdefault(pid, [])
                have = {w["id"] for w in cur}
                wmap = {w["id"]: w for w in st["workers"]}
                for wid in ids:
                    if wid in have or wid not in wmap:
                        continue
                    w = wmap[wid]
                    cur.append(pworker(int(w["id"][1:]), 0, w["first_name"], w["last_name"],
                                       w["specialty"]) | {"rut": w["rut"]})
                return j({"added": len(ids)})
        mp = re.search(r"/projects/([^/]+)$", path)
        if mp and m == "GET":
            pid = mp.group(1)
            for p in st["projects"]:
                if p["id"] == pid:
                    return j(p)
            return j(st["projects"][0] if st["projects"] else {}, status=200)
        if path.endswith("/projects") and m == "GET":
            ps = st["projects"]
            return j({"items": ps, "total": len(ps), "page": 1, "size": 50,
                      "pages": max(1, len(ps))})
        if path.endswith("/projects") and m == "POST":
            try:
                d = req.post_data_json or {}
            except Exception:
                d = {}
            pid = f"p{len(st['projects']) + 1}"
            p = {"id": pid, "name": d.get("name", "Proyecto"),
                 "client_name": d.get("client_name"), "location": d.get("location"),
                 "start_date": d.get("start_date"), "end_date": d.get("end_date"),
                 "status": "active", "worker_count": 0, "evaluation_count": 0,
                 "created_at": "2026-01-02T00:00:00"}
            st["projects"].append(p)
            st["project_workers"].setdefault(pid, [])
            return j(p, status=201)

        # Trabajadores
        if "/workers/import" in path and m == "POST":
            st["workers"].extend(st["import_extra"])
            return j({"created": len(st["import_extra"]), "updated": 0, "errors": []})
        mw = re.search(r"/workers/([^/]+)$", path)
        if mw and m == "GET" and mw.group(1) not in ("import",):
            wid = mw.group(1)
            for w in st["workers"]:
                if w["id"] == wid:
                    return j(w)
            return j(st["workers"][0] if st["workers"] else {})
        if "/workers" in path and m == "POST":
            try:
                d = req.post_data_json or {}
            except Exception:
                d = {}
            w = worker(len(st["workers"]) + 1, 0, d.get("first_name", "Nuevo"),
                       d.get("last_name", ""), d.get("specialty", "Otro"))
            w["rut"] = d.get("rut", w["rut"])
            st["workers"].append(w)
            return j(w, status=201)
        if "/workers" in path and m == "GET":
            ws = st["workers"]
            return j({"items": ws, "total": len(ws), "page": 1, "size": 20,
                      "pages": max(1, (len(ws) + 19) // 20)})

        if "/organizations" in path and m == "POST":
            return j({"id": ORG_ID, "name": ORG_NAME, "slug": "andes",
                      "industry": "construccion_mineria", "created_at": "2026-01-01T00:00:00"})
        return j({})

    return handler


# ── ffmpeg / utilidades ──────────────────────────────────────────────
def sh(cmd):
    subprocess.run(cmd, check=True)


def dur_of(path):
    out = subprocess.check_output([
        brand.FFPROBE, "-v", "error", "-show_entries", "format=duration",
        "-of", "default=nk=1:nw=1", str(path)])
    return float(out.strip())


def move(page, x, y, steps=25):
    page.mouse.move(x, y, steps=steps)
    page.wait_for_timeout(110)


def move_to(page, locator, steps=25):
    try:
        box = locator.bounding_box()
        if box:
            move(page, box["x"] + box["width"] / 2, box["y"] + box["height"] / 2, steps)
            return box
    except Exception:
        pass
    return None


# ── TTS ──────────────────────────────────────────────────────────────
def tts(scenes, order, prefix, dur_file):
    from openai import OpenAI
    client = OpenAI(api_key=brand.openai_key())
    durations = {}
    for name in order:
        mp3 = brand.AUDIO_DIR / f"{prefix}_{name}.mp3"
        with client.audio.speech.with_streaming_response.create(
            model=brand.TTS_MODEL, voice=brand.TTS_VOICE,
            input=scenes[name], instructions=brand.TTS_INSTRUCTIONS,
            response_format="mp3",
        ) as resp:
            resp.stream_to_file(mp3)
        d = dur_of(mp3)
        durations[name] = d
        print(f"  {name}: {d:.1f}s -> {mp3.name}")
    dur_file.write_text(json.dumps(durations, indent=2))


# ── Subtítulos ───────────────────────────────────────────────────────
def check_subs(subs, scenes, order):
    squash = lambda s: "".join(s.split())
    for name in order:
        if squash(" ".join(subs[name])) != squash(scenes[name]):
            raise SystemExit(f"SUBS[{name}] no coincide con SCENES[{name}] (verbatim).")


def _srt_time(t):
    h = int(t // 3600); m = int((t % 3600) // 60); s = int(t % 60); ms = int((t - int(t)) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def build_srt(subs, order, durations, intro_secs, path):
    lines, idx, t = [], 1, intro_secs
    for name in order:
        dur = durations[name]
        chunks = subs[name]
        total = sum(len(c) for c in chunks)
        ct = t
        for c in chunks:
            seg = dur * (len(c) / total)
            lines += [str(idx), f"{_srt_time(ct)} --> {_srt_time(ct + seg)}", c, ""]
            idx += 1
            ct += seg
        t += dur
    path.write_text("\n".join(lines), encoding="utf-8")


# ── Segmentos ────────────────────────────────────────────────────────
def seg_intro_animated(out, secs, title_png):
    fc = (f"[1:v]scale={W}:{H},setsar=1[bg];"
          f"[0:v]scale=1280:700:force_original_aspect_ratio=decrease,setsar=1[lg];"
          f"[bg][lg]overlay=(W-w)/2:80[ov];[ov]fps={brand.FPS}[v]")
    sh([brand.FFMPEG, "-y", "-i", str(INTRO_VIDEO), "-loop", "1", "-i", str(title_png),
        "-filter_complex", fc, "-map", "[v]", "-map", "0:a", "-t", f"{secs:.3f}",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", str(brand.FPS),
        "-c:a", "aac", "-ar", "44100", "-ac", "2", str(out)])


def seg_from_scene(prefix, name, dur, out, lead=0.0):
    src = brand.RAW_DIR / f"{prefix}_{name}.webm"
    audio = brand.AUDIO_DIR / f"{prefix}_{name}.mp3"
    vf = (f"scale={W}:{H}:force_original_aspect_ratio=decrease,"
          f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2,fps={brand.FPS},setsar=1,"
          f"tpad=stop_mode=clone:stop_duration=12")
    sh([brand.FFMPEG, "-y", "-ss", f"{max(0.0, lead):.3f}", "-i", str(src),
        "-i", str(audio), "-filter_complex", f"[0:v]{vf}[v]", "-map", "[v]", "-map", "1:a",
        "-t", f"{dur:.3f}", "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-r", str(brand.FPS), "-c:a", "aac", "-ar", "44100", "-ac", "2", str(out)])


def seg_from_card(png, secs, out):
    fade = f"fade=in:0:12,fade=out:{int(secs * brand.FPS) - 12}:12"
    sh([brand.FFMPEG, "-y", "-loop", "1", "-i", str(png),
        "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
        "-filter_complex", f"[0:v]scale={W}:{H},fps={brand.FPS},setsar=1,{fade}[v]",
        "-map", "[v]", "-map", "1:a", "-t", f"{secs:.3f}",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", str(brand.FPS),
        "-c:a", "aac", "-ar", "44100", "-ac", "2", str(out)])


# ── Tarjetas ─────────────────────────────────────────────────────────
def make_cards(prefix, intro_title, intro_sub, outro_next):
    from PIL import Image, ImageDraw, ImageFont

    def font(sz, bold=True):
        return ImageFont.truetype(brand.FONT_BOLD if bold else brand.FONT_REG, sz)

    def center(d, cx, y, text, f, fill):
        d.text((cx - d.textlength(text, font=f) / 2, y), text, font=f, fill=fill)

    logo = Image.open(brand.LOGO).convert("RGBA")
    lw = 720
    logo = logo.resize((lw, int(logo.height * lw / logo.width)))

    img = Image.new("RGB", (W, H), (247, 248, 251))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 14], fill=brand.BLUE)
    d.rectangle([0, H - 14, W, H], fill=brand.BLUE)
    center(d, W / 2, 824, intro_title, font(56), brand.INK)
    center(d, W / 2, 910, intro_sub, font(32, bold=False), brand.SLATE)
    img.save(brand.OUTPUT_DIR / f"{prefix}_intro_title.png")

    img = Image.new("RGB", (W, H), brand.WHITE)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 14], fill=brand.BLUE)
    d.rectangle([0, H - 14, W, H], fill=brand.BLUE)
    img.paste(logo, ((W - logo.width) // 2, 300), logo)
    center(d, W / 2, 560, brand.CTA, font(48), brand.BLUE)
    center(d, W / 2, 660, outro_next, font(34, bold=False), brand.SLATE)
    img.save(brand.OUTPUT_DIR / f"{prefix}_outro.png")
    print("  tarjetas intro/outro generadas")


# ── Captura genérica (un contexto por escena, mock sembrado) ─────────
def capture(prefix, order, scene_fn, scene_initial, dur_file, lead_file,
            viewport=None, extra_init=None):
    from playwright.sync_api import sync_playwright
    durations = json.loads(dur_file.read_text())
    vp = viewport or {"width": W, "height": H}
    rec = {"width": vp["width"], "height": vp["height"]}
    leads = {}
    with sync_playwright() as p:
        for name in order:
            dur = durations[name]
            browser = p.chromium.launch()
            ctx = browser.new_context(viewport=vp, record_video_dir=str(brand.RAW_DIR),
                                      record_video_size=rec, is_mobile=bool(viewport))
            ctx.add_init_script(INIT_JS)
            if extra_init and name in extra_init:
                ctx.add_init_script(extra_init[name])
            ctx.route("**/api/v1/**", make_handler(scene_initial[name]))
            page = ctx.new_page()
            print(f"  capturando {name} (~{dur:.1f}s)…")
            t0 = time.time()
            leads[name] = round(scene_fn[name](page, dur, t0), 3)
            video = page.video
            ctx.close()
            browser.close()
            src = Path(video.path())
            dst = brand.RAW_DIR / f"{prefix}_{name}.webm"
            if dst.exists():
                dst.unlink()
            shutil.move(str(src), str(dst))
            print(f"    -> {dst.name} ({dur_of(dst):.1f}s, blanco {leads[name]:.1f}s)")
    lead_file.write_text(json.dumps(leads, indent=2))


# ── Ensamblado ───────────────────────────────────────────────────────
SUBTITLE_STYLE = ("FontName=Arial,FontSize=16,PrimaryColour=&H00FFFFFF,"
                  "BackColour=&H66000000,BorderStyle=4,Outline=0,Shadow=0,"
                  "Alignment=2,MarginV=24")


def assemble(prefix, order, subs, scenes, intro_secs, outro_secs, dur_file, lead_file, out):
    check_subs(subs, scenes, order)
    durations = json.loads(dur_file.read_text())
    leads = json.loads(lead_file.read_text()) if lead_file.exists() else {}
    tmp = brand.OUTPUT_DIR / f"_tmp_{prefix}"
    tmp.mkdir(exist_ok=True)
    segs = []

    intro = tmp / "00_intro.mp4"
    seg_intro_animated(intro, intro_secs, brand.OUTPUT_DIR / f"{prefix}_intro_title.png")
    segs.append(intro)
    for i, name in enumerate(order):
        seg = tmp / f"{i+1:02d}_{name}.mp4"
        seg_from_scene(prefix, name, durations[name], seg, lead=leads.get(name, 0.0))
        segs.append(seg)
    outro = tmp / "99_outro.mp4"
    seg_from_card(brand.OUTPUT_DIR / f"{prefix}_outro.png", outro_secs, outro)
    segs.append(outro)

    inputs = []
    for s in segs:
        inputs += ["-i", str(s)]
    n = len(segs)
    fc = "".join(f"[{i}:v][{i}:a]" for i in range(n)) + f"concat=n={n}:v=1:a=1[v][a]"
    pre = brand.OUTPUT_DIR / f"{prefix}_pre.mp4"
    sh([brand.FFMPEG, "-y", *inputs, "-filter_complex", fc, "-map", "[v]", "-map", "[a]",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac",
        "-movflags", "+faststart", str(pre)])

    srt = brand.OUTPUT_DIR / f"{prefix}.srt"
    build_srt(subs, order, durations, intro_secs, srt)
    subprocess.run([brand.FFMPEG, "-y", "-i", f"{prefix}_pre.mp4",
                    "-vf", f"subtitles={prefix}.srt:force_style='{SUBTITLE_STYLE}'",
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "copy",
                    f"{prefix}.mp4"], check=True, cwd=str(brand.OUTPUT_DIR))
    print(f"  -> {out}  ({dur_of(out):.1f}s)")
