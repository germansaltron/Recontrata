"""Identidad de marca de Recontrata para la serie de tutoriales en video.

Calcado del enfoque de CasiListo (tutorial/), adaptado a la marca azul de
Recontrata. Lo consumen los scripts de produccion.
"""
from pathlib import Path
import shutil

# ── Rutas ────────────────────────────────────────────────────────────
SCRIPTS_DIR = Path(__file__).resolve().parent
TUTORIAL_DIR = SCRIPTS_DIR.parent
REPO_DIR = TUTORIAL_DIR.parent
GUIONES_DIR = TUTORIAL_DIR / "guiones"
OUTPUT_DIR = TUTORIAL_DIR / "output"
RAW_DIR = OUTPUT_DIR / "raw"
AUDIO_DIR = OUTPUT_DIR / "audio"
LOGO = REPO_DIR / "frontend" / "public" / "logo-recontrata.png"

for d in (OUTPUT_DIR, RAW_DIR, AUDIO_DIR):
    d.mkdir(parents=True, exist_ok=True)

# ── Colores (Tailwind blue-600, paleta de la app) ────────────────────
BLUE = "#2563EB"        # blue-600 — primario
BLUE_DARK = "#1E3A8A"   # blue-900 — gradiente
INK = "#111827"         # gray-900 — texto
SLATE = "#475569"       # texto secundario
WHITE = "#FFFFFF"

# ── Identidad verbal ─────────────────────────────────────────────────
BRAND = "Recontrata"
SITE = "recontrata.cl"
CTA = "Pruébalo en recontrata.cl"
ACCESS_CODE = "recontrata2211"   # gate de pre-lanzamiento

# ── Produccion de video ──────────────────────────────────────────────
VIDEO_W = 1920
VIDEO_H = 1080
FPS = 30
TTS_MODEL = "gpt-4o-mini-tts"
TTS_VOICE = "alloy"
TTS_INSTRUCTIONS = (
    "Eres un narrador profesional de videos tutoriales. Hablas en español "
    "latinoamericano neutro con acento chileno natural y cálido. Pronunciación "
    "clara, ritmo pausado y didáctico. Evita POR COMPLETO cualquier rasgo de "
    "acento estadounidense o anglosajón: vocales puras, erre y doble erre bien "
    "marcadas, sin aspirar consonantes ni arrastrar las vocales."
)

# ── Fuentes (Windows) ────────────────────────────────────────────────
FONT_BOLD = "C:/Windows/Fonts/arialbd.ttf"
FONT_REG = "C:/Windows/Fonts/arial.ttf"


def _find(tool: str) -> str:
    found = shutil.which(tool)
    if found:
        return found
    link = Path.home() / f"AppData/Local/Microsoft/WinGet/Links/{tool}.exe"
    if link.exists():
        return str(link)
    hits = list((Path.home() / "AppData/Local/Microsoft/WinGet/Packages").glob(
        f"Gyan.FFmpeg*/**/bin/{tool}.exe"))
    return str(hits[0]) if hits else tool


FFMPEG = _find("ffmpeg")
FFPROBE = _find("ffprobe")


def openai_key() -> str:
    """Lee la OPENAI_API_KEY de la variable de entorno (no de ningún .env)."""
    import os
    k = os.environ.get("OPENAI_API_KEY")
    if not k:
        raise RuntimeError(
            "Falta OPENAI_API_KEY en el entorno. Expórtala antes de correr el TTS, "
            "por ejemplo: setx OPENAI_API_KEY \"sk-…\" (y reabre la terminal), o "
            "$env:OPENAI_API_KEY=\"sk-…\" en PowerShell.")
    return k
