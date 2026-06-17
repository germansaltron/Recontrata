import { api } from './api'
import { getQueuedEvaluations, removeQueuedEvaluation, countQueuedEvaluations } from './offlineQueue'

// Envío de la cola offline (apuesta #3, punto 3). Reenvía a la API las
// evaluaciones que se guardaron sin señal (punto 2) y las saca de la cola.

export interface FlushResult {
  sent: number
  failed: { label: string; reason: string }[]
  remaining: number
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
        await api.createEvaluation(item.orgId, item.payload)
        await removeQueuedEvaluation(item.id)
        sent++
      } catch (e) {
        // Error de red (fetch lanza TypeError) → dejar en cola y reintentar luego.
        if (e instanceof TypeError || !navigator.onLine) break
        // Error del servidor (4xx, p. ej. validación o duplicado): no va a pasar nunca,
        // se saca de la cola para no bloquearla y se reporta al usuario.
        failed.push({ label: item.label, reason: e instanceof Error ? e.message : 'Error del servidor' })
        await removeQueuedEvaluation(item.id)
      }
    }

    return remainingResult(sent, failed)
  } finally {
    flushing = false
  }
}
