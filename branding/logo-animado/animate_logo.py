"""
Animación del logo de Recontrata (concepto B: flecha de retorno).
Anima: aparición del cuadro -> trazado del arco (barrido angular) -> la flecha
de retorno (Lucide rotate-ccw) queda dibujada -> giro de cierre del ciclo ->
entrada del wordmark. Exporta MP4 + GIF (claro y oscuro).

La marca NO se dibuja a mano: se rasteriza el SVG real de Lucide con resvg, de
modo que la punta de la flecha es exactamente la del símbolo (apunta "hacia
adentro", retorno), nunca hacia afuera. El trazado se simula revelando el arco
por ángulo polar desde la cola hasta la punta.

Reproducible:  python animate_logo.py   (requiere: pip install resvg-py pillow imageio imageio-ffmpeg numpy)
Salida:        output/recontrata_intro.mp4 + .gif  (claro)
               output/recontrata_intro_dark.mp4 + .gif  (oscuro)
"""
import io
import math
import os

import numpy as np
import resvg_py
from PIL import Image, ImageDraw, ImageFont

# ----------------------------------------------------------------------------
SS = 2                      # supersampling para antialias del canvas
W, H = 1600, 900           # tamaño final
FPS = 30
DUR = 3.2                  # segundos
N = int(FPS * DUR)
RASTER = 600               # resolución a la que se rasteriza la marca (px)
OUT = os.path.join(os.path.dirname(__file__), "output")
os.makedirs(OUT, exist_ok=True)

BLUE = (37, 99, 235)        # #2563eb
BLUE_D = (59, 130, 246)     # #3b82f6  (sobre fondo oscuro)
INK = (30, 41, 59)          # #1e293b
INK_LIGHT = (226, 232, 240) # #e2e8f0
WHITE = (255, 255, 255)

# Geometría del símbolo Lucide dentro del viewBox 0..100 de la marca.
_MARK_SCALE = 2.0833                       # escala del icono 24px
_MARK_T = 50 - 12 * _MARK_SCALE            # traslación para centrar (12,12)->50

# Camino del trazo (rotate-ccw): cola en (3,12), punta de flecha en (3,8).
_REVEAL_SWEEP = 345.0       # grados a revelar (cola -> punta ~336°, con holgura)


def _svg_square(blue):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{RASTER}" height="{RASTER}" '
        f'viewBox="0 0 100 100">'
        f'<rect x="4" y="4" width="92" height="92" rx="20" '
        f'fill="rgb({blue[0]},{blue[1]},{blue[2]})"/></svg>'
    )


def _svg_arrow():
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{RASTER}" height="{RASTER}" '
        f'viewBox="0 0 100 100">'
        f'<g transform="translate({_MARK_T:.3f},{_MARK_T:.3f}) scale({_MARK_SCALE:.4f})" '
        f'fill="none" stroke="#ffffff" stroke-width="2.4" '
        f'stroke-linecap="round" stroke-linejoin="round">'
        f'<path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/>'
        f'<path d="M3 3v5h5"/>'
        f'</g></svg>'
    )


def _rasterize(svg):
    raw = resvg_py.svg_to_bytes(svg_string=svg)
    return Image.open(io.BytesIO(bytes(raw))).convert("RGBA")


def _reveal_rel(size):
    """Matriz (size,size) con el 'progreso angular' 0..~345 de cada pixel a lo
    largo del trazo del arco (0 = cola en (3,12), creciente en sentido de
    dibujado hasta la punta de flecha). Sirve de máscara de revelado."""
    cx = cy = size / 2.0
    ys, xs = np.mgrid[0:size, 0:size]
    ang = np.degrees(np.arctan2(ys - cy, xs - cx))   # -180..180, y hacia abajo
    rel = (180.0 - ang) % 360.0                      # 0 en la cola (ang=180)
    return rel


def find_font(size):
    for name in ("segoeuib.ttf", "seguisb.ttf", "arialbd.ttf", "Arial Bold.ttf"):
        for base in (r"C:\Windows\Fonts", "/usr/share/fonts", os.path.expanduser("~/.fonts")):
            p = os.path.join(base, name)
            if os.path.exists(p):
                try:
                    return ImageFont.truetype(p, size)
                except Exception:
                    pass
    try:
        return ImageFont.truetype("DejaVuSans-Bold.ttf", size)
    except Exception:
        return ImageFont.load_default()


def ease_out(t):       # cubic ease-out
    return 1 - (1 - t) ** 3


def ease_in_out(t):
    return 3 * t * t - 2 * t * t * t


def clamp01(x):
    return max(0.0, min(1.0, x))


def seg(t, a, b):
    """progreso 0..1 del tramo [a,b] dentro del tiempo global t (0..1)."""
    if b <= a:
        return 1.0 if t >= b else 0.0
    return clamp01((t - a) / (b - a))


def build_mark(square_rgba, arrow_arr, rel, arc_progress):
    """Compone cuadro + flecha revelada por barrido angular. Devuelve RGBA."""
    mark = square_rgba.copy()
    if arc_progress > 0:
        thr = _REVEAL_SWEEP * clamp01(arc_progress)
        mask = (rel <= thr).astype(np.uint8)
        a = arrow_arr.copy()
        a[:, :, 3] = (a[:, :, 3] * mask)
        mark.alpha_composite(Image.fromarray(a, "RGBA"))
    return mark


def render(dark=False):
    bg = (15, 23, 42) if dark else (248, 250, 252)   # #0f172a / #f8fafc
    blue = BLUE_D if dark else BLUE
    re_col = (96, 165, 250) if dark else BLUE         # "Re"
    rest_col = INK_LIGHT if dark else INK             # "contrata"

    mark_size = 150            # px finales de la marca
    font = find_font(96 * SS)

    square_rgba = _rasterize(_svg_square(blue))
    arrow_arr = np.asarray(_rasterize(_svg_arrow())).copy()   # HxWx4 uint8
    rel = _reveal_rel(RASTER)

    frames = []
    for i in range(N):
        t = i / (N - 1)

        p_sq = ease_out(seg(t, 0.00, 0.16))
        p_arc = ease_in_out(seg(t, 0.12, 0.48))
        p_spin = ease_in_out(seg(t, 0.52, 0.74))
        p_re = ease_out(seg(t, 0.56, 0.68))
        p_rest = ease_out(seg(t, 0.64, 0.80))

        canvas = Image.new("RGBA", (W * SS, H * SS), bg + (255,))

        # ---- marca con su animación ----
        mark = build_mark(square_rgba, arrow_arr, rel, p_arc)
        msz = int(mark_size * SS * (0.7 + 0.3 * p_sq))   # scale-in
        mark = mark.resize((msz, msz), Image.LANCZOS)
        if p_spin > 0:                                    # giro de cierre del ciclo
            mark = mark.rotate(-360 * p_spin, resample=Image.BICUBIC, expand=False)
        if p_sq < 1:                                      # fade de entrada
            alpha = mark.split()[3].point(lambda v: int(v * p_sq))
            mark.putalpha(alpha)

        # layout: marca + wordmark centrados como bloque
        gap = int(28 * SS)
        f_bbox = font.getbbox("Recontrata")
        tw = f_bbox[2] - f_bbox[0]
        th = f_bbox[3] - f_bbox[1]
        mw = mark.width
        block_w = mw + gap + tw
        x0 = (W * SS - block_w) // 2
        cy = H * SS // 2

        mark_y = cy - mark.height // 2
        canvas.alpha_composite(mark, (x0, mark_y))

        # ---- wordmark: "Re" + "contrata" con fade + slide ----
        td = ImageDraw.Draw(canvas)
        text_x = x0 + mw + gap
        text_y = cy - th // 2 - f_bbox[1]
        re_w = font.getbbox("Re")[2]

        if p_re > 0:
            off = int(-16 * SS * (1 - p_re))
            td.text((text_x + off, text_y), "Re", font=font, fill=re_col + (int(255 * p_re),))
        if p_rest > 0:
            off = int(-16 * SS * (1 - p_rest))
            td.text((text_x + re_w + off, text_y), "contrata", font=font, fill=rest_col + (int(255 * p_rest),))

        frame = canvas.convert("RGB").resize((W, H), Image.LANCZOS)
        frames.append(frame)

    suffix = "_dark" if dark else ""
    gif_path = os.path.join(OUT, f"recontrata_intro{suffix}.gif")
    mp4_path = os.path.join(OUT, f"recontrata_intro{suffix}.mp4")

    # hold final repitiendo el último frame
    hold = [frames[-1]] * int(FPS * 0.8)
    seq = frames + hold
    seq[0].save(gif_path, save_all=True, append_images=seq[1:],
                duration=int(1000 / FPS), loop=0, optimize=True, disposal=2)
    print(f"GIF  -> {gif_path}")

    try:
        import imageio.v2 as imageio
        with imageio.get_writer(mp4_path, fps=FPS, codec="libx264", quality=8,
                                macro_block_size=8) as w:
            for fr in seq:
                w.append_data(np.asarray(fr))
        print(f"MP4  -> {mp4_path}")
    except Exception as e:
        print(f"[MP4 omitido] {e}  (instala: pip install imageio imageio-ffmpeg)")


if __name__ == "__main__":
    render(dark=False)
    render(dark=True)
    print("Listo.")
