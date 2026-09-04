import { useEffect, useState } from 'react'
import { NavLink, useLocation } from 'react-router-dom'
import PillNav from './PillNav.jsx'

const links = [
  { to: '/chat', label: 'Ask Sarthi' },
  { to: '/scan', label: 'Scan Product' },
  { to: '/standards', label: 'Find Standard' },
  { to: '/forms', label: 'Forms Hub' },
  { to: '/roadmap', label: 'Roadmap' },
]

// Built once at module scope, not inside the component: PillNav's items prop needs a
// stable reference. A fresh .map() on every Navbar render (which happens on every route
// change and every scroll-threshold toggle) was making PillNav think its item list had
// changed, which reran its intro animation each time.
const pillNavItems = links.map(l => ({ label: l.label, href: l.to }))

// Past this many pixels of scroll, the bar detaches from the top edge and floats.
const SCROLL_THRESHOLD = 24

export default function Navbar() {
  const { pathname } = useLocation()
  const [scrolled, setScrolled] = useState(false)

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > SCROLL_THRESHOLD)
    onScroll() // in case the page loads already scrolled (e.g. a deep link with a hash)
    window.addEventListener('scroll', onScroll, { passive: true })
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  return (
    // The outer element stays flush at the very top always — it's the inner bar below
    // that visually shrinks and floats, via a top margin that opens a gap above it once
    // scrolled. Splitting them this way means the floating state can have its own margin
    // without the sticky positioning itself having to move.
    <header className="sticky top-0 z-40" style={{ fontFamily: '"Claire Hand", var(--font-display)' }}>
      <div
        className={`mx-auto transition-all duration-300 ease-out ${
          scrolled
            ? 'mt-3 max-w-5xl rounded-full border border-navy-800/10 bg-paper-50/90 shadow-lg shadow-navy-900/10 backdrop-blur-md'
            : 'mt-0 max-w-7xl rounded-none border-b border-navy-800/10 bg-paper-50/85 backdrop-blur-md'
        }`}
      >
        {/* Three columns so the nav can sit at true center regardless of how wide the
            wordmark or the toggle are — a flex justify-between would center the nav only
            when its neighbours happened to match in width. */}
        <div className="grid h-16 grid-cols-[1fr_auto_1fr] items-center px-6">
          <NavLink to="/" className="justify-self-start text-2xl font-bold tracking-tight text-navy-900">
            BIS SARTHI
          </NavLink>

          {/* PillNav owns pills + its own mobile hamburger/popover; no logo prop, since the
              wordmark above already fills that role and a second one would duplicate it.
              Colors are a placeholder (navy fill on hover, transparent idle) — flagged for
              the wider palette pass still to come. */}
          <div className="justify-self-center">
            <PillNav
              items={pillNavItems}
              activeHref={pathname}
              ease="power2.easeOut"
              baseColor="var(--color-navy-900)"
              pillColor="transparent"
              pillTextColor="var(--color-navy-700)"
              hoveredPillTextColor="#ffffff"
            />
          </div>

          <button
            type="button"
            className="press justify-self-end rounded-full border border-navy-800/15 px-3 py-1.5 text-base font-normal text-navy-800 hover:bg-navy-900/5"
            title="Switch language"
          >
            EN / हिं
          </button>
        </div>
      </div>
    </header>
  )
}
