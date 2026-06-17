import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import { VitePWA } from 'vite-plugin-pwa'

export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
    // PWA / offline-first (apuesta #3, punto 1): service worker que precachea el
    // app shell para que Recontrata abra y navegue en faenas sin señal.
    VitePWA({
      // Actualización controlada por el usuario (toast "Actualizar"), no automática:
      // evita recargar la app en medio de una evaluación en terreno.
      registerType: 'prompt',
      injectRegister: false,
      // Reusamos el manifest existente (public/manifest.webmanifest, ya enlazado en
      // index.html). No dejamos que el plugin genere uno duplicado.
      manifest: false,
      workbox: {
        // Precacheamos solo el shell de la app y los iconos. La media pesada
        // (video del intro, hero, og) se sirve por red y no infla la instalación.
        globPatterns: ['**/*.{js,css,html,svg,ico,woff,woff2}', 'icon-*.png', 'apple-touch-icon.png', 'logo-recontrata.png', 'manifest.webmanifest'],
        globIgnores: ['**/logo-intro.mp4', '**/hero-faena.jpg', '**/og-image.png', '**/dashboard-preview.png', '**/phone-eval.png'],
        // Rutas SPA sin señal → servir el shell (index.html). Las llamadas a la
        // API NO deben caer al shell: que fallen y las maneje la cola (punto 2).
        navigateFallback: '/index.html',
        navigateFallbackDenylist: [/^\/api\//],
        cleanupOutdatedCaches: true,
        clientsClaim: true,
      },
      devOptions: {
        // En dev el SW queda desactivado para no interferir con HMR.
        enabled: false,
      },
    }),
  ],
  server: {
    proxy: {
      '/api': 'http://localhost:8001',
    },
  },
  build: {
    chunkSizeWarningLimit: 800,
  },
})
