import { useEffect, useState } from 'react'
import { NavLink, Outlet } from 'react-router-dom'
import { LayoutDashboard, FolderKanban, Users, ClipboardCheck, Scale, Menu, X, AlertTriangle } from 'lucide-react'
import { UserButton } from '@clerk/clerk-react'
import { useOrg } from '../../lib/org'
import { api } from '../../lib/api'
import { prefetch } from '../../lib/swr'

const navItems = [
  { to: '/app', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/app/projects', icon: FolderKanban, label: 'Proyectos' },
  { to: '/app/workers', icon: Users, label: 'Trabajadores' },
  { to: '/app/evaluate', icon: ClipboardCheck, label: 'Evaluar' },
]

// Items secundarios: solo en el sidebar de escritorio (la bottom-nav móvil
// mantiene 4 accesos para no romper su grilla).
const secondaryNavItems = [
  { to: '/app/formula', icon: Scale, label: 'Fórmula del puntaje' },
]

// UserButton solo funciona dentro de <ClerkProvider>. En modo mock (sin Clerk)
// no debe montarse, o crashea toda la app.
const clerkEnabled = Boolean(import.meta.env.VITE_CLERK_PUBLISHABLE_KEY) &&
  import.meta.env.VITE_AUTH_MOCK_ENABLED !== 'true'

export default function AppShell() {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const { orgId, loading, error, retry } = useOrg()

  // Warm up Evaluate (data + JS chunk) while the user is on any panel screen,
  // so the click feels instant. Best-effort, no UI impact.
  useEffect(() => {
    if (!orgId) return
    prefetch(`projects-pending:${orgId}`, () => api.getProjectsPending(orgId))
    import('../../pages/Evaluate').catch(() => { /* best-effort */ })
  }, [orgId])

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Mobile overlay */}
      {sidebarOpen && (
        <div className="fixed inset-0 bg-black/50 z-40 md:hidden" onClick={() => setSidebarOpen(false)} />
      )}

      {/* Sidebar */}
      <aside className={`fixed md:static inset-y-0 left-0 z-50 w-64 bg-white border-r border-gray-200 transform transition-transform md:translate-x-0 ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}`}>
        <div className="flex items-center justify-between h-16 px-4 border-b border-gray-200">
          <h1 className="text-xl font-bold text-gray-900">Recontrata</h1>
          <button className="md:hidden p-1" onClick={() => setSidebarOpen(false)} aria-label="Cerrar menú">
            <X className="w-5 h-5" />
          </button>
        </div>
        <nav className="p-4 space-y-1">
          {navItems.map(({ to, icon: Icon, label }) => (
            <NavLink
              key={to}
              to={to}
              end={to === '/app'}
              onClick={() => setSidebarOpen(false)}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                  isActive ? 'bg-blue-50 text-blue-700' : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
                }`
              }
            >
              <Icon className="w-5 h-5" />
              {label}
            </NavLink>
          ))}
          <div className="my-2 border-t border-gray-100" />
          {secondaryNavItems.map(({ to, icon: Icon, label }) => (
            <NavLink
              key={to}
              to={to}
              onClick={() => setSidebarOpen(false)}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                  isActive ? 'bg-blue-50 text-blue-700' : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
                }`
              }
            >
              <Icon className="w-5 h-5" />
              {label}
            </NavLink>
          ))}
        </nav>
      </aside>

      {/* Main */}
      <div className="flex-1 flex flex-col min-w-0">
        <header className="h-16 bg-white border-b border-gray-200 flex items-center px-4 md:px-6">
          <button className="md:hidden p-2 -ml-2 mr-2" onClick={() => setSidebarOpen(true)} aria-label="Abrir menú">
            <Menu className="w-5 h-5" />
          </button>
          <div className="flex-1" />
          {clerkEnabled ? (
            <UserButton
              afterSignOutUrl="/"
              showName
              appearance={{ elements: { userButtonBox: 'flex-row-reverse gap-2', userButtonOuterIdentifier: 'text-sm text-gray-700' } }}
            />
          ) : (
            <span className="text-sm text-gray-400">Modo demo</span>
          )}
        </header>
        {/* pb-20 en móvil deja espacio para la bottom-nav */}
        <main className="flex-1 overflow-auto p-4 md:p-6 pb-20 md:pb-6">
          {error ? (
            <OrgError message={error} onRetry={retry} />
          ) : loading && !orgId ? (
            <div className="flex items-center gap-2 text-gray-400" aria-busy="true">
              <span className="w-4 h-4 border-2 border-gray-300 border-t-blue-600 rounded-full animate-spin" />
              Cargando tu organización…
            </div>
          ) : (
            <Outlet />
          )}
        </main>
      </div>

      {/* Bottom-nav (solo móvil): acceso a 1 tap a las secciones clave */}
      <nav className="md:hidden fixed bottom-0 inset-x-0 z-40 bg-white border-t border-gray-200 grid grid-cols-4 pb-[env(safe-area-inset-bottom)]" aria-label="Navegación principal">
        {navItems.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/app'}
            className={({ isActive }) =>
              `flex flex-col items-center justify-center gap-0.5 py-2 text-[11px] font-medium min-h-[56px] ${
                isActive ? 'text-blue-700' : 'text-gray-500'
              }`
            }
          >
            <Icon className="w-5 h-5" />
            {label}
          </NavLink>
        ))}
      </nav>
    </div>
  )
}

function OrgError({ message, onRetry }: { message: string; onRetry: () => void }) {
  return (
    <div className="max-w-md mx-auto mt-10 bg-white rounded-xl border border-gray-200 p-6 text-center">
      <div className="w-12 h-12 mx-auto rounded-full bg-red-50 flex items-center justify-center text-red-500">
        <AlertTriangle className="w-6 h-6" />
      </div>
      <h2 className="mt-4 font-semibold text-gray-900">No pudimos cargar tu organización</h2>
      <p className="mt-2 text-sm text-gray-500">{message}</p>
      <button
        onClick={onRetry}
        className="mt-5 inline-flex items-center justify-center px-5 py-2.5 rounded-lg bg-blue-600 text-white text-sm font-medium hover:bg-blue-700"
      >
        Reintentar
      </button>
    </div>
  )
}
