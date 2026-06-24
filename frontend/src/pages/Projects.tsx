import { useCallback, useEffect, useState } from 'react'
import { WatchButton } from '../components/ui/TutorialModal'
import { Link } from 'react-router-dom'
import { Plus, FolderKanban } from 'lucide-react'
import { api, type Project } from '../lib/api'
import { useOrg } from '../lib/org'
import { PROJECT_STATUSES } from '../lib/constants'
import Modal from '../components/ui/Modal'
import { CardSkeleton } from '../components/ui/Skeleton'
import NewProjectForm from '../components/forms/NewProjectForm'

export default function Projects() {
  const { orgId: ORG_ID } = useOrg()
  const [projects, setProjects] = useState<Project[]>([])
  const [loading, setLoading] = useState(true)
  const [statusFilter, setStatusFilter] = useState('')
  const [showNew, setShowNew] = useState(false)

  const load = useCallback(async () => {
    if (!ORG_ID) return
    setLoading(true)
    try {
      const res = await api.listProjects(ORG_ID, { status: statusFilter || undefined, size: 50 })
      setProjects(res.items)
    } catch { /* expected without DB */ }
    finally { setLoading(false) }
  }, [ORG_ID, statusFilter])

  useEffect(() => { load() }, [load])

  const statusBadge = (s: string) => {
    const colors: Record<string, string> = { active: 'bg-green-100 text-green-700', completed: 'bg-blue-100 text-blue-700', planning: 'bg-gray-100 text-gray-700', cancelled: 'bg-red-100 text-red-700' }
    return colors[s] || 'bg-gray-100 text-gray-700'
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Proyectos</h1>
        <button onClick={() => setShowNew(true)} className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-blue-700">
          <Plus className="w-4 h-4" /> Nuevo Proyecto
        </button>
      </div>

      <div className="flex gap-2">
        <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)} className="px-3 py-2 border border-gray-300 rounded-lg text-sm">
          <option value="">Todos los estados</option>
          {PROJECT_STATUSES.map((s) => <option key={s.value} value={s.value}>{s.label}</option>)}
        </select>
      </div>

      {loading ? (
        <CardSkeleton count={4} />
      ) : projects.length === 0 ? (
        <div className="text-center py-12 text-gray-500 bg-white rounded-xl border border-gray-200">
          <FolderKanban className="w-12 h-12 mx-auto mb-3 text-gray-300" />
          <p className="font-medium text-gray-700">No hay proyectos</p>
          <p className="text-sm text-gray-500 mt-1">Crea tu primer proyecto para comenzar a evaluar trabajadores</p>
          <button onClick={() => setShowNew(true)} className="mt-4 inline-flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-blue-700">
            <Plus className="w-4 h-4" /> Crear Proyecto
          </button>
          <div className="mt-3"><WatchButton clip="clip3" /></div>
        </div>
      ) : (
        <div className="grid gap-3 md:grid-cols-2">
          {projects.map((p) => (
            <Link key={p.id} to={`/app/projects/${p.id}`} className="bg-white rounded-xl border border-gray-200 p-4 hover:border-blue-200 hover:shadow-sm transition-all">
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="font-semibold text-gray-900">{p.name}</h3>
                  {p.client_name && <p className="text-sm text-gray-500">{p.client_name}</p>}
                  {p.location && <p className="text-xs text-gray-400">{p.location}</p>}
                </div>
                <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${statusBadge(p.status)}`}>
                  {PROJECT_STATUSES.find((s) => s.value === p.status)?.label || p.status}
                </span>
              </div>
              <div className="flex gap-4 mt-3 text-xs text-gray-500">
                <span>{p.worker_count} trabajadores</span>
                <span>{p.evaluation_count} evaluaciones</span>
              </div>
            </Link>
          ))}
        </div>
      )}

      {ORG_ID && (
        <Modal open={showNew} onClose={() => setShowNew(false)} title="Nuevo Proyecto">
          <NewProjectForm
            orgId={ORG_ID}
            onCreated={() => { setShowNew(false); load() }}
            onCancel={() => setShowNew(false)}
          />
        </Modal>
      )}
    </div>
  )
}
