# Assets del hero de la landing

## Foto del hero (`frontend/public/hero-faena.jpg`) — solo paisaje
Fuente: Pexels (licencia libre, uso comercial sin atribución).
- Mina a cielo abierto (gran minería), foto ID **2892618**.
- Proceso: descargar w=1920, cover a banda ratio 2.2 (1600×727), q84. SIN persona
  (Germán pidió no mostrar a nadie, 31 may).
- `compose_hero.py` queda como referencia del modo "paisaje + persona recortada con
  rembg" por si se quisiera retomar; la versión vigente es solo el paisaje.

## Mock del celular (`frontend/public/phone-eval.png`)
Reproduce la pantalla real de evaluación (EvaluateWorker) sin levantar el backend:
1. `eval_mock.html` — replica la pantalla con Tailwind CDN (datos demo: Sergio Díaz,
   5 dimensiones, estrellas 5/5/4/5/4, "Sí" recontratar). Necesita `logo-recontrata.png` al lado.
2. `python render_mock.py` — Playwright captura la pantalla en móvil -> `eval_screen.png`.
3. `python make_phone.py` — mete el screenshot en un frame de teléfono -> `phone-eval.png`.
Tamaño en el hero: `w-32 sm:w-48 md:w-64` (agrandado a pedido).
