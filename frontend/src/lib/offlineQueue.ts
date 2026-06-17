import type { CreateEvaluationData } from './api'

// Cola offline de evaluaciones (apuesta #3, punto 2). Cuando no hay señal en
// terreno, las evaluaciones se guardan en IndexedDB en vez de perderse, y se
// envían cuando vuelve la conexión (el envío/sync es el punto 3).
//
// Se usa IndexedDB (no localStorage) porque persiste estructurado, soporta
// varios registros y no se borra con la caché del navegador.

const DB_NAME = 'recontrata-offline'
const DB_VERSION = 1
const STORE = 'pending-evaluations'

// Evento que se dispara al cambiar la cola, para que la UI actualice el contador.
export const QUEUE_CHANGED_EVENT = 'recontrata:queue-changed'

export interface QueuedEvaluation {
  id: string // uuid local
  orgId: string
  payload: CreateEvaluationData
  label: string // "Juan Pérez · Proyecto X" para mostrar en la UI
  createdAt: number
  attempts: number
}

function openDB(): Promise<IDBDatabase> {
  return new Promise((resolve, reject) => {
    const req = indexedDB.open(DB_NAME, DB_VERSION)
    req.onupgradeneeded = () => {
      const db = req.result
      if (!db.objectStoreNames.contains(STORE)) {
        db.createObjectStore(STORE, { keyPath: 'id' })
      }
    }
    req.onsuccess = () => resolve(req.result)
    req.onerror = () => reject(req.error)
  })
}

function tx<T>(mode: IDBTransactionMode, run: (store: IDBObjectStore) => IDBRequest<T>): Promise<T> {
  return openDB().then(
    (db) =>
      new Promise<T>((resolve, reject) => {
        const transaction = db.transaction(STORE, mode)
        const req = run(transaction.objectStore(STORE))
        req.onsuccess = () => resolve(req.result)
        req.onerror = () => reject(req.error)
        transaction.oncomplete = () => db.close()
      }),
  )
}

function emitChange() {
  window.dispatchEvent(new Event(QUEUE_CHANGED_EVENT))
}

function uuid(): string {
  if (typeof crypto !== 'undefined' && 'randomUUID' in crypto) return crypto.randomUUID()
  // Fallback simple si randomUUID no existe (navegadores muy viejos).
  return `${Date.now()}-${Math.floor(Math.random() * 1e9)}`
}

// Encola una evaluación creada sin conexión. Devuelve el id local.
export async function enqueueEvaluation(
  orgId: string,
  payload: CreateEvaluationData,
  label: string,
): Promise<string> {
  const record: QueuedEvaluation = {
    id: uuid(),
    orgId,
    payload,
    label,
    createdAt: Date.now(),
    attempts: 0,
  }
  await tx('readwrite', (store) => store.add(record))
  emitChange()
  return record.id
}

export async function getQueuedEvaluations(): Promise<QueuedEvaluation[]> {
  const all = await tx<QueuedEvaluation[]>('readonly', (store) => store.getAll())
  return all.sort((a, b) => a.createdAt - b.createdAt)
}

export async function removeQueuedEvaluation(id: string): Promise<void> {
  await tx('readwrite', (store) => store.delete(id))
  emitChange()
}

export async function countQueuedEvaluations(): Promise<number> {
  try {
    return await tx<number>('readonly', (store) => store.count())
  } catch {
    return 0
  }
}
