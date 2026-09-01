import { Search, FileText, ExternalLink } from 'lucide-react'

const forms = [
  { code: 'Form V', name: 'Application for Grant of Licence', purpose: 'Initial ISI mark licence application for a product.', scheme: 'ISI Scheme' },
  { code: 'Form VI', name: 'Test Report Format', purpose: 'Submitting product test results from a recognised lab.', scheme: 'ISI Scheme' },
  { code: 'CRS-1', name: 'CRS Registration Application', purpose: 'Registration under the Compulsory Registration Scheme.', scheme: 'CRS' },
]

export default function Forms() {
  return (
    <div className="mx-auto max-w-4xl px-6 py-14">
      <h1 className="font-display text-3xl font-extrabold text-navy-900">Forms Hub</h1>
      <p className="mt-2 text-navy-700/65">
        Ask what you need in plain language — Sārthi finds the right form for your stage.
      </p>

      <div className="mt-6 flex items-center gap-2 rounded-2xl border border-navy-900/10 bg-white p-2 shadow-sm">
        <Search className="ml-2 h-4 w-4 text-navy-700/40" />
        <input
          placeholder="e.g. What form do I need to apply for an ISI licence?"
          className="flex-1 bg-transparent px-2 py-2.5 text-sm outline-none placeholder:text-navy-700/40"
        />
        <button className="rounded-full bg-navy-900 px-5 py-2 text-sm font-semibold text-white hover:bg-navy-800">
          Search
        </button>
      </div>

      <div className="mt-8 space-y-3">
        {forms.map((f) => (
          <div key={f.code} className="card flex items-start gap-4 p-5">
            <span className="mt-0.5 inline-flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-navy-900/5 text-navy-800">
              <FileText className="h-4 w-4" />
            </span>
            <div className="flex-1">
              <div className="flex flex-wrap items-center gap-2">
                <p className="font-display text-sm font-bold text-navy-900">{f.code} — {f.name}</p>
                <span className="rounded-full bg-saffron-100 px-2 py-0.5 text-[10px] font-bold text-saffron-600">
                  {f.scheme}
                </span>
              </div>
              <p className="mt-1 text-xs leading-relaxed text-navy-700/65">{f.purpose}</p>
              <div className="mt-2.5 flex items-center gap-4">
                <button className="text-xs font-semibold text-navy-700 hover:underline">View Form</button>
                <button className="inline-flex items-center gap-1 text-xs font-semibold text-saffron-600 hover:underline">
                  Official BIS source <ExternalLink className="h-3 w-3" />
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
