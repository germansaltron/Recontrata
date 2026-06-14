const API_BASE = import.meta.env.VITE_API_URL || '/api/v1'

type TokenGetter = () => Promise<string | null>
let _getAuthToken: TokenGetter | null = null

export function setAuthTokenGetter(getter: TokenGetter) {
  _getAuthToken = getter
}

function formatApiError(body: unknown, status: number): string {
  if (!body || typeof body !== 'object') return `Error ${status}`
  const detail = (body as { detail?: unknown }).detail
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail)) {
    // FastAPI validation errors: [{loc, msg, type}, ...]
    const msgs = detail
      .map((d) => {
        if (typeof d === 'string') return d
        if (d && typeof d === 'object') {
          const m = (d as { msg?: string; loc?: unknown[] })
          const field = Array.isArray(m.loc) ? m.loc.slice(1).join('.') : ''
          return field ? `${field}: ${m.msg}` : m.msg
        }
        return null
      })
      .filter(Boolean)
    if (msgs.length) return msgs.join('; ')
  }
  if (detail && typeof detail === 'object') {
    const msg = (detail as { detail?: string }).detail
    if (typeof msg === 'string') return msg
  }
  return `Error ${status}`
}

async function apiFetch<T>(path: string, options: RequestInit = {}): Promise<T> {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string> || {}),
  }

  if (_getAuthToken) {
    const token = await Promise.race([
      _getAuthToken(),
      new Promise<null>((resolve) => setTimeout(() => resolve(null), 5000)),
    ])
    if (token) {
      headers['Authorization'] = `Bearer ${token}`
    }
  }

  const res = await fetch(`${API_BASE}${path}`, { ...options, headers })

  if (!res.ok) {
    const body = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(formatApiError(body, res.status))
  }

  if (res.status === 204) return undefined as T
  return res.json()
}

// --- Types ---

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  size: number
  pages: number
}

export interface Organization {
  id: string
  name: string
  slug: string
  industry: string
  created_at: string
}

export interface DimensionWeight {
  key: string
  label: string
  weight: number
}

export interface ScoringProfile {
  industry: string
  label: string
  description: string
  weights: DimensionWeight[]
}

export interface ScoringFormula {
  active_industry: string
  active_profile: ScoringProfile
  profiles: ScoringProfile[]
}

// --- Portal del Trabajador (acceso público por token) ---
export interface PortalEvaluation {
  id: string
  project_name: string
  score_quality: number
  score_safety: number
  score_punctuality: number
  score_teamwork: number
  score_technical: number
  score_average: number
  score_weighted: number
  would_rehire: string
  rehire_reason: string | null
  comment: string | null
  worker_reply: string | null
  worker_reply_at: string | null
  created_at: string
}

export interface PortalProfile {
  worker_name: string
  rut: string
  specialty: string
  org_name: string
  evaluation_count: number
  avg_score: number | null
  consent_status: string
  rehire_yes: number
  rehire_reservations: number
  rehire_no: number
  formula: ScoringProfile
  score_trend: { project_name: string; date: string | null; score_weighted: number }[]
  evaluations: PortalEvaluation[]
}

export interface PortalLink {
  token: string
  path: string
}

export interface UserProfile {
  id: string
  email: string
  full_name: string | null
  organizations: { org_id: string; org_name: string; role: string }[]
}

export interface Project {
  id: string
  name: string
  client_name: string | null
  location: string | null
  start_date: string | null
  end_date: string | null
  status: string
  worker_count: number
  evaluation_count: number
  created_at: string
}

export interface Worker {
  id: string
  rut: string
  first_name: string
  last_name: string
  specialty: string
  phone: string | null
  email: string | null
  is_active: boolean
  evaluation_count: number
  avg_score: number | null
  created_at: string
}

export interface WorkerDetail extends Worker {
  certifications: string | null
  notes: string | null
  portal_token: string | null
  avg_scores: { quality: number; safety: number; punctuality: number; teamwork: number; technical: number; overall: number } | null
  score_trend: { project_name: string; date: string | null; score_average: number }[]
  rehire_stats: { yes: number; reservations: number; no: number }
  evaluations: EvaluationSummary[]
  consent: WorkerConsent | null
}

export type ConsentStatus = 'pending' | 'informed' | 'granted' | 'revoked'
export type ConsentMethod = 'verbal' | 'written' | 'email' | 'contract' | 'platform'

export interface WorkerConsent {
  worker_id: string
  status: ConsentStatus
  method: ConsentMethod | null
  consent_date: string | null
  notes: string | null
  recorded_by_name: string | null
  updated_at: string | null
}

export interface EvaluationSummary {
  id: string
  project_name: string
  score_quality: number
  score_safety: number
  score_punctuality: number
  score_teamwork: number
  score_technical: number
  score_average: number
  score_weighted: number
  would_rehire: string
  rehire_reason: string | null
  comment: string | null
  evaluator_name: string | null
  worker_reply: string | null
  worker_reply_at: string | null
  created_at: string
}

export interface Evaluation {
  id: string
  project_id: string
  project_name: string
  worker_id: string
  worker_name: string
  evaluator_name: string | null
  score_quality: number
  score_safety: number
  score_punctuality: number
  score_teamwork: number
  score_technical: number
  score_average: number
  score_weighted: number
  would_rehire: string
  rehire_reason: string | null
  comment: string | null
  created_at: string
}

export interface DashboardStats {
  project_count: number
  active_project_count: number
  worker_count: number
  evaluation_count: number
  avg_score_overall: number | null
  rehire_rate: number | null
  specialty_distribution: { specialty: string; count: number }[]
}

export interface TopWorker {
  id: string
  full_name: string
  specialty: string
  avg_score: number
  evaluation_count: number
  would_rehire_pct: number
}

export interface RecentEvaluation {
  id: string
  worker_id: string
  worker_name: string
  project_name: string
  score_average: number
  score_weighted: number
  would_rehire: string
  created_at: string
}

export interface ProjectWorkerItem {
  id: string
  rut: string
  first_name: string
  last_name: string
  specialty: string
  role_in_project: string | null
  assigned_at: string | null
  evaluated: boolean
  score_in_project: number | null
}

// --- API Functions ---

export const api = {
  // Auth
  getProfile: () => apiFetch<UserProfile>('/me'),
  createOrg: (name: string) => apiFetch<Organization>('/organizations', { method: 'POST', body: JSON.stringify({ name }) }),

  // Organization
  getOrg: (orgId: string) => apiFetch<Organization>(`/organizations/${orgId}`),
  updateOrg: (orgId: string, data: { name?: string; industry?: string }) =>
    apiFetch<Organization>(`/organizations/${orgId}`, { method: 'PATCH', body: JSON.stringify(data) }),

  // Scoring (fórmula pública del puntaje)
  getScoringFormula: (orgId: string) => apiFetch<ScoringFormula>(`/organizations/${orgId}/scoring/formula`),

  // Projects
  listProjects: (orgId: string, params?: { page?: number; size?: number; status?: string; search?: string }) => {
    const q = new URLSearchParams()
    if (params?.page) q.set('page', String(params.page))
    if (params?.size) q.set('size', String(params.size))
    if (params?.status) q.set('status', params.status)
    if (params?.search) q.set('search', params.search)
    return apiFetch<PaginatedResponse<Project>>(`/organizations/${orgId}/projects?${q}`)
  },
  createProject: (orgId: string, data: { name: string; client_name?: string; location?: string; start_date?: string; end_date?: string }) =>
    apiFetch<Project>(`/organizations/${orgId}/projects`, { method: 'POST', body: JSON.stringify(data) }),
  getProject: (orgId: string, projectId: string) => apiFetch<Project>(`/organizations/${orgId}/projects/${projectId}`),
  updateProject: (orgId: string, projectId: string, data: Record<string, unknown>) =>
    apiFetch<Project>(`/organizations/${orgId}/projects/${projectId}`, { method: 'PATCH', body: JSON.stringify(data) }),
  assignWorkers: (orgId: string, projectId: string, workerIds: string[]) =>
    apiFetch<{ added: number }>(`/organizations/${orgId}/projects/${projectId}/workers`, { method: 'POST', body: JSON.stringify({ worker_ids: workerIds }) }),
  listProjectWorkers: (orgId: string, projectId: string) =>
    apiFetch<ProjectWorkerItem[]>(`/organizations/${orgId}/projects/${projectId}/workers`),
  unassignWorker: (orgId: string, projectId: string, workerId: string) =>
    apiFetch<void>(`/organizations/${orgId}/projects/${projectId}/workers/${workerId}`, { method: 'DELETE' }),

  // Workers
  listWorkers: (orgId: string, params?: { page?: number; size?: number; search?: string; specialty?: string; min_score?: number; is_active?: boolean; sort_by?: string; sort_order?: string }) => {
    const q = new URLSearchParams()
    if (params?.page) q.set('page', String(params.page))
    if (params?.size) q.set('size', String(params.size))
    if (params?.search) q.set('search', params.search)
    if (params?.specialty) q.set('specialty', params.specialty)
    if (params?.min_score) q.set('min_score', String(params.min_score))
    if (params?.is_active !== undefined) q.set('is_active', String(params.is_active))
    if (params?.sort_by) q.set('sort_by', params.sort_by)
    if (params?.sort_order) q.set('sort_order', params.sort_order)
    return apiFetch<PaginatedResponse<Worker>>(`/organizations/${orgId}/workers?${q}`)
  },
  createWorker: (orgId: string, data: { rut: string; first_name: string; last_name: string; specialty: string; phone?: string; email?: string }) =>
    apiFetch<Worker>(`/organizations/${orgId}/workers`, { method: 'POST', body: JSON.stringify(data) }),
  getWorker: (orgId: string, workerId: string) => apiFetch<WorkerDetail>(`/organizations/${orgId}/workers/${workerId}`),
  updateWorker: (orgId: string, workerId: string, data: Record<string, unknown>) =>
    apiFetch<Worker>(`/organizations/${orgId}/workers/${workerId}`, { method: 'PATCH', body: JSON.stringify(data) }),
  getWorkerConsent: (orgId: string, workerId: string) =>
    apiFetch<WorkerConsent>(`/organizations/${orgId}/workers/${workerId}/consent`),
  createPortalLink: (orgId: string, workerId: string, regenerate = false) =>
    apiFetch<PortalLink>(`/organizations/${orgId}/workers/${workerId}/portal-link${regenerate ? '?regenerate=true' : ''}`, { method: 'POST' }),

  // Portal del Trabajador (público, por token — sin auth)
  getPortal: (token: string) => apiFetch<PortalProfile>(`/portal/${token}`),
  portalReply: (token: string, evalId: string, reply: string) =>
    apiFetch<PortalEvaluation>(`/portal/${token}/evaluations/${evalId}/reply`, { method: 'POST', body: JSON.stringify({ reply }) }),
  portalOptOut: (token: string, notes?: string) =>
    apiFetch<void>(`/portal/${token}/opt-out`, { method: 'POST', body: JSON.stringify({ notes: notes ?? null }) }),
  setWorkerConsent: (orgId: string, workerId: string, data: { status: ConsentStatus; method?: ConsentMethod | null; consent_date?: string | null; notes?: string | null }) =>
    apiFetch<WorkerConsent>(`/organizations/${orgId}/workers/${workerId}/consent`, { method: 'PUT', body: JSON.stringify(data) }),
  importWorkers: async (orgId: string, file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    const headers: Record<string, string> = {}
    if (_getAuthToken) {
      const token = await _getAuthToken()
      if (token) headers['Authorization'] = `Bearer ${token}`
    }
    const res = await fetch(`${API_BASE}/organizations/${orgId}/workers/import`, { method: 'POST', body: formData, headers })
    if (!res.ok) throw new Error((await res.json()).detail || 'Error importing')
    return res.json() as Promise<{ created: number; updated: number; errors: string[] }>
  },

  // Evaluations
  createEvaluation: (orgId: string, data: { project_id: string; worker_id: string; score_quality: number; score_safety: number; score_punctuality: number; score_teamwork: number; score_technical: number; would_rehire: string; rehire_reason?: string; comment?: string }) =>
    apiFetch<Evaluation>(`/organizations/${orgId}/evaluations`, { method: 'POST', body: JSON.stringify(data) }),
  listEvaluations: (orgId: string, params?: { page?: number; project_id?: string; worker_id?: string }) => {
    const q = new URLSearchParams()
    if (params?.page) q.set('page', String(params.page))
    if (params?.project_id) q.set('project_id', params.project_id)
    if (params?.worker_id) q.set('worker_id', params.worker_id)
    return apiFetch<PaginatedResponse<Evaluation>>(`/organizations/${orgId}/evaluations?${q}`)
  },

  // Dashboard
  getStats: (orgId: string) => apiFetch<DashboardStats>(`/organizations/${orgId}/dashboard/stats`),
  getTopWorkers: (orgId: string) => apiFetch<TopWorker[]>(`/organizations/${orgId}/dashboard/top-workers`),
  getRecentEvaluations: (orgId: string) => apiFetch<RecentEvaluation[]>(`/organizations/${orgId}/dashboard/recent-evaluations`),
  getNextEvaluation: (orgId: string) => apiFetch<NextEvaluation>(`/organizations/${orgId}/dashboard/next-evaluation`),
  getProjectsPending: (orgId: string) => apiFetch<ProjectPending[]>(`/organizations/${orgId}/dashboard/projects-pending`),

  // Workers export (returns Blob, with auth header)
  exportWorkersCsv: async (orgId: string): Promise<Blob> => {
    const headers: Record<string, string> = {}
    if (_getAuthToken) {
      const token = await _getAuthToken()
      if (token) headers['Authorization'] = `Bearer ${token}`
    }
    const res = await fetch(`${API_BASE}/organizations/${orgId}/workers/export.csv`, { headers })
    if (!res.ok) throw new Error('Error al exportar')
    return res.blob()
  },
}

export interface NextEvaluation {
  project_id: string | null
  project_name: string | null
  worker_id: string | null
  worker_name: string | null
  pending_count: number
}

export interface ProjectPending {
  id: string
  name: string
  client_name: string | null
  worker_count: number
  pending_count: number
  first_pending_worker_id: string | null
}
