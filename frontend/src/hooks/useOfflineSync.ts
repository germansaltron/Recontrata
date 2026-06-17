import { useCallback, useEffect, useRef, useState } from 'react'
import { flushQueue } from '../lib/offlineSync'
import { countQueuedEvaluations } from '../lib/offlineQueue'
import { invalidate } from '../lib/swr'
import { toast } from '../lib/toast'

// Orquesta el envío de la cola offline (apuesta #3, punto 3): dispara al volver
// la conexión, al montar (si hay pendientes) y por botón manual. Muestra toasts
// y refresca los pendientes por proyecto tras sincronizar.
export function useOfflineSync() {
  const running = useRef(false)
  const [syncing, setSyncing] = useState(false)

  const sync = useCallback(async (opts?: { manual?: boolean }) => {
    if (running.current) return
    if (!navigator.onLine) {
      if (opts?.manual) toast.info('Sin conexión', 'Conéctate para sincronizar.')
      return
    }
    const pending = await countQueuedEvaluations()
    if (pending === 0) {
      if (opts?.manual) toast.info('Todo al día', 'No hay evaluaciones pendientes.')
      return
    }

    running.current = true
    setSyncing(true)
    try {
      const res = await flushQueue()
      if (res.sent > 0) {
        // Los pendientes por proyecto cambiaron: forzar refetch en la próxima visita.
        invalidate((k) => k.startsWith('projects-pending:'))
        toast.success(
          res.sent === 1 ? 'Evaluación sincronizada' : `${res.sent} evaluaciones sincronizadas`,
          res.remaining > 0 ? `Quedan ${res.remaining} por enviar.` : undefined,
        )
      }
      if (res.failed.length > 0) {
        toast.error(
          res.failed.length === 1
            ? '1 evaluación no se pudo enviar'
            : `${res.failed.length} evaluaciones no se pudieron enviar`,
          res.failed[0].reason,
        )
      }
    } finally {
      running.current = false
      setSyncing(false)
    }
  }, [])

  useEffect(() => {
    const onOnline = () => { void sync() }
    window.addEventListener('online', onOnline)
    void sync() // intento al montar (si hay conexión y pendientes)
    return () => window.removeEventListener('online', onOnline)
  }, [sync])

  return { sync, syncing }
}
