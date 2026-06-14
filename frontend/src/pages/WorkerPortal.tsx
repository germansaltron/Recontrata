import { useCallback, useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { Scale, ShieldCheck, MessageSquare, Info } from 'lucide-react'
import { api, type PortalProfile, type PortalEvaluation, type ScoringProfile } from '../lib/api'
import { toast } from '../lib/toast'

const REHIRE: Record<string, { label: string; cls: string }> = {
  yes: { label: 'Sí, recontratable', cls: 'bg-green-100 text-green-800' },
  reservations: { label: 'Con reservas', cls: 'bg-yellow-100 text-yellow-800' },
  no: { label: 'No recontratable', cls: 'bg-red-100 text-red-800' },
}

const DIMS: { key: keyof PortalEvaluation; short: string }[] = [
  { key: 'score_quality', short: 'Calidad' },
  { key: 'score_safety', short: 'Seguridad' },
  { key: 'score_punctuality', short: 'Puntualidad' },
  { key: 'score_teamwork', short: 'Equipo' },
  { key: 'score_technical', short: 'Técnica' },
]

function fmtDate(iso: string | null) {
  return iso ? new Date(iso).toLocaleDateString('es-CL') : ''
}

function FormulaBox({ profile }: { profile: ScoringProfile }) {
  const sorted = [...profile.weights].sort((a, b) => b.weight - a.weight)
  const max = Math.max(...sorted.map((w) => w.weight))
  return (
    <div className="bg-white rounded-xl border border-gray-200 p-4">
      <h2 className="font-semibold text-gray-900 flex items-center gap-2 mb-1">
        <Scale className="w-4 h-4 text-blue-600" /> Cómo se calcula tu puntaje
      </h2>
      <p className="text-sm text-gray-500 mb-3">
        Perfil <span className="font-medium">{profile.label}</span>. Cada dimensión pesa distinto:
      </p>
      <div className="space-y-2">
        {sorted.map((w) => (
          <div key={w.key} className="flex items-center gap-3">
            <span className="w-36 shrink-0 text-sm text-gray-700">{w.label}</span>
            <div className="flex-1 h-5 bg-gray-100 rounded-md overflow-hidden">
              <div className="h-full bg-blue-600 rounded-md" style={{ width: `${(w.weight / max) * 100}%` }} />
            </div>
            <span className="w-10 text-right text-sm font-semibold text-gray-900 tabular-nums">{Math.round(w.weight * 100)}%</span>
          </div>
        ))}
      </div>
    </div>
  )
}

function EvaluationCard({ token, ev, onReplied }: { token: string; ev: PortalEvaluation; onReplied: () => void }) {
  const [replying, setReplying] = useState(false)
  const [text, setText] = useState('')
  const [saving, setSaving] = useState(false)
  const rehire = REHIRE[ev.would_rehire] ?? { label: ev.would_rehire, cls: 'bg-gray-100 text-gray-700' }

  const submit = async () => {
    if (!text.trim()) return
    setSaving(true)
    try {
      await api.portalReply(token, ev.id, text.trim())
      toast.success('Tu respuesta quedó registrada')
      setReplying(false)
      onReplied()
    } catch (e) {
      toast.error(e instanceof Error ? e.message : 'No se pudo enviar tu respuesta')
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="bg-white rounded-xl border border-gray-200 p-4">
      <div className="flex items-center justify-between gap-2 mb-3">
        <div className="min-w-0">
          <p className="font-medium text-gray-900 truncate">{ev.project_name}</p>
          <p className="text-xs text-gray-400">{fmtDate(ev.created_at)}</p>
        </div>
        <div className="text-right shrink-0">
          <div className="text-xl font-bold text-gray-900 tabular-nums">{ev.score_weighted.toFixed(1)}<span className="text-sm text-gray-400"> / 5</span></div>
        </div>
      </div>

      <div className="grid grid-cols-5 gap-1.5 text-center mb-3">
        {DIMS.map((d) => (
          <div key={d.key} className="bg-gray-50 rounded-md py-1.5">
            <div className="text-[10px] uppercase tracking-wide text-gray-400">{d.short}</div>
            <div className="text-sm font-semibold text-gray-800 tabular-nums">{ev[d.key] as number}</div>
          </div>
        ))}
      </div>

      <div className="text-sm">
        <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${rehire.cls}`}>{rehire.label}</span>
        {ev.rehire_reason && <p className="mt-1.5 text-gray-600"><span className="text-gray-400">Motivo: </span>{ev.rehire_reason}</p>}
        {ev.comment && <p className="mt-1 text-gray-600">{ev.comment}</p>}
      </div>

      {/* Réplica del trabajador */}
      {ev.worker_reply ? (
        <div className="mt-3 border-l-2 border-blue-300 pl-3">
          <p className="text-xs font-medium text-blue-700 flex items-center gap-1">
            <MessageSquare className="w-3.5 h-3.5" /> Tu respuesta {ev.worker_reply_at && `· ${fmtDate(ev.worker_reply_at)}`}
          </p>
          <p className="text-sm text-gray-700 mt-0.5">{ev.worker_reply}</p>
        </div>
      ) : replying ? (
        <div className="mt-3 space-y-2">
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            rows={3}
            maxLength={2000}
            placeholder="Escribe tu respuesta a esta evaluación…"
            className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm"
          />
          <div className="flex gap-2">
            <button onClick={submit} disabled={saving || !text.trim()} className="bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white text-sm font-medium rounded-lg px-4 py-2">
              {saving ? 'Enviando…' : 'Enviar respuesta'}
            </button>
            <button onClick={() => setReplying(false)} disabled={saving} className="text-gray-600 hover:bg-gray-100 text-sm rounded-lg px-4 py-2">Cancelar</button>
          </div>
        </div>
      ) : (
        <button onClick={() => setReplying(true)} className="mt-3 inline-flex items-center gap-1.5 text-sm text-blue-600 hover:text-blue-700 font-medium">
          <MessageSquare className="w-4 h-4" /> Responder a esta evaluación
        </button>
      )}
    </div>
  )
}

export default function WorkerPortal() {
  const { token } = useParams()
  const [profile, setProfile] = useState<PortalProfile | null>(null)
  const [loading, setLoading] = useState(true)
  const [notFound, setNotFound] = useState(false)
  const [optingOut, setOptingOut] = useState(false)
  const [optNotes, setOptNotes] = useState('')

  const load = useCallback(() => {
    if (!token) return
    api.getPortal(token)
      .then((p) => { setProfile(p); setNotFound(false) })
      .catch(() => setNotFound(true))
      .finally(() => setLoading(false))
  }, [token])

  useEffect(() => { load() }, [load])

  const doOptOut = async () => {
    if (!token) return
    try {
      await api.portalOptOut(token, optNotes.trim() || undefined)
      toast.success('Registramos tu solicitud de baja')
      setOptingOut(false)
      setOptNotes('')
      load()
    } catch (e) {
      toast.error(e instanceof Error ? e.message : 'No se pudo registrar tu solicitud')
    }
  }

  if (loading) return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center text-gray-400" aria-busy="true">
      <span className="w-5 h-5 border-2 border-gray-300 border-t-blue-600 rounded-full animate-spin mr-2" /> Cargando…
    </div>
  )

  if (notFound || !profile) return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
      <div className="max-w-md text-center bg-white rounded-xl border border-gray-200 p-8">
        <h1 className="text-xl font-bold text-gray-900">Enlace no válido</h1>
        <p className="mt-2 text-sm text-gray-500">Este enlace no existe o fue desactivado. Pide a la empresa que te comparta uno nuevo.</p>
      </div>
    </div>
  )

  const revoked = profile.consent_status === 'revoked'

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-2xl mx-auto px-4 h-14 flex items-center justify-between">
          <span className="text-lg font-bold text-gray-900">Recontrata</span>
          <span className="text-xs text-gray-400">Portal del trabajador</span>
        </div>
      </header>

      <main className="max-w-2xl mx-auto px-4 py-6 space-y-5">
        {/* Identidad + score */}
        <div className="bg-white rounded-xl border border-gray-200 p-5">
          <div className="flex items-start justify-between gap-3">
            <div className="min-w-0">
              <h1 className="text-2xl font-bold text-gray-900 truncate">{profile.worker_name}</h1>
              <p className="text-sm text-gray-500">{profile.specialty} · {profile.rut}</p>
              <p className="text-xs text-gray-400 mt-0.5">Historial en {profile.org_name}</p>
            </div>
            {profile.avg_score != null && (
              <div className="text-right shrink-0">
                <div className="text-3xl font-bold text-blue-600 tabular-nums">{profile.avg_score.toFixed(1)}</div>
                <div className="text-xs text-gray-400">de 5 · ponderado</div>
              </div>
            )}
          </div>
          <div className="mt-4 flex flex-wrap gap-3 text-center">
            <div className="flex-1 min-w-[80px] bg-green-50 rounded-lg py-2">
              <p className="text-xl font-bold text-green-600">{profile.rehire_yes}</p>
              <p className="text-xs text-gray-500">Sí</p>
            </div>
            <div className="flex-1 min-w-[80px] bg-yellow-50 rounded-lg py-2">
              <p className="text-xl font-bold text-yellow-600">{profile.rehire_reservations}</p>
              <p className="text-xs text-gray-500">Reservas</p>
            </div>
            <div className="flex-1 min-w-[80px] bg-red-50 rounded-lg py-2">
              <p className="text-xl font-bold text-red-600">{profile.rehire_no}</p>
              <p className="text-xs text-gray-500">No</p>
            </div>
          </div>
        </div>

        {revoked && (
          <div className="bg-amber-50 border border-amber-200 rounded-xl p-4 text-sm text-amber-800 flex gap-2">
            <ShieldCheck className="w-5 h-5 shrink-0" />
            Registramos tu solicitud de no ser evaluado. La empresa fue notificada en tu ficha.
          </div>
        )}

        <FormulaBox profile={profile.formula} />

        {/* Evaluaciones */}
        <div className="space-y-3">
          <h2 className="font-semibold text-gray-900">Tus evaluaciones ({profile.evaluation_count})</h2>
          {profile.evaluations.length === 0 ? (
            <p className="text-sm text-gray-500 bg-white rounded-xl border border-gray-200 p-4">Aún no tienes evaluaciones registradas.</p>
          ) : (
            profile.evaluations.map((ev) => (
              <EvaluationCard key={ev.id} token={token!} ev={ev} onReplied={load} />
            ))
          )}
        </div>

        {/* Transparencia + opt-out */}
        <div className="flex gap-3 text-xs text-gray-500 bg-gray-100 rounded-xl p-4">
          <Info className="w-4 h-4 shrink-0 text-gray-400" />
          <p>Ves tu propio historial por transparencia (art. 16, Ley N° 21.719). Puedes responder cada evaluación; tu respuesta queda visible para la empresa.</p>
        </div>

        {!revoked && (
          <div className="text-center">
            {optingOut ? (
              <div className="bg-white rounded-xl border border-gray-200 p-4 text-left space-y-2">
                <p className="text-sm text-gray-700">¿Solicitar dejar de ser evaluado? La empresa quedará notificada.</p>
                <textarea
                  value={optNotes}
                  onChange={(e) => setOptNotes(e.target.value)}
                  rows={2}
                  maxLength={2000}
                  placeholder="Motivo (opcional)"
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm"
                />
                <div className="flex gap-2">
                  <button onClick={doOptOut} className="bg-red-600 hover:bg-red-700 text-white text-sm font-medium rounded-lg px-4 py-2">Confirmar baja</button>
                  <button onClick={() => setOptingOut(false)} className="text-gray-600 hover:bg-gray-100 text-sm rounded-lg px-4 py-2">Cancelar</button>
                </div>
              </div>
            ) : (
              <button onClick={() => setOptingOut(true)} className="text-sm text-gray-500 hover:text-red-600 underline">
                Solicitar dejar de ser evaluado
              </button>
            )}
          </div>
        )}
      </main>
    </div>
  )
}
