import { useEffect, useState } from 'react'
import { countQueuedEvaluations, QUEUE_CHANGED_EVENT } from '../lib/offlineQueue'

// Cantidad de evaluaciones en la cola offline (apuesta #3, punto 2). Se actualiza
// cuando la cola cambia (evento) y al volver/irse la conexión.
export function usePendingSync(): number {
  const [count, setCount] = useState(0)

  useEffect(() => {
    let active = true
    const refresh = () => {
      countQueuedEvaluations().then((n) => {
        if (active) setCount(n)
      })
    }
    refresh()
    window.addEventListener(QUEUE_CHANGED_EVENT, refresh)
    window.addEventListener('online', refresh)
    window.addEventListener('offline', refresh)
    return () => {
      active = false
      window.removeEventListener(QUEUE_CHANGED_EVENT, refresh)
      window.removeEventListener('online', refresh)
      window.removeEventListener('offline', refresh)
    }
  }, [])

  return count
}
