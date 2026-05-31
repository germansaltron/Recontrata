"""Mete eval_screen.png en un frame de telefono (bisel negro redondeado)."""
from PIL import Image, ImageDraw

SS = 2  # el screenshot vino a device_scale_factor 2
screen = Image.open("eval_screen.png").convert("RGB")
sw, sh = screen.size  # ~780 x 1432

bezel = int(22 * SS)          # grosor del bisel
r_in = int(34 * SS)           # radio esquina pantalla
r_out = int(58 * SS)          # radio esquina exterior

W, H = sw + 2 * bezel, sh + 2 * bezel
phone = Image.new("RGBA", (W, H), (0, 0, 0, 0))
d = ImageDraw.Draw(phone)
# cuerpo negro
d.rounded_rectangle([0, 0, W, H], radius=r_out, fill=(17, 19, 24, 255))

# pantalla con esquinas redondeadas (mascara)
mask = Image.new("L", (sw, sh), 0)
ImageDraw.Draw(mask).rounded_rectangle([0, 0, sw, sh], radius=r_in, fill=255)
phone.paste(screen, (bezel, bezel), mask)

# isla dinamica / notch
nw, nh = int(95 * SS), int(26 * SS)
nx = (W - nw) // 2
ny = bezel + int(9 * SS)
ImageDraw.Draw(phone).rounded_rectangle([nx, ny, nx + nw, ny + nh], radius=nh // 2, fill=(17, 19, 24, 255))

phone.save("phone-eval.png")
print("phone frame", phone.size)
