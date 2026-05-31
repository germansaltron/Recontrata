# Assets del hero de la landing

## Foto del hero (`frontend/public/hero-faena.jpg`) — composición paisaje + persona
Fuente: Pexels (licencia libre, uso comercial sin atribución). Composición:
- **Fondo**: mina a cielo abierto (gran minería), foto ID **2892618**.
- **Persona**: ingeniera con EPP completo (casco amarillo, chaleco, lentes), foto ID **8487994**.
Pasos (`compose_hero.py`):
1. Descargar ambas fotos (w=1600).
2. `rembg` recorta a la persona -> `persona_epp.png` (fondo transparente).
3. `python compose_hero.py` — paisaje cover a banda 2.2 + degradado izq + sombra de
   contacto + persona anclada abajo-izquierda mirando hacia la escena. -> hero-faena.jpg q84.
Requiere: `pip install rembg onnxruntime pillow`.

## Mock del celular (`frontend/public/phone-eval.png`)
Reproduce la pantalla real de evaluación (EvaluateWorker) sin levantar el backend:
1. `eval_mock.html` — replica la pantalla con Tailwind CDN (datos demo: Sergio Díaz,
   5 dimensiones, estrellas 5/5/4/5/4, "Sí" recontratar). Necesita `logo-recontrata.png` al lado.
2. `python render_mock.py` — Playwright captura la pantalla en móvil -> `eval_screen.png`.
3. `python make_phone.py` — mete el screenshot en un frame de teléfono -> `phone-eval.png`.
Tamaño en el hero: `w-32 sm:w-48 md:w-64` (agrandado a pedido).
