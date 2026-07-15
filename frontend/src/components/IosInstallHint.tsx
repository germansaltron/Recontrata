import { useState } from 'react'
import { Share, X } from 'lucide-react'

const DISMISS_KEY = 'recontrata_ios_install_dismissed'

/** Detecta iOS (incluye iPadOS que se reporta como Mac con pantalla táctil). */
function isIos(): boolean {
  const ua = navigator.userAgent
  const iOSDevice = /iPhone|iPad|iPod/.test(ua)
  const iPadOSAsMac = /Macintosh/.test(ua) && navigator.maxTouchPoints > 1
  return iOSDevice || iPadOSAsMac
}

/** ¿La app ya corre instalada (standalone)? Entonces el offline sí funciona y no hay que avisar. */
function isStandalone(): boolean {
  return (
    window.matchMedia('(display-mode: standalone)').matches ||
    // Safari iOS expone este flag no estándar.
    (window.navigator as unknown as { standalone?: boolean }).standalone === true
  )
}

/**
 * Aviso para usuarios de iOS Safari (no instalada): en iOS el modo terreno "sin señal"
 * solo funciona con la app agregada a la pantalla de inicio, y Safari no muestra botón
 * de instalar. Este banner explica cómo hacerlo. Feedback de tester (Vanessa, 15-jul).
 */
export function IosInstallHint() {
  // Estado inicial perezoso: navigator y localStorage ya están disponibles al montar.
  const [show, setShow] = useState(() => {
    if (typeof window === 'undefined') return false
    if (localStorage.getItem(DISMISS_KEY) === '1') return false
    return isIos() && !isStandalone()
  })

  if (!show) return null

  function dismiss() {
    localStorage.setItem(DISMISS_KEY, '1')
    setShow(false)
  }

  return (
    <div
      role="note"
      className="flex items-start gap-2 bg-blue-50 text-blue-900 text-sm px-4 py-2.5 border-b border-blue-100"
    >
      <Share className="w-4 h-4 shrink-0 mt-0.5" />
      <p className="flex-1 leading-snug">
        Para usar Recontrata <strong>sin señal en faena</strong>, agrégala a tu pantalla de inicio: toca{' '}
        <span className="inline-flex items-center gap-1 font-medium">Compartir <Share className="w-3.5 h-3.5" /></span>{' '}
        y luego <strong>“Agregar a inicio”</strong>. Así abre y guarda tus evaluaciones aunque te quedes sin
        internet.
      </p>
      <button onClick={dismiss} className="p-0.5 hover:bg-blue-100 rounded shrink-0" aria-label="Cerrar aviso">
        <X className="w-4 h-4" />
      </button>
    </div>
  )
}
