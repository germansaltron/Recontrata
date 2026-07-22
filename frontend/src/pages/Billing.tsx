import { useEffect, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { Check, Infinity as InfinityIcon, Sparkles } from 'lucide-react'
import { useOrg } from '../lib/org'
import { useSubscription } from '../hooks/useSubscription'
import { PLANS, STATUS_LABEL, formatCLP, type PlanMeta } from '../lib/plans'
import { toast } from '../lib/toast'
import { api, type PlanUsage } from '../lib/api'

export default function Billing() {
  const { orgId } = useOrg()
  const { sub, loading, error } = useSubscription(orgId)
  const [searchParams, setSearchParams] = useSearchParams()

  // Retorno desde Flow (?checkout=success|error): avisa y limpia el parámetro.
  useEffect(() => {
    const checkout = searchParams.get('checkout')
    if (!checkout) return
    if (checkout === 'success') {
      toast.success('¡Listo!', 'Tu plan quedó activo. Comienzas con 14 días de prueba.')
    } else {
      toast.error('No se pudo completar la contratación', 'No se registró tu tarjeta. Puedes intentarlo de nuevo.')
    }
    searchParams.delete('checkout')
    setSearchParams(searchParams, { replace: true })
  }, [searchParams, setSearchParams])

  if (loading && !sub) {
    return (
      <div className="max-w-4xl mx-auto">
        <div className="h-8 w-56 bg-gray-100 rounded animate-pulse" />
        <div className="mt-6 h-40 bg-gray-100 rounded-xl animate-pulse" />
      </div>
    )
  }

  if (error && !sub) {
    return <p className="text-sm text-red-600 bg-red-50 border border-red-200 rounded-lg p-3">{error}</p>
  }

  const currentPlan = sub ? sub.plan : 'free'

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Suscripción</h1>
        <p className="mt-1 text-sm text-gray-500">
          Pagas por trabajadores activos, no por usuario. Supervisores e historial ilimitados en todos los planes.
        </p>
      </div>

      {sub && <CurrentPlanCard sub={sub} />}

      <div>
        <h2 className="text-lg font-semibold text-gray-900">Planes</h2>
        <div className="mt-4 grid md:grid-cols-3 gap-5">
          {PLANS.map((plan) => (
            <PlanCard key={plan.key} plan={plan} current={plan.key === currentPlan} orgId={orgId} />
          ))}
        </div>
        <p className="mt-6 text-center text-xs text-gray-500">
          ¿Más de 500 trabajadores? Tenemos plan Enterprise a medida —{' '}
          <a href="mailto:contacto@recontrata.cl?subject=Plan%20Enterprise" className="underline hover:text-blue-600">escríbenos</a>.
          Facturación mensual o anual (2 meses gratis). Precios en CLP.
        </p>
      </div>
    </div>
  )
}

function CurrentPlanCard({ sub }: { sub: { plan: string; plan_display_name: string; status: string; trial_ends_at: string | null; current_period_end: string | null; usage: PlanUsage } }) {
  const statusLabel = STATUS_LABEL[sub.status] ?? sub.status
  const statusColor =
    sub.status === 'active' ? 'bg-green-50 text-green-700 border-green-200'
    : sub.status === 'trialing' ? 'bg-blue-50 text-blue-700 border-blue-200'
    : sub.status === 'past_due' ? 'bg-amber-50 text-amber-800 border-amber-200'
    : 'bg-gray-50 text-gray-600 border-gray-200'

  return (
    <div className="bg-white rounded-xl border border-gray-200 p-5">
      <div className="flex items-center justify-between flex-wrap gap-2">
        <div>
          <p className="text-xs font-medium text-gray-500 uppercase tracking-wide">Tu plan actual</p>
          <p className="mt-0.5 text-xl font-bold text-gray-900">{sub.plan_display_name}</p>
        </div>
        <span className={`inline-flex items-center rounded-full border px-3 py-1 text-xs font-medium ${statusColor}`}>
          {statusLabel}
        </span>
      </div>

      {sub.status === 'trialing' && sub.trial_ends_at && (
        <p className="mt-3 text-sm text-blue-700 bg-blue-50 border border-blue-100 rounded-lg px-3 py-2">
          Estás en tu período de prueba. Termina el {new Date(sub.trial_ends_at).toLocaleDateString('es-CL')}.
        </p>
      )}
      {sub.status === 'past_due' && (
        <p className="mt-3 text-sm text-amber-800 bg-amber-50 border border-amber-100 rounded-lg px-3 py-2">
          Tu último pago no se pudo procesar. Mientras tanto aplican los límites del plan gratuito
          (tu historial se conserva completo).
        </p>
      )}

      <div className="mt-5 grid sm:grid-cols-2 gap-4">
        <UsageBar label="Trabajadores activos" current={sub.usage.active_workers} limit={sub.usage.active_workers_limit} />
        <UsageBar label="Proyectos activos" current={sub.usage.active_projects} limit={sub.usage.active_projects_limit} />
      </div>
    </div>
  )
}

function UsageBar({ label, current, limit }: { label: string; current: number; limit: number | null }) {
  const unlimited = limit === null
  const pct = unlimited || limit === 0 ? 0 : Math.min(100, Math.round((current / limit) * 100))
  const nearFull = !unlimited && pct >= 80
  const barColor = nearFull ? 'bg-amber-500' : 'bg-blue-600'

  return (
    <div>
      <div className="flex items-center justify-between text-sm">
        <span className="text-gray-600">{label}</span>
        <span className="font-medium text-gray-900 inline-flex items-center gap-1">
          {current} / {unlimited ? <InfinityIcon className="w-4 h-4 text-gray-400" /> : limit}
        </span>
      </div>
      <div className="mt-1.5 h-2 rounded-full bg-gray-100 overflow-hidden">
        <div
          className={`h-full rounded-full transition-all ${unlimited ? 'bg-gray-200' : barColor}`}
          style={{ width: unlimited ? '100%' : `${pct}%` }}
        />
      </div>
    </div>
  )
}

function PlanCard({ plan, current, orgId }: { plan: PlanMeta; current: boolean; orgId: string | null }) {
  const isFree = plan.key === 'free'
  const [loading, setLoading] = useState(false)

  async function handleUpgrade() {
    if (!orgId || loading) return
    setLoading(true)
    try {
      // v1: contratación mensual. El toggle mensual/anual llega como mejora posterior.
      const { redirect_url } = await api.checkout(orgId, plan.key, 'monthly')
      // Redirige a Flow para registrar la tarjeta; vuelve a /app/suscripcion?checkout=...
      window.location.href = redirect_url
    } catch (e) {
      toast.fromError(e, 'No se pudo iniciar la contratación')
      setLoading(false)
    }
  }

  return (
    <div className={`relative flex flex-col rounded-2xl border p-5 ${plan.featured ? 'border-blue-300 ring-1 ring-blue-200 shadow-sm' : 'border-gray-200'}`}>
      {plan.featured && (
        <span className="absolute -top-2.5 left-1/2 -translate-x-1/2 inline-flex items-center gap-1 rounded-full bg-blue-600 px-2.5 py-0.5 text-[11px] font-semibold text-white">
          <Sparkles className="w-3 h-3" /> Recomendado
        </span>
      )}
      <div className="flex items-center justify-between gap-2">
        <h3 className="font-semibold text-gray-900">{plan.name}</h3>
        {current && (
          <span className="inline-flex items-center rounded-full bg-gray-900 px-2.5 py-0.5 text-[11px] font-semibold text-white">Tu plan</span>
        )}
      </div>
      <p className="mt-1 text-xs text-gray-500 min-h-[2.5rem]">{plan.tagline}</p>
      <div className="mt-3">
        <span className="text-2xl font-bold text-gray-900">{plan.monthlyCLP === 0 ? '$0' : formatCLP(plan.monthlyCLP!)}</span>
        <span className="text-sm text-gray-500"> {isFree ? 'para siempre' : 'CLP / mes'}</span>
        {plan.annualCLP !== null && plan.annualCLP > 0 && (
          <p className="mt-0.5 text-xs text-gray-400">o {formatCLP(plan.annualCLP)}/año (2 meses gratis)</p>
        )}
      </div>
      <ul className="mt-4 space-y-2 flex-1">
        {plan.features.map((f) => (
          <li key={f} className="flex items-start gap-2 text-sm text-gray-600">
            <Check className="w-4 h-4 text-green-600 shrink-0 mt-0.5" /> {f}
          </li>
        ))}
      </ul>
      <div className="mt-5">
        {current ? (
          <button disabled className="w-full px-4 py-2.5 rounded-lg border border-gray-200 text-sm font-medium text-gray-400 cursor-default">
            Plan actual
          </button>
        ) : isFree ? (
          <button disabled className="w-full px-4 py-2.5 rounded-lg border border-gray-200 text-sm font-medium text-gray-400 cursor-default">
            Incluido
          </button>
        ) : (
          <button
            onClick={handleUpgrade}
            disabled={loading || !orgId}
            className={`w-full px-4 py-2.5 rounded-lg text-sm font-medium disabled:opacity-60 disabled:cursor-not-allowed ${plan.featured ? 'bg-blue-600 text-white hover:bg-blue-700' : 'border border-gray-300 text-gray-800 hover:bg-gray-50'}`}
          >
            {loading ? 'Redirigiendo…' : `Mejorar a ${plan.name.split(' ')[0]}`}
          </button>
        )}
      </div>
    </div>
  )
}
