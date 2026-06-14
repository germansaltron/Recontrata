import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Users, FolderKanban, ClipboardCheck, TrendingUp } from 'lucide-react'
import { api, type DashboardStats, type TopWorker, type RecentEvaluation, type NextEvaluation } from '../lib/api'
import { useOrg } from '../lib/org'
import ScoreBadge from '../components/ui/ScoreBadge'
import { formatRelative } from '../lib/dates'

function DashboardSkeleton() {
  return (
    <div className="space-y-6" aria-busy="true" aria-label="Cargando dashboard">
      <div className="h-7 w-40 bg-gray-200 rounded animate-pulse" />
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <div key={i} className="bg-white rounded-xl border border-gray-200 p-4 space-y-3">
            <div className="h-4 w-20 bg-gray-200 rounded animate-pulse" />
            <div className="h-7 w-16 bg-gray-200 rounded animate-pulse" />
            <div className="h-3 w-24 bg-gray-200 rounded animate-pulse" />
          </div>
        ))}
      </div>
      <div className="grid md:grid-cols-2 gap-6">
        {Array.from({ length: 2 }).map((_, i) => (
          <div key={i} className="bg-white rounded-xl border border-gray-200 p-4 space-y-3">
            <div className="h-5 w-40 bg-gray-200 rounded animate-pulse" />
            {Array.from({ length: 4 }).map((_, j) => (
              <div key={j} className="flex items-center justify-between py-1">
                <div className="space-y-2 flex-1">
                  <div className="h-4 w-32 bg-gray-200 rounded animate-pulse" />
                  <div className="h-3 w-48 bg-gray-200 rounded animate-pulse" />
                </div>
                <div className="h-6 w-12 bg-gray-200 rounded animate-pulse" />
              </div>
            ))}
          </div>
        ))}
      </div>
    </div>
  )
}

export default function Dashboard() {
  const { orgId: ORG_ID } = useOrg()
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [topWorkers, setTopWorkers] = useState<TopWorker[]>([])
  const [recent, setRecent] = useState<RecentEvaluation[]>([])
  const [nextEval, setNextEval] = useState<NextEvaluation | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!ORG_ID) return
    async function load() {
      try {
        const [s, tw, re, ne] = await Promise.all([
          api.getStats(ORG_ID!),
          api.getTopWorkers(ORG_ID!),
          api.getRecentEvaluations(ORG_ID!),
          api.getNextEvaluation(ORG_ID!),
        ])
        setStats(s)
        setTopWorkers(tw)
        setRecent(re)
        setNextEval(ne)
      } catch {
        // Will fail without DB — expected in dev without docker
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [ORG_ID])

  if (loading) return <DashboardSkeleton />

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>

      {nextEval && nextEval.project_id && nextEval.worker_id && (
        <Link
          to={`/app/evaluate/${nextEval.project_id}/${nextEval.worker_id}`}
          className="flex items-center justify-between bg-blue-50 border border-blue-200 rounded-xl p-4 hover:bg-blue-100 transition-colors"
        >
          <div>
            <p className="font-medium text-blue-900">Evaluar siguiente pendiente</p>
            <p className="text-sm text-blue-700">
              {nextEval.worker_name} · {nextEval.project_name} · {nextEval.pending_count} pendientes
            </p>
          </div>
          <ClipboardCheck className="w-5 h-5 text-blue-700" />
        </Link>
      )}

      {/* KPI Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <KPICard icon={<FolderKanban className="w-5 h-5 text-blue-600" />} label="Proyectos" value={stats?.project_count ?? 0} sub={`${stats?.active_project_count ?? 0} activos`} />
        <KPICard icon={<Users className="w-5 h-5 text-emerald-600" />} label="Trabajadores" value={stats?.worker_count ?? 0} />
        <KPICard icon={<ClipboardCheck className="w-5 h-5 text-violet-600" />} label="Evaluaciones" value={stats?.evaluation_count ?? 0} />
        <KPICard icon={<TrendingUp className="w-5 h-5 text-amber-600" />} label="Score Ponderado" value={stats?.avg_score_overall != null ? `${stats.avg_score_overall.toFixed(1)} / 5` : '—'} sub={stats?.rehire_rate != null ? `${(stats.rehire_rate * 100).toFixed(0)}% recomienda recontratar` : undefined} />
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        {/* Top Workers */}
        <div className="bg-white rounded-xl border border-gray-200 p-4">
          <h2 className="text-lg font-semibold text-gray-900 mb-3">Top Trabajadores</h2>
          {topWorkers.length === 0 ? (
            <div className="text-sm text-gray-500">
              <p>Sin evaluaciones aún.</p>
              <Link to="/app/evaluate" className="inline-flex items-center gap-1 mt-2 text-blue-600 hover:text-blue-700 font-medium">
                <ClipboardCheck className="w-4 h-4" /> Evaluar equipo
              </Link>
            </div>
          ) : (
            <div className="space-y-2">
              {topWorkers.map((w) => (
                <Link key={w.id} to={`/app/workers/${w.id}`} className="flex items-center justify-between p-2 rounded-lg hover:bg-gray-50">
                  <div>
                    <p className="text-sm font-medium text-gray-900">{w.full_name}</p>
                    <p className="text-xs text-gray-500">{w.specialty} · {w.evaluation_count === 1 ? '1 evaluación' : `${w.evaluation_count} evaluaciones`}</p>
                  </div>
                  <ScoreBadge score={w.avg_score} />
                </Link>
              ))}
            </div>
          )}
        </div>

        {/* Recent Evaluations */}
        <div className="bg-white rounded-xl border border-gray-200 p-4">
          <h2 className="text-lg font-semibold text-gray-900 mb-3">Evaluaciones Recientes</h2>
          {recent.length === 0 ? (
            <div className="text-sm text-gray-500">
              <p>Sin evaluaciones aún.</p>
              <Link to="/app/evaluate" className="inline-flex items-center gap-1 mt-2 text-blue-600 hover:text-blue-700 font-medium">
                <ClipboardCheck className="w-4 h-4" /> Evaluar al primer pendiente
              </Link>
            </div>
          ) : (
            <div className="space-y-2">
              {recent.map((e) => (
                <Link key={e.id} to={`/app/workers/${e.worker_id}`} className="flex items-center justify-between p-2 rounded-lg hover:bg-gray-50">
                  <div className="min-w-0">
                    <p className="text-sm font-medium text-gray-900 truncate">{e.worker_name}</p>
                    <p className="text-xs text-gray-500 truncate">
                      {e.project_name}
                      <span className="text-gray-400"> · {formatRelative(e.created_at)}</span>
                    </p>
                  </div>
                  <div className="flex items-center gap-2 shrink-0">
                    <ScoreBadge score={e.score_weighted} size="sm" />
                    <span className={`text-xs px-1.5 py-0.5 rounded-full ${e.would_rehire === 'yes' ? 'bg-green-100 text-green-700' : e.would_rehire === 'no' ? 'bg-red-100 text-red-700' : 'bg-yellow-100 text-yellow-700'}`}>
                      {e.would_rehire === 'yes' ? 'Sí' : e.would_rehire === 'no' ? 'No' : 'Reservas'}
                    </span>
                  </div>
                </Link>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

function KPICard({ icon, label, value, sub }: { icon: React.ReactNode; label: string; value: string | number; sub?: string }) {
  return (
    <div className="bg-white rounded-xl border border-gray-200 p-3 sm:p-4">
      <div className="flex items-center gap-2 mb-2">
        <span className="shrink-0">{icon}</span>
        <span className="text-xs sm:text-sm text-gray-600 leading-tight">{label}</span>
      </div>
      <p className="text-xl sm:text-2xl font-bold text-gray-900">{value}</p>
      {sub && <p className="text-xs text-gray-500 mt-1 leading-tight">{sub}</p>}
    </div>
  )
}
