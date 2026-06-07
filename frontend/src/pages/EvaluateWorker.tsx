import { useEffect, useRef, useState } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { Save, ArrowLeft, Check } from 'lucide-react'
import StarRating from '../components/ui/StarRating'
import { api } from '../lib/api'
import { useOrg } from '../lib/org'
import { SCORE_DIMENSIONS, REHIRE_OPTIONS } from '../lib/constants'
import { formatRelative } from '../lib/dates'

const draftKey = (projectId: string, workerId: string) => `faenascore:draft:${projectId}:${workerId}`

interface Draft {
  scores: number[]
  wouldRehire: string
  rehireReason: string
  comment: string
  ts: number
}

interface ContextHeader {
  worker_name: string
  worker_rut: string
  worker_specialty: string
  project_name: string
  project_client?: string | null
}

export default function EvaluateWorker() {
  const { orgId: ORG_ID } = useOrg()
  const { projectId, workerId } = useParams()
  const navigate = useNavigate()

  const [ctx, setCtx] = useState<ContextHeader | null>(null)
  const [scores, setScores] = useState([0, 0, 0, 0, 0])
  const [wouldRehire, setWouldRehire] = useState('')
  const [rehireReason, setRehireReason] = useState('')
  const [comment, setComment] = useState('')
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')
  const [draftSavedAt, setDraftSavedAt] = useState<number | null>(null)
  const draftRestoredRef = useRef(false)

  // Restore draft from localStorage on mount
  useEffect(() => {
    if (!projectId || !workerId) return
    const raw = localStorage.getItem(draftKey(projectId, workerId))
    if (!raw) { draftRestoredRef.current = true; return }
    try {
      const d = JSON.parse(raw) as Partial<Draft>
      if (Array.isArray(d.scores) && d.scores.length === 5) setScores(d.scores.map((n) => Number(n) || 0))
      if (typeof d.wouldRehire === 'string') setWouldRehire(d.wouldRehire)
      if (typeof d.rehireReason === 'string') setRehireReason(d.rehireReason)
      if (typeof d.comment === 'string') setComment(d.comment)
      if (typeof d.ts === 'number') setDraftSavedAt(d.ts)
    } catch { /* corrupt draft -> ignore */ }
    draftRestoredRef.current = true
  }, [projectId, workerId])

  // Persist draft on every change (after initial restore)
  useEffect(() => {
    if (!projectId || !workerId || !draftRestoredRef.current) return
    const hasContent = scores.some((s) => s > 0) || wouldRehire !== '' || rehireReason !== '' || comment !== ''
    const key = draftKey(projectId, workerId)
    if (!hasContent) {
      localStorage.removeItem(key)
      setDraftSavedAt(null)
      return
    }
    const ts = Date.now()
    const payload: Draft = { scores, wouldRehire, rehireReason, comment, ts }
    try {
      localStorage.setItem(key, JSON.stringify(payload))
      setDraftSavedAt(ts)
    } catch { /* localStorage full or disabled -> silently skip */ }
  }, [scores, wouldRehire, rehireReason, comment, projectId, workerId])

  useEffect(() => {
    if (!ORG_ID || !projectId || !workerId) return
    let cancelled = false
    Promise.all([
      api.getWorker(ORG_ID, workerId),
      api.getProject(ORG_ID, projectId),
    ])
      .then(([w, p]) => {
        if (cancelled) return
        setCtx({
          worker_name: `${w.first_name} ${w.last_name}`,
          worker_rut: w.rut,
          worker_specialty: w.specialty,
          project_name: p.name,
          project_client: p.client_name,
        })
      })
      .catch(() => { /* header stays in loading state; submit still works */ })
    return () => { cancelled = true }
  }, [ORG_ID, projectId, workerId])

  const missingScores = scores.filter((s) => s === 0).length
  const allScoresSet = missingScores === 0
  const needsReason = wouldRehire === 'reservations' || wouldRehire === 'no'
  const reasonOk = !needsReason || rehireReason.trim().length >= 3
  const canSubmit = allScoresSet && wouldRehire !== '' && reasonOk

  let missingLabel = ''
  if (!allScoresSet) {
    missingLabel = missingScores === 5
      ? 'Completa los 5 puntajes'
      : `Falta ${missingScores === 1 ? '1 puntaje' : `${missingScores} puntajes`}`
  } else if (wouldRehire === '') {
    missingLabel = 'Indica si recontratarías'
  } else if (!reasonOk) {
    missingLabel = 'Escribe el motivo (mínimo 3 caracteres)'
  }

  async function handleSubmit() {
    if (!canSubmit || !projectId || !workerId) return
    setSaving(true)
    setError('')

    try {
      await api.createEvaluation(ORG_ID!, {
        project_id: projectId,
        worker_id: workerId,
        score_quality: scores[0],
        score_safety: scores[1],
        score_punctuality: scores[2],
        score_teamwork: scores[3],
        score_technical: scores[4],
        would_rehire: wouldRehire,
        rehire_reason: rehireReason || undefined,
        comment: comment || undefined,
      })
      localStorage.removeItem(draftKey(projectId, workerId))
      navigate(`/app/projects/${projectId}`)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Error al guardar')
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="max-w-lg mx-auto space-y-6">
      {/* Header */}
      <div>
        {ctx && projectId && (
          <nav className="flex items-center gap-1 text-xs text-gray-500 mb-2 pl-11" aria-label="Breadcrumb">
            <Link to="/app/projects" className="hover:text-gray-700">Proyectos</Link>
            <span className="text-gray-400">/</span>
            <Link to={`/app/projects/${projectId}`} className="hover:text-gray-700 truncate max-w-[10rem]">{ctx.project_name}</Link>
            <span className="text-gray-400">/</span>
            <span className="text-gray-700">Evaluar</span>
          </nav>
        )}
        <div className="flex items-start gap-3">
          <button onClick={() => navigate(-1)} className="p-2 hover:bg-gray-100 rounded-lg shrink-0 mt-0.5" aria-label="Volver">
            <ArrowLeft className="w-5 h-5" />
          </button>
          <div className="min-w-0 flex-1">
            <p className="text-xs font-medium text-gray-500 uppercase tracking-wide">Evaluar Trabajador</p>
            {ctx ? (
              <>
                <h1 className="text-xl font-bold text-gray-900 truncate">{ctx.worker_name}</h1>
                <p className="text-sm text-gray-600 truncate">
                  {ctx.worker_specialty} · RUT {ctx.worker_rut}
                </p>
                <p className="text-sm text-gray-500 mt-1 truncate">
                  Proyecto: <span className="font-medium text-gray-700">{ctx.project_name}</span>
                  {ctx.project_client ? ` · ${ctx.project_client}` : ''}
                </p>
              </>
            ) : (
              <>
                <div className="h-5 w-40 bg-gray-200 rounded animate-pulse mt-1" />
                <div className="h-4 w-32 bg-gray-100 rounded animate-pulse mt-1" />
              </>
            )}
          </div>
        </div>
      </div>

      {/* Score dimensions */}
      <div className="bg-white rounded-xl border border-gray-200 p-4 divide-y divide-gray-100">
        {SCORE_DIMENSIONS.map((dim, i) => {
          const current = scores[i] as 0 | 1 | 2 | 3 | 4 | 5
          return (
            <div key={dim.label} className="py-4 first:pt-0 last:pb-0">
              <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
                <div className="min-w-0">
                  <span className="text-sm font-medium text-gray-700">{dim.label}</span>
                  <p className="text-xs text-gray-400 mt-0.5">{dim.hint}</p>
                </div>
                <StarRating value={current} onChange={(v) => { const n = [...scores]; n[i] = v; setScores(n) }} size="lg" />
              </div>
              {/* Ancla del nivel seleccionado: evaluación más objetiva (BARS) */}
              {current > 0 && (
                <p className="mt-1.5 text-xs text-gray-600 bg-gray-50 rounded-md px-2.5 py-1.5">
                  <span className="font-semibold text-gray-700">{current}/5 ·</span> {dim.anchors[current as 1 | 2 | 3 | 4 | 5]}
                </p>
              )}
            </div>
          )
        })}
      </div>

      {/* Rehire */}
      <div className="bg-white rounded-xl border border-gray-200 p-4 space-y-3">
        <p className="text-sm font-medium text-gray-700">¿Recontratarías a este trabajador?</p>
        <div className="grid grid-cols-3 gap-2">
          {REHIRE_OPTIONS.map((opt) => (
            <button
              key={opt.value}
              type="button"
              onClick={() => setWouldRehire(opt.value)}
              className={`py-3 px-2 rounded-lg text-sm font-medium border-2 transition-all touch-manipulation ${
                wouldRehire === opt.value
                  ? `${opt.color} border-current`
                  : 'border-gray-200 text-gray-600 hover:border-gray-300'
              }`}
            >
              {opt.label}
            </button>
          ))}
        </div>

        {needsReason && (
          <div>
            <textarea
              placeholder="Motivo (requerido)..."
              value={rehireReason}
              onChange={(e) => setRehireReason(e.target.value)}
              rows={2}
              className={`w-full px-3 py-2 border rounded-lg text-sm resize-none focus:ring-2 focus:ring-blue-500 ${
                rehireReason.trim().length > 0 && !reasonOk ? 'border-red-400' : 'border-gray-300'
              }`}
            />
            {!reasonOk && rehireReason.trim().length > 0 && (
              <p className="text-xs text-red-600 mt-1">El motivo debe tener al menos 3 caracteres</p>
            )}
          </div>
        )}
      </div>

      {/* Comment */}
      <div className="bg-white rounded-xl border border-gray-200 p-4">
        <textarea
          placeholder="Comentario adicional (opcional)..."
          value={comment}
          onChange={(e) => setComment(e.target.value)}
          rows={3}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm resize-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      {/* Error */}
      {error && <p className="text-sm text-red-600 bg-red-50 p-3 rounded-lg">{error}</p>}

      {/* Submit */}
      <div className="space-y-2">
        <button
          onClick={handleSubmit}
          disabled={!canSubmit || saving}
          title={canSubmit ? undefined : missingLabel}
          className="w-full flex items-center justify-center gap-2 bg-blue-600 text-white py-3.5 rounded-xl text-base font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed touch-manipulation"
        >
          <Save className="w-5 h-5" />
          {saving ? 'Guardando...' : 'Guardar Evaluación'}
        </button>
        {!canSubmit && !saving && missingLabel && (
          <p className="text-xs text-center text-gray-500">{missingLabel}</p>
        )}
        {canSubmit && !saving && draftSavedAt && (
          <p className="flex items-center justify-center gap-1 text-xs text-gray-400">
            <Check className="w-3 h-3" />
            Borrador guardado {formatRelative(new Date(draftSavedAt).toISOString())}
          </p>
        )}
      </div>
    </div>
  )
}
