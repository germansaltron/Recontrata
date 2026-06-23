"""Clip 3 — Crea tu faena (dashboard autenticado, escritorio).
Crea un proyecto y le asigna trabajadores. Usa el kit común (clipkit).
Requiere el dev server: cd frontend && npm run dev
"""
import sys
import time

import brand
import clipkit as kit

PREFIX = "clip3"
DUR_FILE = brand.OUTPUT_DIR / "clip3_durations.json"
LEAD_FILE = brand.OUTPUT_DIR / "clip3_leads.json"
OUT = brand.OUTPUT_DIR / "clip3.mp4"
INTRO_SECS, OUTRO_SECS = 4.0, 4.0

SCENES = {
    "esc2": "En Recontrata, cada faena o contrato es un 'proyecto'. Así sabes quién "
            "trabajó dónde, y el desempeño queda asociado al lugar correcto. Entra a 'Proyectos'.",
    "esc3": "Crea el proyecto con su nombre, el cliente y las fechas. Déjalo en estado "
            "'Activo' cuando ya esté en marcha: eso es lo que te habilita para evaluar a la cuadrilla.",
    "esc4": "Ahora asigna a los trabajadores que estuvieron en esta faena. Recontrata te "
            "irá mostrando cuántos te faltan por evaluar, para que no se te quede nadie afuera.",
    "esc5": "Faena lista, cuadrilla asignada. Llegó lo importante: evaluar. Te espero en el próximo video.",
}
ORDER = ["esc2", "esc3", "esc4", "esc5"]
SUBS = {
    "esc2": [
        "En Recontrata, cada faena o contrato es un 'proyecto'.",
        "Así sabes quién trabajó dónde, y el desempeño queda asociado al lugar correcto.",
        "Entra a 'Proyectos'.",
    ],
    "esc3": [
        "Crea el proyecto con su nombre, el cliente y las fechas.",
        "Déjalo en estado 'Activo' cuando ya esté en marcha:",
        "eso es lo que te habilita para evaluar a la cuadrilla.",
    ],
    "esc4": [
        "Ahora asigna a los trabajadores que estuvieron en esta faena.",
        "Recontrata te irá mostrando cuántos te faltan por evaluar,",
        "para que no se te quede nadie afuera.",
    ],
    "esc5": [
        "Faena lista, cuadrilla asignada.",
        "Llegó lo importante: evaluar.",
        "Te espero en el próximo video.",
    ],
}

PROJECT = {"id": "p1", "name": "Parada de Planta de Ácido N°2", "client_name": "Codelco",
           "location": "Calama", "start_date": "2026-02-01", "end_date": "2026-03-15",
           "status": "active", "worker_count": 0, "evaluation_count": 0,
           "created_at": "2026-01-02T00:00:00"}
CREW5 = [kit.pworker(i + 1, *kit.ROSTER[i]) for i in range(5)]


def esc2(page, dur, t0):
    page.goto(f"{kit.BASE}/app", wait_until="domcontentloaded")
    page.wait_for_selector("h1", state="visible", timeout=12000)
    lead = time.time() - t0
    page.wait_for_timeout(800)
    link = page.get_by_role("link", name="Proyectos").first
    kit.move_to(page, link); link.click()
    page.wait_for_selector("text=No hay proyectos", timeout=8000)
    page.wait_for_timeout(int(dur * 0.30 * 1000))
    return lead


def esc3(page, dur, t0):
    page.goto(f"{kit.BASE}/app/projects", wait_until="domcontentloaded")
    page.wait_for_selector("h1", state="visible", timeout=12000)
    lead = time.time() - t0
    page.wait_for_timeout(500)
    nuevo = page.get_by_role("button", name="Nuevo Proyecto").first
    kit.move_to(page, nuevo); nuevo.click()
    # .fill() (no hace hit-test de puntero) evita que el label del modal intercepte el click.
    name_in = page.locator("input[placeholder='Mantención Molino SAG']").first
    name_in.wait_for(state="visible", timeout=6000)
    kit.move_to(page, name_in); name_in.fill("Parada de Planta de Ácido N°2")
    page.wait_for_timeout(350)
    cli = page.locator("input[placeholder='Minera Escondida']").first
    kit.move_to(page, cli); cli.fill("Codelco")
    page.wait_for_timeout(300)
    loc = page.locator("input[placeholder='Antofagasta']").first
    kit.move_to(page, loc); loc.fill("Calama")
    page.wait_for_timeout(300)
    dates = page.locator("input[type='date']")
    dates.nth(0).fill("2026-02-01")
    dates.nth(1).fill("2026-03-15")
    page.wait_for_timeout(400)
    crear = page.get_by_role("button", name="Crear Proyecto").first
    kit.move_to(page, crear); crear.click(force=True)
    try:
        name_in.wait_for(state="detached", timeout=8000)
    except Exception:
        page.wait_for_timeout(1500)
    page.wait_for_timeout(int(dur * 0.18 * 1000))
    return lead


def esc4(page, dur, t0):
    page.goto(f"{kit.BASE}/app/projects/p1", wait_until="domcontentloaded")
    page.wait_for_selector("h1", state="visible", timeout=12000)
    lead = time.time() - t0
    page.wait_for_timeout(600)
    asignar = page.get_by_role("button", name="Asignar").first
    kit.move_to(page, asignar); asignar.click(force=True)
    page.wait_for_selector("input[placeholder*='Buscar por nombre']", timeout=6000)
    # Click en el LABEL de cada trabajador (objetivo grande); force evita el hit-test del modal.
    for nm in ["Sergio Díaz", "Marcela Rojas", "Pedro Cáceres", "Luis Tapia", "Jorge Muñoz"]:
        lab = page.locator("label", has_text=nm).first
        lab.scroll_into_view_if_needed()
        kit.move_to(page, lab); lab.click(force=True)
        page.wait_for_timeout(230)
    page.wait_for_timeout(400)
    confirm = page.get_by_role("button", name="Asignar 5").first
    kit.move_to(page, confirm); confirm.click(force=True)
    page.wait_for_selector("text=sin evaluar", timeout=8000)
    page.wait_for_timeout(int(dur * 0.15 * 1000))
    return lead


def esc5(page, dur, t0):
    page.goto(f"{kit.BASE}/app/projects/p1", wait_until="domcontentloaded")
    page.wait_for_selector("text=sin evaluar", timeout=12000)
    lead = time.time() - t0
    page.wait_for_timeout(int(dur * 0.45 * 1000))
    page.mouse.wheel(0, 200)
    page.wait_for_timeout(int(dur * 0.35 * 1000))
    return lead


SCENE_FN = {"esc2": esc2, "esc3": esc3, "esc4": esc4, "esc5": esc5}
SCENE_INITIAL = {
    "esc2": {"projects": []},
    "esc3": {"projects": []},
    "esc4": {"projects": [PROJECT], "project_workers": {"p1": []}, "workers": kit.all_workers()},
    "esc5": {"projects": [PROJECT], "project_workers": {"p1": CREW5}},
}


def main():
    stage = sys.argv[1] if len(sys.argv) > 1 else "all"
    if stage in ("tts", "all"):
        print("[1/4] TTS…"); kit.tts(SCENES, ORDER, PREFIX, DUR_FILE)
    if stage in ("capture", "all"):
        print("[2/4] Captura…")
        kit.capture(PREFIX, ORDER, SCENE_FN, SCENE_INITIAL, DUR_FILE, LEAD_FILE)
    if stage in ("cards", "all"):
        print("[3/4] Tarjetas…")
        kit.make_cards(PREFIX, "Crea tu faena", "Tutorial 3 de 8", "Siguiente: La fórmula del puntaje")
    if stage in ("assemble", "all"):
        print("[4/4] Ensamblado…")
        kit.assemble(PREFIX, ORDER, SUBS, SCENES, INTRO_SECS, OUTRO_SECS, DUR_FILE, LEAD_FILE, OUT)
    print("OK")


if __name__ == "__main__":
    main()
