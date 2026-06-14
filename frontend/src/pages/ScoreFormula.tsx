import { useCallback, useEffect, useState } from 'react'
import { Scale, Info } from 'lucide-react'
import { api, type ScoringFormula, type ScoringProfile } from '../lib/api'
import { useOrg } from '../lib/org'
import { toast } from '../lib/toast'

function WeightBars({ profile }: { profile: ScoringProfile }) {
  // Ordenadas de mayor a menor peso: deja a la vista qué dimensión manda.
  const sorted = [...profile.weights].sort((a, b) => b.weight - a.weight)
  const max = Math.max(...sorted.map((w) => w.weight))
  return (
    <div className="space-y-2.5">
      {sorted.map((w) => (
        <div key={w.key} className="flex items-center gap-3">
          <span className="w-40 shrink-0 text-sm text-gray-700">{w.label}</span>
          <div className="flex-1 h-6 bg-gray-100 rounded-md overflow-hidden">
            <div
              className="h-full bg-blue-600 rounded-md transition-all"
              style={{ width: `${(w.weight / max) * 100}%` }}
            />
          </div>
          <span className="w-12 shrink-0 text-right text-sm font-semibold text-gray-900 tabular-nums">
            {Math.round(w.weight * 100)}%
          </span>
        </div>
      ))}
    </div>
  )
}

export default function ScoreFormula() {
  const { orgId } = useOrg()
  const [formula, setFormula] = useState<ScoringFormula | null>(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)

  const load = useCallback(() => {
    if (!orgId) return
    setLoading(true)
    api.getScoringFormula(orgId).then(setFormula).catch(() => {}).finally(() => setLoading(false))
  }, [orgId])

  useEffect(() => { load() }, [load])

  const changeIndustry = async (industry: string) => {
    if (!orgId || industry === formula?.active_industry) return
    setSaving(true)
    try {
      await api.updateOrg(orgId, { industry })
      toast.success('Industria actualizada. Las nuevas evaluaciones usarán estos pesos.')
      load()
    } catch (e) {
      toast.error(e instanceof Error ? e.message : 'No se pudo cambiar la industria (¿eres admin?)')
    } finally {
      setSaving(false)
    }
  }

  if (loading) return (
    <div className="space-y-6" aria-busy="true" aria-label="Cargando fórmula">
      <div className="h-7 w-64 bg-gray-200 rounded animate-pulse" />
      <div className="h-48 bg-gray-100 rounded-xl border border-gray-200 animate-pulse" />
    </div>
  )
  if (!formula) return <div className="text-gray-500">No pudimos cargar la fórmula del puntaje.</div>

  const active = formula.active_profile

  return (
    <div className="space-y-6 max-w-3xl">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
          <Scale className="w-6 h-6 text-blue-600" /> Fórmula del puntaje
        </h1>
        <p className="mt-1 text-sm text-gray-500">
          El puntaje de cada trabajador no es un promedio simple: cada dimensión pesa
          distinto según la industria. Así una decisión de recontratación es defendible.
        </p>
      </div>

      {/* Perfil activo */}
      <div className="bg-white rounded-xl border border-gray-200 p-5">
        <div className="flex items-center justify-between gap-2 mb-1">
          <h2 className="font-semibold text-gray-900">Perfil activo: {active.label}</h2>
          <span className="text-xs bg-blue-50 text-blue-700 rounded-full px-2.5 py-1 font-medium">En uso</span>
        </div>
        <p className="text-sm text-gray-500 mb-4">{active.description}</p>
        <WeightBars profile={active} />
        <div className="mt-4 pt-4 border-t border-gray-100 text-sm text-gray-600">
          <span className="font-mono text-gray-800">
            puntaje = Σ (dimensión × peso)
          </span>
          <p className="mt-1 text-xs text-gray-400">
            Los pesos suman 100%, por lo que el puntaje queda en la misma escala 1 – 5 que cada dimensión.
          </p>
        </div>
      </div>

      {/* Selector de industria */}
      <div className="bg-white rounded-xl border border-gray-200 p-5">
        <h2 className="font-semibold text-gray-900 mb-1">Industria de la organización</h2>
        <p className="text-sm text-gray-500 mb-3">
          Elige el perfil de pesos que mejor refleja tu operación. Afecta las evaluaciones nuevas.
        </p>
        <div className="grid gap-2 sm:grid-cols-2">
          {formula.profiles.map((p) => {
            const isActive = p.industry === formula.active_industry
            return (
              <button
                key={p.industry}
                onClick={() => changeIndustry(p.industry)}
                disabled={saving || isActive}
                className={`text-left rounded-lg border p-3 transition-colors disabled:cursor-default ${
                  isActive ? 'border-blue-600 bg-blue-50' : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium text-gray-900">{p.label}</span>
                  {isActive && <span className="text-xs text-blue-700 font-medium">Activo</span>}
                </div>
                <p className="text-xs text-gray-500 mt-0.5">{p.description}</p>
              </button>
            )
          })}
        </div>
      </div>

      {/* Transparencia legal */}
      <div className="flex gap-3 text-sm text-gray-500 bg-gray-50 rounded-xl p-4">
        <Info className="w-5 h-5 shrink-0 text-gray-400" />
        <p>
          Esta fórmula es pública y consultable por transparencia (art. 16, Ley N° 21.719 de
          protección de datos personales). El trabajador tiene derecho a conocer cómo se construye
          el puntaje que se usa para decisiones que lo afectan.
        </p>
      </div>
    </div>
  )
}
