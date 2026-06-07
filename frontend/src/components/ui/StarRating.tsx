import { Star } from 'lucide-react'

interface StarRatingProps {
  value: number
  onChange?: (value: number) => void
  size?: 'sm' | 'md' | 'lg'
  readonly?: boolean
}

const sizes = { sm: 'w-5 h-5', md: 'w-7 h-7', lg: 'w-9 h-9' }
const tapSizes = { sm: 'p-1', md: 'p-1.5', lg: 'p-2' }
// Targets tactiles minimos para uso en terreno con guantes (lg ~68px, recomendado UX/WCAG).
const interactiveTap = {
  sm: 'min-w-[36px] min-h-[36px]',
  md: 'min-w-[48px] min-h-[48px]',
  lg: 'min-w-[68px] min-h-[68px]',
}

function getColor(value: number) {
  if (value <= 2) return 'text-red-500'
  if (value <= 3) return 'text-yellow-500'
  return 'text-green-500'
}

export default function StarRating({ value, onChange, size = 'md', readonly = false }: StarRatingProps) {
  return (
    <div
      className="flex items-center gap-0.5"
      role={readonly ? 'img' : 'radiogroup'}
      aria-label={readonly ? `Puntaje ${value} de 5` : 'Selecciona un puntaje del 1 al 5'}
    >
      {[1, 2, 3, 4, 5].map((star) => {
        const label = star === 1 ? '1 estrella' : `${star} estrellas`
        return (
          <button
            key={star}
            type="button"
            role={readonly ? undefined : 'radio'}
            aria-checked={readonly ? undefined : star === value}
            aria-label={label}
            title={label}
            disabled={readonly}
            onClick={() => onChange?.(star)}
            className={`${tapSizes[size]} ${readonly ? 'cursor-default' : `cursor-pointer hover:scale-110 flex items-center justify-center ${interactiveTap[size]}`} transition-transform touch-manipulation`}
          >
            <Star
              className={`${sizes[size]} ${star <= value ? getColor(value) : 'text-gray-300'}`}
              fill={star <= value ? 'currentColor' : 'none'}
            />
          </button>
        )
      })}
    </div>
  )
}
