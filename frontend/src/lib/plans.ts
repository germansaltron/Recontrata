// Metadata de planes para la UI. Refleja el catálogo del backend
// (backend/app/billing/plans.py). Fuente de precios: PROPUESTA_MONETIZACION.md.

export type PlanKey = 'free' | 'pro' | 'empresa' | 'enterprise'

export interface PlanMeta {
  key: PlanKey
  name: string
  tagline: string
  monthlyCLP: number | null // null = a cotización
  annualCLP: number | null
  maxActiveWorkers: number | null // null = ilimitado
  maxActiveProjects: number | null
  features: string[]
  featured?: boolean
}

export const PLANS: PlanMeta[] = [
  {
    key: 'free',
    name: 'Gratis "Capataz"',
    tagline: 'Para probar la herramienta en un proyecto pequeño.',
    monthlyCLP: 0,
    annualCLP: 0,
    maxActiveWorkers: 15,
    maxActiveProjects: 1,
    features: [
      'Hasta 15 trabajadores activos',
      '1 proyecto activo',
      'Supervisores ilimitados',
      'Historial completo por trabajador',
      'Import / export Excel y CSV',
    ],
  },
  {
    key: 'pro',
    name: 'Pro "Faena"',
    tagline: 'Para contratistas con proyectos activos de forma permanente.',
    monthlyCLP: 49990,
    annualCLP: 499900,
    maxActiveWorkers: 100,
    maxActiveProjects: null,
    featured: true,
    features: [
      'Hasta 100 trabajadores activos',
      'Proyectos y supervisores ilimitados',
      'Búsqueda y filtros avanzados',
      'Alertas y exportación',
      '14 días de prueba gratis',
    ],
  },
  {
    key: 'empresa',
    name: 'Empresa "Contratista"',
    tagline: 'Para empresas con múltiples equipos y muchos trabajadores.',
    monthlyCLP: 149990,
    annualCLP: 1499900,
    maxActiveWorkers: 500,
    maxActiveProjects: null,
    features: [
      'Hasta 500 trabajadores activos',
      'Multi-proyecto y multi-usuario',
      'Acceso a la API e integraciones',
      'Insights con IA y onboarding asistido',
      'Soporte prioritario',
    ],
  },
]

export const PLAN_BY_KEY: Record<string, PlanMeta> = Object.fromEntries(PLANS.map((p) => [p.key, p]))

/** Formatea un monto CLP: 49990 -> "$49.990". */
export function formatCLP(amount: number): string {
  return '$' + amount.toLocaleString('es-CL')
}

/** Etiqueta legible del estado de la suscripción. */
export const STATUS_LABEL: Record<string, string> = {
  trialing: 'En prueba',
  active: 'Activo',
  past_due: 'Pago pendiente',
  canceled: 'Cancelado',
  incomplete: 'Incompleto',
}
