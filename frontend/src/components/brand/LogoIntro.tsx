import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'

const KEY = 'recontrata_intro_seen'

type Flyer = {
  left: number
  top: number
  h: number
  dx: number
  dy: number
  scale: number
}

// BootIntro orquesta el splash del index.html (#boot-splash con el video que ARMA
// el logo de Recontrata) y, al terminar, hace el "magic move": un clon del logo
// vuela desde el centro hasta su posicion real en el navbar (#nav-logo) y se
// desvanece dejando el logo del navbar en su lugar. Sin spinner, sin texto: lo
// primero que se ve es el logo construyendose. 1 vez por sesion, saltable,
// respeta prefers-reduced-motion (ver el script inline de index.html).
export default function BootIntro() {
  const [flyer, setFlyer] = useState<Flyer | null>(null)

  useEffect(() => {
    const splash = document.getElementById('boot-splash')
    const video = document.getElementById('boot-video') as HTMLVideoElement | null
    if (!splash || !video) {
      splash?.remove()
      return
    }
    try {
      sessionStorage.setItem(KEY, '1')
    } catch {
      /* ignore */
    }

    let done = false

    const finish = () => {
      if (done) return
      done = true
      cleanup()

      const vr = video.getBoundingClientRect()
      const nav = document.getElementById('nav-logo')
      if (nav) {
        const nr = nav.getBoundingClientRect()
        const vcx = vr.left + vr.width / 2
        const vcy = vr.top + vr.height / 2
        const ncx = nr.left + nr.width / 2
        const ncy = nr.top + nr.height / 2
        setFlyer({
          left: vr.left,
          top: vr.top,
          h: vr.height,
          dx: ncx - vcx,
          dy: ncy - vcy,
          scale: nr.height / vr.height,
        })
      }

      splash.style.transition = 'opacity .45s ease'
      splash.style.opacity = '0'
      window.setTimeout(() => splash.remove(), 480)
    }

    const onEnded = () => finish()
    const skip = () => finish()
    const safety = window.setTimeout(finish, 5000)

    const cleanup = () => {
      video.removeEventListener('ended', onEnded)
      splash.removeEventListener('click', skip)
      window.removeEventListener('wheel', skip)
      window.removeEventListener('keydown', skip)
      window.clearTimeout(safety)
    }

    // Si el video ya termino (React monto tarde), hacer el morph de inmediato.
    if (video.ended || (video.duration && video.currentTime >= video.duration - 0.15)) {
      finish()
    } else {
      video.addEventListener('ended', onEnded)
      splash.addEventListener('click', skip)
      window.addEventListener('wheel', skip, { passive: true })
      window.addEventListener('keydown', skip)
    }

    return cleanup
  }, [])

  if (!flyer) return null

  return (
    <motion.img
      src="/logo-recontrata.png"
      alt=""
      aria-hidden="true"
      style={{
        position: 'fixed',
        left: flyer.left,
        top: flyer.top,
        height: flyer.h,
        zIndex: 66,
      }}
      className="w-auto pointer-events-none"
      initial={{ x: 0, y: 0, scale: 1 }}
      animate={{ x: flyer.dx, y: flyer.dy, scale: flyer.scale }}
      transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
      onAnimationComplete={() => setFlyer(null)}
    />
  )
}
