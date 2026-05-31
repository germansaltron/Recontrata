"""
Genera el set de assets de marca de Recontrata desde el logo (concepto B:
flecha de retorno). Salida directa a ../frontend/public + copia en brand-assets/.

  favicon.svg            icono vectorial (cuadro azul + flecha Lucide blanca)
  favicon.ico            16/32/48 px
  apple-touch-icon.png   180x180 (fondo lleno, para iOS)
  icon-192.png           PWA
  icon-512.png           PWA
  icon-maskable-512.png   PWA maskable (safe zone Android)
  og-image.png           1200x630 (preview al compartir)
  manifest.webmanifest

Reproducible:  python gen_brand_assets.py
Requiere:      resvg-py, pillow
"""
import io
import os
import shutil

import resvg_py
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(__file__)
PUBLIC = os.path.abspath(os.path.join(HERE, "..", "frontend", "public"))
ASSETS = os.path.join(HERE, "brand-assets")
os.makedirs(ASSETS, exist_ok=True)

BLUE = (37, 99, 235)        # #2563eb
INK = (30, 41, 59)          # #1e293b
BG = (248, 250, 252)        # #f8fafc
WHITE = (255, 255, 255)

# Geometría del icono Lucide rotate-ccw dentro de un viewBox 0..100
_SCALE = 2.0833
_T = 50 - 12 * _SCALE
_ARROW = (
    f'<g transform="translate({_T:.3f},{_T:.3f}) scale({_SCALE:.4f})" fill="none" '
    f'stroke="#ffffff" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round">'
    f'<path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/>'
    f'<path d="M3 3v5h5"/></g>'
)
# Flecha centrada y reducida para maskable (safe zone): escala menor, recentra
_SCALE_M = 1.55
_TM = 50 - 12 * _SCALE_M
_ARROW_M = (
    f'<g transform="translate({_TM:.3f},{_TM:.3f}) scale({_SCALE_M:.4f})" fill="none" '
    f'stroke="#ffffff" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round">'
    f'<path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/>'
    f'<path d="M3 3v5h5"/></g>'
)

FAVICON_SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" role="img" '
    'aria-label="Recontrata">'
    '<rect x="4" y="4" width="92" height="92" rx="22" fill="#2563eb"/>'
    f'{_ARROW}</svg>'
)


def svg_icon(size, maskable=False, rounded=True):
    if maskable:
        body = f'<rect width="100" height="100" fill="#2563eb"/>{_ARROW_M}'
    elif rounded:
        body = f'<rect x="4" y="4" width="92" height="92" rx="22" fill="#2563eb"/>{_ARROW}'
    else:  # fondo lleno con esquinas suaves (apple touch)
        body = f'<rect width="100" height="100" rx="20" fill="#2563eb"/>{_ARROW}'
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" '
           f'viewBox="0 0 100 100">{body}</svg>')
    raw = resvg_py.svg_to_bytes(svg_string=svg)
    return Image.open(io.BytesIO(bytes(raw))).convert("RGBA")


def find_font(size):
    for name in ("segoeuib.ttf", "seguisb.ttf", "arialbd.ttf"):
        p = os.path.join(r"C:\Windows\Fonts", name)
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    return ImageFont.truetype("DejaVuSans-Bold.ttf", size)


def save(img, name):
    p_pub = os.path.join(PUBLIC, name)
    img.save(p_pub)
    shutil.copy(p_pub, os.path.join(ASSETS, name))
    print(f"  {name:24s} {img.size}")


print(f"Public -> {PUBLIC}")

# 1. favicon.svg (vectorial)
for d in (PUBLIC, ASSETS):
    with open(os.path.join(d, "favicon.svg"), "w", encoding="utf-8") as f:
        f.write(FAVICON_SVG)
print("  favicon.svg")

# 2. favicon.ico (multi-size)
ico = svg_icon(64)
ico_path = os.path.join(PUBLIC, "favicon.ico")
ico.save(ico_path, sizes=[(16, 16), (32, 32), (48, 48)])
shutil.copy(ico_path, os.path.join(ASSETS, "favicon.ico"))
print("  favicon.ico              [16,32,48]")

# 3. apple-touch-icon (fondo lleno, sin transparencia en esquinas)
apple = Image.new("RGBA", (180, 180), BLUE + (255,))
apple.alpha_composite(svg_icon(180, rounded=False))
save(apple.convert("RGB"), "apple-touch-icon.png")

# 4. PWA icons
save(svg_icon(192), "icon-192.png")
save(svg_icon(512), "icon-512.png")
save(svg_icon(512, maskable=True).convert("RGB"), "icon-maskable-512.png")

# 5. og-image 1200x630
W, H = 1200, 630
og = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(og)
# acento diagonal sutil de marca (franja clara azulada arriba-derecha)
d.polygon([(W, 0), (W, 150), (W - 380, 0)], fill=(232, 238, 252))
# bloque logo centrado: icono + wordmark
icon_px = 150
icon = svg_icon(icon_px)
font = find_font(112)
tag_font = find_font(40)
word = "Recontrata"
re_w = font.getbbox("Re")[2]
wb = font.getbbox(word)
tw = wb[2] - wb[0]
gap = 34
block_w = icon_px + gap + tw
x0 = (W - block_w) // 2
cy = H // 2 - 36
og.paste(icon, (x0, cy - icon_px // 2), icon)
tx = x0 + icon_px + gap
ty = cy - (wb[3] - wb[1]) // 2 - wb[1]
d.text((tx, ty), "Re", font=font, fill=BLUE)
d.text((tx + re_w, ty), "contrata", font=font, fill=INK)
# tagline centrado
tag = "Evalúa el desempeño. Recontrata con datos."
tbb = d.textbbox((0, 0), tag, font=tag_font)
d.text(((W - (tbb[2] - tbb[0])) // 2, cy + icon_px // 2 + 28), tag,
       font=tag_font, fill=(71, 85, 105))
save(og, "og-image.png")

# 6. manifest
manifest = '''{
  "name": "Recontrata",
  "short_name": "Recontrata",
  "description": "Evalúa el desempeño y decide a quién recontratar.",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#f8fafc",
  "theme_color": "#2563eb",
  "icons": [
    { "src": "/icon-192.png", "sizes": "192x192", "type": "image/png" },
    { "src": "/icon-512.png", "sizes": "512x512", "type": "image/png" },
    { "src": "/icon-maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable" }
  ]
}
'''
for d_ in (PUBLIC, ASSETS):
    with open(os.path.join(d_, "manifest.webmanifest"), "w", encoding="utf-8") as f:
        f.write(manifest)
print("  manifest.webmanifest")
print("Listo.")
