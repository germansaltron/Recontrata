"""Clip 8 — Transparencia y confianza (Portal del Trabajador, escritorio).

El admin genera el enlace del portal; el trabajador entra sin login y ve sus puntajes y
la fórmula (nunca al evaluador); puede responder (réplica), pedir baja y descargar su
certificado. Último clip de la serie principal. Usa el kit común.
Requiere el dev server: cd frontend && npm run dev
"""
import sys
import time

import brand
import clipkit as kit

PREFIX = "clip8"
DUR_FILE = brand.OUTPUT_DIR / "clip8_durations.json"
LEAD_FILE = brand.OUTPUT_DIR / "clip8_leads.json"
OUT = brand.OUTPUT_DIR / "clip8.mp4"
INTRO_SECS, OUTRO_SECS = 4.0, 5.0
TOKEN = "demo-token"

SCENES = {
    "esc2": "Las 'listas negras' de trabajadores son ilegales, y con razón: nadie debería "
            "quedar marcado a sus espaldas, sin saberlo ni poder defenderse. Recontrata se "
            "construyó al revés: con transparencia. Y eso vive en el Portal del Trabajador.",
    "esc3": "Generas un enlace y se lo compartes al trabajador. Él entra sin crear cuenta y "
            "ve sus propios puntajes y cómo se calculan. Eso sí: nunca ve el nombre de quién "
            "lo evaluó. Transparencia con el dato, cuidado con las personas.",
    "esc4": "Y puede hacer tres cosas más: responder una evaluación con su versión —su "
            "derecho a réplica, visible para ambos—; pedir salir de la plataforma; y "
            "descargar un certificado con su desempeño, una especie de 'currículum de faena' "
            "que se lleva consigo. De herramienta del contratista, pasa a ser también un "
            "activo del trabajador.",
    "esc5": "Datos para decidir mejor, y transparencia para hacerlo bien. Eso es Recontrata. "
            "Empieza hoy en recontrata punto cl.",
}
ORDER = ["esc2", "esc3", "esc4", "esc5"]
SUBS = {
    "esc2": [
        "Las 'listas negras' de trabajadores son ilegales, y con razón:",
        "nadie debería quedar marcado a sus espaldas, sin saberlo ni poder defenderse.",
        "Recontrata se construyó al revés: con transparencia. Y eso vive en el Portal del Trabajador.",
    ],
    "esc3": [
        "Generas un enlace y se lo compartes al trabajador.",
        "Él entra sin crear cuenta y ve sus propios puntajes y cómo se calculan.",
        "Eso sí: nunca ve el nombre de quién lo evaluó. Transparencia con el dato, cuidado con las personas.",
    ],
    "esc4": [
        "Y puede hacer tres cosas más: responder una evaluación con su versión —su derecho a réplica, visible para ambos—;",
        "pedir salir de la plataforma; y descargar un certificado con su desempeño, una especie de 'currículum de faena' que se lleva consigo.",
        "De herramienta del contratista, pasa a ser también un activo del trabajador.",
    ],
    "esc5": [
        "Datos para decidir mejor, y transparencia para hacerlo bien.",
        "Eso es Recontrata. Empieza hoy en recontrata punto cl.",
    ],
}

# ── Datos sembrados (Sergio Díaz) ────────────────────────────────────
_SERGIO_EVALS = [
    kit.eval_summary(1, "Mantención Molino SAG", (4, 3, 4, 4, 4), "reservations",
                     "2025-11-10T10:00:00", reason="Reforzar el uso de EPP en trabajos en altura."),
    kit.eval_summary(2, "Montaje Correa Overland CV-7", (5, 5, 4, 4, 5), "yes", "2026-01-15T10:00:00"),
    kit.eval_summary(3, "Parada de Planta de Ácido N°2", (5, 5, 5, 5, 5), "yes", "2026-04-22T10:00:00"),
]
SERGIO_DETAIL = kit.worker_detail("w1", 15333444, "Sergio", "Díaz", "Soldador", _SERGIO_EVALS)

_PORTAL_EVALS = [
    kit.portal_eval(1, "Mantención Molino SAG", (4, 3, 4, 4, 4), "reservations",
                    "2025-11-10T10:00:00", reason="Reforzar el uso de EPP en trabajos en altura."),
    kit.portal_eval(2, "Montaje Correa Overland CV-7", (5, 5, 4, 4, 5), "yes", "2026-01-15T10:00:00"),
    kit.portal_eval(3, "Parada de Planta de Ácido N°2", (5, 5, 5, 5, 5), "yes", "2026-04-22T10:00:00"),
]
SERGIO_PORTAL = kit.portal_profile("Sergio Díaz", 15333444, "Soldador", _PORTAL_EVALS)

DATA = {"workers": kit.all_workers(), "worker_details": {"w1": SERGIO_DETAIL},
        "portal_profile": SERGIO_PORTAL}


def esc2(page, dur, t0):
    page.goto(f"{kit.BASE}/app/workers/w1", wait_until="domcontentloaded")
    page.wait_for_selector("text=Portal del trabajador", timeout=12000)
    lead = time.time() - t0
    card = page.get_by_text("Portal del trabajador").first
    card.scroll_into_view_if_needed()
    kit.move_to(page, card)
    page.wait_for_timeout(int(dur * 0.55 * 1000))
    return lead


def esc3(page, dur, t0):
    page.goto(f"{kit.BASE}/app/workers/w1", wait_until="domcontentloaded")
    page.wait_for_selector("text=Portal del trabajador", timeout=12000)
    lead = time.time() - t0
    gen = page.get_by_role("button", name="Generar enlace").first
    gen.scroll_into_view_if_needed()
    kit.move_to(page, gen); gen.click()
    page.wait_for_selector("text=Copiar", timeout=8000)
    page.wait_for_timeout(int(dur * 0.20 * 1000))
    page.goto(f"{kit.BASE}/p/{TOKEN}", wait_until="domcontentloaded")   # vista del trabajador
    page.wait_for_selector("text=Tus evaluaciones", timeout=10000)
    page.wait_for_timeout(int(dur * 0.30 * 1000))
    return lead


def esc4(page, dur, t0):
    page.goto(f"{kit.BASE}/p/{TOKEN}", wait_until="domcontentloaded")
    page.wait_for_selector("text=Tus evaluaciones", timeout=12000)
    lead = time.time() - t0
    page.wait_for_timeout(400)
    # 1) réplica
    resp = page.get_by_role("button", name="Responder a esta evaluación").first
    resp.scroll_into_view_if_needed()
    kit.move_to(page, resp); resp.click()
    ta = page.locator("textarea[placeholder*='Escribe tu respuesta']").first
    ta.wait_for(state="visible", timeout=5000)
    kit.move_to(page, ta)
    ta.fill("En esa faena el andamio llegó tarde por bodega; ya quedó regularizado con prevención.")
    enviar = page.get_by_role("button", name="Enviar respuesta").first
    kit.move_to(page, enviar); enviar.click()
    page.wait_for_selector("text=Tu respuesta", timeout=8000)
    page.wait_for_timeout(int(dur * 0.12 * 1000))
    # 2) mostrar el botón de baja (sin confirmar)
    opt = page.get_by_role("button", name="Solicitar dejar de ser evaluado").first
    opt.scroll_into_view_if_needed()
    kit.move_to(page, opt)
    page.wait_for_timeout(int(dur * 0.10 * 1000))
    # 3) certificado
    cert = page.get_by_role("link", name="Descargar mi certificado").first
    cert.scroll_into_view_if_needed()
    kit.move_to(page, cert); cert.click()
    page.wait_for_selector("text=Certificado de desempeño", timeout=10000)
    page.wait_for_timeout(int(dur * 0.12 * 1000))
    return lead


def esc5(page, dur, t0):
    page.goto(f"{kit.BASE}/p/{TOKEN}/certificado", wait_until="domcontentloaded")
    page.wait_for_selector("text=Certificado de desempeño", timeout=12000)
    lead = time.time() - t0
    page.wait_for_timeout(int(dur * 0.5 * 1000))
    page.mouse.wheel(0, 320)
    page.wait_for_timeout(int(dur * 0.4 * 1000))
    return lead


SCENE_FN = {"esc2": esc2, "esc3": esc3, "esc4": esc4, "esc5": esc5}
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
        kit.make_cards(PREFIX, "Transparencia y confianza", "Tutorial 8 de 8",
                       "Serie completa — ¡gracias!")
    if stage in ("assemble", "all"):
        print("[4/4] Ensamblado…")
        kit.assemble(PREFIX, ORDER, SUBS, SCENES, INTRO_SECS, OUTRO_SECS, DUR_FILE, LEAD_FILE, OUT)
    print("OK")


if __name__ == "__main__":
    main()
