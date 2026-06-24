import { useEffect, useState } from 'react'
import { X, PlayCircle } from 'lucide-react'
import { getTutorial, type Tutorial } from '../../lib/tutorials'

// Reproductor de un tutorial en un modal (embed de YouTube 16:9).
export function TutorialModal({ tutorial, onClose }: { tutorial: Tutorial; onClose: () => void }) {
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => e.key === 'Escape' && onClose()
    window.addEventListener('keydown', onKey)
    document.body.style.overflow = 'hidden'
    return () => {
      window.removeEventListener('keydown', onKey)
      document.body.style.overflow = ''
    }
  }, [onClose])

  return (
    <div className="fixed inset-0 z-[60] flex items-center justify-center bg-black/70 p-4" onClick={onClose}>
      <div className="bg-white w-full max-w-3xl rounded-2xl shadow-xl overflow-hidden" onClick={(e) => e.stopPropagation()}>
        <div className="flex items-center justify-between px-5 py-3 border-b border-gray-200">
          <h2 className="font-semibold text-gray-900 text-sm">
            <span className="text-gray-400">Tutorial {tutorial.clip} · </span>{tutorial.title}
          </h2>
          <button onClick={onClose} className="p-1 hover:bg-gray-100 rounded-lg" aria-label="Cerrar">
            <X className="w-5 h-5 text-gray-500" />
          </button>
        </div>
        <div className="aspect-video bg-gray-900">
          {tutorial.youtubeId ? (
            <iframe
              className="w-full h-full"
              src={`https://www.youtube-nocookie.com/embed/${tutorial.youtubeId}?autoplay=1&rel=0&modestbranding=1`}
              title={tutorial.title}
              allow="accelerated-destination; autoplay; encrypted-media; picture-in-picture"
              allowFullScreen
            />
          ) : (
            <div className="w-full h-full flex flex-col items-center justify-center text-center text-gray-300 gap-2 px-6">
              <PlayCircle className="w-10 h-10 text-gray-500" />
              <p className="text-sm">Este tutorial estará disponible muy pronto.</p>
            </div>
          )}
        </div>
        <p className="px-5 py-3 text-sm text-gray-500">{tutorial.blurb}</p>
      </div>
    </div>
  )
}

// Botón/enlace contextual que abre el tutorial indicado por su `clip` (key, ej. "clip2").
export function WatchButton({ clip, label, variant = 'link' }: {
  clip: string
  label?: string
  variant?: 'link' | 'button'
}) {
  const [open, setOpen] = useState(false)
  const tutorial = getTutorial(clip)
  if (!tutorial) return null

  const text = label ?? `Ver cómo (${tutorial.duration})`
  const cls = variant === 'button'
    ? 'inline-flex items-center gap-1.5 bg-blue-50 text-blue-700 hover:bg-blue-100 rounded-lg px-3 py-2 text-sm font-medium'
    : 'inline-flex items-center gap-1.5 text-sm font-medium text-blue-600 hover:text-blue-700'

  return (
    <>
      <button type="button" onClick={() => setOpen(true)} className={cls}>
        <PlayCircle className="w-4 h-4" /> {text}
      </button>
      {open && <TutorialModal tutorial={tutorial} onClose={() => setOpen(false)} />}
    </>
  )
}
