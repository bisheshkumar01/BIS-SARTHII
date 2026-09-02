import { NavLink } from 'react-router-dom'
import Logo from './Logo.jsx'

const links = [
  { to: '/chat', label: 'Ask Sarthi' },
  { to: '/scan', label: 'Scan Product' },
  { to: '/standards', label: 'Find Standard' },
  { to: '/forms', label: 'Forms Hub' },
  { to: '/roadmap', label: 'Roadmap' },
]

export default function Navbar() {
  return (
    <header className="sticky top-0 z-40 border-b border-navy-800/10 bg-paper-50/85 backdrop-blur-md">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-6">
        <NavLink to="/" className="flex items-center gap-2.5">
          <Logo className="h-8 w-8" />
          <span className="font-display text-lg font-extrabold tracking-tight text-navy-900">
            BIS SARTHI
          </span>
        </NavLink>

        <nav className="hidden items-center gap-1 md:flex">
          {links.map((l) => (
            <NavLink
              key={l.to}
              to={l.to}
              className={({ isActive }) =>
                `rounded-full px-4 py-2 text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-navy-900 text-white'
                    : 'text-navy-700 hover:bg-navy-900/5'
                }`
              }
            >
              {l.label}
            </NavLink>
          ))}
        </nav>

        <div className="flex items-center gap-3">
          <button
            type="button"
            className="rounded-full border border-navy-800/15 px-3 py-1.5 text-sm font-semibold text-navy-800 hover:bg-navy-900/5"
            title="Switch language"
          >
            EN / हिं
          </button>
          <NavLink
            to="/chat"
            className="hidden rounded-full bg-saffron-500 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-saffron-600 sm:block"
          >
            Ask Sarthi
          </NavLink>
        </div>
      </div>
    </header>
  )
}
