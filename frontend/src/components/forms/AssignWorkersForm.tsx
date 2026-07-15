import { useEffect, useState, type FormEvent } from 'react'
import { Search } from 'lucide-react'
import { api, ApiError, type Worker } from '../../lib/api'

interface Props {
  orgId: string
  projectId: string
  excludeIds: string[]
  onAssigned: () => void
  onCancel: () => void
}

export default function AssignWorkersForm({ orgId, projectId, excludeIds, onAssigned, onCancel }: Props) {
  const [workers, setWorkers] = useState<Worker[]>([])
  const [selected, setSelected] = useState<Set<string>>(new Set())
  const [search, setSearch] = useState('')
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    async function load() {
      setLoading(true)
      try {
        const res = await api.listWorkers(orgId, { size: 100, sort_by: 'last_name', is_active: true })
        setWorkers(res.items.filter((w) => !excludeIds.includes(w.id)))
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Error cargando trabajadores')
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [orgId, excludeIds])

  const filtered = search
    ? workers.filter((w) =>
        `${w.first_name} ${w.last_name} ${w.rut} ${w.specialty}`.toLowerCase().includes(search.toLowerCase())
      )
    : workers

  function toggle(id: string) {
    const next = new Set(selected)
    if (next.has(id)) next.delete(id)
    else next.add(id)
    setSelected(next)
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    if (selected.size === 0) return
    setSubmitting(true)
    setError(null)
    try {
      await api.assignWorkers(orgId, projectId, Array.from(selected))
      onAssigned()
    } catch (err) {
      // Límite de plan → el paywall global se muestra; cerramos este modal.
      if (err instanceof ApiError && err.planLimit) { onCancel(); return }
      setError(err instanceof Error ? err.message : 'Error al asignar')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-3">
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
        <input
          type="text"
          placeholder="Buscar por nombre, RUT o especialidad..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="w-full pl-10 pr-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        />
      </div>

      {loading ? (
        <div className="text-center py-8 text-gray-400 text-sm">Cargando...</div>
      ) : filtered.length === 0 ? (
        <div className="text-center py-8 text-gray-500 text-sm">
          {workers.length === 0 ? 'No hay trabajadores disponibles para asignar' : 'Sin resultados'}
        </div>
      ) : (
        <div className="max-h-80 overflow-y-auto border border-gray-200 rounded-lg divide-y divide-gray-100">
          {filtered.map((w) => (
            <label key={w.id} className="flex items-center gap-3 px-3 py-2.5 hover:bg-gray-50 cursor-pointer">
              <input
                type="checkbox"
                checked={selected.has(w.id)}
                onChange={() => toggle(w.id)}
                className="w-4 h-4 text-blue-600 rounded"
              />
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900 truncate">{w.first_name} {w.last_name}</p>
                <p className="text-xs text-gray-500 truncate">{w.specialty} · {w.rut}</p>
              </div>
            </label>
          ))}
        </div>
      )}

      <p className="text-xs text-gray-500">{selected.size} seleccionados</p>
      {error && <p className="text-sm text-red-600 bg-red-50 border border-red-200 rounded-lg p-2">{error}</p>}

      <div className="flex gap-2 pt-2">
        <button type="button" onClick={onCancel} className="flex-1 px-4 py-2.5 border border-gray-300 rounded-lg text-sm font-medium hover:bg-gray-50">
          Cancelar
        </button>
        <button type="submit" disabled={submitting || selected.size === 0} className="flex-1 px-4 py-2.5 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 disabled:opacity-50">
          {submitting ? 'Asignando...' : `Asignar ${selected.size || ''}`}
        </button>
      </div>
    </form>
  )
}
