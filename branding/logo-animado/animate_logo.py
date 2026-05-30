"""
Animación del logo de Recontrata (concepto B: flecha de retorno).
Anima: aparición del cuadro -> trazado del arco girando -> cabeza de flecha ->
giro de cierre del ciclo -> entrada del wordmark. Exporta MP4 + GIF.

Reproducible:  python animate_logo.py
Salida:        output/recontrata_intro.mp4  +  output/recontrata_intro.gif
               output/recontrata_intro_dark.mp4 + .gif
"""
import math
import os

from PIL import Image, ImageDraw, ImageFont

# ----------------------------------------------------------------------------
SS = 2                      # supersampling para antialias
W, H = 1600, 900           # tamaño final
FPS = 30
DUR = 3.2                  # segundos
N = int(FPS * DUR)
OUT = os.path.join(os.path.dirname(__file__), "output")
os.makedirs(OUT, exist_ok=True)

BLUE = (37, 99, 235)        # #2563eb
BLUE_D = (59, 130, 246)     # #3b82f6  (sobre fondo oscuro)
INK = (30, 41, 59)          # #1e293b
INK_LIGHT = (226, 232, 240) # #e2e8f0
WHITE = (255, 255, 255)


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


def draw_mark(size_px, arc_progress, head_alpha, blue):
    """Dibuja la marca (cuadro + arco + cabeza) en una capa RGBA cuadrada.
    arc_progress 0..1 controla cuánto del arco está dibujado."""
    s = size_px * SS
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    # cuadrado redondeado azul
    pad = int(s * 0.04)
    d.rounded_rectangle([pad, pad, s - pad, s - pad], radius=int(s * 0.20), fill=blue + (255,))

    # geometría del arco (flecha de retorno)
    cx = cy = s / 2
    r = s * 0.27
    width = max(2, int(s * 0.052))
    start_deg = -50
    sweep = 300                      # grados totales del arco
    end_deg = start_deg + sweep * arc_progress
    bbox = [cx - r, cy - r, cx + r, cy + r]

    def dot(px, py, col):
        rr = width / 2
        d.ellipse([px - rr, py - rr, px + rr, py + rr], fill=col)

    if arc_progress > 0:
        d.arc(bbox, start_deg, end_deg, fill=WHITE + (255,), width=width)
        # extremos redondeados (cola en el inicio, punta en el frente actual)
        sx = cx + r * math.cos(math.radians(start_deg))
        sy = cy + r * math.sin(math.radians(start_deg))
        dot(sx, sy, WHITE + (255,))

    # punta de flecha (chevron) en el frente del trazo, tangente al arco
    if head_alpha > 0:
        a = int(255 * clamp01(head_alpha))
        pop = 0.85 + 0.15 * clamp01(head_alpha)   # leve crecimiento al aparecer
        ae = math.radians(end_deg)
        pe = (cx + r * math.cos(ae), cy + r * math.sin(ae))
        # tangente en sentido de avance (horario) = dirección a la que apunta la punta
        tang = (-math.sin(ae), math.cos(ae))
        back = (-tang[0], -tang[1])               # barbas hacia atrás desde la punta

        def rot(v, deg):
            ar = math.radians(deg); c = math.cos(ar); sn = math.sin(ar)
            return (v[0] * c - v[1] * sn, v[0] * sn + v[1] * c)

        Lh = s * 0.16 * pop
        dot(pe[0], pe[1], WHITE + (a,))
        for bd in (34, -34):
            bv = rot(back, bd)
            bx, by = pe[0] + Lh * bv[0], pe[1] + Lh * bv[1]
            d.line([pe, (bx, by)], fill=WHITE + (a,), width=width)
            dot(bx, by, WHITE + (a,))

    return img


def render(dark=False):
    bg = (15, 23, 42) if dark else (248, 250, 252)   # #0f172a / #f8fafc
    blue = BLUE_D if dark else BLUE
    re_col = (96, 165, 250) if dark else BLUE         # "Re"
    rest_col = INK_LIGHT if dark else INK             # "contrata"

    mark_size = 150            # px finales de la marca
    font = find_font(96 * SS)

    frames = []
    for i in range(N):
        t = i / (N - 1)

        p_sq = ease_out(seg(t, 0.00, 0.16))
        p_arc = ease_in_out(seg(t, 0.12, 0.46))
        p_head = seg(t, 0.40, 0.52)
        p_spin = ease_in_out(seg(t, 0.50, 0.72))
        p_re = ease_out(seg(t, 0.54, 0.66))
        p_rest = ease_out(seg(t, 0.62, 0.78))

        canvas = Image.new("RGBA", (W * SS, H * SS), bg + (255,))

        # ---- marca con su animación ----
        msz = int(mark_size * (0.7 + 0.3 * p_sq))     # scale-in
        mark = draw_mark(msz, p_arc, p_head, blue)
        # giro de cierre del ciclo
        if p_spin > 0:
            mark = mark.rotate(-360 * p_spin, resample=Image.BICUBIC, expand=False)
        # alpha del cuadro entrando
        if p_sq < 1:
            a = mark.split()[3].point(lambda v: int(v * p_sq))
            mark.putalpha(a)

        # layout: marca + wordmark centrados como bloque
        gap = int(28 * SS)
        f_bbox = font.getbbox("Recontrata")
        tw = f_bbox[2] - f_bbox[0]
        th = f_bbox[3] - f_bbox[1]
        mw = mark.width
        block_w = mw + gap + tw
        x0 = (W * SS - block_w) // 2
        cy = H * SS // 2

        mark_x = x0
        mark_y = cy - mark.height // 2
        canvas.alpha_composite(mark, (mark_x, mark_y))

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

    # GIF (Pillow) — hold final repitiendo el último frame
    hold = [frames[-1]] * int(FPS * 0.8)
    seq = frames + hold
    seq[0].save(gif_path, save_all=True, append_images=seq[1:],
                duration=int(1000 / FPS), loop=0, optimize=True, disposal=2)
    print(f"GIF  -> {gif_path}")

    # MP4 (imageio + ffmpeg)
    try:
        import imageio.v2 as imageio
        import numpy as np
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
