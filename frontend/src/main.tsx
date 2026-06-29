import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { ClerkProvider } from '@clerk/clerk-react'
import { esES } from '@clerk/localizations'
import { Toaster } from 'sonner'
import * as Sentry from '@sentry/react'
import './index.css'
import App from './App'
import { setupPWA } from './lib/pwa'
import { FeedbackButton } from './components/FeedbackButton'

// Observabilidad: inicializa Sentry solo si hay DSN (no-op en su ausencia).
const sentryDsn = (import.meta.env.VITE_SENTRY_DSN as string | undefined) || ''
if (sentryDsn) {
  Sentry.init({
    dsn: sentryDsn,
    environment: (import.meta.env.VITE_SENTRY_ENVIRONMENT as string | undefined) || 'production',
    tracesSampleRate: 0.1,
    sendDefaultPii: false,
  })
}

const clerkPubKey = import.meta.env.VITE_CLERK_PUBLISHABLE_KEY || ''
const isMockAuth = import.meta.env.VITE_AUTH_MOCK_ENABLED === 'true'

// eslint-disable-next-line react-refresh/only-export-components -- main.tsx es el entry point; Root no se reutiliza (solo afecta HMR en dev)
function Root() {
  if (isMockAuth || !clerkPubKey) {
    return (
      <BrowserRouter>
        <App />
      </BrowserRouter>
    )
  }

  return (
    <ClerkProvider publishableKey={clerkPubKey} localization={esES}>
      <BrowserRouter>
        <App />
      </BrowserRouter>
    </ClerkProvider>
  )
}

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <Root />
    <Toaster position="top-center" richColors closeButton toastOptions={{ duration: 4000 }} />
    <FeedbackButton />
  </StrictMode>,
)

// Service worker para soporte offline en terreno (apuesta #3, punto 1).
setupPWA()
