import { useState } from 'react'
import { PlayCircle, LifeBuoy } from 'lucide-react'
import { TUTORIALS, STAGES, type Tutorial } from '../lib/tutorials'
import { TutorialModal } from '../components/ui/TutorialModal'

export default function Ayuda() {
  const [active, setActive] = useState<Tutorial | null>(null)

  return (
    <div className="space-y-8 max-w-5xl">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
          <LifeBuoy className="w-6 h-6 text-blue-600" /> Centro de ayuda
        </h1>
        <p className="mt-1 text-sm text-gray-500">
          Tutoriales cortos para sacarle todo el provecho a Recontrata. Cada uno dura cerca de un minuto.
        </p>
      </div>

      {STAGES.map((stage) => {
        const items = TUTORIALS.filter((t) => t.stage === stage.key)
        if (items.length === 0) return null
        return (
          <section key={stage.key}>
            <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-3">{stage.label}</h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {items.map((t) => (
                <button
                  key={t.key}
                  onClick={() => setActive(t)}
                  className="text-left bg-white border border-gray-200 rounded-xl overflow-hidden hover:border-blue-300 hover:shadow-sm transition group"
                >
                  <div className="aspect-video bg-gray-100 flex items-center justify-center">
                    <PlayCircle className="w-10 h-10 text-gray-300 group-hover:text-blue-500 transition" />
                  </div>
                  <div className="p-4">
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-medium text-blue-600">Tutorial {t.clip}</span>
                      <span className="text-xs text-gray-400">· {t.duration}</span>
                    </div>
                    <h3 className="font-semibold text-gray-900 mt-0.5">{t.title}</h3>
                    <p className="text-sm text-gray-500 mt-1">{t.blurb}</p>
                  </div>
                </button>
              ))}
            </div>
          </section>
        )
      })}

      {active && <TutorialModal tutorial={active} onClose={() => setActive(null)} />}
    </div>
  )
}
