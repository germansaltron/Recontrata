// Wrapper sobre sonner: un solo punto de entrada para notificaciones.
// Centraliza el estilo y facilita cambiar de librería en el futuro.
import { toast as sonner } from 'sonner'

export const toast = {
  success: (msg: string, description?: string) => sonner.success(msg, { description }),
  error: (msg: string, description?: string) => sonner.error(msg, { description }),
  info: (msg: string, description?: string) => sonner.message(msg, { description }),
  /** Extrae el mensaje de un error desconocido y lo muestra como toast de error. */
  fromError: (e: unknown, fallback = 'Algo salió mal') =>
    sonner.error(e instanceof Error ? e.message : fallback),
}
