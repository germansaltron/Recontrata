import { useCallback, useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../lib/api'
import { toast } from '../lib/toast'

// Gate de aceptación del Contrato (primer ingreso). Envuelve la app protegida: si el
// usuario autenticado no ha aceptado la versión vigente del contrato, bloquea el acceso
// hasta que lo acepte. Fail-closed: ante un error de verificación no deja pasar, ofrece
// reintentar (la aceptación es requisito legal, previo a cualquier uso o pago).
type State = 'loading' | 'ok' | 'needs-accept' | 'error'

export default function ContractGate({ children }: { children: React.ReactNode }) {
  const [state, setState] = useState<State>('loading')
  const [checked, setChecked] = useState(false)
  const [accepting, setAccepting] = useState(false)

  const check = useCallback(() => {
    setState('loading')
    api.getContractStatus()
      .then((s) => setState(s.accepted ? 'ok' : 'needs-accept'))
      .catch(() => setState('error'))
  }, [])

  useEffect(() => { check() }, [check])

  async function handleAccept() {
    if (!checked || accepting) return
    setAccepting(true)
    try {
      await api.acceptContract()
      setState('ok')
    } catch {
      toast.error('No pudimos registrar tu aceptación', 'Revisa tu conexión e inténtalo de nuevo.')
    } finally {
      setAccepting(false)
    }
  }

  if (state === 'ok') return <>{children}</>

  if (state === 'loading') {
    return <div className="min-h-screen flex items-center justify-center text-gray-400">Cargando…</div>
  }

  if (state === 'error') {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50 p-4">
        <div className="max-w-md text-center bg-white rounded-xl border border-gray-200 p-6">
          <h1 className="font-semibold text-gray-900">No pudimos verificar tu aceptación</h1>
          <p className="mt-2 text-sm text-gray-500">Revisa tu conexión e inténtalo de nuevo.</p>
          <button
            onClick={check}
            className="mt-4 px-4 py-2 rounded-lg bg-blue-600 text-white text-sm font-medium hover:bg-blue-700"
          >
            Reintentar
          </button>
        </div>
      </div>
    )
  }

  // needs-accept
  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-50 p-4">
      <div className="max-w-lg w-full bg-white rounded-2xl border border-gray-200 shadow-sm p-6 md:p-8">
        <h1 className="text-xl font-bold text-gray-900">Antes de continuar</h1>
        <p className="mt-3 text-sm text-gray-600 leading-relaxed">
          Para usar Recontrata necesitas aceptar el Contrato de Suscripción y Términos de Servicio.
          Es importante: define cómo tratas los datos de tus trabajadores conforme a la Ley N° 21.719
          y las condiciones del servicio.
        </p>
        <label className="mt-6 flex items-start gap-3 text-sm text-gray-700 cursor-pointer">
          <input
            type="checkbox"
            checked={checked}
            onChange={(e) => setChecked(e.target.checked)}
            className="mt-1 h-4 w-4 shrink-0"
          />
          <span>
            He leído y acepto el{' '}
            <Link to="/terminos" target="_blank" className="text-blue-600 hover:underline">
              Contrato de Suscripción y Términos de Servicio
            </Link>{' '}
            y la{' '}
            <Link to="/privacidad" target="_blank" className="text-blue-600 hover:underline">
              Política de Privacidad
            </Link>.
          </span>
        </label>
        <button
          onClick={handleAccept}
          disabled={!checked || accepting}
          className="mt-6 w-full px-4 py-2.5 rounded-lg bg-blue-600 text-white font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {accepting ? 'Registrando…' : 'Aceptar y continuar'}
        </button>
      </div>
    </div>
  )
}
