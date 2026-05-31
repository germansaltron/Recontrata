import { lazy, Suspense } from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { SignedIn, SignedOut, SignIn, SignUp, useAuth } from '@clerk/clerk-react'
import { OrgProvider } from './lib/org'
import AppShell from './components/layout/AppShell'
import Landing from './pages/Landing'
import BootIntro from './components/brand/LogoIntro'
import { setAuthTokenGetter } from './lib/api'

const Dashboard = lazy(() => import('./pages/Dashboard'))
const Projects = lazy(() => import('./pages/Projects'))
const ProjectDetail = lazy(() => import('./pages/ProjectDetail'))
const Workers = lazy(() => import('./pages/Workers'))
const WorkerDetail = lazy(() => import('./pages/WorkerDetail'))
const Evaluate = lazy(() => import('./pages/Evaluate'))
const EvaluateWorker = lazy(() => import('./pages/EvaluateWorker'))
const Terms = lazy(() => import('./pages/Terms'))
const Privacy = lazy(() => import('./pages/Privacy'))

const clerkEnabled = Boolean(import.meta.env.VITE_CLERK_PUBLISHABLE_KEY) &&
  import.meta.env.VITE_AUTH_MOCK_ENABLED !== 'true'

const PageFallback = () => <div className="animate-pulse text-gray-400 p-6">Cargando...</div>

function ProtectedApp() {
  return (
    <OrgProvider>
      <Routes>
        <Route element={<AppShell />}>
          <Route index element={<Suspense fallback={<PageFallback />}><Dashboard /></Suspense>} />
          <Route path="projects" element={<Suspense fallback={<PageFallback />}><Projects /></Suspense>} />
          <Route path="projects/:id" element={<Suspense fallback={<PageFallback />}><ProjectDetail /></Suspense>} />
          <Route path="workers" element={<Suspense fallback={<PageFallback />}><Workers /></Suspense>} />
          <Route path="workers/:id" element={<Suspense fallback={<PageFallback />}><WorkerDetail /></Suspense>} />
          <Route path="evaluate" element={<Suspense fallback={<PageFallback />}><Evaluate /></Suspense>} />
          <Route path="evaluate/:projectId/:workerId" element={<Suspense fallback={<PageFallback />}><EvaluateWorker /></Suspense>} />
        </Route>
      </Routes>
    </OrgProvider>
  )
}

function AuthenticatedApp() {
  const { getToken } = useAuth()
  setAuthTokenGetter(() => getToken())
  return <ProtectedApp />
}

export default function App() {
  if (!clerkEnabled) {
    return (
      <>
      <BootIntro />
      <Routes>
        <Route path="/" element={<Landing isSignedIn={true} />} />
        <Route path="/terminos" element={<Suspense fallback={<PageFallback />}><Terms /></Suspense>} />
        <Route path="/privacidad" element={<Suspense fallback={<PageFallback />}><Privacy /></Suspense>} />
        <Route path="/app/*" element={<ProtectedApp />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
      </>
    )
  }

  return (
    <>
    <BootIntro />
    <Routes>
      <Route
        path="/"
        element={
          <>
            <SignedIn>
              <Landing isSignedIn={true} />
            </SignedIn>
            <SignedOut>
              <Landing isSignedIn={false} />
            </SignedOut>
          </>
        }
      />
      <Route path="/terminos" element={<Suspense fallback={<PageFallback />}><Terms /></Suspense>} />
      <Route path="/privacidad" element={<Suspense fallback={<PageFallback />}><Privacy /></Suspense>} />
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
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
    </>
  )
}
