import { registerSW } from 'virtual:pwa-register'
import { toast } from 'sonner'

// Registro del service worker (apuesta #3, punto 1: app shell offline).
// Modo "prompt": cuando hay una versión nueva, el usuario decide cuándo
// actualizar (así no se recarga la app en medio de una evaluación en terreno).
export function setupPWA() {
  // En dev el SW está desactivado (vite.config devOptions.enabled=false).
  if (import.meta.env.DEV) return

  const updateSW = registerSW({
    onNeedRefresh() {
      toast('Hay una versión nueva de Recontrata', {
        description: 'Actualiza para obtener las últimas mejoras.',
        duration: Infinity,
        action: {
          label: 'Actualizar',
          onClick: () => updateSW(true),
        },
      })
    },
    onOfflineReady() {
      toast.success('Listo para usar sin conexión', {
        description: 'Recontrata seguirá funcionando aunque te quedes sin señal en terreno.',
      })
    },
  })
}
