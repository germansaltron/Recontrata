"""Clip 4 — La fórmula del puntaje (dashboard autenticado, escritorio).

Explica que el puntaje NO es un promedio plano: cada dimensión pesa distinto según la
industria (en construcción/minería la Seguridad pesa 30% y la Puntualidad 10%), y que el
perfil de pesos se puede cambiar. Recorre la página /app/formula. Usa el kit común.
Requiere el dev server: cd frontend && npm run dev
"""
import sys
import time

import brand
import clipkit as kit

PREFIX = "clip4"
DUR_FILE = brand.OUTPUT_DIR / "clip4_durations.json"
LEAD_FILE = brand.OUTPUT_DIR / "clip4_leads.json"
OUT = brand.OUTPUT_DIR / "clip4.mp4"
INTRO_SECS, OUTRO_SECS = 4.0, 4.0

SCENES = {
    "esc2": "No todas las faenas son iguales, y no todo pesa lo mismo. En 'Fórmula del "
            "puntaje', Recontrata te muestra con total transparencia cómo se calcula la "
            "nota de cada trabajador.",
    "esc3": "En construcción y minería, la Seguridad es lo que más pesa: un treinta por "
            "ciento. La Puntualidad, solo un diez. Así, quien es impecable en seguridad "
            "sube más que quien apenas llega temprano. El puntaje es la suma de cada "
            "dimensión por su peso.",
    "esc4": "¿Tu operación es distinta? Cambias el perfil con un clic. En logística, la "
            "puntualidad pesa más; en taller, la calidad. El perfil que elijas se aplica a "
            "las evaluaciones nuevas.",
    "esc5": "Reglas claras, iguales para todos y a la vista. Eso hace que una evaluación "
            "sea justa y defendible. Ahora sí: vamos a evaluar.",
}
ORDER = ["esc2", "esc3", "esc4", "esc5"]
SUBS = {
    "esc2": [
        "No todas las faenas son iguales, y no todo pesa lo mismo.",
        "En 'Fórmula del puntaje', Recontrata te muestra con total transparencia cómo se calcula la nota de cada trabajador.",
    ],
    "esc3": [
        "En construcción y minería, la Seguridad es lo que más pesa: un treinta por ciento. La Puntualidad, solo un diez.",
        "Así, quien es impecable en seguridad sube más que quien apenas llega temprano.",
        "El puntaje es la suma de cada dimensión por su peso.",
    ],
    "esc4": [
        "¿Tu operación es distinta? Cambias el perfil con un clic.",
        "En logística, la puntualidad pesa más; en taller, la calidad.",
        "El perfil que elijas se aplica a las evaluaciones nuevas.",
    ],
    "esc5": [
        "Reglas claras, iguales para todos y a la vista.",
        "Eso hace que una evaluación sea justa y defendible.",
        "Ahora sí: vamos a evaluar.",
    ],
}


def esc2(page, dur, t0):
    page.goto(f"{kit.BASE}/app", wait_until="domcontentloaded")
    page.wait_for_selector("h1", state="visible", timeout=12000)
    lead = time.time() - t0
    page.wait_for_timeout(800)
    link = page.get_by_role("link", name="Fórmula del puntaje").first
    kit.move_to(page, link); link.click()
    page.wait_for_selector("text=Perfil activo", timeout=8000)
    page.wait_for_timeout(int(dur * 0.28 * 1000))
    return lead


def esc3(page, dur, t0):
    page.goto(f"{kit.BASE}/app/formula", wait_until="domcontentloaded")
    page.wait_for_selector("text=Perfil activo", timeout=12000)
    lead = time.time() - t0
    page.wait_for_timeout(int(dur * 0.55 * 1000))
    page.mouse.wheel(0, 160)
    page.wait_for_timeout(int(dur * 0.35 * 1000))
    return lead


def esc4(page, dur, t0):
    page.goto(f"{kit.BASE}/app/formula", wait_until="domcontentloaded")
    page.wait_for_selector("text=Industria de la organización", timeout=12000)
    lead = time.time() - t0
    page.wait_for_timeout(500)
    log = page.get_by_role("button", name="Logística / Transporte").first
    log.scroll_into_view_if_needed()
    kit.move_to(page, log); log.click()
    page.wait_for_timeout(1600)   # toast + recarga: los pesos se reordenan
    con = page.get_by_role("button", name="Construcción / Minería").first
    con.scroll_into_view_if_needed()
    kit.move_to(page, con); con.click()
    page.wait_for_timeout(int(dur * 0.18 * 1000))
    return lead


def esc5(page, dur, t0):
    page.goto(f"{kit.BASE}/app/formula", wait_until="domcontentloaded")
    page.wait_for_selector("text=Perfil activo", timeout=12000)
    lead = time.time() - t0
    page.wait_for_timeout(int(dur * 0.8 * 1000))
    return lead


SCENE_FN = {"esc2": esc2, "esc3": esc3, "esc4": esc4, "esc5": esc5}
SCENE_INITIAL = {n: {"active_industry": "construccion_mineria"} for n in ORDER}


def main():
    stage = sys.argv[1] if len(sys.argv) > 1 else "all"
    if stage in ("tts", "all"):
        print("[1/4] TTS…"); kit.tts(SCENES, ORDER, PREFIX, DUR_FILE)
    if stage in ("capture", "all"):
        print("[2/4] Captura…")
        kit.capture(PREFIX, ORDER, SCENE_FN, SCENE_INITIAL, DUR_FILE, LEAD_FILE)
    if stage in ("cards", "all"):
        print("[3/4] Tarjetas…")
        kit.make_cards(PREFIX, "La fórmula del puntaje", "Tutorial 4 de 8",
                       "Siguiente: Evalúa en terreno")
    if stage in ("assemble", "all"):
        print("[4/4] Ensamblado…")
        kit.assemble(PREFIX, ORDER, SUBS, SCENES, INTRO_SECS, OUTRO_SECS, DUR_FILE, LEAD_FILE, OUT)
    print("OK")


if __name__ == "__main__":
    main()
