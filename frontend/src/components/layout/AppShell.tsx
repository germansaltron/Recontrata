import { useEffect, useState } from 'react'
import { NavLink, Outlet } from 'react-router-dom'
import { LayoutDashboard, FolderKanban, Users, ClipboardCheck, Menu, X } from 'lucide-react'
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

export default function AppShell() {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const { orgId } = useOrg()

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
          <button className="md:hidden p-1" onClick={() => setSidebarOpen(false)}>
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
        </nav>
      </aside>

      {/* Main */}
      <div className="flex-1 flex flex-col min-w-0">
        <header className="h-16 bg-white border-b border-gray-200 flex items-center px-4 md:px-6">
          <button className="md:hidden p-2 -ml-2 mr-2" onClick={() => setSidebarOpen(true)}>
            <Menu className="w-5 h-5" />
          </button>
          <div className="flex-1" />
          <UserButton
            afterSignOutUrl="/"
            showName
            appearance={{ elements: { userButtonBox: 'flex-row-reverse gap-2', userButtonOuterIdentifier: 'text-sm text-gray-700' } }}
          />
        </header>
        <main className="flex-1 overflow-auto p-4 md:p-6">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
