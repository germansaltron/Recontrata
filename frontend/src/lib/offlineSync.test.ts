import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

// Mock de la API: reemplazamos api.createEvaluation por un spy y exponemos una
// clase ApiError equivalente a la real (misma forma: name + status). Como
// offlineSync importa ApiError de este mismo mock, `e instanceof ApiError`
// funciona de forma consistente entre el test y el código bajo prueba, sin
// cargar el api.ts real (que depende de import.meta.env de Vite).
vi.mock('./api', () => {
  class ApiError extends Error {
    status: number
    detail: unknown
    constructor(message: string, status: number, detail: unknown = null) {
      super(message)
      this.name = 'ApiError'
      this.status = status
      this.detail = detail
    }
  }
  return { api: { createEvaluation: vi.fn() }, ApiError }
})

// Mock de la cola: en memoria, sin IndexedDB.
vi.mock('./offlineQueue', () => ({
  getQueuedEvaluations: vi.fn(),
  removeQueuedEvaluation: vi.fn(async () => {}),
  countQueuedEvaluations: vi.fn(async () => 0),
}))

import { api, ApiError } from './api'
import { getQueuedEvaluations, removeQueuedEvaluation, countQueuedEvaluations } from './offlineQueue'
import { classifyFlushError, flushQueue } from './offlineSync'

const createEvaluation = vi.mocked(api.createEvaluation)
const mockGetQueued = vi.mocked(getQueuedEvaluations)
const mockRemove = vi.mocked(removeQueuedEvaluation)
const mockCount = vi.mocked(countQueuedEvaluations)

function queued(id: string) {
  return { id, orgId: 'org-1', payload: {} as never, label: `eval ${id}`, createdAt: Number(id), attempts: 0 }
}

function setOnline(online: boolean) {
  vi.stubGlobal('navigator', { onLine: online })
}

beforeEach(() => {
  vi.clearAllMocks()
  setOnline(true)
  mockCount.mockResolvedValue(0)
})

afterEach(() => {
  vi.unstubAllGlobals()
})

describe('classifyFlushError', () => {
  it('trata la red caída como network (fetch lanza TypeError)', () => {
    expect(classifyFlushError(new TypeError('Failed to fetch'), true)).toBe('network')
  })

  it('trata el navegador offline como network sin importar el error', () => {
    expect(classifyFlushError(new ApiError('x', 500, null), false)).toBe('network')
  })

  it.each([400, 409, 422])('descarta el item ante %i (validación/duplicado)', (status) => {
    expect(classifyFlushError(new ApiError('x', status, null), true)).toBe('permanent')
  })

  it.each([401, 402, 408, 429, 500, 503])('conserva el item ante %i (transitorio)', (status) => {
    expect(classifyFlushError(new ApiError('x', status, null), true)).toBe('retriable')
  })

  it('ante un error desconocido conserva el item (nunca borra por defecto)', () => {
    expect(classifyFlushError(new Error('raro'), true)).toBe('retriable')
  })
})

describe('flushQueue — el fix de A1 (no perder evaluaciones)', () => {
  it('envía todas las evaluaciones cuando el servidor responde bien', async () => {
    mockGetQueued.mockResolvedValue([queued('1'), queued('2')])
    createEvaluation.mockResolvedValue({ id: 'srv' } as never)

    const res = await flushQueue()

    expect(res.sent).toBe(2)
    expect(res.failed).toHaveLength(0)
    expect(mockRemove).toHaveBeenCalledTimes(2)
  })

  it('NO borra la evaluación ante un 401 (token lento): la conserva para reintentar', async () => {
    mockGetQueued.mockResolvedValue([queued('1'), queued('2')])
    createEvaluation.mockRejectedValue(new ApiError('sin token', 401, null))
    mockCount.mockResolvedValue(2)

    const res = await flushQueue()

    expect(res.sent).toBe(0)
    expect(res.failed).toHaveLength(0) // no se reporta como fallo definitivo
    expect(mockRemove).not.toHaveBeenCalled() // <-- lo importante: NO se borró nada
    expect(res.remaining).toBe(2)
  })

  it('NO borra la evaluación ante un 500 transitorio del servidor', async () => {
    mockGetQueued.mockResolvedValue([queued('1')])
    createEvaluation.mockRejectedValue(new ApiError('server error', 500, null))
    mockCount.mockResolvedValue(1)

    const res = await flushQueue()

    expect(res.sent).toBe(0)
    expect(mockRemove).not.toHaveBeenCalled()
  })

  it('NO borra ante red caída (TypeError)', async () => {
    mockGetQueued.mockResolvedValue([queued('1')])
    createEvaluation.mockRejectedValue(new TypeError('Failed to fetch'))

    await flushQueue()

    expect(mockRemove).not.toHaveBeenCalled()
  })

  it('descarta SOLO el item duplicado (409) y sigue enviando los demás', async () => {
    mockGetQueued.mockResolvedValue([queued('1'), queued('2')])
    createEvaluation
      .mockRejectedValueOnce(new ApiError('ya existe', 409, null)) // item 1: duplicado
      .mockResolvedValueOnce({ id: 'srv' } as never) // item 2: entra bien

    const res = await flushQueue()

    expect(res.sent).toBe(1)
    expect(res.failed).toHaveLength(1)
    expect(res.failed[0].label).toBe('eval 1')
    expect(mockRemove).toHaveBeenCalledTimes(2) // el duplicado (descartado) + el enviado
  })
})
