"""Compone el hero: paisaje de mina (fondo) + persona con EPP (izquierda)."""
from PIL import Image, ImageDraw, ImageFilter

RATIO = 2.2
W = 1600
H = int(W / RATIO)  # 727

# 1) fondo: paisaje de mina, cover
bg = Image.open("P3_hi.jpg").convert("RGB")
# cover a WxH
s = max(W / bg.width, H / bg.height)
bg = bg.resize((int(bg.width * s), int(bg.height * s)), Image.LANCZOS)
left = (bg.width - W) // 2
top = (bg.height - H) // 2
bg = bg.crop((left, top, left + W, top + H)).convert("RGBA")

# leve degradado oscuro desde la izquierda para asentar a la persona
grad = Image.new("L", (W, 1), 0)
for x in range(W):
    grad.putpixel((x, 0), int(150 * max(0, 1 - x / (W * 0.5))))
grad = grad.resize((W, H))
shade = Image.new("RGBA", (W, H), (10, 14, 22, 0))
shade.putalpha(grad)
bg.alpha_composite(shade)

# 2) persona recortada
person = Image.open("persona_epp.png").convert("RGBA")
person = person.crop(person.getbbox())
ph = int(H * 1.02)                      # un poco mas alta que la banda (primer plano)
pw = int(person.width * ph / person.height)
person = person.resize((pw, ph), Image.LANCZOS)

px = -int(pw * 0.06)                     # sangra el borde izquierdo (estaba cortado)
py = H - ph + int(H * 0.02)              # anclada abajo

# sombra suave de contacto bajo la persona
shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
sd = ImageDraw.Draw(shadow)
sd.ellipse([px + pw * 0.1, H - 40, px + pw * 0.9, H + 30], fill=(0, 0, 0, 120))
shadow = shadow.filter(ImageFilter.GaussianBlur(18))
bg.alpha_composite(shadow)
bg.alpha_composite(person, (px, py))

bg.convert("RGB").save("../../frontend/public/hero-faena.jpg", quality=84, optimize=True)
import os
print("hero-faena.jpg", (W, H), os.path.getsize("../../frontend/public/hero-faena.jpg") // 1024, "KB")
# preview
bg.convert("RGB").resize((900, int(900 / W * H))).save("_hero_compose_check.png")
