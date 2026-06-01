import { useEffect, useState } from 'react'

// Gate de acceso para el pre-lanzamiento: muestra un overlay de marca que pide
// un código antes de dejar entrar a la app. Es del lado del cliente (suficiente
// para "aún no público"); el código se comparte con testers.
//
// Para DESACTIVARLO al lanzar: poner VITE_ACCESS_GATE=false (o quitar el wrapper).
// El código se puede sobrescribir con VITE_ACCESS_CODE.
const KEY = 'recontrata_access'
const CODE = (import.meta.env.VITE_ACCESS_CODE || 'recontrata2211').toLowerCase()
const ENABLED = import.meta.env.VITE_ACCESS_GATE !== 'false'
const TTL = 90 * 24 * 60 * 60 * 1000 // 90 días

function isUnlocked(): boolean {
  try {
    const raw = localStorage.getItem(KEY)
    if (!raw) return false
    const exp = parseInt(raw, 10)
    return Number.isFinite(exp) && exp > Date.now()
  } catch {
    return false
  }
}

export default function AccessGate({ children }: { children: React.ReactNode }) {
  const [unlocked, setUnlocked] = useState(() => !ENABLED || isUnlocked())
  const [code, setCode] = useState('')
  const [error, setError] = useState(false)

  // Si mostramos el gate, retirar el splash del logo (no debe taparlo).
  useEffect(() => {
    if (!unlocked) document.getElementById('boot-splash')?.remove()
  }, [unlocked])

  if (unlocked) return <>{children}</>

  const submit = (e: React.FormEvent) => {
    e.preventDefault()
    if (code.trim().toLowerCase() === CODE) {
      try {
        localStorage.setItem(KEY, String(Date.now() + TTL))
      } catch {
        /* ignore */
      }
      setUnlocked(true)
    } else {
      setError(true)
    }
  }

  return (
    <div className="relative flex min-h-screen items-center justify-center overflow-hidden bg-slate-50 px-4">
      <div className="pointer-events-none absolute -left-24 -top-24 h-[26rem] w-[26rem] rounded-full bg-blue-300/30 blur-3xl" />
      <div className="pointer-events-none absolute -bottom-24 -right-24 h-[26rem] w-[26rem] rounded-full bg-sky-300/30 blur-3xl" />
      <div className="relative z-10 w-full max-w-sm rounded-2xl border border-blue-100 bg-white p-8 text-center shadow-xl shadow-blue-500/10">
        <img src="/logo-recontrata.png" alt="Recontrata" className="mx-auto h-12 w-auto" />
        <h1 className="mt-6 text-lg font-semibold text-slate-900">
          Estamos afinando los últimos detalles
        </h1>
        <p className="mt-2 text-sm text-slate-500">
          Recontrata está en preparación. Ingresa tu código de acceso para entrar.
        </p>
        <form onSubmit={submit} className="mt-6">
          <input
            type="text"
            value={code}
            onChange={(e) => {
              setCode(e.target.value)
              setError(false)
            }}
            placeholder="Código de acceso"
            autoFocus
            autoComplete="off"
            className={`w-full rounded-xl border px-4 py-2.5 text-center text-slate-900 outline-none transition ${
              error
                ? 'border-rose-300 focus:border-rose-400 focus:ring-2 focus:ring-rose-100'
                : 'border-blue-200 focus:border-blue-400 focus:ring-2 focus:ring-blue-100'
            }`}
          />
          {error && (
            <p className="mt-2 text-xs text-rose-500">
              Código incorrecto. Inténtalo de nuevo.
            </p>
          )}
          <button
            type="submit"
            className="mt-4 w-full rounded-xl bg-gradient-to-r from-blue-700 to-blue-600 px-4 py-2.5 font-medium text-white shadow-lg shadow-blue-600/25 transition hover:brightness-110"
          >
            Entrar
          </button>
        </form>
        <p className="mt-5 text-xs text-slate-400">
          ¿No tienes código? Pídeselo a tu contacto en Recontrata.
        </p>
      </div>
    </div>
  )
}
