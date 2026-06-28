import { useCallback, useEffect, useState } from 'react'
import { WatchButton } from '../components/ui/TutorialModal'
import { Link } from 'react-router-dom'
import { Sliders, Info } from 'lucide-react'
import { api, type CalibrationResponse, type EvaluatorCalibration } from '../lib/api'
import { useOrg } from '../lib/org'

const FLAG_META: Record<string, { label: string; cls: string; help: string }> = {
  lenient: { label: 'Indulgente', cls: 'bg-amber-100 text-amber-800', help: 'Puntúa sistemáticamente más alto que el resto.' },
  severe: { label: 'Severo', cls: 'bg-red-100 text-red-800', help: 'Puntúa sistemáticamente más bajo que el resto.' },
  halo: { label: 'Efecto halo', cls: 'bg-purple-100 text-purple-800', help: 'Casi no diferencia entre las 5 dimensiones.' },
  low_sample: { label: 'Pocos datos', cls: 'bg-gray-100 text-gray-600', help: 'Aún no hay suficientes evaluaciones para concluir.' },
}

function Delta({ value }: { value: number }) {
  const sign = value > 0 ? '+' : ''
  const cls = value > 0 ? 'text-amber-600' : value < 0 ? 'text-red-600' : 'text-gray-500'
  return <span className={`tabular-nums font-medium ${cls}`}>{sign}{value.toFixed(2)}</span>
}

export default function Calibration() {
  const { orgId } = useOrg()
  const [data, setData] = useState<CalibrationResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [forbidden, setForbidden] = useState(false)

  const load = useCallback(() => {
    if (!orgId) return
    setLoading(true)
    api.getCalibration(orgId)
      .then((d) => { setData(d); setForbidden(false) })
      .catch((e) => { if (String(e).includes('403') || String(e).toLowerCase().includes('admin')) setForbidden(true) })
      .finally(() => setLoading(false))
  }, [orgId])

  // eslint-disable-next-line react-hooks/set-state-in-effect -- load() dispara el fetch inicial; el setLoading interno es intencional
  useEffect(() => { load() }, [load])

  if (loading) return (
    <div className="space-y-6" aria-busy="true" aria-label="Cargando calibración">
      <div className="h-7 w-64 bg-gray-200 rounded animate-pulse" />
      <div className="h-48 bg-gray-100 rounded-xl border border-gray-200 animate-pulse" />
    </div>
  )

  if (forbidden) return (
    <div className="max-w-md mx-auto mt-10 text-center bg-white rounded-xl border border-gray-200 p-6">
      <h1 className="font-semibold text-gray-900">Solo para administradores</h1>
      <p className="mt-2 text-sm text-gray-500">La calibración de evaluadores es información sensible sobre los supervisores y solo la ve un administrador de la organización.</p>
    </div>
  )

  if (!data) return <div className="text-gray-500">No pudimos cargar la calibración.</div>

  const hasData = data.evaluators.length > 0 && data.org_mean != null

  return (
    <div className="space-y-6 max-w-4xl">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
          <Sliders className="w-6 h-6 text-blue-600" /> Calibración de evaluadores
        </h1>
        <p className="mt-1 text-sm text-gray-500">
          Detecta sesgos sistemáticos de quién evalúa (indulgencia, severidad, efecto halo) para que el puntaje sea más justo y defendible.
        </p>
        <div className="mt-2"><WatchButton clip="clip9" /></div>
      </div>

      {!hasData ? (
        <div className="bg-white rounded-xl border border-gray-200 p-6 text-sm text-gray-500">
          Aún no hay evaluaciones suficientes para calibrar. Vuelve cuando tu equipo haya registrado más evaluaciones.
        </div>
      ) : (
        <>
          <div className="flex flex-wrap gap-4 text-sm">
            <div className="bg-white rounded-xl border border-gray-200 px-4 py-3">
              <p className="text-xs text-gray-500">Promedio de la organización</p>
              <p className="text-xl font-bold text-gray-900 tabular-nums">{data.org_mean?.toFixed(2)} <span className="text-sm text-gray-400">/ 5</span></p>
            </div>
            <div className="bg-white rounded-xl border border-gray-200 px-4 py-3">
              <p className="text-xs text-gray-500">Evaluadores</p>
              <p className="text-xl font-bold text-gray-900 tabular-nums">{data.evaluators.length}</p>
            </div>
          </div>

          <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-gray-50 text-gray-500 text-xs">
                  <th className="text-left px-4 py-2.5 font-medium">Evaluador</th>
                  <th className="text-center px-3 py-2.5 font-medium">Evals</th>
                  <th className="text-center px-3 py-2.5 font-medium">Promedio</th>
                  <th className="text-center px-3 py-2.5 font-medium" title="Desviación respecto al promedio de la organización">Δ vs org</th>
                  <th className="text-center px-3 py-2.5 font-medium" title="Cuánto diferencia entre dimensiones (bajo = efecto halo)">Dispersión</th>
                  <th className="text-left px-4 py-2.5 font-medium">Señales</th>
                </tr>
              </thead>
              <tbody>
                {data.evaluators.map((e: EvaluatorCalibration, i) => (
                  <tr key={e.evaluator_id ?? `unknown-${i}`} className="border-t border-gray-100">
                    <td className="px-4 py-2.5 text-gray-800">{e.evaluator_name || 'Sin identificar'}</td>
                    <td className="px-3 py-2.5 text-center tabular-nums text-gray-600">{e.evaluation_count}</td>
                    <td className="px-3 py-2.5 text-center tabular-nums text-gray-800">{e.mean_score.toFixed(2)}</td>
                    <td className="px-3 py-2.5 text-center"><Delta value={e.leniency_delta} /></td>
                    <td className="px-3 py-2.5 text-center tabular-nums text-gray-600">{e.dimension_spread.toFixed(2)}</td>
                    <td className="px-4 py-2.5">
                      {e.flags.length === 0 ? (
                        <span className="text-xs text-green-700">✓ Sin sesgo detectado</span>
                      ) : (
                        <div className="flex flex-wrap gap-1">
                          {e.flags.map((f) => {
                            const m = FLAG_META[f] ?? { label: f, cls: 'bg-gray-100 text-gray-600', help: '' }
                            return <span key={f} title={m.help} className={`px-2 py-0.5 rounded-full text-xs font-medium ${m.cls}`}>{m.label}</span>
                          })}
                        </div>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Leyenda */}
          <div className="bg-gray-50 rounded-xl p-4 text-sm text-gray-600 space-y-1.5">
            <p className="font-medium text-gray-700">Cómo leer esto</p>
            <p><span className="font-medium">Δ vs org</span>: cuánto se desvía el promedio del evaluador respecto al de la organización. Se marca a partir de ±{data.leniency_threshold.toFixed(1)} puntos.</p>
            <p><span className="font-medium">Dispersión</span>: cuánto diferencia entre las 5 dimensiones. Bajo {data.halo_threshold.toFixed(1)} sugiere <span className="font-medium">efecto halo</span> (pone notas parecidas a todo).</p>
            <p>Las señales solo se marcan con al menos {data.min_sample} evaluaciones.</p>
          </div>
        </>
      )}

      <div className="flex gap-3 text-sm text-gray-500 bg-gray-50 rounded-xl p-4">
        <Info className="w-5 h-5 shrink-0 text-gray-400" />
        <p>
          Esto no cambia los puntajes: es una herramienta para conversar con tus supervisores y mejorar la consistencia.
          Ver también la <Link to="/app/formula" className="text-blue-600 hover:text-blue-700 font-medium">fórmula del puntaje</Link>.
        </p>
      </div>
    </div>
  )
}
