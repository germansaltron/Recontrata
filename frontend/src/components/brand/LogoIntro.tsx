import { useEffect, useState } from 'react'
import { AnimatePresence, motion } from 'framer-motion'

const KEY = 'recontrata_intro_seen'
const DURATION = 1700

// Decision sincrona: mostrar la intro solo si no se vio en esta sesion y el
// usuario no pidio menos movimiento. Va en el lazy initializer para no tener
// side-effects y ser idempotente bajo StrictMode (doble montaje en dev).
function decideShow() {
  try {
    if (sessionStorage.getItem(KEY) === '1') return false
  } catch {
    /* ignore */
  }
  try {
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return false
  } catch {
    /* ignore */
  }
  return true
}

// Intro del logo: se muestra UNA vez por sesion, es saltable (clic/scroll/tecla)
// y respeta prefers-reduced-motion. El logo hace "magic move" hacia el navbar
// via layoutId compartido con el logo del header (ver Landing.tsx).
// El timer de auto-cierre depende de `showIntro` (no de releer storage), asi el
// segundo montaje de StrictMode vuelve a armar el timeout y la intro cierra.
export function useLogoIntro() {
  const [showIntro, setShowIntro] = useState(decideShow)

  useEffect(() => {
    if (!showIntro) return
    try {
      sessionStorage.setItem(KEY, '1')
    } catch {
      /* ignore */
    }
    const t = window.setTimeout(() => setShowIntro(false), DURATION)
    return () => window.clearTimeout(t)
  }, [showIntro])

  return { showIntro, dismiss: () => setShowIntro(false) }
}

export function LogoIntroOverlay({
  show,
  onDismiss,
}: {
  show: boolean
  onDismiss: () => void
}) {
  // Saltar con scroll / touch / teclado
  useEffect(() => {
    if (!show) return
    const dismiss = () => onDismiss()
    window.addEventListener('wheel', dismiss, { passive: true })
    window.addEventListener('touchmove', dismiss, { passive: true })
    window.addEventListener('keydown', dismiss)
    return () => {
      window.removeEventListener('wheel', dismiss)
      window.removeEventListener('touchmove', dismiss)
      window.removeEventListener('keydown', dismiss)
    }
  }, [show, onDismiss])

  return (
    <AnimatePresence>
      {show && (
        <motion.div
          key="logo-intro"
          className="fixed inset-0 z-[70] flex cursor-pointer items-center justify-center overflow-hidden bg-gradient-to-br from-blue-50 via-[#F5F8FF] to-indigo-50"
          initial={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.55, ease: 'easeInOut' }}
          onClick={onDismiss}
          aria-hidden="true"
        >
          <div className="pointer-events-none absolute -left-24 -top-24 h-[28rem] w-[28rem] rounded-full bg-blue-300/40 blur-3xl" />
          <div className="pointer-events-none absolute -bottom-24 -right-24 h-[28rem] w-[28rem] rounded-full bg-indigo-300/40 blur-3xl" />
          <div className="pointer-events-none absolute right-1/4 top-1/3 h-72 w-72 rounded-full bg-sky-200/30 blur-3xl" />
          <motion.img
            layoutId="brand-logo"
            src="/logo-recontrata.png"
            alt="Recontrata"
            className="relative h-14 w-auto max-w-[82vw] object-contain px-2 drop-shadow-[0_24px_50px_rgba(37,99,235,0.28)] sm:h-20 md:h-24"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, ease: 'easeOut' }}
          />
          <motion.div
            className="absolute bottom-12 text-xs font-medium tracking-wide text-blue-400"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.8, duration: 0.4 }}
          >
            toca para entrar
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}
