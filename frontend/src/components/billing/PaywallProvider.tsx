import { useCallback, useEffect, useState, type ReactNode } from 'react'
import { useNavigate } from 'react-router-dom'
import { Lock, TrendingUp } from 'lucide-react'
import { setPlanLimitHandler, type PlanLimitDetail } from '../../lib/api'
import { PLAN_BY_KEY } from '../../lib/plans'
import Modal from '../ui/Modal'

/** Registra el handler global de límites de plan y muestra el paywall cuando
 *  cualquier llamada recibe un 402 PLAN_LIMIT. El gatillo emocional es "no pierdas
 *  el historial que ya construiste" (ver docs/PASARELA_PAGO_FLOW.md §6). */
export default function PaywallProvider({ children }: { children: ReactNode }) {
  const [limit, setLimit] = useState<PlanLimitDetail | null>(null)
  const navigate = useNavigate()

  useEffect(() => {
    setPlanLimitHandler((detail) => setLimit(detail))
    return () => setPlanLimitHandler(null)
  }, [])

  const close = useCallback(() => setLimit(null), [])
  const goToPlans = useCallback(() => {
    setLimit(null)
    navigate('/app/suscripcion')
  }, [navigate])

  const resource = limit?.resource === 'projects' ? 'proyectos activos' : 'trabajadores activos'
  const planName = limit ? PLAN_BY_KEY[limit.plan]?.name ?? limit.plan : ''

  return (
    <>
      {children}
      <Modal open={limit !== null} onClose={close} title="Llegaste al límite de tu plan" size="sm">
        {limit && (
          <div className="space-y-4">
            <div className="flex items-start gap-3">
              <div className="w-10 h-10 shrink-0 rounded-full bg-amber-50 flex items-center justify-center text-amber-600">
                <Lock className="w-5 h-5" />
              </div>
              <div className="text-sm text-gray-700">
                <p>
                  Tu plan <span className="font-semibold">{planName}</span> permite hasta{' '}
                  <span className="font-semibold">{limit.limit} {resource}</span> y ya estás usando{' '}
                  <span className="font-semibold">{limit.current}</span>.
                </p>
                <p className="mt-2 text-gray-600">
                  No pierdas el historial que ya construiste — sube de plan y sigue creciendo. Todo tu
                  trabajo se conserva completo.
                </p>
              </div>
            </div>

            <div className="flex flex-col-reverse sm:flex-row gap-2 pt-1">
              <button
                onClick={close}
                className="flex-1 px-4 py-2.5 border border-gray-300 rounded-lg text-sm font-medium hover:bg-gray-50"
              >
                Ahora no
              </button>
              <button
                onClick={goToPlans}
                className="flex-1 inline-flex items-center justify-center gap-2 px-4 py-2.5 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700"
              >
                <TrendingUp className="w-4 h-4" /> Ver planes
              </button>
            </div>
          </div>
        )}
      </Modal>
    </>
  )
}
