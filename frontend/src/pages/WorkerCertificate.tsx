import { useCallback, useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { ArrowLeft, Printer } from 'lucide-react'
import { api, type PortalProfile, type PortalEvaluation } from '../lib/api'

const REHIRE_LABEL: Record<string, string> = { yes: 'Sí', reservations: 'Con reservas', no: 'No' }

const DIMS: { key: keyof PortalEvaluation; short: string }[] = [
  { key: 'score_quality', short: 'Cal' },
  { key: 'score_safety', short: 'Seg' },
  { key: 'score_punctuality', short: 'Pun' },
  { key: 'score_teamwork', short: 'Eq' },
  { key: 'score_technical', short: 'Téc' },
]

function fmt(iso: string | null) {
  return iso ? new Date(iso).toLocaleDateString('es-CL') : '—'
}

export default function WorkerCertificate() {
  const { token } = useParams()
  const [profile, setProfile] = useState<PortalProfile | null>(null)
  const [loading, setLoading] = useState(true)
  const [notFound, setNotFound] = useState(false)

  const load = useCallback(() => {
    if (!token) return
    api.getPortal(token)
      .then((p) => { setProfile(p); setNotFound(false) })
      .catch(() => setNotFound(true))
      .finally(() => setLoading(false))
  }, [token])

  useEffect(() => { load() }, [load])

  // Fecha de emisión (lado navegador: new Date() es válido aquí).
  const issued = new Date().toLocaleDateString('es-CL', { year: 'numeric', month: 'long', day: 'numeric' })

  if (loading) return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center text-gray-400" aria-busy="true">
      <span className="w-5 h-5 border-2 border-gray-300 border-t-blue-600 rounded-full animate-spin mr-2" /> Cargando…
    </div>
  )

  if (notFound || !profile) return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center p-4">
      <div className="max-w-md text-center bg-white rounded-xl border border-gray-200 p-8">
        <h1 className="text-xl font-bold text-gray-900">Enlace no válido</h1>
        <p className="mt-2 text-sm text-gray-500">Este enlace no existe o fue desactivado.</p>
      </div>
    </div>
  )

  const sortedWeights = [...profile.formula.weights].sort((a, b) => b.weight - a.weight)

  return (
    <div className="min-h-screen bg-gray-100">
      {/* CSS de impresión: oculta la barra de acciones y ajusta márgenes de página */}
      <style>{`
        @media print {
          @page { margin: 1.5cm; }
          .no-print { display: none !important; }
          body { background: white !important; }
          .cert-sheet { box-shadow: none !important; border: none !important; margin: 0 !important; max-width: none !important; }
        }
      `}</style>

      {/* Barra de acciones (no se imprime) */}
      <div className="no-print sticky top-0 bg-white border-b border-gray-200">
        <div className="max-w-3xl mx-auto px-4 h-14 flex items-center justify-between">
          <Link to={`/p/${token}`} className="inline-flex items-center gap-1.5 text-sm text-gray-600 hover:text-gray-900">
            <ArrowLeft className="w-4 h-4" /> Volver al portal
          </Link>
          <button
            onClick={() => window.print()}
            className="inline-flex items-center gap-1.5 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded-lg px-4 py-2"
          >
            <Printer className="w-4 h-4" /> Imprimir / Guardar PDF
          </button>
        </div>
      </div>

      {/* Hoja del certificado */}
      <div className="cert-sheet max-w-3xl mx-auto my-6 bg-white border border-gray-200 shadow-sm rounded-lg p-8 print:p-0">
        {/* Encabezado */}
        <div className="flex items-start justify-between border-b border-gray-200 pb-4">
          <div>
            <p className="text-xl font-bold text-gray-900">Recontrata</p>
            <p className="text-sm text-gray-500">Certificado de desempeño</p>
          </div>
          <div className="text-right text-xs text-gray-500">
            <p>Emitido el {issued}</p>
            <p>{profile.org_name}</p>
          </div>
        </div>

        {/* Identidad + resumen */}
        <div className="flex items-start justify-between gap-4 mt-6">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">{profile.worker_name}</h1>
            <p className="text-sm text-gray-600">{profile.specialty} · {profile.rut}</p>
          </div>
          {profile.avg_score != null && (
            <div className="text-right">
              <div className="text-4xl font-bold text-blue-600 tabular-nums leading-none">{profile.avg_score.toFixed(1)}</div>
              <div className="text-xs text-gray-500 mt-1">de 5 · puntaje ponderado</div>
            </div>
          )}
        </div>

        <div className="grid grid-cols-4 gap-3 mt-6 text-center">
          <div className="border border-gray-200 rounded-lg py-2">
            <p className="text-lg font-bold text-gray-900">{profile.evaluation_count}</p>
            <p className="text-xs text-gray-500">Evaluaciones</p>
          </div>
          <div className="border border-gray-200 rounded-lg py-2">
            <p className="text-lg font-bold text-green-600">{profile.rehire_yes}</p>
            <p className="text-xs text-gray-500">Recontratable</p>
          </div>
          <div className="border border-gray-200 rounded-lg py-2">
            <p className="text-lg font-bold text-yellow-600">{profile.rehire_reservations}</p>
            <p className="text-xs text-gray-500">Con reservas</p>
          </div>
          <div className="border border-gray-200 rounded-lg py-2">
            <p className="text-lg font-bold text-red-600">{profile.rehire_no}</p>
            <p className="text-xs text-gray-500">No</p>
          </div>
        </div>

        {/* Tabla de evaluaciones */}
        <h2 className="font-semibold text-gray-900 mt-8 mb-2">Historial de evaluaciones</h2>
        {profile.evaluations.length === 0 ? (
          <p className="text-sm text-gray-500">Sin evaluaciones registradas.</p>
        ) : (
          <table className="w-full text-sm border-collapse">
            <thead>
              <tr className="border-y border-gray-200 text-gray-500 text-xs">
                <th className="text-left py-2 font-medium">Proyecto</th>
                <th className="text-left py-2 font-medium">Fecha</th>
                {DIMS.map((d) => <th key={d.key} className="text-center py-2 font-medium">{d.short}</th>)}
                <th className="text-center py-2 font-medium">Pond.</th>
                <th className="text-left py-2 font-medium pl-2">Recontrata</th>
              </tr>
            </thead>
            <tbody>
              {profile.evaluations.map((ev) => (
                <tr key={ev.id} className="border-b border-gray-100">
                  <td className="py-2 pr-2 text-gray-800">{ev.project_name}</td>
                  <td className="py-2 pr-2 text-gray-500 whitespace-nowrap">{fmt(ev.created_at)}</td>
                  {DIMS.map((d) => <td key={d.key} className="text-center py-2 text-gray-700 tabular-nums">{ev[d.key] as number}</td>)}
                  <td className="text-center py-2 font-semibold text-gray-900 tabular-nums">{ev.score_weighted.toFixed(1)}</td>
                  <td className="py-2 pl-2 text-gray-700">{REHIRE_LABEL[ev.would_rehire] ?? ev.would_rehire}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}

        {/* Fórmula */}
        <h2 className="font-semibold text-gray-900 mt-8 mb-2">Cómo se calcula el puntaje</h2>
        <p className="text-sm text-gray-600">
          Perfil <span className="font-medium">{profile.formula.label}</span>. Promedio ponderado de las 5 dimensiones:{' '}
          {sortedWeights.map((w, i) => (
            <span key={w.key}>
              {w.label} {Math.round(w.weight * 100)}%{i < sortedWeights.length - 1 ? ' · ' : ''}
            </span>
          ))}.
        </p>

        {/* Pie */}
        <div className="mt-8 pt-4 border-t border-gray-200 text-xs text-gray-400">
          <p>Documento generado por el propio trabajador desde su portal en recontrata.cl ({issued}).</p>
          <p>Transparencia conforme al art. 16 de la Ley N° 21.719. No constituye un certificado oficial de la empresa.</p>
        </div>
      </div>
    </div>
  )
}
