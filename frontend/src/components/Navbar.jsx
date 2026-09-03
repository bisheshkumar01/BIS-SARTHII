import { NavLink } from 'react-router-dom'

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
      {/* Three columns so the nav can sit at true center regardless of how wide the
          wordmark or the toggle are — a flex justify-between would center the nav only
          when its neighbours happened to match in width. */}
      <div className="mx-auto grid h-16 max-w-7xl grid-cols-[1fr_auto_1fr] items-center px-6">
        <NavLink to="/" className="font-display justify-self-start text-lg font-extrabold tracking-tight text-navy-900">
          BIS SARTHI
        </NavLink>

        <nav className="hidden items-center gap-1 justify-self-center md:flex">
          {links.map((l) => (
            <NavLink
              key={l.to}
              to={l.to}
              className={({ isActive }) =>
                `rounded-full px-4 py-2 text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-navy-900 text-white'
                    : 'link-underline text-navy-700 hover:bg-navy-900/5'
                }`
              }
            >
              {l.label}
            </NavLink>
          ))}
        </nav>

        <button
          type="button"
          className="press justify-self-end rounded-full border border-navy-800/15 px-3 py-1.5 text-sm font-semibold text-navy-800 hover:bg-navy-900/5"
          title="Switch language"
        >
          EN / हिं
        </button>
      </div>
    </header>
  )
}
