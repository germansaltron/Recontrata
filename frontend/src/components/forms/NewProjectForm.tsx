import { useState, type FormEvent } from 'react'
import { api, ApiError, type Project } from '../../lib/api'
import { PROJECT_STATUSES } from '../../lib/constants'

interface Props {
  orgId: string
  initial?: Project
  onCreated: () => void
  onCancel: () => void
}

export default function NewProjectForm({ orgId, initial, onCreated, onCancel }: Props) {
  const isEdit = Boolean(initial)
  const [name, setName] = useState(initial?.name ?? '')
  const [clientName, setClientName] = useState(initial?.client_name ?? '')
  const [location, setLocation] = useState(initial?.location ?? '')
  const [startDate, setStartDate] = useState(initial?.start_date ?? '')
  const [endDate, setEndDate] = useState(initial?.end_date ?? '')
  const [status, setStatus] = useState(initial?.status ?? 'active')
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setError(null)
    if (!name.trim()) {
      setError('El nombre es requerido')
      return
    }
    setSubmitting(true)
    try {
      const payload = {
        name: name.trim(),
        client_name: clientName.trim() || null,
        location: location.trim() || null,
        start_date: startDate || null,
        end_date: endDate || null,
      }
      if (isEdit && initial) {
        await api.updateProject(orgId, initial.id, { ...payload, status })
      } else {
        await api.createProject(orgId, {
          name: payload.name,
          client_name: payload.client_name || undefined,
          location: payload.location || undefined,
          start_date: payload.start_date || undefined,
          end_date: payload.end_date || undefined,
        })
      }
      onCreated()
    } catch (err) {
      // Si es un límite de plan, el paywall global ya se abre: cerramos este modal
      // para no apilar dos diálogos.
      if (err instanceof ApiError && err.planLimit) { onCancel(); return }
      setError(err instanceof Error ? err.message : 'Error al guardar proyecto')
    } finally {
      setSubmitting(false)
    }
  }

  const inputCls = 'w-full px-3 py-2.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500'

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Nombre *</label>
        <input type="text" value={name} onChange={(e) => setName(e.target.value)} className={inputCls} placeholder="Mantención Molino SAG" autoFocus />
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Cliente</label>
        <input type="text" value={clientName ?? ''} onChange={(e) => setClientName(e.target.value)} className={inputCls} placeholder="Minera Escondida" />
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Ubicación</label>
        <input type="text" value={location ?? ''} onChange={(e) => setLocation(e.target.value)} className={inputCls} placeholder="Antofagasta" />
      </div>
      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Inicio</label>
          <input type="date" value={startDate ?? ''} onChange={(e) => setStartDate(e.target.value)} className={inputCls} />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Fin</label>
          <input type="date" value={endDate ?? ''} onChange={(e) => setEndDate(e.target.value)} className={inputCls} />
        </div>
      </div>
      {isEdit && (
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Estado</label>
          <select value={status} onChange={(e) => setStatus(e.target.value)} className={inputCls}>
            {PROJECT_STATUSES.map((s) => <option key={s.value} value={s.value}>{s.label}</option>)}
          </select>
        </div>
      )}

      {error && <p className="text-sm text-red-600 bg-red-50 border border-red-200 rounded-lg p-2">{error}</p>}

      <div className="flex gap-2 pt-2">
        <button type="button" onClick={onCancel} className="flex-1 px-4 py-2.5 border border-gray-300 rounded-lg text-sm font-medium hover:bg-gray-50">
          Cancelar
        </button>
        <button type="submit" disabled={submitting} className="flex-1 px-4 py-2.5 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 disabled:opacity-50">
          {submitting ? 'Guardando...' : isEdit ? 'Guardar cambios' : 'Crear Proyecto'}
        </button>
      </div>
    </form>
  )
}
