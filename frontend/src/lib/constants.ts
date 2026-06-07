export const SPECIALTIES = [
  'Soldador',
  'Mecánico',
  'Eléctrico',
  'Instrumentista',
  'Cañerista',
  'Calderero',
  'Tornero',
  'Fresador',
  'Operador Grúa',
  'Rigger',
  'Pintor Industrial',
  'Andamiero',
  'Ayudante',
  'Supervisor',
  'Prevencionista',
  'Otro',
]

export const PROJECT_STATUSES = [
  { value: 'planning', label: 'Planificación' },
  { value: 'active', label: 'Activo' },
  { value: 'completed', label: 'Completado' },
  { value: 'cancelled', label: 'Cancelado' },
]

export const SCORE_LABELS = ['Calidad del Trabajo', 'Seguridad', 'Puntualidad', 'Trabajo en Equipo', 'Habilidad Técnica']

// Anclas de comportamiento (BARS): describen qué significa cada nivel por dimensión.
// Hacen la evaluación más objetiva y defendible (clave para el riesgo legal del score).
// Orden alineado con SCORE_LABELS y con score_quality/safety/punctuality/teamwork/technical.
export interface ScoreDimension {
  label: string
  hint: string
  anchors: Record<1 | 2 | 3 | 4 | 5, string>
}

export const SCORE_DIMENSIONS: ScoreDimension[] = [
  {
    label: 'Calidad del Trabajo',
    hint: 'Terminaciones, retrabajos y cumplimiento del estándar.',
    anchors: {
      1: 'Trabajo rechazado o con retrabajo constante.',
      2: 'Errores frecuentes que requieren corrección.',
      3: 'Cumple el estándar con supervisión normal.',
      4: 'Trabajo prolijo, casi sin observaciones.',
      5: 'Calidad ejemplar, referente para el equipo.',
    },
  },
  {
    label: 'Seguridad',
    hint: 'Uso de EPP, procedimientos y reporte de riesgos.',
    anchors: {
      1: 'Incurre en actos inseguros graves.',
      2: 'Olvida EPP o procedimientos con frecuencia.',
      3: 'Cumple las normas de seguridad básicas.',
      4: 'Proactivo: identifica y reporta riesgos.',
      5: 'Referente de seguridad, corrige a otros.',
    },
  },
  {
    label: 'Puntualidad',
    hint: 'Asistencia, horarios y cumplimiento de plazos.',
    anchors: {
      1: 'Ausencias o atrasos reiterados sin aviso.',
      2: 'Atrasos ocasionales que afectan la cuadrilla.',
      3: 'Cumple horarios y asistencia.',
      4: 'Siempre a tiempo y disponible.',
      5: 'Llega antes y deja todo listo para el turno.',
    },
  },
  {
    label: 'Trabajo en Equipo',
    hint: 'Colaboración, comunicación y actitud con el grupo.',
    anchors: {
      1: 'Genera conflictos o trabaja aislado.',
      2: 'Colabora solo si se lo piden.',
      3: 'Se integra y coopera con el equipo.',
      4: 'Apoya a sus compañeros por iniciativa.',
      5: 'Lidera y mejora el clima de la cuadrilla.',
    },
  },
  {
    label: 'Habilidad Técnica',
    hint: 'Dominio del oficio, autonomía y resolución.',
    anchors: {
      1: 'No domina las tareas de su especialidad.',
      2: 'Requiere apoyo constante para su oficio.',
      3: 'Maneja su especialidad con autonomía.',
      4: 'Resuelve problemas complejos solo.',
      5: 'Experto: enseña y define el método.',
    },
  },
]

export const REHIRE_OPTIONS = [
  { value: 'yes', label: 'Sí', color: 'bg-green-100 text-green-800' },
  { value: 'reservations', label: 'Con Reservas', color: 'bg-yellow-100 text-yellow-800' },
  { value: 'no', label: 'No', color: 'bg-red-100 text-red-800' },
]
