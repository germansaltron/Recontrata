"""Clip 5 — Evalúa en terreno, en 30 segundos (móvil, 375px).
El supervisor evalúa 5 dimensiones + recontratación y encadena al siguiente.
Las escenas del formulario pre-cargan el borrador (localStorage) para mostrar el
estado correcto sin re-hacer pasos. Usa el kit común (clipkit).
Requiere el dev server: cd frontend && npm run dev
"""
import sys
import time

import brand
import clipkit as kit

PREFIX = "clip5"
DUR_FILE = brand.OUTPUT_DIR / "clip5_durations.json"
LEAD_FILE = brand.OUTPUT_DIR / "clip5_leads.json"
OUT = brand.OUTPUT_DIR / "clip5.mp4"
INTRO_SECS, OUTRO_SECS = 4.0, 4.0
VIEWPORT = {"width": 390, "height": 844}

# Puntajes y motivo de la evaluación demo (Seguridad baja → "Con Reservas" coherente).
VALUES = [4, 3, 5, 4, 4]   # Calidad, Seguridad, Puntualidad, Equipo, Técnica
REASON = "Buen rendimiento, pero debe reforzar el uso de EPP en trabajos en altura."

SCENES = {
    "esc2": "Estás en terreno, con el celular. Toca 'Evaluar', elige la faena, y "
            "Recontrata te muestra al primero de tu cuadrilla. No tienes que buscar nada.",
    "esc3": "Calificas cinco cosas: calidad, seguridad, puntualidad, trabajo en equipo y "
            "habilidad técnica. Y no quedas a la deriva: al tocar una nota, Recontrata te "
            "dice exactamente qué significa ese nivel. Así dos supervisores califican "
            "parejo, y la evaluación es justa y defendible.",
    "esc4": "Y la pregunta que de verdad importa: ¿lo recontratarías? Sí, con reservas, o "
            "no. Si marcas reservas o no, Recontrata te pide el motivo — porque una "
            "decisión así siempre tiene que tener su porqué, por respeto al trabajador y "
            "para tu propio respaldo.",
    "esc5": "Guardas, y Recontrata te ofrece pasar al siguiente de la cuadrilla de "
            "inmediato. Así evalúas a todo el equipo de corrido, sin parar el trabajo. Y "
            "fíjate en los botones: grandes, pensados para usarse con una mano y con guantes puestos.",
    "esc6": "¿Y si en la faena no hay internet? Ningún problema. Eso es justo lo que vemos ahora.",
}
ORDER = ["esc2", "esc3", "esc4", "esc5", "esc6"]
SUBS = {
    "esc2": [
        "Estás en terreno, con el celular.",
        "Toca 'Evaluar', elige la faena, y Recontrata te muestra al primero de tu cuadrilla.",
        "No tienes que buscar nada.",
    ],
    "esc3": [
        "Calificas cinco cosas: calidad, seguridad, puntualidad, trabajo en equipo y habilidad técnica.",
        "Y no quedas a la deriva: al tocar una nota, Recontrata te dice exactamente qué significa ese nivel.",
        "Así dos supervisores califican parejo, y la evaluación es justa y defendible.",
    ],
    "esc4": [
        "Y la pregunta que de verdad importa: ¿lo recontratarías? Sí, con reservas, o no.",
        "Si marcas reservas o no, Recontrata te pide el motivo —",
        "porque una decisión así siempre tiene que tener su porqué, por respeto al trabajador y para tu propio respaldo.",
    ],
    "esc5": [
        "Guardas, y Recontrata te ofrece pasar al siguiente de la cuadrilla de inmediato.",
        "Así evalúas a todo el equipo de corrido, sin parar el trabajo.",
        "Y fíjate en los botones: grandes, pensados para usarse con una mano y con guantes puestos.",
    ],
    "esc6": [
        "¿Y si en la faena no hay internet? Ningún problema.",
        "Eso es justo lo que vemos ahora.",
    ],
}

PROJECT = {"id": "p1", "name": "Parada de Planta de Ácido N°2", "client_name": "Codelco",
           "location": "Calama", "start_date": "2026-02-01", "end_date": "2026-03-15",
           "status": "active", "worker_count": 5, "evaluation_count": 0,
           "created_at": "2026-01-02T00:00:00"}
CREW5 = [kit.pworker(i + 1, *kit.ROSTER[i]) for i in range(5)]


def _star_name(v):
    return f"{v} estrella" + ("" if v == 1 else "s")


def esc2(page, dur, t0):
    page.goto(f"{kit.BASE}/app", wait_until="domcontentloaded")
    page.wait_for_selector("h1", state="visible", timeout=12000)
    lead = time.time() - t0
    page.wait_for_timeout(700)
    ev = page.locator("nav[aria-label='Navegación principal'] a[href='/app/evaluate']").first
    ev.scroll_into_view_if_needed()
    kit.move_to(page, ev); ev.click(force=True)
    page.wait_for_selector("text=Evaluar Equipo", timeout=8000)
    page.wait_for_timeout(700)
    card = page.locator("a[href^='/app/evaluate/p1/']").first
    kit.move_to(page, card); card.click(force=True)
    page.wait_for_selector("text=Evaluar Trabajador", timeout=8000)
    page.wait_for_timeout(int(dur * 0.18 * 1000))
    return lead


def esc3(page, dur, t0):
    page.goto(f"{kit.BASE}/app/evaluate/p1/w1", wait_until="domcontentloaded")
    page.wait_for_selector("text=Evaluar Trabajador", timeout=12000)
    lead = time.time() - t0
    page.wait_for_timeout(500)
    for k, v in enumerate(VALUES):
        star = page.get_by_role("radio", name=_star_name(v)).nth(k)
        star.click()   # click normal: auto-scroll + actionability (no es modal)
        page.wait_for_timeout(550)
    page.wait_for_timeout(int(dur * 0.08 * 1000))
    return lead


def esc4(page, dur, t0):
    page.goto(f"{kit.BASE}/app/evaluate/p1/w1", wait_until="domcontentloaded")
    page.wait_for_selector("text=¿Recontratarías", timeout=12000)
    lead = time.time() - t0
    page.wait_for_timeout(600)
    btn = page.get_by_role("button", name="Con Reservas").first
    kit.move_to(page, btn); btn.click()
    page.wait_for_timeout(450)
    motivo = page.locator("textarea[placeholder*='Motivo']").first
    motivo.wait_for(state="visible", timeout=4000)
    kit.move_to(page, motivo); motivo.fill(REASON)
    page.wait_for_timeout(int(dur * 0.12 * 1000))
    return lead


def esc5(page, dur, t0):
    page.goto(f"{kit.BASE}/app/evaluate/p1/w1", wait_until="domcontentloaded")
    page.wait_for_selector("button:has-text('Guardar Evaluación')", timeout=12000)
    lead = time.time() - t0
    page.wait_for_timeout(700)
    save = page.get_by_role("button", name="Guardar Evaluación").first
    kit.move_to(page, save); save.click()
    sig = page.locator("text=Evaluar siguiente").first
    try:
        sig.wait_for(state="visible", timeout=6000)
        page.wait_for_timeout(900)
        kit.move_to(page, sig); sig.click(force=True)
        page.wait_for_selector("text=Evaluar Trabajador", timeout=8000)
    except Exception:
        page.wait_for_timeout(1500)
    page.wait_for_timeout(int(dur * 0.10 * 1000))
    return lead


def esc6(page, dur, t0):
    page.goto(f"{kit.BASE}/app/evaluate", wait_until="domcontentloaded")
    page.wait_for_selector("text=Evaluar Equipo", timeout=12000)
    lead = time.time() - t0
    page.wait_for_timeout(int(dur * 0.7 * 1000))
    return lead


SCENE_FN = {"esc2": esc2, "esc3": esc3, "esc4": esc4, "esc5": esc5, "esc6": esc6}
SCENE_INITIAL = {
    "esc2": {"projects": [PROJECT], "project_workers": {"p1": CREW5}, "workers": kit.all_workers()},
    "esc3": {"projects": [PROJECT], "project_workers": {"p1": CREW5}, "workers": kit.all_workers()},
    "esc4": {"projects": [PROJECT], "project_workers": {"p1": CREW5}, "workers": kit.all_workers()},
    "esc5": {"projects": [PROJECT], "project_workers": {"p1": CREW5}, "workers": kit.all_workers()},
    "esc6": {"projects": [PROJECT], "project_workers": {"p1": CREW5}, "evaluated": {"w1", "w2"}},
}
EXTRA_INIT = {
    "esc4": kit.draft_js("p1", "w1", VALUES),
    "esc5": kit.draft_js("p1", "w1", VALUES, "reservations", REASON),
}


def main():
    stage = sys.argv[1] if len(sys.argv) > 1 else "all"
    if stage in ("tts", "all"):
        print("[1/4] TTS…"); kit.tts(SCENES, ORDER, PREFIX, DUR_FILE)
    if stage in ("capture", "all"):
        print("[2/4] Captura…")
        kit.capture(PREFIX, ORDER, SCENE_FN, SCENE_INITIAL, DUR_FILE, LEAD_FILE,
                    viewport=VIEWPORT, extra_init=EXTRA_INIT)
    if stage in ("cards", "all"):
        print("[3/4] Tarjetas…")
        kit.make_cards(PREFIX, "Evalúa en terreno", "Tutorial 5 de 8",
                       "Siguiente: ¿Sin señal? Igual evalúas")
    if stage in ("assemble", "all"):
        print("[4/4] Ensamblado…")
        kit.assemble(PREFIX, ORDER, SUBS, SCENES, INTRO_SECS, OUTRO_SECS, DUR_FILE, LEAD_FILE, OUT)
    print("OK")


if __name__ == "__main__":
    main()
