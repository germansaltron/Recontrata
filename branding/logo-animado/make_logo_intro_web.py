"""Genera el MP4 del logo animado para el INTRO de la landing web de Recontrata.

Reutiliza la animacion de animate_logo.py pero sobre fondo BLANCO puro (#FFFFFF)
y recortado al logo, optimizado para web (yuv420p, +faststart, mudo). El intro
de la landing reproduce este video como splash nativo antes de React (ver
frontend/index.html) y luego React hace el "magic move" al navbar (BootIntro).

Aprendizaje clave (de CasiListo): el fondo del video decodificado debe ser
blanco puro para que el rectangulo del <video> sea invisible en todos los
navegadores. Por eso bg=(255,255,255) y se verifica la esquina al final.

Reproducible:  python make_logo_intro_web.py
Salida:        ../../frontend/public/logo-intro.mp4
"""
import os
import shutil
import subprocess

import numpy as np
from PIL import Image, ImageDraw

import animate_logo as al
import imageio_ffmpeg

FPS = 30
HOLD_S = 0.55                     # hold con el logo ya armado antes del morph
TARGET_W = 1400                   # ancho de salida
BG = (255, 255, 255)              # BLANCO puro (critico, ver docstring)
HERE = os.path.dirname(__file__)
PUBLIC = os.path.abspath(os.path.join(HERE, "..", "..", "frontend", "public"))
FRAMES = os.path.join(al.OUT, "_intro_web_frames")


def render_frame(t, square_rgba, arrow_arr, rel, font, on_bg):
    """Replica un frame de animate_logo.render() sobre `on_bg` (RGBA tuple o None
    para transparente). Devuelve RGBA a tamano canvas completo (W*SS, H*SS)."""
    SS, W, H = al.SS, al.W, al.H
    p_sq = al.ease_out(al.seg(t, 0.00, 0.16))
    p_arc = al.ease_in_out(al.seg(t, 0.12, 0.48))
    p_spin = al.ease_in_out(al.seg(t, 0.52, 0.74))
    p_re = al.ease_out(al.seg(t, 0.56, 0.68))
    p_rest = al.ease_out(al.seg(t, 0.64, 0.80))

    fill = (on_bg if on_bg is not None else (0, 0, 0, 0))
    canvas = Image.new("RGBA", (W * SS, H * SS), fill)

    mark = al.build_mark(square_rgba, arrow_arr, rel, p_arc)
    msz = int(150 * SS * (0.7 + 0.3 * p_sq))
    mark = mark.resize((msz, msz), Image.LANCZOS)
    if p_spin > 0:
        mark = mark.rotate(-360 * p_spin, resample=Image.BICUBIC, expand=False)
    if p_sq < 1:
        a = mark.split()[3].point(lambda v: int(v * p_sq))
        mark.putalpha(a)

    gap = int(28 * SS)
    f_bbox = font.getbbox("Recontrata")
    tw = f_bbox[2] - f_bbox[0]
    th = f_bbox[3] - f_bbox[1]
    mw = mark.width
    block_w = mw + gap + tw
    x0 = (W * SS - block_w) // 2
    cy = H * SS // 2
    canvas.alpha_composite(mark, (x0, cy - mark.height // 2))

    td = ImageDraw.Draw(canvas)
    text_x = x0 + mw + gap
    text_y = cy - th // 2 - f_bbox[1]
    re_w = font.getbbox("Re")[2]
    if p_re > 0:
        off = int(-16 * SS * (1 - p_re))
        td.text((text_x + off, text_y), "Re", font=font, fill=al.BLUE + (int(255 * p_re),))
    if p_rest > 0:
        off = int(-16 * SS * (1 - p_rest))
        td.text((text_x + re_w + off, text_y), "contrata", font=font, fill=al.INK + (int(255 * p_rest),))
    return canvas


def main():
    SS = al.SS
    font = al.find_font(96 * SS)
    square_rgba = al._rasterize(al._svg_square(al.BLUE))
    arrow_arr = np.asarray(al._rasterize(al._svg_arrow())).copy()
    rel = al._reveal_rel(al.RASTER)

    N = int(FPS * al.DUR)

    # 1) box de recorte: del frame final (todo visible) sobre transparente
    final = render_frame(1.0, square_rgba, arrow_arr, rel, font, None)
    bbox = final.getbbox()
    # pad chico: el clon que vuela (logo-recontrata.png, recortado) debe calzar
    # con el ultimo frame del video para que el morph no "salte".
    pad = 10 * SS
    box = (max(0, bbox[0] - pad), max(0, bbox[1] - pad),
           min(final.width, bbox[2] + pad), min(final.height, bbox[3] + pad))

    if os.path.isdir(FRAMES):
        shutil.rmtree(FRAMES)
    os.makedirs(FRAMES, exist_ok=True)

    # 2) frames de la animacion sobre blanco, recortados al box
    idx = 0
    last = None
    for i in range(N):
        t = i / (N - 1)
        fr = render_frame(t, square_rgba, arrow_arr, rel, font, BG + (255,))
        last = fr.crop(box).convert("RGB")
        last.save(os.path.join(FRAMES, f"f{idx:04d}.png"))
        idx += 1
    # 3) hold final
    for _ in range(int(HOLD_S * FPS)):
        last.save(os.path.join(FRAMES, f"f{idx:04d}.png"))
        idx += 1
    print(f"frames: {idx}  crop={tuple(int(b/SS) for b in box)}")

    # 4) encode web
    os.makedirs(PUBLIC, exist_ok=True)
    out = os.path.join(PUBLIC, "logo-intro.mp4")
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    cmd = [ff, "-y", "-framerate", str(FPS),
           "-i", os.path.join(FRAMES, "f%04d.png"),
           "-vf", f"scale={TARGET_W}:-2:flags=lanczos,format=yuv420p",
           "-c:v", "libx264", "-profile:v", "high", "-crf", "20",
           "-movflags", "+faststart", "-an", out]
    subprocess.run(cmd, check=True, capture_output=True)
    size_kb = os.path.getsize(out) // 1024
    print(f"MP4 -> {out}  ({size_kb} KB)")

    # 5) verificar color de la esquina decodificada
    probe = os.path.join(al.OUT, "_intro_corner.png")
    subprocess.run([ff, "-y", "-i", out, "-frames:v", "1",
                    "-vf", "crop=8:8:0:0,scale=1:1", probe],
                   check=True, capture_output=True)
    px = Image.open(probe).convert("RGB").getpixel((0, 0))
    print(f"fondo esquina decodificado: rgb{px} -> #{px[0]:02X}{px[1]:02X}{px[2]:02X}")
    os.remove(probe)
    shutil.rmtree(FRAMES)


if __name__ == "__main__":
    main()
