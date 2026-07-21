import { lazy, Suspense, useEffect } from 'react'
import { Routes, Route, Navigate, Outlet } from 'react-router-dom'
import { toast } from './lib/toast'
import { SignedIn, SignedOut, SignIn, SignUp, useAuth } from '@clerk/clerk-react'
import { OrgProvider } from './lib/org'
import AppShell from './components/layout/AppShell'
import PaywallProvider from './components/billing/PaywallProvider'
import Landing from './pages/Landing'
import BootIntro from './components/brand/LogoIntro'
import AccessGate from './components/AccessGate'
import { setAuthTokenGetter, setUnauthorizedHandler } from './lib/api'

const Dashboard = lazy(() => import('./pages/Dashboard'))
const Projects = lazy(() => import('./pages/Projects'))
const ProjectDetail = lazy(() => import('./pages/ProjectDetail'))
const Workers = lazy(() => import('./pages/Workers'))
const WorkerDetail = lazy(() => import('./pages/WorkerDetail'))
const Evaluate = lazy(() => import('./pages/Evaluate'))
const EvaluateWorker = lazy(() => import('./pages/EvaluateWorker'))
const ScoreFormula = lazy(() => import('./pages/ScoreFormula'))
const Calibration = lazy(() => import('./pages/Calibration'))
const Terms = lazy(() => import('./pages/Terms'))
const Privacy = lazy(() => import('./pages/Privacy'))
const WorkerPortal = lazy(() => import('./pages/WorkerPortal'))
const WorkerCertificate = lazy(() => import('./pages/WorkerCertificate'))
const Ayuda = lazy(() => import('./pages/Ayuda'))
const Billing = lazy(() => import('./pages/Billing'))

const clerkEnabled = Boolean(import.meta.env.VITE_CLERK_PUBLISHABLE_KEY) &&
  import.meta.env.VITE_AUTH_MOCK_ENABLED !== 'true'

const PageFallback = () => <div className="animate-pulse text-gray-400 p-6">Cargando...</div>

function ProtectedApp() {
  return (
    <OrgProvider>
      <PaywallProvider>
        <Routes>
          <Route element={<AppShell />}>
            <Route index element={<Suspense fallback={<PageFallback />}><Dashboard /></Suspense>} />
            <Route path="projects" element={<Suspense fallback={<PageFallback />}><Projects /></Suspense>} />
            <Route path="projects/:id" element={<Suspense fallback={<PageFallback />}><ProjectDetail /></Suspense>} />
            <Route path="workers" element={<Suspense fallback={<PageFallback />}><Workers /></Suspense>} />
            <Route path="workers/:id" element={<Suspense fallback={<PageFallback />}><WorkerDetail /></Suspense>} />
            <Route path="evaluate" element={<Suspense fallback={<PageFallback />}><Evaluate /></Suspense>} />
            <Route path="evaluate/:projectId/:workerId" element={<Suspense fallback={<PageFallback />}><EvaluateWorker /></Suspense>} />
            <Route path="formula" element={<Suspense fallback={<PageFallback />}><ScoreFormula /></Suspense>} />
            <Route path="calibracion" element={<Suspense fallback={<PageFallback />}><Calibration /></Suspense>} />
            <Route path="suscripcion" element={<Suspense fallback={<PageFallback />}><Billing /></Suspense>} />
            <Route path="ayuda" element={<Suspense fallback={<PageFallback />}><Ayuda /></Suspense>} />
          </Route>
        </Routes>
      </PaywallProvider>
    </OrgProvider>
  )
}

function AuthenticatedApp() {
  const { getToken, signOut } = useAuth()
  setAuthTokenGetter(() => getToken())

  // Sesión expirada (401 del servidor): avisa una vez y cierra sesión → login.
  // El guard evita disparar signOut en bucle si hay varias requests con 401 a la vez.
  useEffect(() => {
    let firedAt = 0
    setUnauthorizedHandler(() => {
      const now = Date.now()
      if (now - firedAt < 10_000) return
      firedAt = now
      toast.info('Tu sesión expiró', 'Vuelve a iniciar sesión para continuar.')
      void signOut()
    })
    return () => setUnauthorizedHandler(null)
  }, [signOut])

  return <ProtectedApp />
}

// Layout de la vitrina pública (landing + legales): intro de marca, SIN gate.
//
// El gate de pre-lanzamiento protege la aplicación —los datos, las evaluaciones,
// el registro—, no el escaparate. Un visitante debe poder ver de qué se trata el
// producto sin un código, y hay dos razones concretas:
//   * el bot de WhatsApp deriva prospectos aquí (docs/BOT_WHATSAPP.md);
//   * la revisión de Meta valida que el negocio existe visitando el sitio, y un
//     muro de contraseña es causa probable de rechazo.
// El `noindex` de index.html sigue evitando que aparezca en buscadores.
function PublicLayout() {
  return (
    <>
      <BootIntro />
      <Outlet />
    </>
  )
}

// Layout que aplica el gate de pre-lanzamiento + intro de marca a la app y al
// registro (el Portal del Trabajador y la vitrina pública quedan fuera).
//
// Hardening móvil: un usuario YA autenticado (invitado que pasó el registro) no
// debe toparse con el gate del código, sin importar el navegador/contexto. Esto
// evita el re-prompt del código cuando la sesión de Clerk existe pero el flag
// local del gate no (p. ej. al volver a la app instalada tras verificar por OTP).
function GateLayout() {
  if (!clerkEnabled) {
    return (
      <AccessGate>
        <BootIntro />
        <Outlet />
      </AccessGate>
    )
  }
  return (
    <>
      <SignedIn>
        <BootIntro />
        <Outlet />
      </SignedIn>
      <SignedOut>
        <AccessGate>
          <BootIntro />
          <Outlet />
        </AccessGate>
      </SignedOut>
    </>
  )
}

export default function App() {
  return (
    <Routes>
      {/* Portal del Trabajador: público por token, FUERA del AccessGate */}
      <Route path="/p/:token" element={<Suspense fallback={<PageFallback />}><WorkerPortal /></Suspense>} />
      <Route path="/p/:token/certificado" element={<Suspense fallback={<PageFallback />}><WorkerCertificate /></Suspense>} />

      {/* Vitrina pública: landing y legales, FUERA del AccessGate. */}
      <Route element={<PublicLayout />}>
        <Route
          path="/"
          element={
            !clerkEnabled ? (
              <Landing isSignedIn={true} />
            ) : (
              <>
                <SignedIn>
                  <Landing isSignedIn={true} />
                </SignedIn>
                <SignedOut>
                  <Landing isSignedIn={false} />
                </SignedOut>
              </>
            )
          }
        />
        <Route path="/terminos" element={<Suspense fallback={<PageFallback />}><Terms /></Suspense>} />
        <Route path="/privacidad" element={<Suspense fallback={<PageFallback />}><Privacy /></Suspense>} />
      </Route>

      <Route element={<GateLayout />}>
        {!clerkEnabled ? (
          <>
            <Route path="/app/*" element={<ProtectedApp />} />
          </>
        ) : (
          <>
            <Route
              path="/sign-in/*"
              element={
                <div className="min-h-screen flex items-center justify-center bg-slate-50 p-4">
                  <SignIn routing="path" path="/sign-in" signUpUrl="/sign-up" afterSignInUrl="/app" afterSignUpUrl="/app" />
                </div>
              }
            />
            <Route
              path="/sign-up/*"
              element={
                <div className="min-h-screen flex items-center justify-center bg-slate-50 p-4">
                  <SignUp routing="path" path="/sign-up" signInUrl="/sign-in" afterSignUpUrl="/app" afterSignInUrl="/app" />
                </div>
              }
            />
            <Route
              path="/app/*"
              element={
                <>
                  <SignedIn>
                    <AuthenticatedApp />
                  </SignedIn>
                  <SignedOut>
                    <Navigate to="/sign-in" replace />
                  </SignedOut>
                </>
              }
            />
          </>
        )}
      </Route>

      {/* Ruta desconocida → landing público (no al gate: rebotar a un muro de
          contraseña es hostil para un visitante que llegó por un enlace viejo). */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
