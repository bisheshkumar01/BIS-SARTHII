import Logo from './Logo.jsx'

export default function Footer() {
  return (
    <footer className="border-t border-navy-800/10 bg-white">
      <div className="mx-auto max-w-7xl px-6 py-10">
        <div className="flex flex-col items-start justify-between gap-6 md:flex-row md:items-center">
          <div className="flex items-center gap-2.5">
            <Logo className="h-6 w-6" />
            <span className="font-display text-sm font-bold text-navy-900">BIS SARTHI</span>
          </div>
          <p className="max-w-xl text-sm leading-relaxed text-navy-700/70">
            Every answer is grounded in official BIS sources and shown with its evidence.
            BIS SARTHI does not replace the Bureau of Indian Standards — it helps you navigate it.
          </p>
        </div>
        <div className="mt-6 flex flex-wrap items-center gap-x-6 gap-y-2 border-t border-navy-800/10 pt-6 text-xs text-navy-700/60">
          <span>Team THE BEES · Smart India Hackathon 2026</span>
          <span>Problem Statement SIH26107</span>
          <a
            href="https://www.bis.gov.in"
            target="_blank"
            rel="noreferrer"
            className="font-medium text-navy-800 hover:text-saffron-600"
          >
            Official BIS website ↗
          </a>
        </div>
      </div>
    </footer>
  )
}
