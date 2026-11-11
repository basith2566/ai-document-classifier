import { useEffect, useState } from 'react'
import { NavLink, Outlet, useLocation } from 'react-router-dom'
import { Clock, FileSearch, LayoutDashboard, Menu, UploadCloud, X } from 'lucide-react'
import { apiConfigured, getHealth } from '../api/client.js'
import { Alert } from './ui.jsx'

const NAV = [
  { to: '/', label: 'Dashboard', icon: LayoutDashboard, end: true },
  { to: '/upload', label: 'Upload', icon: UploadCloud },
  { to: '/results', label: 'Results', icon: FileSearch },
  { to: '/history', label: 'History', icon: Clock },
]

function ServerStatus() {
  const [state, setState] = useState('checking')
  useEffect(() => {
    getHealth()
      .then((h) => setState(h.model_ready ? 'ready' : 'no-model'))
      .catch(() => setState('offline'))
  }, [])
  const info = {
    checking: ['bg-navy-400', 'Connecting…'],
    ready: ['bg-emerald-400', 'API online · model ready'],
    'no-model': ['bg-amber-400', 'API online · model missing'],
    offline: ['bg-red-400', 'API unreachable'],
  }[state]
  return (
    <div className="flex items-center gap-2 text-xs text-navy-200">
      <span className={`h-2 w-2 rounded-full ${info[0]}`} /> {info[1]}
    </div>
  )
}

function Sidebar({ onNavigate }) {
  return (
    <div className="flex h-full flex-col bg-navy-950 text-white">
      <div className="px-6 py-6">
        <p className="text-lg font-semibold tracking-tight">DocuSort</p>
        <p className="text-xs text-navy-300">AI document classification</p>
      </div>
      <nav className="flex-1 space-y-1 px-3">
        {NAV.map(({ to, label, icon: Icon, end }) => (
          <NavLink
            key={to}
            to={to}
            end={end}
            onClick={onNavigate}
            className={({ isActive }) =>
              `flex items-center gap-3 rounded-md px-3 py-2.5 text-sm font-medium transition-colors ${
                isActive ? 'bg-white/10 text-white' : 'text-navy-200 hover:bg-white/5 hover:text-white'
              }`
            }
          >
            <Icon className="h-4 w-4" /> {label}
          </NavLink>
        ))}
      </nav>
      <div className="border-t border-white/10 px-6 py-4">
        <ServerStatus />
      </div>
    </div>
  )
}

export default function Layout() {
  const [open, setOpen] = useState(false)
  const location = useLocation()
  useEffect(() => setOpen(false), [location.pathname])

  return (
    <div className="min-h-screen">
      <aside className="fixed inset-y-0 left-0 z-30 hidden w-60 lg:block">
        <Sidebar />
      </aside>

      <header className="sticky top-0 z-20 flex items-center justify-between bg-navy-950 px-4 py-3 text-white lg:hidden">
        <p className="font-semibold">DocuSort</p>
        <button onClick={() => setOpen(true)} aria-label="Open menu" className="rounded p-1 hover:bg-white/10">
          <Menu className="h-5 w-5" />
        </button>
      </header>

      {open && (
        <div className="fixed inset-0 z-40 lg:hidden">
          <div className="absolute inset-0 bg-navy-950/60" onClick={() => setOpen(false)} />
          <div className="absolute inset-y-0 left-0 w-64">
            <Sidebar onNavigate={() => setOpen(false)} />
            <button onClick={() => setOpen(false)} aria-label="Close menu" className="absolute right-3 top-4 rounded p-1 text-white hover:bg-white/10">
              <X className="h-5 w-5" />
            </button>
          </div>
        </div>
      )}

      <main className="lg:pl-60">
        <div className="mx-auto max-w-6xl px-4 py-8 sm:px-8">
          {!apiConfigured && (
            <div className="mb-6">
              <Alert title="API URL is not configured">
                Set the <code>VITE_API_URL</code> environment variable to your backend URL and redeploy.
              </Alert>
            </div>
          )}
          <Outlet />
        </div>
      </main>
    </div>
  )
}
