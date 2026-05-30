// Minimal stale-while-revalidate cache (in-memory, per session).
// Lets pages render last-known data instantly while a fresh fetch runs in the
// background, and lets the shell prefetch data before the user navigates.

type Entry<T> = { data: T; ts: number }

const store = new Map<string, Entry<unknown>>()
const inflight = new Map<string, Promise<unknown>>()

/** Returns cached data if present (does not trigger a fetch). */
export function getCached<T>(key: string): T | undefined {
  return store.get(key)?.data as T | undefined
}

/** Fetches and caches, de-duplicating concurrent calls for the same key. */
export function swr<T>(key: string, fetcher: () => Promise<T>): Promise<T> {
  const existing = inflight.get(key)
  if (existing) return existing as Promise<T>
  const p = fetcher()
    .then((data) => {
      store.set(key, { data, ts: Date.now() })
      return data
    })
    .finally(() => { inflight.delete(key) })
  inflight.set(key, p)
  return p
}

/** Warms the cache in the background; no-op if already cached or in flight. */
export function prefetch<T>(key: string, fetcher: () => Promise<T>): void {
  if (store.has(key) || inflight.has(key)) return
  swr(key, fetcher).catch(() => { /* prefetch is best-effort */ })
}
