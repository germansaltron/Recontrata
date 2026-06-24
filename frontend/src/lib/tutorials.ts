// Catálogo de tutoriales en video de Recontrata.
//
// 👉 Para activarlos: sube cada clip a YouTube (puede ser "Sin listar") y pega aquí
//    su ID (lo que va después de `watch?v=` o de `youtu.be/`). Mientras `youtubeId`
//    esté vacío, el reproductor muestra "disponible muy pronto" y todo lo demás funciona.

export type TutorialStage = 'empezar' | 'terreno' | 'decidir' | 'avanzado'

export interface Tutorial {
  clip: number
  key: string
  title: string
  blurb: string
  duration: string
  stage: TutorialStage
  youtubeId: string
}

export const STAGES: { key: TutorialStage; label: string }[] = [
  { key: 'empezar', label: 'Para empezar' },
  { key: 'terreno', label: 'En terreno' },
  { key: 'decidir', label: 'Decidir y compartir' },
  { key: 'avanzado', label: 'Avanzado' },
]

export const TUTORIALS: Tutorial[] = [
  { clip: 1, key: 'clip1', title: 'Bienvenida y tu cuenta', stage: 'empezar', duration: '1:00',
    blurb: 'Qué resuelve Recontrata y cómo crear tu cuenta.', youtubeId: '' },
  { clip: 2, key: 'clip2', title: 'Trae tu gente', stage: 'empezar', duration: '0:58',
    blurb: 'Carga a tus trabajadores, uno a uno o importando tu Excel.', youtubeId: '' },
  { clip: 3, key: 'clip3', title: 'Crea tu faena', stage: 'empezar', duration: '0:49',
    blurb: 'Crea un proyecto y asígnale tu cuadrilla.', youtubeId: '' },
  { clip: 4, key: 'clip4', title: 'La fórmula del puntaje', stage: 'empezar', duration: '1:05',
    blurb: 'Cómo se pondera el puntaje: en minería, la seguridad pesa más.', youtubeId: '' },
  { clip: 5, key: 'clip5', title: 'Evalúa en terreno', stage: 'terreno', duration: '1:25',
    blurb: 'Evalúa a tu gente en 30 segundos, desde el celular.', youtubeId: '' },
  { clip: 6, key: 'clip6', title: '¿Sin señal? Igual evalúas', stage: 'terreno', duration: '1:02',
    blurb: 'Modo offline: evalúa sin internet y sincroniza al volver la señal.', youtubeId: '' },
  { clip: 7, key: 'clip7', title: 'Decide con datos', stage: 'decidir', duration: '0:58',
    blurb: 'Lee el panel, el historial de cada trabajador y el ranking.', youtubeId: '' },
  { clip: 8, key: 'clip8', title: 'Transparencia y confianza', stage: 'decidir', duration: '1:16',
    blurb: 'Portal del Trabajador: derecho a réplica y certificado.', youtubeId: '' },
  { clip: 9, key: 'clip9', title: 'Evaluaciones más justas', stage: 'avanzado', duration: '0:57',
    blurb: 'Calibración de evaluadores para detectar sesgos.', youtubeId: '' },
]

export function getTutorial(key: string): Tutorial | undefined {
  return TUTORIALS.find((t) => t.key === key)
}
