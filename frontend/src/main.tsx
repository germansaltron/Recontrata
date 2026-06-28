import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { ClerkProvider } from '@clerk/clerk-react'
import { esES } from '@clerk/localizations'
import { Toaster } from 'sonner'
import './index.css'
import App from './App'
import { setupPWA } from './lib/pwa'

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
  </StrictMode>,
)

// Service worker para soporte offline en terreno (apuesta #3, punto 1).
setupPWA()
