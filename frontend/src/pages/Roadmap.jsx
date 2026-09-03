import { CheckCircle2, Circle, ChevronRight } from 'lucide-react'

const steps = [
  { title: 'Product identified', status: 'done', detail: 'Stainless steel water bottle, 1L, food-grade.' },
  { title: 'Applicable standard identified', status: 'done', detail: 'IS 14543 : 2016 — Packaged Drinking Water Specification.' },
  { title: 'Certification applicability', status: 'current', detail: 'Checking whether ISI marking is mandatory for this category.' },
  { title: 'Testing requirements', status: 'pending', detail: 'Lab tests required before licence application.' },
  { title: 'Required documents & forms', status: 'pending', detail: 'Form V and supporting test reports.' },
  { title: 'Application & licensing process', status: 'pending', detail: 'Submit to BIS regional office.' },
  { title: 'Inspection / assessment', status: 'pending', detail: 'Factory inspection where applicable.' },
  { title: 'Certification & post-certification', status: 'pending', detail: 'Ongoing surveillance and renewal.' },
]

const statusStyle = {
  done: 'text-verified-600',
  current: 'text-saffron-600',
  pending: 'text-navy-700/30',
}

export default function Roadmap() {
  return (
    <div className="mx-auto max-w-5xl px-6 py-14">
      <h1 className="font-display text-3xl font-extrabold text-navy-900">Your BIS Compliance Roadmap</h1>
      <p className="mt-2 text-navy-700/65">
        A personalised path from product to certification, with sources at every step.
      </p>

      <div className="mt-10 space-y-0">
        {steps.map((s, i) => (
          <div key={s.title} className="flex gap-4">
            <div className="flex flex-col items-center">
              {s.status === 'done' ? (
                <CheckCircle2 className="h-6 w-6 text-verified-600" />
              ) : (
                <Circle className={`h-6 w-6 ${statusStyle[s.status]}`} />
              )}
              {i < steps.length - 1 && <span className="my-1 h-full w-px flex-1 bg-navy-900/10" />}
            </div>
            <div className={`flex-1 pb-8 ${s.status === 'pending' ? 'opacity-50' : ''}`}>
              <div className="flex items-center justify-between">
                <p className="text-sm font-semibold text-navy-900">{s.title}</p>
                {s.status === 'current' && (
                  <span className="rounded-full bg-saffron-100 px-2.5 py-0.5 text-[10px] font-bold text-saffron-600">
                    IN PROGRESS
                  </span>
                )}
              </div>
              <p className="mt-1 text-xs leading-relaxed text-navy-700/65">{s.detail}</p>
              {s.status !== 'pending' && (
                <button className="mt-2 inline-flex items-center gap-1 text-xs font-semibold text-navy-700 hover:text-saffron-600">
                  View details <ChevronRight className="h-3 w-3" />
                </button>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
