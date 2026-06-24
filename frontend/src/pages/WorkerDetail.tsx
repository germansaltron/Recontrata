import { useCallback, useEffect, useState } from 'react'
import { WatchButton } from '../components/ui/TutorialModal'
import { useParams, Link } from 'react-router-dom'
import { ArrowLeft, Phone, Mail, Pencil, ClipboardCheck, ShieldCheck, Download, Link2, Copy, MessageSquare } from 'lucide-react'
import { api, type WorkerDetail as WorkerDetailType, type WorkerConsent, type ConsentStatus, type ConsentMethod, type EvaluationSummary } from '../lib/api'
import { useOrg } from '../lib/org'
import { REHIRE_OPTIONS } from '../lib/constants'
import StarRating from '../components/ui/StarRating'
import ScoreBadge from '../components/ui/ScoreBadge'
import Modal from '../components/ui/Modal'
import NewWorkerForm from '../components/forms/NewWorkerForm'
import { toast } from '../lib/toast'

// Dimensiones por evaluación, con etiqueta corta para la grilla del historial.
const EVAL_DIMS: { key: keyof EvaluationSummary; short: string; full: string }[] = [
  { key: 'score_quality', short: 'Cal', full: 'Calidad' },
  { key: 'score_safety', short: 'Seg', full: 'Seguridad' },
  { key: 'score_punctuality', short: 'Pun', full: 'Puntualidad' },
  { key: 'score_teamwork', short: 'Eq', full: 'Equipo' },
  { key: 'score_technical', short: 'Téc', full: 'Técnica' },
]

const REHIRE_LABEL: Record<string, string> = { yes: 'Sí', reservations: 'Con reservas', no: 'No' }

function csvCell(v: unknown): string {
  const s = v == null ? '' : String(v)
  return /[",\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s
}

function exportEvaluationsCsv(worker: WorkerDetailType) {
  const headers = ['Proyecto', 'Calidad', 'Seguridad', 'Puntualidad', 'Equipo', 'Tecnica', 'Promedio', 'Ponderado', 'Recontratacion', 'Motivo', 'Comentario', 'Evaluador', 'Fecha']
  const rows = worker.evaluations.map((ev) => [
    ev.project_name, ev.score_quality, ev.score_safety, ev.score_punctuality, ev.score_teamwork,
    ev.score_technical, ev.score_average, ev.score_weighted, REHIRE_LABEL[ev.would_rehire] ?? ev.would_rehire,
    ev.rehire_reason ?? '', ev.comment ?? '', ev.evaluator_name ?? '',
    new Date(ev.created_at).toLocaleDateString('es-CL'),
  ])
  const csv = [headers, ...rows].map((r) => r.map(csvCell).join(',')).join('\n')
  const blob = new Blob(['﻿' + csv], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `evaluaciones_${worker.last_name}_${worker.first_name}.csv`.toLowerCase().replace(/\s+/g, '_')
  a.click()
  URL.revokeObjectURL(url)
  toast.success('Historial exportado')
}

type TrendPoint = { project_name: string; date: string | null; score_average: number }

function ScoreSparkline({ points }: { points: TrendPoint[] }) {
  const width = 600
  const height = 160
  const padX = 16
  const padY = 20
  const innerW = width - padX * 2
  const innerH = height - padY * 2
  const minY = 1
  const maxY = 5
  const n = points.length
  const coords = points.map((p, i) => {
    const x = padX + (n === 1 ? innerW / 2 : (i * innerW) / (n - 1))
    const y = padY + innerH - ((p.score_average - minY) / (maxY - minY)) * innerH
    return { x, y, p }
  })
  const path = coords.map((c, i) => `${i === 0 ? 'M' : 'L'}${c.x.toFixed(1)} ${c.y.toFixed(1)}`).join(' ')

  return (
    <svg viewBox={`0 0 ${width} ${height}`} className="w-full h-40" role="img" aria-label="Tendencia de scores por proyecto">
      {[1, 2, 3, 4, 5].map((v) => {
        const y = padY + innerH - ((v - minY) / (maxY - minY)) * innerH
        return (
          <g key={v}>
            <line x1={padX} x2={width - padX} y1={y} y2={y} stroke="#e5e7eb" strokeDasharray="3 3" />
            <text x={padX - 4} y={y + 4} textAnchor="end" fontSize="10" fill="#9ca3af">{v}</text>
          </g>
        )
      })}
      <path d={path} fill="none" stroke="#2563eb" strokeWidth="2" />
      {coords.map((c, i) => (
        <g key={i}>
          <circle cx={c.x} cy={c.y} r="4" fill="#2563eb">
            <title>{c.p.project_name}: {c.p.score_average.toFixed(1)} / 5</title>
          </circle>
          <text x={c.x} y={height - 4} textAnchor="middle" fontSize="10" fill="#6b7280">
            {c.p.project_name.length > 14 ? c.p.project_name.slice(0, 13) + '…' : c.p.project_name}
          </text>
        </g>
      ))}
    </svg>
  )
}

const CONSENT_STATUS: Record<ConsentStatus, { label: string; cls: string }> = {
  pending: { label: 'Pendiente', cls: 'bg-gray-100 text-gray-700' },
  informed: { label: 'Informado', cls: 'bg-blue-100 text-blue-700' },
  granted: { label: 'Otorgado', cls: 'bg-green-100 text-green-700' },
  revoked: { label: 'Revocado', cls: 'bg-red-100 text-red-700' },
}

const CONSENT_METHOD: Record<ConsentMethod, string> = {
  verbal: 'Verbal',
  written: 'Escrito',
  email: 'Correo',
  contract: 'Contrato',
  platform: 'Plataforma',
}

function ConsentCard({ orgId, workerId, consent, onSaved }: { orgId: string; workerId: string; consent: WorkerConsent | null; onSaved: () => void }) {
  const current = consent ?? { worker_id: workerId, status: 'pending' as ConsentStatus, method: null, consent_date: null, notes: null, recorded_by_name: null, updated_at: null }
  const [editing, setEditing] = useState(false)
  const [status, setStatus] = useState<ConsentStatus>(current.status)
  const [method, setMethod] = useState<ConsentMethod | ''>(current.method ?? '')
  const [notes, setNotes] = useState(current.notes ?? '')
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const startEdit = () => {
    setStatus(current.status); setMethod(current.method ?? ''); setNotes(current.notes ?? '')
    setError(null); setEditing(true)
  }

  const save = async () => {
    setSaving(true); setError(null)
    try {
      const consentDate = (status === 'granted' || status === 'informed') ? new Date().toISOString() : null
      await api.setWorkerConsent(orgId, workerId, {
        status,
        method: method || null,
        consent_date: consentDate,
        notes: notes.trim() || null,
      })
      setEditing(false)
      toast.success('Consentimiento actualizado')
      onSaved()
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Error al guardar')
    } finally {
      setSaving(false)
    }
  }

  const badge = CONSENT_STATUS[current.status]

  return (
    <div className="bg-white rounded-xl border border-gray-200 p-4">
      <div className="flex items-center justify-between mb-3">
        <h2 className="font-semibold text-gray-900 flex items-center gap-2">
          <ShieldCheck className="w-4 h-4 text-gray-500" /> Consentimiento del trabajador
        </h2>
        {!editing && (
          <button onClick={startEdit} className="text-sm text-blue-600 hover:text-blue-700 font-medium">
            {consent ? 'Editar' : 'Registrar'}
          </button>
        )}
      </div>

      {!editing ? (
        <div className="space-y-1 text-sm">
          <div className="flex items-center gap-2">
            <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${badge.cls}`}>{badge.label}</span>
            {current.method && <span className="text-gray-500">· {CONSENT_METHOD[current.method]}</span>}
          </div>
          {current.notes && <p className="text-gray-600">{current.notes}</p>}
          {current.recorded_by_name && (
            <p className="text-xs text-gray-400">
              Registrado por {current.recorded_by_name}
              {current.updated_at && ` · ${new Date(current.updated_at).toLocaleDateString('es-CL')}`}
            </p>
          )}
          {current.status === 'pending' && (
            <p className="text-xs text-gray-400">
              Registra el consentimiento del trabajador para evaluar su desempeño (Ley N° 21.719).
            </p>
          )}
        </div>
      ) : (
        <div className="space-y-3">
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">Estado</label>
            <select value={status} onChange={(e) => setStatus(e.target.value as ConsentStatus)} className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm">
              {(Object.keys(CONSENT_STATUS) as ConsentStatus[]).map((s) => (
                <option key={s} value={s}>{CONSENT_STATUS[s].label}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">Vía (opcional)</label>
            <select value={method} onChange={(e) => setMethod(e.target.value as ConsentMethod | '')} className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm">
              <option value="">—</option>
              {(Object.keys(CONSENT_METHOD) as ConsentMethod[]).map((m) => (
                <option key={m} value={m}>{CONSENT_METHOD[m]}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">Notas (opcional)</label>
            <textarea value={notes} onChange={(e) => setNotes(e.target.value)} rows={2} className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" />
          </div>
          {error && <p className="text-sm text-red-600">{error}</p>}
          <div className="flex gap-2">
            <button onClick={save} disabled={saving} className="bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white text-sm font-medium rounded-lg px-4 py-2">
              {saving ? 'Guardando…' : 'Guardar'}
            </button>
            <button onClick={() => setEditing(false)} disabled={saving} className="text-gray-600 hover:bg-gray-100 text-sm rounded-lg px-4 py-2">
              Cancelar
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

function PortalShareCard({ orgId, workerId, token }: { orgId: string; workerId: string; token: string | null }) {
  const [url, setUrl] = useState<string | null>(token ? `${window.location.origin}/p/${token}` : null)
  const [busy, setBusy] = useState(false)

  const generate = async (regenerate = false) => {
    setBusy(true)
    try {
      const link = await api.createPortalLink(orgId, workerId, regenerate)
      const full = `${window.location.origin}${link.path}`
      setUrl(full)
      await navigator.clipboard.writeText(full).catch(() => {})
      toast.success(regenerate ? 'Enlace regenerado y copiado' : 'Enlace generado y copiado')
    } catch (e) {
      toast.error(e instanceof Error ? e.message : 'No se pudo generar el enlace')
    } finally {
      setBusy(false)
    }
  }

  const copy = async () => {
    if (!url) return
    await navigator.clipboard.writeText(url).catch(() => {})
    toast.success('Enlace copiado')
  }

  return (
    <div className="bg-white rounded-xl border border-gray-200 p-4">
      <h2 className="font-semibold text-gray-900 flex items-center gap-2 mb-1">
        <Link2 className="w-4 h-4 text-gray-500" /> Portal del trabajador
      </h2>
      <p className="text-sm text-gray-500 mb-2">
        Comparte un enlace privado para que el trabajador vea su historial, responda evaluaciones y ejerza sus derechos (Ley N° 21.719).
      </p>
      <div className="mb-3"><WatchButton clip="clip8" /></div>
      {url ? (
        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <input readOnly value={url} className="flex-1 min-w-0 border border-gray-300 rounded-lg px-3 py-2 text-xs text-gray-600 bg-gray-50" />
            <button onClick={copy} className="shrink-0 inline-flex items-center gap-1 text-sm text-blue-600 hover:text-blue-700 font-medium border border-gray-300 rounded-lg px-3 py-2">
              <Copy className="w-4 h-4" /> Copiar
            </button>
          </div>
          <button onClick={() => generate(true)} disabled={busy} className="text-xs text-gray-400 hover:text-gray-600 underline">
            Regenerar enlace (invalida el anterior)
          </button>
        </div>
      ) : (
        <button onClick={() => generate(false)} disabled={busy} className="inline-flex items-center gap-1.5 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white text-sm font-medium rounded-lg px-4 py-2">
          <Link2 className="w-4 h-4" /> {busy ? 'Generando…' : 'Generar enlace'}
        </button>
      )}
    </div>
  )
}

export default function WorkerDetail() {
  const { orgId: ORG_ID } = useOrg()
  const { id } = useParams()
  const [worker, setWorker] = useState<WorkerDetailType | null>(null)
  const [loading, setLoading] = useState(true)
  const [showEdit, setShowEdit] = useState(false)

  const load = useCallback(() => {
    if (!id || !ORG_ID) return
    api.getWorker(ORG_ID!, id).then(setWorker).catch(() => {}).finally(() => setLoading(false))
  }, [id, ORG_ID])

  useEffect(() => { load() }, [load])

  if (loading) return (
    <div className="space-y-6" aria-busy="true" aria-label="Cargando trabajador">
      <div className="h-7 w-56 bg-gray-200 rounded animate-pulse" />
      <div className="h-24 bg-gray-100 rounded-xl border border-gray-200 animate-pulse" />
      <div className="h-40 bg-gray-100 rounded-xl border border-gray-200 animate-pulse" />
      <div className="h-40 bg-gray-100 rounded-xl border border-gray-200 animate-pulse" />
    </div>
  )
  if (!worker) return <div className="text-gray-500">Trabajador no encontrado</div>

  const { avg_scores, score_trend, rehire_stats, evaluations } = worker
  const totalRehire = rehire_stats.yes + rehire_stats.reservations + rehire_stats.no

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <nav className="flex items-center gap-1 text-xs text-gray-500 mb-2" aria-label="Breadcrumb">
          <Link to="/app/workers" className="hover:text-gray-700">Trabajadores</Link>
          <span className="text-gray-400">/</span>
          <span className="text-gray-700 truncate">{worker.first_name} {worker.last_name}</span>
        </nav>
        <div className="flex items-center gap-3">
          <Link to="/app/workers" className="p-2 hover:bg-gray-100 rounded-lg" aria-label="Volver a trabajadores">
            <ArrowLeft className="w-5 h-5" />
          </Link>
          <div className="flex-1 min-w-0">
            <h1 className="text-2xl font-bold text-gray-900 truncate">{worker.first_name} {worker.last_name}</h1>
            <p className="text-sm text-gray-500 truncate">{worker.specialty} · {worker.rut}</p>
          </div>
          <ScoreBadge score={worker.avg_score} showScale />
          <button onClick={() => setShowEdit(true)} className="p-2 hover:bg-gray-100 rounded-lg text-gray-600" title="Editar">
            <Pencil className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Contact */}
      <div className="flex gap-3">
        {worker.phone && (
          <a href={`tel:${worker.phone}`} className="flex items-center gap-1.5 text-sm text-gray-600 bg-white border border-gray-200 rounded-lg px-3 py-2 hover:bg-gray-50">
            <Phone className="w-4 h-4" /> {worker.phone}
          </a>
        )}
        {worker.email && (
          <a href={`mailto:${worker.email}`} className="flex items-center gap-1.5 text-sm text-gray-600 bg-white border border-gray-200 rounded-lg px-3 py-2 hover:bg-gray-50">
            <Mail className="w-4 h-4" /> {worker.email}
          </a>
        )}
      </div>

      {/* Consent */}
      {ORG_ID && id && (
        <ConsentCard orgId={ORG_ID} workerId={id} consent={worker.consent} onSaved={load} />
      )}

      {/* Portal del trabajador */}
      {ORG_ID && id && (
        <PortalShareCard orgId={ORG_ID} workerId={id} token={worker.portal_token} />
      )}

      {/* Scores breakdown */}
      {avg_scores && (
        <div className="bg-white rounded-xl border border-gray-200 p-4">
          <div className="flex items-center justify-between gap-2 mb-1">
            <h2 className="font-semibold text-gray-900">Promedio por dimensión</h2>
            <Link to="/app/formula" className="text-xs text-blue-600 hover:text-blue-700 font-medium whitespace-nowrap">
              Cómo se pondera
            </Link>
          </div>
          <p className="text-xs text-gray-400 mb-3">
            El puntaje destacado ({worker.avg_score?.toFixed(1)}) es ponderado por industria; abajo, el promedio simple de cada dimensión.
          </p>
          <div className="space-y-3">
            {[
              { label: 'Calidad', value: avg_scores.quality },
              { label: 'Seguridad', value: avg_scores.safety },
              { label: 'Puntualidad', value: avg_scores.punctuality },
              { label: 'Trabajo en Equipo', value: avg_scores.teamwork },
              { label: 'Habilidad Técnica', value: avg_scores.technical },
            ].map(({ label, value }) => (
              <div key={label} className="flex items-center justify-between">
                <span className="text-sm text-gray-600">{label}</span>
                <div className="flex items-center gap-2">
                  <span className="text-xs text-gray-500 tabular-nums">{value.toFixed(1)} / 5</span>
                  <StarRating value={Math.round(value)} readonly size="sm" />
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Score trend chart */}
      {score_trend.length > 1 && (
        <div className="bg-white rounded-xl border border-gray-200 p-4">
          <h2 className="font-semibold text-gray-900 mb-3">Tendencia</h2>
          <ScoreSparkline points={score_trend} />
        </div>
      )}

      {/* Rehire stats */}
      {totalRehire > 0 && (
        <div className="bg-white rounded-xl border border-gray-200 p-4">
          <h2 className="font-semibold text-gray-900 mb-3">Recontratación</h2>
          <div className="flex gap-4">
            <div className="text-center">
              <p className="text-2xl font-bold text-green-600">{rehire_stats.yes}</p>
              <p className="text-xs text-gray-500">Sí</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-yellow-600">{rehire_stats.reservations}</p>
              <p className="text-xs text-gray-500">Reservas</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-red-600">{rehire_stats.no}</p>
              <p className="text-xs text-gray-500">No</p>
            </div>
          </div>
        </div>
      )}

      {ORG_ID && (
        <Modal open={showEdit} onClose={() => setShowEdit(false)} title="Editar Trabajador">
          <NewWorkerForm
            orgId={ORG_ID}
            initial={worker}
            onCreated={() => { setShowEdit(false); load() }}
            onCancel={() => setShowEdit(false)}
          />
        </Modal>
      )}

      {/* Evaluation history */}
      <div className="bg-white rounded-xl border border-gray-200 p-4">
        <div className="flex items-center justify-between mb-3">
          <h2 className="font-semibold text-gray-900">Historial de Evaluaciones</h2>
          {evaluations.length > 0 && (
            <button
              onClick={() => exportEvaluationsCsv(worker)}
              className="flex items-center gap-1.5 text-sm text-gray-600 border border-gray-300 rounded-lg px-2.5 py-1.5 hover:bg-gray-50"
              title="Exportar historial a CSV"
            >
              <Download className="w-4 h-4" /> <span className="hidden sm:inline">CSV</span>
            </button>
          )}
        </div>
        {evaluations.length === 0 ? (
          <div className="text-sm text-gray-500">
            <p>Sin evaluaciones todavía</p>
            <Link to="/app/evaluate" className="inline-flex items-center gap-1 mt-2 text-blue-600 hover:text-blue-700 font-medium">
              <ClipboardCheck className="w-4 h-4" /> Evaluar en un proyecto
            </Link>
          </div>
        ) : (
          <div className="space-y-3">
            {evaluations.map((ev) => {
              const rehire = REHIRE_OPTIONS.find((o) => o.value === ev.would_rehire)
              return (
                <div key={ev.id} className="border border-gray-100 rounded-lg p-3">
                  <div className="flex items-center justify-between gap-2 mb-2">
                    <span className="text-sm font-medium text-gray-900 truncate">{ev.project_name}</span>
                    <ScoreBadge score={ev.score_weighted} size="sm" />
                  </div>
                  {/* 5 dimensiones (no solo el promedio) */}
                  <div className="grid grid-cols-5 gap-1.5 text-center">
                    {EVAL_DIMS.map((d) => (
                      <div key={d.key} className="bg-gray-50 rounded-md py-1.5">
                        <div className="text-[10px] uppercase tracking-wide text-gray-400">{d.short}</div>
                        <div className="text-sm font-semibold text-gray-800 tabular-nums">{ev[d.key]}</div>
                      </div>
                    ))}
                  </div>
                  {rehire && (
                    <p className="mt-2 text-xs">
                      <span className="text-gray-500">Recontratación: </span>
                      <span className={`px-1.5 py-0.5 rounded-full font-medium ${rehire.color}`}>{rehire.label}</span>
                      {ev.rehire_reason && <span className="text-gray-500"> — {ev.rehire_reason}</span>}
                    </p>
                  )}
                  {ev.comment && <p className="text-xs text-gray-600 mt-1.5">{ev.comment}</p>}
                  {ev.worker_reply && (
                    <div className="mt-2 border-l-2 border-blue-300 pl-2.5">
                      <p className="text-[11px] font-medium text-blue-700 flex items-center gap-1">
                        <MessageSquare className="w-3 h-3" /> Respuesta del trabajador
                        {ev.worker_reply_at && ` · ${new Date(ev.worker_reply_at).toLocaleDateString('es-CL')}`}
                      </p>
                      <p className="text-xs text-gray-700">{ev.worker_reply}</p>
                    </div>
                  )}
                  <p className="text-xs text-gray-400 mt-1">{ev.evaluator_name || 'Sin evaluador'} · {new Date(ev.created_at).toLocaleDateString('es-CL')}</p>
                </div>
              )
            })}
          </div>
        )}
      </div>
    </div>
  )
}
