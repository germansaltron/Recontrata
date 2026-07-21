import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { api, ApiError, setAuthTokenGetter, setUnauthorizedHandler } from './api'

// Respuesta fetch mínima simulada.
function res(status: number, body: unknown = { detail: 'x' }) {
  return { ok: status < 400, status, json: async () => body } as unknown as Response
}

const onUnauthorized = vi.fn()
const fetchMock = vi.fn()

beforeEach(() => {
  vi.clearAllMocks()
  vi.stubGlobal('fetch', fetchMock)
  setUnauthorizedHandler(onUnauthorized)
  setAuthTokenGetter(() => Promise.resolve('tok')) // token OK por defecto
})

afterEach(() => {
  vi.unstubAllGlobals()
  setUnauthorizedHandler(null)
})

describe('apiFetch — handler global de 401 (M5) sin romper A1', () => {
  it('un 401 del servidor dispara el handler de sesión expirada', async () => {
    fetchMock.mockResolvedValue(res(401))
    await expect(api.createEvaluation('org-1', {} as never)).rejects.toBeInstanceOf(ApiError)
    expect(onUnauthorized).toHaveBeenCalledTimes(1)
  })

  it('un 401 en una llamada silent (flush offline) NO cierra la sesión', async () => {
    fetchMock.mockResolvedValue(res(401))
    await expect(api.createEvaluation('org-1', {} as never, { silent: true })).rejects.toBeInstanceOf(ApiError)
    expect(onUnauthorized).not.toHaveBeenCalled()
  })

  it('el 401 por token ausente (fix A1) NO cierra la sesión ni llama al backend', async () => {
    setAuthTokenGetter(() => Promise.resolve(null)) // Clerk no entrega token
    await expect(api.createEvaluation('org-1', {} as never)).rejects.toMatchObject({ status: 401 })
    expect(onUnauthorized).not.toHaveBeenCalled()
    expect(fetchMock).not.toHaveBeenCalled()
  })

  it('un 200 no dispara el handler', async () => {
    fetchMock.mockResolvedValue(res(201, { id: 'srv' }))
    await api.createEvaluation('org-1', {} as never)
    expect(onUnauthorized).not.toHaveBeenCalled()
  })
})
