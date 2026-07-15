import { useCallback, useEffect, useState } from 'react'
import { api, type SubscriptionResponse } from '../lib/api'
import { getCached, invalidate, swr } from '../lib/swr'

const key = (orgId: string) => `subscription:${orgId}`

/** Suscripción + uso de la organización (SWR: pinta lo cacheado y revalida). */
export function useSubscription(orgId: string | null) {
  const [sub, setSub] = useState<SubscriptionResponse | null>(() =>
    orgId ? getCached<SubscriptionResponse>(key(orgId)) ?? null : null
  )
  const [loading, setLoading] = useState(!sub)
  const [error, setError] = useState<string | null>(null)

  const load = useCallback(async () => {
    if (!orgId) return
    setError(null)
    try {
      const data = await swr(key(orgId), () => api.getSubscription(orgId))
      setSub(data)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'No pudimos cargar tu plan')
    } finally {
      setLoading(false)
    }
  }, [orgId])

  const reload = useCallback(async () => {
    if (!orgId) return
    invalidate((k) => k === key(orgId))
    setLoading(true)
    await load()
  }, [orgId, load])

  useEffect(() => { load() }, [load])

  return { sub, loading, error, reload }
}
