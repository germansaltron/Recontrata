import { MessageSquare } from 'lucide-react'

/**
 * Botón flotante de feedback para el beta cerrado.
 * Apunta a VITE_FEEDBACK_URL (un formulario de Google, un chat de WhatsApp, etc.).
 * Si la variable no está configurada, no se renderiza (no estorba en producción).
 */
export function FeedbackButton() {
  const url = (import.meta.env.VITE_FEEDBACK_URL as string | undefined) || ''
  if (!url) return null

  return (
    <a
      href={url}
      target="_blank"
      rel="noopener noreferrer"
      className="fixed bottom-4 right-4 z-50 inline-flex items-center gap-2 rounded-full bg-blue-600 px-4 py-2.5 text-sm font-medium text-white shadow-lg transition-colors hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-400 focus:ring-offset-2"
      title="Cuéntanos qué encontraste"
    >
      <MessageSquare className="h-4 w-4" aria-hidden="true" />
      Feedback
    </a>
  )
}
