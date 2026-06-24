"""Clip 9 (opcional) — Evaluaciones más justas / Calibración (escritorio).

Explica la calibración de evaluadores (anti-sesgo): por cada evaluador, si es
indulgente/severo o cae en efecto halo, para que todos evalúen parejo. Recorre
/app/calibracion. Usa el kit común.
Requiere el dev server: cd frontend && npm run dev
"""
import sys
import time

import brand
import clipkit as kit

PREFIX = "clip9"
DUR_FILE = brand.OUTPUT_DIR / "clip9_durations.json"
LEAD_FILE = brand.OUTPUT_DIR / "clip9_leads.json"
OUT = brand.OUTPUT_DIR / "clip9.mp4"
INTRO_SECS, OUTRO_SECS = 4.0, 5.0

SCENES = {
    "esc2": "Todos lo sabemos: hay supervisores más exigentes y otros más blandos. Si uno "
            "pone puros cuatros y otro puros dos, comparar a sus trabajadores no es justo. "
            "Recontrata mide eso, y se llama calibración.",
    "esc3": "Por cada evaluador, ves si tiende a calificar más alto o más bajo que el resto, "
            "y si cae en el 'efecto halo' —poner casi la misma nota en todo. No es para "
            "señalar a nadie: es para conversar con tus supervisores y que todos evalúen "
            "parejo. Las notas no se cambian; solo se hacen más confiables.",
    "esc4": "Un puntaje justo es un puntaje en el que puedes confiar para decidir. Eso es "
            "calibración. Nos vemos en recontrata punto cl.",
}
ORDER = ["esc2", "esc3", "esc4"]
SUBS = {
    "esc2": [
        "Todos lo sabemos: hay supervisores más exigentes y otros más blandos.",
        "Si uno pone puros cuatros y otro puros dos, comparar a sus trabajadores no es justo.",
        "Recontrata mide eso, y se llama calibración.",
    ],
    "esc3": [
        "Por cada evaluador, ves si tiende a calificar más alto o más bajo que el resto,",
        "y si cae en el 'efecto halo' —poner casi la misma nota en todo.",
        "No es para señalar a nadie: es para conversar con tus supervisores y que todos evalúen parejo. Las notas no se cambian; solo se hacen más confiables.",
    ],
    "esc4": [
        "Un puntaje justo es un puntaje en el que puedes confiar para decidir.",
        "Eso es calibración. Nos vemos en recontrata punto cl.",
    ],
}

CALIBRATION = {
    "org_mean": 3.9, "min_sample": 3, "leniency_threshold": 0.4, "halo_threshold": 0.5,
    "evaluators": [
        {"evaluator_id": "u-german", "evaluator_name": "Germán Saltrón", "evaluation_count": 14,
         "mean_score": 4.4, "leniency_delta": 0.5, "dimension_spread": 1.1, "flags": ["lenient"]},
        {"evaluator_id": "u-rodrigo", "evaluator_name": "Rodrigo Rojas", "evaluation_count": 11,
         "mean_score": 3.3, "leniency_delta": -0.6, "dimension_spread": 0.9, "flags": ["severe"]},
        {"evaluator_id": "u-jorge", "evaluator_name": "Jorge Muñoz", "evaluation_count": 9,
         "mean_score": 3.9, "leniency_delta": 0.0, "dimension_spread": 0.3, "flags": ["halo"]},
        {"evaluator_id": "u-camila", "evaluator_name": "Camila Fuentes", "evaluation_count": 2,
         "mean_score": 4.0, "leniency_delta": 0.1, "dimension_spread": 0.7, "flags": ["low_sample"]},
    ],
}
DATA = {"workers": kit.all_workers(), "calibration": CALIBRATION}


def esc2(page, dur, t0):
    page.goto(f"{kit.BASE}/app", wait_until="domcontentloaded")
    page.wait_for_selector("h1", state="visible", timeout=12000)
    link = page.get_by_role("link", name="Calibración").first
    link.scroll_into_view_if_needed()
    kit.move_to(page, link); link.click()
    page.wait_for_selector("text=Germán Saltrón", timeout=10000)
    lead = time.time() - t0     # recorta dashboard + navegación
    page.wait_for_timeout(int(dur * 0.5 * 1000))
    return lead


def esc3(page, dur, t0):
    page.goto(f"{kit.BASE}/app/calibracion", wait_until="domcontentloaded")
    page.wait_for_selector("text=Germán Saltrón", timeout=12000)
    lead = time.time() - t0
    page.wait_for_timeout(int(dur * 0.45 * 1000))
    page.mouse.wheel(0, 240)        # recorrer columnas / leyenda
    page.wait_for_timeout(int(dur * 0.45 * 1000))
    return lead


def esc4(page, dur, t0):
    page.goto(f"{kit.BASE}/app/calibracion", wait_until="domcontentloaded")
    page.wait_for_selector("text=Germán Saltrón", timeout=12000)
    lead = time.time() - t0
    page.wait_for_timeout(int(dur * 0.5 * 1000))
    page.mouse.wheel(0, 280)        # mostrar la leyenda
    page.wait_for_timeout(int(dur * 0.35 * 1000))
    return lead


SCENE_FN = {"esc2": esc2, "esc3": esc3, "esc4": esc4}
SCENE_INITIAL = {n: dict(DATA) for n in ORDER}


def main():
    stage = sys.argv[1] if len(sys.argv) > 1 else "all"
    if stage in ("tts", "all"):
        print("[1/4] TTS…"); kit.tts(SCENES, ORDER, PREFIX, DUR_FILE)
    if stage in ("capture", "all"):
        print("[2/4] Captura…")
        kit.capture(PREFIX, ORDER, SCENE_FN, SCENE_INITIAL, DUR_FILE, LEAD_FILE)
    if stage in ("cards", "all"):
        print("[3/4] Tarjetas…")
        kit.make_cards(PREFIX, "Evaluaciones más justas", "Tutorial 9 · avanzado (opcional)",
                       "¡Gracias por ver la serie!")
    if stage in ("assemble", "all"):
        print("[4/4] Ensamblado…")
        kit.assemble(PREFIX, ORDER, SUBS, SCENES, INTRO_SECS, OUTRO_SECS, DUR_FILE, LEAD_FILE, OUT)
    print("OK")


if __name__ == "__main__":
    main()
