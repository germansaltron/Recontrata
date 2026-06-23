"""Clip 6 — ¿Sin señal? Igual evalúas (móvil, 390px).

Muestra el modo offline: se cae la red (banner ámbar), se evalúa igual (la evaluación
se guarda en la cola IndexedDB), y al volver la señal se sincroniza sola. Se simula la
red con context.set_offline(). Usa el kit común.
Requiere el dev server: cd frontend && npm run dev
"""
import sys
import time

import brand
import clipkit as kit

PREFIX = "clip6"
DUR_FILE = brand.OUTPUT_DIR / "clip6_durations.json"
LEAD_FILE = brand.OUTPUT_DIR / "clip6_leads.json"
OUT = brand.OUTPUT_DIR / "clip6.mp4"
INTRO_SECS, OUTRO_SECS = 4.0, 4.0
VIEWPORT = {"width": 390, "height": 844}

VALUES = [4, 3, 5, 4, 4]
REASON = "Buen rendimiento, pero debe reforzar el uso de EPP en trabajos en altura."

SCENES = {
    "esc2": "En la mina, en el cerro, dentro de una nave… muchas veces no hay señal. Con "
            "otras apps, ahí se acaba todo. Recontrata te avisa que estás sin conexión, y "
            "sigue funcionando.",
    "esc3": "Evalúas igual que siempre: las cinco notas, la recontratación, guardas. Y "
            "aunque no haya internet, tu evaluación no se pierde: queda guardada en el "
            "teléfono, segura, esperando.",
    "esc4": "Recontrata lleva la cuenta de lo que tienes pendiente por enviar. Y en cuanto "
            "recuperas señal —al bajar del cerro, al volver al campamento— las manda solas, "
            "sin que tengas que acordarte de nada. Si prefieres, también puedes tocar "
            "'Sincronizar ahora'.",
    "esc5": "Evalúa donde sea, con o sin internet. Ahora veamos cómo todo eso se convierte "
            "en decisiones.",
}
ORDER = ["esc2", "esc3", "esc4", "esc5"]
SUBS = {
    "esc2": [
        "En la mina, en el cerro, dentro de una nave… muchas veces no hay señal.",
        "Con otras apps, ahí se acaba todo.",
        "Recontrata te avisa que estás sin conexión, y sigue funcionando.",
    ],
    "esc3": [
        "Evalúas igual que siempre: las cinco notas, la recontratación, guardas.",
        "Y aunque no haya internet, tu evaluación no se pierde:",
        "queda guardada en el teléfono, segura, esperando.",
    ],
    "esc4": [
        "Recontrata lleva la cuenta de lo que tienes pendiente por enviar.",
        "Y en cuanto recuperas señal —al bajar del cerro, al volver al campamento— las manda solas, sin que tengas que acordarte de nada.",
        "Si prefieres, también puedes tocar 'Sincronizar ahora'.",
    ],
    "esc5": [
        "Evalúa donde sea, con o sin internet.",
        "Ahora veamos cómo todo eso se convierte en decisiones.",
    ],
}

PROJECT = {"id": "p1", "name": "Parada de Planta de Ácido N°2", "client_name": "Codelco",
           "location": "Calama", "start_date": "2026-02-01", "end_date": "2026-03-15",
           "status": "active", "worker_count": 5, "evaluation_count": 0,
           "created_at": "2026-01-02T00:00:00"}
CREW5 = [kit.pworker(i + 1, *kit.ROSTER[i]) for i in range(5)]


def esc2(page, dur, t0):
    page.goto(f"{kit.BASE}/app/evaluate/p1/w1", wait_until="domcontentloaded")
    page.wait_for_selector("text=Evaluar Trabajador", timeout=12000)
    lead = time.time() - t0
    page.wait_for_timeout(700)
    page.context.set_offline(True)            # se cae la red
    page.wait_for_selector("text=Sin conexión", timeout=6000)
    page.wait_for_timeout(int(dur * 0.45 * 1000))
    return lead


def _preload_and_open_eval(page):
    """Precarga el chunk de ProjectDetail y abre el formulario por la app (client-side),
    para que ambos chunks queden en memoria y la navegación tras guardar funcione offline
    (en dev los chunks lazy no están cacheados como en prod)."""
    page.goto(f"{kit.BASE}/app/projects/p1", wait_until="domcontentloaded")
    page.wait_for_selector("text=sin evaluar", timeout=12000)
    page.locator("a[href^='/app/evaluate/p1/']").first.click()
    page.wait_for_selector("button:has-text('Guardar Evaluación')", timeout=12000)
    page.wait_for_timeout(500)


def esc3(page, dur, t0):
    _preload_and_open_eval(page)
    lead = time.time() - t0     # recorta la precarga; el video empieza en el formulario
    page.context.set_offline(True)
    page.wait_for_selector("text=Sin conexión", timeout=6000)
    page.wait_for_timeout(600)
    save = page.get_by_role("button", name="Guardar Evaluación").first
    save.scroll_into_view_if_needed()
    kit.move_to(page, save); save.click()
    page.wait_for_selector("text=guardada en el dispositivo", timeout=8000)
    page.wait_for_timeout(int(dur * 0.20 * 1000))
    return lead


def esc4(page, dur, t0):
    _preload_and_open_eval(page)
    lead = time.time() - t0
    page.context.set_offline(True)
    page.wait_for_selector("text=Sin conexión", timeout=6000)
    save = page.get_by_role("button", name="Guardar Evaluación").first
    save.scroll_into_view_if_needed()
    kit.move_to(page, save); save.click()
    page.wait_for_selector("text=guardada en el dispositivo", timeout=8000)
    page.wait_for_timeout(int(dur * 0.32 * 1000))   # banner ámbar; "lleva la cuenta"
    page.context.set_offline(False)                 # vuelve la señal -> sincroniza sola
    try:
        page.wait_for_selector("text=sincronizada", timeout=9000)
    except Exception:
        page.wait_for_timeout(2500)
    page.wait_for_timeout(int(dur * 0.15 * 1000))
    return lead


def esc5(page, dur, t0):
    page.goto(f"{kit.BASE}/app", wait_until="domcontentloaded")
    page.wait_for_selector("h1", state="visible", timeout=12000)
    lead = time.time() - t0
    page.wait_for_timeout(int(dur * 0.8 * 1000))
    return lead


SCENE_FN = {"esc2": esc2, "esc3": esc3, "esc4": esc4, "esc5": esc5}
_BASE = {"projects": [PROJECT], "project_workers": {"p1": CREW5}, "workers": kit.all_workers()}
SCENE_INITIAL = {
    "esc2": dict(_BASE),
    "esc3": dict(_BASE),
    "esc4": dict(_BASE, post_eval_delay=1.2),   # delay -> "Sincronizando…" visible
    "esc5": {"projects": [PROJECT], "project_workers": {"p1": CREW5}},
}
# Ambas escenas abren el primer pendiente (w1) vía "Evaluar"; el borrador es para w1.
EXTRA_INIT = {
    "esc3": kit.draft_js("p1", "w1", VALUES, "reservations", REASON),
    "esc4": kit.draft_js("p1", "w1", VALUES, "reservations", REASON),
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
        kit.make_cards(PREFIX, "¿Sin señal? Igual evalúas", "Tutorial 6 de 8",
                       "Siguiente: Decide con datos")
    if stage in ("assemble", "all"):
        print("[4/4] Ensamblado…")
        kit.assemble(PREFIX, ORDER, SUBS, SCENES, INTRO_SECS, OUTRO_SECS, DUR_FILE, LEAD_FILE, OUT)
    print("OK")


if __name__ == "__main__":
    main()
