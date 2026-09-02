import { Link } from 'react-router-dom'
import {
  ScanLine,
  MessageCircleQuestion,
  FileSearch,
  ClipboardList,
  Route as RouteIcon,
  ShieldCheck,
  Languages,
  ArrowRight,
  CheckCircle2,
  Factory,
  Ship,
  FlaskConical,
  Users,
  GraduationCap,
  Quote,
} from 'lucide-react'

const actions = [
  { to: '/chat', icon: MessageCircleQuestion, label: 'Ask Sārthi', desc: 'Ask any BIS or standards question in plain language.' },
  { to: '/scan', icon: ScanLine, label: 'Scan Product', desc: 'Upload a photo or label — we read it for you.' },
  { to: '/standards', icon: FileSearch, label: 'Find Standard', desc: 'Match your product to the right Indian Standard.' },
  { to: '/forms', icon: ClipboardList, label: 'Find Form', desc: 'Locate the exact BIS form you need, ranked by relevance.' },
  { to: '/roadmap', icon: RouteIcon, label: 'Compliance Roadmap', desc: 'A step-by-step path from product to certification.' },
]

const steps = [
  { n: '01', title: 'Describe or scan your product', desc: 'Type a description or upload a photo/label — Sārthi extracts what matters.' },
  { n: '02', title: 'Get matched standards, with proof', desc: 'Ranked Indian Standards, each with a relevance score and the evidence behind it.' },
  { n: '03', title: 'Understand certification & forms', desc: 'Mandatory, voluntary, or unclear — stated plainly, with the exact forms required.' },
  { n: '04', title: 'Follow your compliance roadmap', desc: 'A personalised, step-by-step path from product to certified.' },
]

const diffs = [
  { icon: ScanLine, title: 'Product-aware AI', desc: 'Understands product photos, labels, and specs — not just text queries.' },
  { icon: FileSearch, title: 'Smart standard matching', desc: 'A transparent scoring engine, not a guess — every match is explained.' },
  { icon: ShieldCheck, title: 'Evidence-first answers', desc: 'Every claim traces back to an official BIS source. No source, no answer.' },
  { icon: ClipboardList, title: 'Smart Form Finder', desc: 'Recommends the forms relevant to your product and stage — never invented.' },
  { icon: RouteIcon, title: 'Personalised roadmap', desc: 'Turns scattered BIS information into one clear, actionable sequence.' },
  { icon: Languages, title: 'English & हिंदी', desc: 'Ask in either language — standard numbers and form IDs stay unchanged.' },
]

const users = [
  { icon: Factory, label: 'MSMEs & Manufacturers' },
  { icon: Ship, label: 'Importers & Businesses' },
  { icon: FlaskConical, label: 'Testing Labs & Consultants' },
  { icon: Users, label: 'Consumers' },
  { icon: GraduationCap, label: 'Students & Researchers' },
]

export default function Home() {
  return (
    <div>
      {/* HERO */}
      <section className="relative overflow-hidden bg-navy-900">
        <div className="bg-grid absolute inset-0 opacity-40" />
        <div
          className="absolute -top-24 right-[-10%] h-96 w-96 rounded-full opacity-20 blur-3xl"
          style={{ background: 'var(--color-saffron-500)' }}
        />
        <div className="relative mx-auto max-w-7xl px-6 pb-24 pt-20 md:pt-28">
          <div className="mx-auto max-w-3xl text-center">
            <span className="inline-flex items-center gap-2 rounded-full border border-white/15 bg-white/5 px-4 py-1.5 text-xs font-semibold uppercase tracking-wider text-saffron-400">
              Smart India Hackathon 2026 · SIH26107 · Team THE BEES
            </span>
            <h1 className="font-display mt-6 text-4xl font-extrabold leading-tight tracking-tight text-white sm:text-5xl md:text-6xl">
              Your AI-powered guide to
              <span className="text-saffron-400"> BIS compliance</span>
            </h1>
            <p className="mx-auto mt-5 max-w-2xl text-lg leading-relaxed text-white/70">
              Describe your product or scan its label — Sārthi finds the applicable Indian
              Standard, explains certification, surfaces the right forms, and builds you a
              step-by-step roadmap. Every answer backed by an official BIS source.
            </p>

            <div className="mt-9 flex flex-col items-center justify-center gap-3 sm:flex-row">
              <Link
                to="/chat"
                className="inline-flex items-center gap-2 rounded-full bg-saffron-500 px-7 py-3.5 text-base font-semibold text-white shadow-lg shadow-saffron-500/20 transition hover:bg-saffron-600"
              >
                Ask Sārthi <ArrowRight className="h-4 w-4" />
              </Link>
              <Link
                to="/scan"
                className="inline-flex items-center gap-2 rounded-full border border-white/20 bg-white/5 px-7 py-3.5 text-base font-semibold text-white transition hover:bg-white/10"
              >
                <ScanLine className="h-4 w-4" /> Scan a Product
              </Link>
            </div>

            <div className="mt-10 flex flex-wrap items-center justify-center gap-x-8 gap-y-3 text-sm text-white/55">
              <span className="inline-flex items-center gap-1.5">
                <CheckCircle2 className="h-4 w-4 text-verified-500" /> Evidence-backed answers
              </span>
              <span className="inline-flex items-center gap-1.5">
                <CheckCircle2 className="h-4 w-4 text-verified-500" /> Official BIS sources only
              </span>
              <span className="inline-flex items-center gap-1.5">
                <CheckCircle2 className="h-4 w-4 text-verified-500" /> English &amp; हिंदी
              </span>
            </div>
          </div>
        </div>
      </section>

      {/* ACTION CARDS */}
      {/* relative+z-10: the hero above is position:relative, so without its own
          stacking context this section paints *under* it and the cards get clipped. */}
      <section className="relative z-10 mx-auto -mt-12 max-w-7xl px-6">
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-5">
          {actions.map((a) => (
            <Link
              key={a.to}
              to={a.to}
              className="card card-hover group flex flex-col gap-3 p-5"
            >
              <span className="inline-flex h-11 w-11 items-center justify-center rounded-xl bg-navy-900/5 text-navy-800 group-hover:bg-saffron-100 group-hover:text-saffron-600">
                <a.icon className="h-5 w-5" />
              </span>
              <div>
                <p className="font-display text-sm font-bold text-navy-900">{a.label}</p>
                <p className="mt-1 text-xs leading-relaxed text-navy-700/65">{a.desc}</p>
              </div>
            </Link>
          ))}
        </div>
      </section>

      {/* HOW IT WORKS */}
      <section className="mx-auto max-w-7xl px-6 py-24">
        <div className="mx-auto max-w-2xl text-center">
          <span className="text-xs font-bold uppercase tracking-widest text-saffron-600">How it works</span>
          <h2 className="font-display mt-3 text-3xl font-extrabold text-navy-900 sm:text-4xl">
            From a vague product to an actionable compliance path
          </h2>
        </div>
        <div className="mt-14 grid grid-cols-1 gap-8 md:grid-cols-4">
          {steps.map((s, i) => (
            <div key={s.n} className="relative">
              <div className="flex items-center gap-3">
                <span className="font-display text-3xl font-extrabold text-navy-900/10">{s.n}</span>
                {i < steps.length - 1 && (
                  <span className="hidden h-px flex-1 bg-navy-900/10 md:block" />
                )}
              </div>
              <h3 className="font-display mt-4 text-base font-bold text-navy-900">{s.title}</h3>
              <p className="mt-2 text-sm leading-relaxed text-navy-700/65">{s.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* DIFFERENTIATORS */}
      <section className="bg-navy-950 py-24">
        <div className="mx-auto max-w-7xl px-6">
          <div className="mx-auto max-w-2xl text-center">
            <span className="text-xs font-bold uppercase tracking-widest text-saffron-400">Why not just ask a chatbot?</span>
            <h2 className="font-display mt-3 text-3xl font-extrabold text-white sm:text-4xl">
              Not a generic AI. A compliance navigator.
            </h2>
          </div>
          <div className="mt-14 grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
            {diffs.map((d) => (
              <div key={d.title} className="rounded-2xl border border-white/10 bg-white/[0.03] p-6">
                <d.icon className="h-6 w-6 text-saffron-400" />
                <h3 className="font-display mt-4 text-base font-bold text-white">{d.title}</h3>
                <p className="mt-2 text-sm leading-relaxed text-white/60">{d.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* EVIDENCE CALLOUT */}
      <section className="mx-auto max-w-7xl px-6 py-24">
        <div className="grid grid-cols-1 items-center gap-12 lg:grid-cols-2">
          <div>
            <span className="text-xs font-bold uppercase tracking-widest text-saffron-600">Trust, by design</span>
            <h2 className="font-display mt-3 text-3xl font-extrabold text-navy-900 sm:text-4xl">
              If we can't verify it, we say so.
            </h2>
            <p className="mt-4 max-w-lg text-base leading-relaxed text-navy-700/70">
              Every answer carries a confidence level and an evidence trail back to its source
              document and official BIS link. When the retrieved evidence isn't strong enough,
              Sārthi tells you plainly instead of guessing.
            </p>
            <div className="mt-6 flex flex-wrap gap-2">
              {['HIGH confidence', 'MEDIUM confidence', 'LOW confidence', 'UNVERIFIED'].map((c) => (
                <span
                  key={c}
                  className="rounded-full border border-navy-900/10 bg-white px-3 py-1 text-xs font-semibold text-navy-800"
                >
                  {c}
                </span>
              ))}
            </div>
          </div>

          <div className="card p-6">
            <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wide text-verified-600">
              <ShieldCheck className="h-4 w-4" /> Evidence
            </div>
            <div className="mt-4 rounded-xl bg-verified-100 p-4">
              <div className="flex items-start gap-3">
                <Quote className="mt-0.5 h-4 w-4 shrink-0 text-verified-600" />
                <p className="text-sm leading-relaxed text-navy-800">
                  "...packaged drinking water shall conform to the requirements specified for
                  quality and safety before sale..."
                </p>
              </div>
            </div>
            <dl className="mt-4 grid grid-cols-2 gap-3 text-xs">
              <div>
                <dt className="text-navy-700/50">Source</dt>
                <dd className="font-semibold text-navy-900">IS 14543 — Packaged Drinking Water</dd>
              </div>
              <div>
                <dt className="text-navy-700/50">Scheme</dt>
                <dd className="font-semibold text-navy-900">Mandatory · ISI Mark</dd>
              </div>
              <div className="col-span-2">
                <dt className="text-navy-700/50">Official BIS source</dt>
                <dd className="truncate font-semibold text-saffron-600">bis.gov.in ↗</dd>
              </div>
            </dl>
          </div>
        </div>
      </section>

      {/* USER TYPES */}
      <section className="border-t border-navy-900/5 bg-white py-20">
        <div className="mx-auto max-w-7xl px-6">
          <h2 className="font-display text-center text-2xl font-extrabold text-navy-900">
            Built for everyone who deals with BIS
          </h2>
          <div className="mt-10 flex flex-wrap items-center justify-center gap-4">
            {users.map((u) => (
              <div
                key={u.label}
                className="inline-flex items-center gap-2.5 rounded-full border border-navy-900/10 bg-paper-50 px-5 py-2.5"
              >
                <u.icon className="h-4 w-4 text-navy-700" />
                <span className="text-sm font-semibold text-navy-800">{u.label}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA BAND */}
      <section className="mx-auto max-w-7xl px-6 py-20">
        <div className="relative overflow-hidden rounded-3xl bg-navy-900 px-8 py-14 text-center sm:px-16">
          <div
            className="absolute -bottom-24 left-1/2 h-72 w-72 -translate-x-1/2 rounded-full opacity-20 blur-3xl"
            style={{ background: 'var(--color-saffron-500)' }}
          />
          <div className="relative">
            <h2 className="font-display text-3xl font-extrabold text-white sm:text-4xl">
              Ready to find your standard?
            </h2>
            <p className="mx-auto mt-3 max-w-xl text-white/65">
              Start a conversation, or upload a photo of your product to begin.
            </p>
            <div className="mt-8 flex flex-col items-center justify-center gap-3 sm:flex-row">
              <Link
                to="/chat"
                className="rounded-full bg-saffron-500 px-7 py-3.5 text-base font-semibold text-white transition hover:bg-saffron-600"
              >
                Ask Sārthi
              </Link>
              <Link
                to="/roadmap"
                className="rounded-full border border-white/20 px-7 py-3.5 text-base font-semibold text-white transition hover:bg-white/10"
              >
                Start Compliance Roadmap
              </Link>
            </div>
          </div>
        </div>
      </section>
    </div>
  )
}
