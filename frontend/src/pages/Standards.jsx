import { useEffect, useState } from 'react'
import {
  Search,
  ShieldCheck,
  ExternalLink,
  Loader2,
} from 'lucide-react'
import { useLocation } from 'react-router-dom'

export default function Standards() {
  const location = useLocation()

  const [query, setQuery] = useState('')
  const [matches, setMatches] = useState([])
  const [explanation, setExplanation] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  // ============================================================
  // RECEIVE OCR TEXT FROM SCAN PAGE
  // ============================================================

  useEffect(() => {
    const detectedText = location.state?.detectedText

    if (detectedText?.length) {
      const text = detectedText.join(' ')

      setQuery(text)

      findStandards(text)
    }
  }, [])


  // ============================================================
  // SEARCH BIS STANDARDS
  // ============================================================

  async function findStandards(searchQuery = query) {
    const value = searchQuery.trim()

    if (!value) {
      setError('Please describe your product first.')
      return
    }

    setLoading(true)
    setError('')
    setMatches([])
    setExplanation('')

    try {
      const response = await fetch('/api/standards', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: value,
        }),
      })

      if (!response.ok) {
        throw new Error('Standards search failed')
      }

      const data = await response.json()

      console.log('Standards response:', data)

      setMatches(data.matches || [])
      setExplanation(data.explanation || '')

      if (data.error) {
        setError(data.error)
      }

    } catch (err) {
      console.error('Standards error:', err)

      setError(
        'Unable to find standards. Make sure FastAPI is running on port 8000.'
      )

    } finally {
      setLoading(false)
    }
  }


  // ============================================================
  // UI
  // ============================================================

  return (
    <div className="mx-auto max-w-4xl px-6 py-14">

      {/* ======================================================
          HEADER
      ====================================================== */}

      <div>

        <h1 className="font-display text-3xl font-bold text-navy-900">
          Find your standard
        </h1>

        <p className="mt-2 text-navy-700/65">
          Describe your product — material, use, and any specifications you have.
        </p>

      </div>


      {/* ======================================================
          SEARCH BAR
      ====================================================== */}

      <div className="mt-6 flex items-center gap-2 rounded-2xl border border-navy-900/10 bg-white p-2 shadow-sm">

        <Search className="ml-2 h-4 w-4 shrink-0 text-navy-700/40" />

        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && !loading) {
              findStandards()
            }
          }}
          placeholder="e.g. 1L stainless steel water bottle, food-grade"
          className="flex-1 bg-transparent px-2 py-2.5 text-sm text-navy-900 outline-none placeholder:text-navy-700/40"
        />

        <button
          type="button"
          onClick={() => findStandards()}
          disabled={loading || !query.trim()}
          className="rounded-full bg-navy-900 px-5 py-2 text-sm font-semibold text-white transition hover:bg-navy-800 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {loading ? 'Searching...' : 'Match'}
        </button>

      </div>


      {/* ======================================================
          ERROR
      ====================================================== */}

      {error && (
        <div className="mt-4 rounded-xl border border-red-200 bg-red-50 px-4 py-3">

          <p className="text-sm font-medium text-red-600">
            {error}
          </p>

        </div>
      )}


      {/* ======================================================
          GEMINI ANALYSIS
      ====================================================== */}

      {explanation && !loading && (
        <div className="mt-6 rounded-2xl border border-verified-600/10 bg-verified-100/40 p-5">

          <div className="flex items-center gap-2">

            <span className="inline-flex h-7 w-7 items-center justify-center rounded-full bg-verified-100">

              <ShieldCheck className="h-4 w-4 text-verified-600" />

            </span>

            <div>

              <h2 className="text-sm font-bold text-navy-900">
                Sarthi's analysis
              </h2>

              <p className="text-[11px] text-navy-700/50">
                Based on retrieved BIS document context
              </p>

            </div>

          </div>


          <div className="mt-4 whitespace-pre-wrap text-sm leading-[1.7] text-navy-800">
            {explanation}
          </div>

        </div>
      )}


      {/* ======================================================
          RESULTS
      ====================================================== */}

      <div className="mt-8 space-y-4">

        <div className="flex items-center justify-between">

          <p className="text-xs font-semibold uppercase tracking-wide text-navy-700/50">
            Potentially applicable standards
          </p>

          {matches.length > 0 && (
            <span className="text-xs text-navy-700/40">
              {matches.length} result{matches.length !== 1 ? 's' : ''}
            </span>
          )}

        </div>


        {/* ==================================================
            LOADING
        ================================================== */}

        {loading && (
          <div className="card flex items-center gap-3 p-5">

            <Loader2 className="h-5 w-5 animate-spin text-saffron-500" />

            <div>

              <p className="text-sm font-semibold text-navy-900">
                Searching BIS documents...
              </p>

              <p className="mt-0.5 text-xs text-navy-700/50">
                Finding relevant standards for your product.
              </p>

            </div>

          </div>
        )}


        {/* ==================================================
            NO RESULTS / BEFORE SEARCH
        ================================================== */}

        {!loading && matches.length === 0 && !error && (
          <div className="card p-6 text-center">

            <Search className="mx-auto h-8 w-8 text-navy-700/20" />

            <p className="mt-3 text-sm font-medium text-navy-700/60">
              No standards searched yet.
            </p>

            <p className="mt-1 text-xs text-navy-700/40">
              Enter a product description above to find relevant BIS standards.
            </p>

          </div>
        )}


        {/* ==================================================
            STANDARD CARDS
        ================================================== */}

        {!loading &&
          matches.map((m, index) => (

            <div
              key={`${m.isNumber || m.title || 'standard'}-${index}`}
              className="card card-hover animate-rise p-5"
              style={{
                '--delay': `${index * 60}ms`,
              }}
            >

              {/* --------------------------------------------
                  TITLE + SCORE
              --------------------------------------------- */}

              <div className="flex items-start justify-between gap-4">

                <div className="min-w-0">

                  <p className="text-base font-bold text-navy-900">
                    {m.isNumber || 'BIS Standard'}
                  </p>

                  <p className="mt-1 text-sm leading-relaxed text-navy-700/70">
                    {m.title || 'Relevant BIS document'}
                  </p>

                </div>


                {/* MATCH SCORE */}

                <div className="flex shrink-0 flex-col items-end">

                  <span className="text-lg font-bold tabular-nums text-saffron-600">
                    {typeof m.score === 'number'
                      ? `${m.score}%`
                      : '—'}
                  </span>

                  <span className="text-[10px] uppercase tracking-wide text-navy-700/40">
                    match
                  </span>

                </div>

              </div>


              {/* --------------------------------------------
                  SCHEME
              --------------------------------------------- */}

              {m.scheme && (
                <span className="mt-3 inline-flex rounded-full bg-verified-100 px-2.5 py-1 text-[11px] font-bold text-verified-600">
                  {m.scheme}
                </span>
              )}


              {/* --------------------------------------------
                  WHY
              --------------------------------------------- */}

              {m.why?.length > 0 && (

                <div className="mt-4">

                  <p className="mb-2 text-xs font-semibold text-navy-900">
                    Why it may apply
                  </p>

                  <ul className="space-y-1.5">

                    {m.why.map((reason, reasonIndex) => (

                      <li
                        key={reasonIndex}
                        className="flex items-start gap-2 text-xs leading-relaxed text-navy-700/65"
                      >

                        <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-navy-700/40" />

                        <span>
                          {reason}
                        </span>

                      </li>

                    ))}

                  </ul>

                </div>

              )}


              {/* --------------------------------------------
                  FOOTER ACTIONS
              --------------------------------------------- */}

              <div className="mt-5 flex flex-wrap items-center gap-4 border-t border-navy-900/5 pt-3">

                {/* WHY STANDARD */}

                <button
                  type="button"
                  onClick={() => {
                    if (explanation) {
                      window.scrollTo({
                        top: 0,
                        behavior: 'smooth',
                      })
                    }
                  }}
                  className="inline-flex items-center gap-1.5 text-xs font-semibold text-saffron-600 transition hover:underline"
                >

                  <ShieldCheck className="h-3.5 w-3.5" />

                  Why this standard?

                </button>


                {/* OFFICIAL SOURCE */}

                {m.url ? (

                  <a
                    href={m.url}
                    target="_blank"
                    rel="noreferrer"
                    className="inline-flex items-center gap-1.5 text-xs font-semibold text-navy-700 transition hover:underline"
                  >

                    Official source

                    <ExternalLink className="h-3 w-3" />

                  </a>

                ) : (

                  <span className="inline-flex items-center gap-1.5 text-xs text-navy-700/35">

                    Official source unavailable

                  </span>

                )}

              </div>

            </div>

          ))}

      </div>


      {/* ======================================================
          DISCLAIMER
      ====================================================== */}

      {!loading && matches.length > 0 && (

        <div className="mt-6 flex items-start gap-2 rounded-xl bg-paper-100 p-4">

          <ShieldCheck className="mt-0.5 h-4 w-4 shrink-0 text-verified-600" />

          <p className="text-xs leading-relaxed text-navy-700/60">
            These are potentially relevant documents retrieved from the BIS
            knowledge base. Always verify the applicable standard and current
            BIS requirements before taking compliance action.
          </p>

        </div>

      )}

    </div>
  )
}