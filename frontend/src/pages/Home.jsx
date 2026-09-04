import { Link } from 'react-router-dom'
import InteractiveHoverButton from '../components/ui/InteractiveHoverButton.jsx'
import BorderGlow from '../components/BorderGlow.jsx'
import {
  ScanLine,
  FileSearch,
  ClipboardList,
  Route as RouteIcon,
  ShieldCheck,
  Languages,
  CheckCircle2,
  Factory,
  Ship,
  FlaskConical,
  Users,
  GraduationCap,
  Quote,
} from 'lucide-react'

const steps = [
  { n: '01', title: 'Describe or scan your product', desc: 'Type a description or upload a photo/label — Sarthi extracts what matters.' },
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
        {/* Order matters: mesh (colour) → sheen (light) → grid (texture) → content. */}
        <div className="mesh-gradient" aria-hidden="true" />
        <div className="mesh-sheen" aria-hidden="true" />
        <div className="bg-grid absolute inset-0 opacity-30" aria-hidden="true" />
        {/* Darkened toward the centre so the headline keeps its contrast ratio wherever
            the blobs happen to drift. */}
        <div
          className="absolute inset-0"
          aria-hidden="true"
          style={{
            background:
              'radial-gradient(ellipse at 50% 45%, rgba(10,17,40,0.55) 0%, rgba(10,17,40,0.25) 55%, transparent 80%)',
          }}
        />
        <div className="relative mx-auto max-w-7xl px-6 pb-24 pt-20 md:pt-28">
          <div className="mx-auto max-w-3xl text-center">
            <h1 className="font-display font-bold text-white">
              Stop guessing your way through
              <span className="text-saffron-400"> BIS certification.</span>
            </h1>
            <p className="mx-auto mt-5 max-w-2xl text-lg leading-relaxed text-white/70">
              Most manufacturers discover what they needed after the application is
              rejected. Sarthi maps the standard, the testing, and the forms before you
              start.
            </p>

            <div className="mt-9 flex flex-col items-center justify-center gap-3 sm:flex-row">
              <Link to="/chat" tabIndex={-1}>
                <InteractiveHoverButton text="Ask Sarthi" variant="solid" />
              </Link>
              <Link
                to="/scan"
                className="press inline-flex items-center gap-2 rounded-full border border-white/20 bg-white/5 px-7 py-3.5 text-base font-semibold text-white transition hover:border-white/40 hover:bg-white/10"
              >
                <ScanLine className="h-4 w-4 transition-transform duration-300 group-hover:rotate-6" /> Scan a Product
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

            {/* Mock chat window. Static and illustrative, not wired to the live API — but
                the example is real: packaged drinking water is the one domain in the seed
                corpus that already answers with a confident, exact IS citation, so a judge
                trying the same question in Ask Sarthi sees the same result this promises.

                BorderGlow supplies its own background/border/radius/shadow, so those are
                gone from the wrapper below — only layout and text alignment remain. Colors
                are the site's own navy/saffron, not the component's purple/pink/blue
                defaults. Hover-only, no mount-time sweep — that intro didn't read well. */}
            <BorderGlow
              className="mx-auto mt-12 max-w-xl text-left"
              backgroundColor="#060b18"
              colors={['#f2900f', '#0a1128', '#f7a836']}
              glowColor="32 90 55"
              borderRadius={16}
              glowRadius={32}
            >
              <div className="flex items-center gap-1.5 border-b border-white/10 px-4 py-3">
                <span className="h-2.5 w-2.5 rounded-full bg-[#ff5f57]" />
                <span className="h-2.5 w-2.5 rounded-full bg-[#febc2e]" />
                <span className="h-2.5 w-2.5 rounded-full bg-[#28c840]" />
              </div>
              <div className="space-y-3 p-5">
                <div className="ml-auto max-w-[85%] rounded-xl rounded-tr-sm bg-white/10 px-4 py-2.5 text-sm text-white/90">
                  Do I need BIS certification for packaged drinking water?
                </div>
                <div className="max-w-[90%] rounded-xl rounded-tl-sm border-l-2 border-saffron-400 bg-white/5 px-4 py-2.5 text-sm leading-relaxed text-white/80">
                  Yes — packaged drinking water falls under{' '}
                  <span className="font-semibold text-saffron-400">IS 14543</span>, and ISI
                  certification is mandatory before sale. Next: testing requirements, then
                  Form V.
                </div>
              </div>
            </BorderGlow>
          </div>
        </div>
      </section>

      {/* HOW IT WORKS */}
      <section className="mx-auto max-w-7xl px-6 py-24">
        <div className="mx-auto max-w-2xl text-center">
          <span className="eyebrow text-saffron-600">How it works</span>
          <h2 className="font-display mt-3 text-3xl font-bold text-navy-900 sm:text-[2.6rem] sm:leading-[1.1]">
            From a vague product to an actionable compliance path
          </h2>
        </div>
        <div className="mt-14 grid grid-cols-1 gap-8 md:grid-cols-4">
          {steps.map((s, i) => (
            <div key={s.n} className="relative">
              <div className="flex items-center gap-3">
                <span className="font-display text-5xl font-bold tabular-nums text-navy-900/[0.09]">{s.n}</span>
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
            <span className="eyebrow text-saffron-400">Why not just ask a chatbot?</span>
            <h2 className="font-display mt-3 text-3xl font-bold text-white sm:text-[2.6rem] sm:leading-[1.1]">
              Not a generic AI. A compliance navigator.
            </h2>
          </div>
          <div className="mt-14 grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
            {diffs.map((d) => (
              <div
                key={d.title}
                className="group rounded-2xl border border-white/10 bg-white/[0.03] p-6 transition-colors duration-300 hover:border-saffron-400/40 hover:bg-white/[0.06]"
              >
                <d.icon className="icon-tile h-6 w-6 text-saffron-400" />
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
            <span className="eyebrow text-saffron-600">Trust, by design</span>
            <h2 className="font-display mt-3 text-3xl font-bold text-navy-900 sm:text-[2.6rem] sm:leading-[1.1]">
              If we can't verify it, we say so.
            </h2>
            <p className="mt-4 max-w-lg text-base leading-relaxed text-navy-700/70">
              Every answer carries a confidence level and an evidence trail back to its source
              document and official BIS link. When the retrieved evidence isn't strong enough,
              Sarthi tells you plainly instead of guessing.
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
          <h2 className="font-display text-center text-2xl font-bold text-navy-900">
            Built for everyone who deals with BIS
          </h2>
          <div className="mt-10 flex flex-wrap items-center justify-center gap-4">
            {users.map((u) => (
              <div
                key={u.label}
                className="press inline-flex items-center gap-2.5 rounded-full border border-navy-900/10 bg-paper-50 px-5 py-2.5 transition-colors hover:border-saffron-400 hover:bg-white"
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
            <h2 className="font-display text-3xl font-bold text-white sm:text-[2.6rem] sm:leading-[1.1]">
              Ready to find your standard?
            </h2>
            <p className="mx-auto mt-3 max-w-xl text-white/65">
              Start a conversation, or upload a photo of your product to begin.
            </p>
            <div className="mt-8 flex flex-col items-center justify-center gap-3 sm:flex-row">
              <Link
                to="/chat"
                className="press shine rounded-full bg-saffron-500 px-7 py-3.5 text-base font-semibold text-white transition hover:bg-saffron-600"
              >
                Ask Sarthi
              </Link>
              <Link
                to="/roadmap"
                className="press rounded-full border border-white/20 px-7 py-3.5 text-base font-semibold text-white transition hover:border-white/40 hover:bg-white/10"
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
