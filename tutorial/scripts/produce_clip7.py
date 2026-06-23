"""Clip 7 — Decide con datos (dashboard autenticado, escritorio).

Lee el panel (top trabajadores + evaluaciones recientes + totales) y el historial de un
trabajador (promedio por dimensión, tendencia, historial faena por faena, export CSV).
El mock se siembra con datos ya evaluados. Usa el kit común.
Requiere el dev server: cd frontend && npm run dev
"""
import sys
import time

import brand
import clipkit as kit

PREFIX = "clip7"
DUR_FILE = brand.OUTPUT_DIR / "clip7_durations.json"
LEAD_FILE = brand.OUTPUT_DIR / "clip7_leads.json"
OUT = brand.OUTPUT_DIR / "clip7.mp4"
INTRO_SECS, OUTRO_SECS = 4.0, 4.0

SCENES = {
    "esc2": "Después de evaluar, todo se ordena en tu panel. De una mirada ves a tus "
            "mejores trabajadores, las evaluaciones más recientes y el pulso de tu "
            "operación. Esto antes vivía en tu cabeza; ahora está acá, ordenado.",
    "esc3": "Y si quieres el detalle, entra a cualquier trabajador: ahí está su desempeño "
            "en cada dimensión, faena por faena, con su tendencia en el tiempo. Y lo "
            "exportas a Excel para tus reuniones o tu carpeta de contratación.",
    "esc4": "Y este ranking no es un promedio cualquiera: usa el puntaje ponderado por tu "
            "industria —donde la seguridad pesa más—. Decisiones con datos, no con "
            "memoria. Y como esto habla de personas, en el próximo video vemos cómo "
            "Recontrata cuida también al trabajador.",
}
ORDER = ["esc2", "esc3", "esc4"]
SUBS = {
    "esc2": [
        "Después de evaluar, todo se ordena en tu panel.",
        "De una mirada ves a tus mejores trabajadores, las evaluaciones más recientes y el pulso de tu operación.",
        "Esto antes vivía en tu cabeza; ahora está acá, ordenado.",
    ],
    "esc3": [
        "Y si quieres el detalle, entra a cualquier trabajador:",
        "ahí está su desempeño en cada dimensión, faena por faena, con su tendencia en el tiempo.",
        "Y lo exportas a Excel para tus reuniones o tu carpeta de contratación.",
    ],
    "esc4": [
        "Y este ranking no es un promedio cualquiera: usa el puntaje ponderado por tu industria —donde la seguridad pesa más—.",
        "Decisiones con datos, no con memoria.",
        "Y como esto habla de personas, en el próximo video vemos cómo Recontrata cuida también al trabajador.",
    ],
}

# ── Datos sembrados ──────────────────────────────────────────────────
# Historial de Sergio Díaz (w1): mejora a través de las faenas (tendencia al alza).
SERGIO_EVALS = [
    kit.eval_summary(1, "Mantención Molino SAG", (4, 3, 4, 4, 4), "reservations",
                     "2025-11-10T10:00:00", reason="Reforzar el uso de EPP en trabajos en altura."),
    kit.eval_summary(2, "Montaje Correa Overland CV-7", (5, 5, 4, 4, 5), "yes", "2026-01-15T10:00:00"),
    kit.eval_summary(3, "Parada de Planta de Ácido N°2", (5, 5, 5, 5, 5), "yes", "2026-04-22T10:00:00"),
]
SERGIO_DETAIL = kit.worker_detail("w1", 15333444, "Sergio", "Díaz", "Soldador", SERGIO_EVALS)

TOP_WORKERS = [
    {"id": "w1", "full_name": "Sergio Díaz", "specialty": "Soldador", "evaluation_count": 3,
     "avg_score": SERGIO_DETAIL["avg_scores"]["overall"], "would_rehire_pct": 67},
    {"id": "w2", "full_name": "Marcela Rojas", "specialty": "Supervisor", "evaluation_count": 2,
     "avg_score": 4.3, "would_rehire_pct": 100},
    {"id": "w3", "full_name": "Pedro Cáceres", "specialty": "Mecánico", "evaluation_count": 2,
     "avg_score": 4.0, "would_rehire_pct": 100},
    {"id": "w6", "full_name": "Camila Fuentes", "specialty": "Prevencionista", "evaluation_count": 2,
     "avg_score": 3.8, "would_rehire_pct": 50},
    {"id": "w4", "full_name": "Luis Tapia", "specialty": "Eléctrico", "evaluation_count": 1,
     "avg_score": 3.5, "would_rehire_pct": 0},
]
RECENT = [
    {"id": "r1", "worker_id": "w1", "worker_name": "Sergio Díaz",
     "project_name": "Parada de Planta de Ácido N°2", "score_average": 5.0,
     "score_weighted": 5.0, "would_rehire": "yes", "created_at": "2026-06-20T10:00:00"},
    {"id": "r2", "worker_id": "w2", "worker_name": "Marcela Rojas",
     "project_name": "Parada de Planta de Ácido N°2", "score_average": 4.4,
     "score_weighted": 4.5, "would_rehire": "yes", "created_at": "2026-06-19T10:00:00"},
    {"id": "r3", "worker_id": "w3", "worker_name": "Pedro Cáceres",
     "project_name": "Montaje Correa Overland CV-7", "score_average": 4.0,
     "score_weighted": 4.0, "would_rehire": "reservations", "created_at": "2026-06-18T10:00:00"},
    {"id": "r4", "worker_id": "w4", "worker_name": "Luis Tapia",
     "project_name": "Mantención Molino SAG", "score_average": 3.6,
     "score_weighted": 3.5, "would_rehire": "no", "created_at": "2026-06-15T10:00:00"},
]
STATS = {"project_count": 3, "active_project_count": 2, "worker_count": 8,
         "evaluation_count": 12, "avg_score_overall": 4.2, "rehire_rate": 0.83,
         "specialty_distribution": []}

DATA = {"stats": STATS, "top_workers": TOP_WORKERS, "recent": RECENT,
        "worker_details": {"w1": SERGIO_DETAIL}, "workers": kit.all_workers()}


def esc2(page, dur, t0):
    page.goto(f"{kit.BASE}/app", wait_until="domcontentloaded")
    page.wait_for_selector("text=Top Trabajadores", timeout=12000)
    lead = time.time() - t0
    page.wait_for_timeout(int(dur * 0.55 * 1000))
    page.mouse.wheel(0, 160)
    page.wait_for_timeout(int(dur * 0.35 * 1000))
    return lead


def esc3(page, dur, t0):
    page.goto(f"{kit.BASE}/app", wait_until="domcontentloaded")
    page.wait_for_selector("text=Top Trabajadores", timeout=12000)
    lead = time.time() - t0
    page.wait_for_timeout(500)
    link = page.locator("a[href='/app/workers/w1']").first   # 1.º del Top → Sergio Díaz
    kit.move_to(page, link); link.click()
    page.wait_for_selector("text=Historial de Evaluaciones", timeout=12000)
    page.wait_for_timeout(int(dur * 0.30 * 1000))
    page.mouse.wheel(0, 360)                                  # mostrar dimensiones/tendencia
    page.wait_for_timeout(int(dur * 0.30 * 1000))
    page.mouse.wheel(0, 420)                                  # historial + CSV
    page.wait_for_timeout(int(dur * 0.20 * 1000))
    return lead


def esc4(page, dur, t0):
    page.goto(f"{kit.BASE}/app", wait_until="domcontentloaded")
    page.wait_for_selector("text=Top Trabajadores", timeout=12000)
    lead = time.time() - t0
    page.wait_for_timeout(int(dur * 0.85 * 1000))
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
        kit.make_cards(PREFIX, "Decide con datos", "Tutorial 7 de 8",
                       "Siguiente: Transparencia y confianza")
    if stage in ("assemble", "all"):
        print("[4/4] Ensamblado…")
        kit.assemble(PREFIX, ORDER, SUBS, SCENES, INTRO_SECS, OUTRO_SECS, DUR_FILE, LEAD_FILE, OUT)
    print("OK")


if __name__ == "__main__":
    main()
