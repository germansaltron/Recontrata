import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { ClipboardCheck, FolderKanban } from 'lucide-react'
import { api, type ProjectPending } from '../lib/api'
import { useOrg } from '../lib/org'
import { CardSkeleton } from '../components/ui/Skeleton'

export default function Evaluate() {
  const { orgId: ORG_ID } = useOrg()
  const [projects, setProjects] = useState<ProjectPending[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!ORG_ID) return
    let cancelled = false
    async function load() {
      try {
        // Single aggregated call: backend returns active projects already enriched
        // with pending_count + first_pending_worker_id (no N+1).
        const items = await api.getProjectsPending(ORG_ID!)
        if (!cancelled) setProjects(items)
      } catch { /* */ }
      finally { if (!cancelled) setLoading(false) }
    }
    load()
    return () => { cancelled = true }
  }, [ORG_ID])

  if (loading) return (
    <div className="space-y-4" aria-busy="true" aria-label="Cargando proyectos">
      <div className="h-7 w-48 bg-gray-200 rounded animate-pulse" />
      <div className="h-4 w-80 bg-gray-200 rounded animate-pulse" />
      <CardSkeleton count={3} />
    </div>
  )

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold text-gray-900">Evaluar Equipo</h1>
      <p className="text-gray-600">Proyectos activos con trabajadores pendientes de evaluar.</p>

      {projects.length === 0 ? (
        <div className="text-center py-12 bg-white rounded-xl border border-gray-200">
          <ClipboardCheck className="w-12 h-12 mx-auto mb-3 text-gray-300" />
          <p className="font-medium text-gray-700">No hay proyectos activos</p>
          <p className="text-sm text-gray-500 mt-1">Crea un proyecto o cambia el estado a "Activo"</p>
          <Link
            to="/app/projects"
            className="mt-4 inline-flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-blue-700"
          >
            <FolderKanban className="w-4 h-4" /> Ir a Proyectos
          </Link>
        </div>
      ) : (
        <div className="grid gap-3">
          {projects.map((p) => {
            const done = p.worker_count - p.pending_count
            const hasPending = p.pending_count > 0 && p.first_pending_worker_id
            return (
              <div key={p.id} className="bg-white rounded-xl border border-gray-200 p-4 flex items-center justify-between gap-4">
                <div className="min-w-0 flex-1">
                  <Link to={`/app/projects/${p.id}`} className="block">
                    <h3 className="font-semibold text-gray-900 hover:text-blue-600 truncate">{p.name}</h3>
                    {p.client_name && <p className="text-sm text-gray-500 truncate">{p.client_name}</p>}
                  </Link>
                  <div className="flex gap-3 mt-2 text-xs text-gray-600">
                    <span className="font-medium text-gray-900">
                      {done} / {p.worker_count} evaluados
                    </span>
                    {p.pending_count > 0 && (
                      <span className="text-amber-700 bg-amber-50 px-2 py-0.5 rounded-full font-medium">
                        {p.pending_count} pendiente{p.pending_count === 1 ? '' : 's'}
                      </span>
                    )}
                  </div>
                </div>
                {hasPending ? (
                  <Link
                    to={`/app/evaluate/${p.id}/${p.first_pending_worker_id}`}
                    className="shrink-0 flex items-center gap-1.5 bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-blue-700"
                  >
                    <ClipboardCheck className="w-4 h-4" /> Evaluar
                  </Link>
                ) : (
                  <span className="shrink-0 text-xs text-green-700 bg-green-50 px-3 py-1.5 rounded-full font-medium">
                    Completo
                  </span>
                )}
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
