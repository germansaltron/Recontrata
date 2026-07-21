import { api, ApiError } from './api'
import { getQueuedEvaluations, removeQueuedEvaluation, countQueuedEvaluations } from './offlineQueue'

// Envío de la cola offline (apuesta #3, punto 3). Reenvía a la API las
// evaluaciones que se guardaron sin señal (punto 2) y las saca de la cola.

export interface FlushResult {
  sent: number
  failed: { label: string; reason: string }[]
  remaining: number
}

export type FlushDecision = 'network' | 'retriable' | 'permanent'

// Solo estos status significan que ESTE item nunca va a entrar (validación o
// duplicado): se descarta de la cola. Cualquier otro error —incluido 401 (token
// lento o sin señal), 402, 408, 429 y 5xx— es transitorio: se conserva la
// evaluación y se reintenta luego. Regla de oro: ante la duda, NUNCA borrar;
// perder una evaluación creada en terreno es el peor resultado para el producto.
const PERMANENT_STATUSES = new Set<number>([400, 409, 422])

/** Decide qué hacer con una evaluación de la cola cuando su envío falla.
 *  - 'network'   → se cayó la red (fetch lanza TypeError, o el navegador está offline).
 *  - 'permanent' → error definitivo de ESE item (validación/duplicado): descartarlo.
 *  - 'retriable' → transitorio (auth, servidor, rate limit, desconocido): conservar. */
export function classifyFlushError(e: unknown, isOnline: boolean): FlushDecision {
  if (e instanceof TypeError || !isOnline) return 'network'
  const status = e instanceof ApiError ? e.status : undefined
  if (typeof status === 'number' && PERMANENT_STATUSES.has(status)) return 'permanent'
  return 'retriable'
}

// Evita flushes concurrentes (varios triggers: evento online, montaje, botón manual).
let flushing = false

export async function flushQueue(): Promise<FlushResult> {
  const remainingResult = async (sent: number, failed: FlushResult['failed']): Promise<FlushResult> => ({
    sent,
    failed,
    remaining: await countQueuedEvaluations(),
  })

  if (flushing || !navigator.onLine) return remainingResult(0, [])

  flushing = true
  try {
    const items = await getQueuedEvaluations()
    let sent = 0
    const failed: FlushResult['failed'] = []

    for (const item of items) {
      if (!navigator.onLine) break // se cayó la red de nuevo: el resto queda para el próximo intento
      try {
        // silent: un 401 durante la sync (token lento en terreno) NO debe cerrar la
        // sesión; se maneja como transitorio y la evaluación se conserva en la cola.
        await api.createEvaluation(item.orgId, item.payload, { silent: true })
        await removeQueuedEvaluation(item.id)
        sent++
      } catch (e) {
        const decision = classifyFlushError(e, navigator.onLine)
        if (decision !== 'permanent') {
          // Red caída o error transitorio (auth/servidor/rate limit): se CONSERVA
          // la evaluación en la cola y se corta el flush. Un 401/5xx suele afectar
          // a todos los items, así que no tiene sentido seguir; se reintenta en el
          // próximo disparo (evento online / montaje / botón manual).
          break
        }
        // Error definitivo de ESTE item (validación o duplicado): se descarta para
        // no bloquear la cola y se reporta al usuario; los demás items siguen.
        failed.push({ label: item.label, reason: e instanceof Error ? e.message : 'Error del servidor' })
        await removeQueuedEvaluation(item.id)
      }
    }

    return remainingResult(sent, failed)
  } finally {
    flushing = false
  }
}
