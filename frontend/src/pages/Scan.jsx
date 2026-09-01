import { UploadCloud, ScanLine, CheckCircle2 } from 'lucide-react'

const detected = [
  { label: 'Detected Product', value: 'Stainless Steel Water Bottle' },
  { label: 'Detected Material', value: 'Stainless Steel (Grade 304)' },
  { label: 'Detected Capacity', value: '1 Litre' },
  { label: 'Label Claims', value: 'BPA-free, Leak-proof' },
]

export default function Scan() {
  return (
    <div className="mx-auto max-w-4xl px-6 py-14">
      <div className="text-center">
        <span className="inline-flex items-center gap-2 rounded-full bg-saffron-100 px-3 py-1 text-xs font-bold uppercase tracking-wide text-saffron-600">
          <ScanLine className="h-3.5 w-3.5" /> Product Scanner
        </span>
        <h1 className="font-display mt-4 text-3xl font-extrabold text-navy-900">
          Upload a photo — we'll read the rest
        </h1>
        <p className="mx-auto mt-2 max-w-xl text-navy-700/65">
          Product photos, labels, or spec sheets. We'll always show what we detected before using it.
        </p>
      </div>

      <div className="mt-10 grid grid-cols-1 gap-6 lg:grid-cols-2">
        <div className="card flex flex-col items-center justify-center gap-3 border-2 border-dashed border-navy-900/15 p-12 text-center">
          <UploadCloud className="h-10 w-10 text-navy-700/40" />
          <p className="text-sm font-semibold text-navy-800">Drag & drop an image, or click to upload</p>
          <p className="text-xs text-navy-700/50">JPG, PNG or WEBP · up to 5MB</p>
          <button className="mt-2 rounded-full bg-navy-900 px-5 py-2 text-sm font-semibold text-white hover:bg-navy-800">
            Choose File
          </button>
          <p className="mt-4 text-[11px] text-navy-700/40">Backend not wired yet — this is a UI preview.</p>
        </div>

        <div className="card p-6">
          <div className="flex items-center justify-between">
            <h2 className="font-display text-sm font-bold text-navy-900">We detected the following</h2>
            <span className="rounded-full bg-verified-100 px-2.5 py-1 text-[11px] font-bold text-verified-600">
              Please verify
            </span>
          </div>
          <dl className="mt-4 divide-y divide-navy-900/5">
            {detected.map((d) => (
              <div key={d.label} className="flex items-center justify-between py-3">
                <dt className="text-xs text-navy-700/50">{d.label}</dt>
                <dd className="text-sm font-semibold text-navy-900">{d.value}</dd>
              </div>
            ))}
          </dl>
          <button className="mt-5 inline-flex w-full items-center justify-center gap-2 rounded-full bg-saffron-500 px-5 py-2.5 text-sm font-semibold text-white hover:bg-saffron-600">
            <CheckCircle2 className="h-4 w-4" /> Confirm & Find Standards
          </button>
        </div>
      </div>
    </div>
  )
}
