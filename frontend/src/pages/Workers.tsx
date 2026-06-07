import { useCallback, useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Search, Filter, UserPlus, Users, Upload, Download, ChevronLeft, ChevronRight } from 'lucide-react'
import { api, type Worker } from '../lib/api'
import { useOrg } from '../lib/org'
import { useDebounce } from '../hooks/useDebounce'
import { SPECIALTIES } from '../lib/constants'
import ScoreBadge from '../components/ui/ScoreBadge'
import Modal from '../components/ui/Modal'
import { RowSkeleton } from '../components/ui/Skeleton'
import NewWorkerForm from '../components/forms/NewWorkerForm'
import ImportWorkersForm from '../components/forms/ImportWorkersForm'
import { toast } from '../lib/toast'

const PAGE_SIZE = 20

export default function Workers() {
  const { orgId: ORG_ID } = useOrg()
  const navigate = useNavigate()
  const [workers, setWorkers] = useState<Worker[]>([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [specialty, setSpecialty] = useState('')
  const [minScore, setMinScore] = useState('')
  const [showFilters, setShowFilters] = useState(false)
  const [showNew, setShowNew] = useState(false)
  const [showImport, setShowImport] = useState(false)
  const [page, setPage] = useState(1)
  const [total, setTotal] = useState(0)
  const [totalPages, setTotalPages] = useState(0)
  const debouncedSearch = useDebounce(search)

  // Reset page when filters change
  useEffect(() => {
    setPage(1)
  }, [debouncedSearch, specialty, minScore])

  const load = useCallback(async () => {
    if (!ORG_ID) return
    setLoading(true)
    try {
      const res = await api.listWorkers(ORG_ID, {
        search: debouncedSearch || undefined,
        specialty: specialty || undefined,
        min_score: minScore ? parseFloat(minScore) : undefined,
        sort_by: 'last_name',
        page,
        size: PAGE_SIZE,
      })
      setWorkers(res.items)
      setTotal(res.total)
      setTotalPages(res.pages)
    } catch { /* expected without DB */ }
    finally { setLoading(false) }
  }, [ORG_ID, debouncedSearch, specialty, minScore, page])

  useEffect(() => { load() }, [load])

  const rangeStart = total === 0 ? 0 : (page - 1) * PAGE_SIZE + 1
  const rangeEnd = Math.min(page * PAGE_SIZE, total)

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Trabajadores</h1>
        <div className="flex gap-2">
          <button
            onClick={async () => {
              if (!ORG_ID) return
              try {
                const blob = await api.exportWorkersCsv(ORG_ID)
                const url = URL.createObjectURL(blob)
                const a = document.createElement('a')
                a.href = url
                a.download = 'trabajadores.csv'
                a.click()
                URL.revokeObjectURL(url)
                toast.success('Exportación lista', 'Se descargó trabajadores.csv')
              } catch (e) {
                toast.fromError(e, 'Error al exportar')
              }
            }}
            className="flex items-center gap-2 border border-gray-300 text-gray-700 px-3 py-2 rounded-lg text-sm font-medium hover:bg-gray-50"
            title="Exportar CSV"
          >
            <Download className="w-4 h-4" /> <span className="hidden sm:inline">Exportar</span>
          </button>
          <button onClick={() => setShowImport(true)} className="flex items-center gap-2 border border-gray-300 text-gray-700 px-3 py-2 rounded-lg text-sm font-medium hover:bg-gray-50">
            <Upload className="w-4 h-4" /> <span className="hidden sm:inline">Importar</span>
          </button>
          <button onClick={() => setShowNew(true)} className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-blue-700">
            <UserPlus className="w-4 h-4" /> Nuevo
          </button>
        </div>
      </div>

      {/* Search + Filters */}
      <div className="space-y-3">
        <div className="flex gap-2">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              placeholder="Buscar por nombre o RUT..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full pl-10 pr-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
          <button onClick={() => setShowFilters(!showFilters)} className={`px-3 py-2.5 border rounded-lg ${showFilters ? 'bg-blue-50 border-blue-300' : 'border-gray-300'}`}>
            <Filter className="w-4 h-4" />
          </button>
        </div>

        {showFilters && (
          <div className="flex flex-wrap gap-3 p-3 bg-gray-50 rounded-lg">
            <select value={specialty} onChange={(e) => setSpecialty(e.target.value)} className="px-3 py-2 border border-gray-300 rounded-lg text-sm">
              <option value="">Todas las especialidades</option>
              {SPECIALTIES.map((s) => <option key={s} value={s}>{s}</option>)}
            </select>
            <input
              type="number"
              placeholder="Score mínimo"
              value={minScore}
              onChange={(e) => setMinScore(e.target.value)}
              min="1" max="5" step="0.5"
              className="w-32 px-3 py-2 border border-gray-300 rounded-lg text-sm"
            />
          </div>
        )}
      </div>

      {/* Results */}
      {loading ? (
        <RowSkeleton count={6} />
      ) : workers.length === 0 ? (
        <div className="text-center py-12 text-gray-500 bg-white rounded-xl border border-gray-200">
          <Users className="w-12 h-12 mx-auto mb-3 text-gray-300" />
          <p className="font-medium text-gray-700">No se encontraron trabajadores</p>
          <p className="text-sm text-gray-500 mt-1">
            {search || specialty || minScore ? 'Ajusta los filtros' : 'Agrega tu primer trabajador o importa un Excel'}
          </p>
          {!search && !specialty && !minScore && (
            <div className="flex gap-2 justify-center mt-4">
              <button onClick={() => setShowImport(true)} className="inline-flex items-center gap-2 border border-gray-300 px-3 py-2 rounded-lg text-sm font-medium hover:bg-gray-50">
                <Upload className="w-4 h-4" /> Importar
              </button>
              <button onClick={() => setShowNew(true)} className="inline-flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-blue-700">
                <UserPlus className="w-4 h-4" /> Nuevo
              </button>
            </div>
          )}
        </div>
      ) : (
        <>
          <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="bg-gray-50 border-b border-gray-200">
                  <tr>
                    <th className="text-left px-4 py-3 font-medium text-gray-600">Nombre</th>
                    <th className="text-left px-4 py-3 font-medium text-gray-600 hidden md:table-cell">RUT</th>
                    <th className="text-left px-4 py-3 font-medium text-gray-600">Especialidad</th>
                    <th className="text-center px-4 py-3 font-medium text-gray-600">Score</th>
                    <th className="text-center px-4 py-3 font-medium text-gray-600 hidden sm:table-cell">Evaluaciones</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {workers.map((w) => (
                    <tr
                      key={w.id}
                      onClick={() => navigate(`/app/workers/${w.id}`)}
                      className="hover:bg-gray-50 cursor-pointer"
                    >
                      <td className="px-4 py-3">
                        <Link
                          to={`/app/workers/${w.id}`}
                          onClick={(e) => e.stopPropagation()}
                          className="font-medium text-gray-900 hover:text-blue-600"
                        >
                          {w.first_name} {w.last_name}
                        </Link>
                      </td>
                      <td className="px-4 py-3 text-gray-600 hidden md:table-cell">{w.rut}</td>
                      <td className="px-4 py-3 text-gray-600">{w.specialty}</td>
                      <td className="px-4 py-3 text-center"><ScoreBadge score={w.avg_score} size="sm" /></td>
                      <td className="px-4 py-3 text-center text-gray-500 hidden sm:table-cell">{w.evaluation_count}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {totalPages > 1 && (
            <div className="flex items-center justify-between gap-3 flex-wrap">
              <p className="text-sm text-gray-600">
                Mostrando <span className="font-medium text-gray-900">{rangeStart}</span>
                {rangeEnd > rangeStart && <>–<span className="font-medium text-gray-900">{rangeEnd}</span></>} de{' '}
                <span className="font-medium text-gray-900">{total}</span>
              </p>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => setPage((p) => Math.max(1, p - 1))}
                  disabled={page <= 1}
                  className="flex items-center gap-1 px-3 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed disabled:hover:bg-white"
                >
                  <ChevronLeft className="w-4 h-4" /> Anterior
                </button>
                <span className="text-sm text-gray-600 px-2">
                  Página <span className="font-medium text-gray-900">{page}</span> de{' '}
                  <span className="font-medium text-gray-900">{totalPages}</span>
                </span>
                <button
                  onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                  disabled={page >= totalPages}
                  className="flex items-center gap-1 px-3 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed disabled:hover:bg-white"
                >
                  Siguiente <ChevronRight className="w-4 h-4" />
                </button>
              </div>
            </div>
          )}
        </>
      )}

      {ORG_ID && (
        <>
          <Modal open={showNew} onClose={() => setShowNew(false)} title="Nuevo Trabajador">
            <NewWorkerForm orgId={ORG_ID} onCreated={() => { setShowNew(false); toast.success('Trabajador agregado'); load() }} onCancel={() => setShowNew(false)} />
          </Modal>
          <Modal open={showImport} onClose={() => setShowImport(false)} title="Importar Trabajadores">
            <ImportWorkersForm orgId={ORG_ID} onDone={() => { setShowImport(false); load() }} onCancel={() => setShowImport(false)} />
          </Modal>
        </>
      )}
    </div>
  )
}
