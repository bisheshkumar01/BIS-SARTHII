import { Search, ShieldCheck, ExternalLink } from 'lucide-react'

const matches = [
  {
    isNumber: 'IS 14543 : 2016',
    title: 'Packaged Drinking Water — Specification',
    score: 92,
    scheme: 'Mandatory · ISI Mark',
    why: ['Product category matches "packaged water"', 'Intended use: human consumption'],

    
  },
  {
    isNumber: 'IS 13428 : 2005',
    title: 'Packaged Natural Mineral Water — Specification',
    score: 61,
    scheme: 'Applicable if mineral-sourced',
    why: ['Partial category overlap', 'Requires source verification'],
  },
]

export default function Standards() {
  return (
    <div className="mx-auto max-w-4xl px-6 py-14">
      <h1 className="font-display text-3xl font-bold text-navy-900">Find your standard</h1>
      <p className="mt-2 text-navy-700/65">
        Describe your product — material, use, and any specifications you have.
      </p>

      <div className="mt-6 flex items-center gap-2 rounded-2xl border border-navy-900/10 bg-white p-2 shadow-sm">
        <Search className="ml-2 h-4 w-4 text-navy-700/40" />
        <input
          placeholder="e.g. 1L stainless steel water bottle, food-grade"
          className="flex-1 bg-transparent px-2 py-2.5 text-sm outline-none placeholder:text-navy-700/40"
        />
        <button className="rounded-full bg-navy-900 px-5 py-2 text-sm font-semibold text-white hover:bg-navy-800">
          Match
        </button>
      </div>

      <div className="mt-8 space-y-4">
        <p className="text-xs font-semibold uppercase tracking-wide text-navy-700/50">
          Potentially applicable standards
        </p>
        {matches.map((m) => (
          <div key={m.isNumber} className="card p-5">
            <div className="flex items-start justify-between gap-4">
              <div>
                <p className="text-base font-semibold text-navy-900">{m.isNumber}</p>
                <p className="mt-0.5 text-sm text-navy-700/70">{m.title}</p>
              </div>
              <div className="flex shrink-0 flex-col items-end">
                <span className="text-lg font-bold tabular-nums text-saffron-600">{m.score}%</span>
                <span className="text-[10px] uppercase tracking-wide text-navy-700/40">match</span>
              </div>
            </div>

            <span className="mt-3 inline-block rounded-full bg-verified-100 px-2.5 py-1 text-[11px] font-bold text-verified-600">
              {m.scheme}
            </span>

            <ul className="mt-3 space-y-1">
              {m.why.map((w) => (
                <li key={w} className="flex items-start gap-1.5 text-xs text-navy-700/65">
                  <span className="mt-1 h-1 w-1 shrink-0 rounded-full bg-navy-700/40" /> {w}
                </li>
              ))}
            </ul>

            <div className="mt-4 flex items-center gap-4 border-t border-navy-900/5 pt-3">
              <button className="inline-flex items-center gap-1.5 text-xs font-semibold text-saffron-600 hover:underline">
                <ShieldCheck className="h-3.5 w-3.5" /> Why this standard?
              </button>
              <button className="inline-flex items-center gap-1.5 text-xs font-semibold text-navy-700 hover:underline">
                Official source <ExternalLink className="h-3 w-3" />
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
