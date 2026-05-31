# Assets del hero de la landing

## Foto de faena (`frontend/public/hero-faena.jpg`)
- Fuente: Pexels (licencia libre, uso comercial sin atribución).
- Foto ID **5553499** (cuadrilla con casco/chaleco en cantera).
- URL: https://images.pexels.com/photos/5553499/pexels-photo-5553499.jpeg
- Procesado: recorte a banda horizontal ratio 2.2, pos vertical 0.35, q82.

## Mock del celular (`frontend/public/phone-eval.png`)
Reproduce la pantalla real de evaluación (EvaluateWorker) sin levantar el backend:
1. `eval_mock.html` — replica la pantalla con Tailwind CDN (datos demo: Sergio Díaz,
   5 dimensiones, estrellas 5/5/4/5/4, "Sí" recontratar). Necesita `logo-recontrata.png` al lado.
2. `python render_mock.py` — Playwright captura la pantalla en móvil -> `eval_screen.png`.
3. `python make_phone.py` — mete el screenshot en un frame de teléfono -> `phone-eval.png`.
Luego redimensionar a ~540px de ancho y copiar a `frontend/public/`.
