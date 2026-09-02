import { useState } from 'react'
import { ChevronDown, ExternalLink, Info } from 'lucide-react'

/*
  Confidence is the product's core honesty signal, but signalling it and SHOUTING it are
  different jobs. A filled amber pill in wide-tracked caps outweighs the answer it labels and
  reads as an error banner, which makes an ordinary low-confidence reply look broken.

  So: a 6px dot plus a sentence-case label, sitting in the card's footer with the other
  metadata. Colour still carries the meaning — green when evidence genuinely supports the
  answer, amber when it doesn't — it just no longer competes with the text.
*/
const CONFIDENCE = {
  high: { label: 'High confidence', dot: 'bg-verified-500', text: 'text-verified-600' },
  medium: { label: 'Medium confidence', dot: 'bg-saffron-500', text: 'text-navy-700/60' },
  low: { label: 'Low confidence', dot: 'bg-saffron-400', text: 'text-navy-700/60' },
  unverified: { label: 'Unverified', dot: 'bg-navy-900/25', text: 'text-navy-700/55' },
}

export function ConfidenceDot({ level }) {
  const c = CONFIDENCE[level] ?? CONFIDENCE.unverified
  return (
    <span className={`inline-flex items-center gap-1.5 text-[11px] font-medium ${c.text}`}>
      <span className={`h-1.5 w-1.5 rounded-full ${c.dot}`} />
      {c.label}
    </span>
  )
}

/*
  Warnings were a stacked list of amber triangles — three of them turned every answer into a
  hazard sign. Collapsed to one muted line that expands, so the caveat stays available without
  being the first thing the eye lands on.
*/
export function Warnings({ items }) {
  const [open, setOpen] = useState(false)
  if (!items?.length) return null

  return (
    <div className="mt-2.5">
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        className="inline-flex items-center gap-1.5 text-[11px] text-navy-700/45 transition-colors hover:text-navy-700/70"
        aria-expanded={open}
      >
        <Info className="h-3 w-3" />
        {items.length} note{items.length > 1 ? 's' : ''} on this answer
        <ChevronDown
          className={`h-3 w-3 transition-transform duration-200 ${open ? 'rotate-180' : ''}`}
        />
      </button>

      {open && (
        <ul className="animate-rise mt-2 space-y-1.5 border-l-2 border-saffron-400/40 pl-3">
          {items.map((w, i) => (
            <li key={i} className="text-[11px] leading-relaxed text-navy-700/65">
              {w}
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}

/** The Evidence Panel: every citation is a real retrieved passage with a live BIS link. */
export function Evidence({ citations }) {
  const [open, setOpen] = useState(false)
  if (!citations?.length) return null

  return (
    <>
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        className="inline-flex items-center gap-1.5 text-[11px] font-medium text-verified-600 transition-colors hover:text-verified-500"
        aria-expanded={open}
      >
        {citations.length} source{citations.length > 1 ? 's' : ''}
        <ChevronDown
          className={`h-3 w-3 transition-transform duration-200 ${open ? 'rotate-180' : ''}`}
        />
      </button>

      {open && (
        <div className="animate-rise mt-3 w-full space-y-2">
          {citations.map((c, i) => (
            <div
              key={c.chunk_id}
              style={{ '--delay': `${i * 50}ms` }}
              className="animate-rise rounded-xl border border-navy-900/5 bg-paper-100/70 p-3"
            >
              <div className="flex items-start justify-between gap-3">
                <div className="min-w-0">
                  <p className="text-xs font-semibold leading-snug text-navy-900">
                    {c.document_title}
                  </p>
                  {c.heading && (
                    <p className="mt-0.5 text-[11px] text-navy-700/50">{c.heading}</p>
                  )}
                </div>
                <span
                  className="shrink-0 rounded-full bg-white px-2 py-0.5 text-[10px] font-semibold tabular-nums text-navy-700/55"
                  title="Retrieval relevance"
                >
                  {(c.score * 100).toFixed(0)}%
                </span>
              </div>

              <p className="mt-2 border-l-2 border-verified-500/30 pl-2.5 text-[11px] leading-relaxed text-navy-800/75">
                {c.snippet}
              </p>

              <a
                href={c.source_url}
                target="_blank"
                rel="noopener noreferrer"
                className="mt-2 inline-flex items-center gap-1 text-[11px] font-medium text-saffron-600 transition-colors hover:text-saffron-500"
              >
                Open official source <ExternalLink className="h-2.5 w-2.5" />
              </a>
            </div>
          ))}
        </div>
      )}
    </>
  )
}
