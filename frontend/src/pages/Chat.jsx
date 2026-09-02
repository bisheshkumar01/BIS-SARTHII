import { useEffect, useRef, useState } from 'react'
import {
  Send,
  ShieldCheck,
  Sparkles,
  Loader2,
  ThumbsUp,
  ThumbsDown,
  ArrowRight,
} from 'lucide-react'
import { ConfidenceDot, Evidence, Warnings } from '../components/Evidence.jsx'
import {
  describeError,
  fetchHistory,
  getSessionId,
  sendChat,
  sendFeedback,
} from '../lib/api.js'

const suggestions = [
  'I manufacture stainless steel water bottles — which standard applies?',
  'Do I need BIS certification for LED bulbs?',
  'Which form do I need for ISI licensing?',
  'क्या पैकेज्ड पेयजल के लिए BIS प्रमाणन अनिवार्य है?',
]

const GREETING = {
  role: 'assistant',
  greeting: true,
  answer:
    "Hi, I'm Sarthi — your BIS compliance guide. Describe your product, or ask about a standard, certification, or form to get started.",
}

export default function Chat() {
  const [messages, setMessages] = useState([GREETING])
  const [input, setInput] = useState('')
  const [busy, setBusy] = useState(false)
  const [language, setLanguage] = useState('en')
  const sessionId = useRef(getSessionId())
  const bottom = useRef(null)
  const inputRef = useRef(null)

  // Replay the stored conversation so a refresh doesn't lose the thread.
  useEffect(() => {
    let cancelled = false
    fetchHistory(sessionId.current)
      .then((rows) => {
        if (cancelled || !rows.length) return
        setMessages([
          GREETING,
          ...rows.map((m) => ({
            role: m.role,
            answer: m.content,
            message_id: m.message_id,
            confidence: m.confidence,
            citations: m.citations ?? [],
          })),
        ])
      })
      .catch(() => {
        /* No history is a normal first visit, and a dead backend surfaces on first send. */
      })
    return () => {
      cancelled = true
    }
  }, [])

  useEffect(() => {
    bottom.current?.scrollIntoView({ behavior: 'smooth', block: 'end' })
  }, [messages, busy])

  async function handleSend(text) {
    const value = (text ?? input).trim()
    if (!value || busy) return

    setMessages((m) => [...m, { role: 'user', answer: value }])
    setInput('')
    setBusy(true)

    try {
      const res = await sendChat({ sessionId: sessionId.current, message: value, language })
      setMessages((m) => [...m, { role: 'assistant', ...res }])
    } catch (err) {
      setMessages((m) => [
        ...m,
        { role: 'assistant', answer: describeError(err), error: true },
      ])
    } finally {
      setBusy(false)
      inputRef.current?.focus()
    }
  }

  return (
    <div className="mx-auto flex h-[calc(100vh-4rem)] max-w-5xl flex-col px-6">
      <div className="flex-1 overflow-y-auto py-8">
        <div className="mb-6 flex items-center justify-between gap-3">
          <div className="flex items-center gap-1.5 text-[11px] font-medium text-navy-700/45">
            <ShieldCheck className="h-3.5 w-3.5 text-verified-600" />
            Answers are grounded in official BIS sources
          </div>
          <button
            type="button"
            onClick={() => setLanguage((l) => (l === 'en' ? 'hi' : 'en'))}
            className="press rounded-full border border-navy-900/10 px-3 py-1 text-xs font-semibold text-navy-700 hover:bg-navy-900/5"
            title="Answer language"
          >
            {language === 'en' ? 'EN' : 'हिं'}
          </button>
        </div>

        <div className="space-y-4">
          {messages.map((m, i) => (
            <Message key={m.message_id ?? i} m={m} />
          ))}

          {busy && (
            <div className="animate-pop flex justify-start">
              <div className="card flex items-center gap-2 border-navy-900/5 px-4 py-3 text-sm text-navy-700/60">
                <Loader2 className="h-4 w-4 animate-spin text-saffron-500" />
                Searching BIS sources…
              </div>
            </div>
          )}
        </div>

        {messages.length === 1 && !busy && (
          <div className="mt-8">
            <p className="mb-3 flex items-center gap-1.5 text-[11px] font-medium text-navy-700/45">
              <Sparkles className="h-3.5 w-3.5" /> Try asking
            </p>
            <div className="flex flex-wrap gap-2">
              {suggestions.map((s, i) => (
                <button
                  key={s}
                  onClick={() => handleSend(s)}
                  style={{ '--delay': `${i * 60}ms` }}
                  className="press animate-rise rounded-full border border-navy-900/10 bg-white px-4 py-2 text-xs font-medium text-navy-700 transition hover:-translate-y-0.5 hover:border-saffron-400 hover:shadow-md hover:shadow-navy-900/5 hover:text-saffron-600"
                >
                  {s}
                </button>
              ))}
            </div>
          </div>
        )}

        <div ref={bottom} />
      </div>

      <form
        onSubmit={(e) => {
          e.preventDefault()
          handleSend()
        }}
        className="sticky bottom-0 mb-6 flex items-center gap-2 rounded-2xl border border-navy-900/10 bg-white p-2 shadow-lg shadow-navy-900/5 transition-all duration-300 focus-within:border-saffron-400 focus-within:shadow-xl focus-within:shadow-saffron-500/10"
      >
        <input
          ref={inputRef}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          disabled={busy}
          placeholder="Ask about a standard, certification, or form…"
          className="flex-1 bg-transparent px-3 py-2 text-sm text-navy-900 outline-none placeholder:text-navy-700/40 disabled:opacity-50"
        />
        <button
          type="submit"
          disabled={busy || !input.trim()}
          className="press inline-flex h-10 w-10 items-center justify-center rounded-xl bg-saffron-500 text-white transition hover:bg-saffron-600 disabled:cursor-not-allowed disabled:opacity-40"
        >
          {busy ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
        </button>
      </form>
    </div>
  )
}

function Message({ m }) {
  if (m.role === 'user') {
    return (
      <div className="animate-rise flex justify-end">
        <div className="max-w-lg rounded-2xl rounded-br-md bg-navy-900 px-4 py-2.5 text-sm leading-relaxed text-white">
          {m.answer}
        </div>
      </div>
    )
  }

  // Metadata belongs together in one quiet footer, not stacked as four competing rows.
  const hasMeta = !m.greeting && !m.error && (m.confidence || m.citations?.length || m.message_id)

  return (
    <div className="animate-rise flex justify-start gap-2.5">
      {/* A small mark so the reply reads as coming from Sarthi rather than floating free. */}
      <span className="mt-0.5 inline-flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-navy-900 text-white">
        <ShieldCheck className="h-3.5 w-3.5 text-saffron-400" />
      </span>

      <div
        className={`max-w-2xl rounded-2xl rounded-tl-md px-4 py-3 ${
          m.error
            ? 'border border-saffron-400/40 bg-saffron-100 text-navy-800'
            : 'card border-navy-900/5 text-navy-800'
        }`}
      >
        <div className="whitespace-pre-wrap text-sm leading-[1.65]">{m.answer}</div>

        {m.next_steps?.length > 0 && (
          <div className="mt-3 rounded-xl bg-paper-100/70 p-3">
            <p className="mb-1.5 text-[11px] font-semibold text-navy-700/60">Next steps</p>
            <ul className="space-y-1.5">
              {m.next_steps.map((s, i) => (
                <li key={i} className="flex gap-2 text-xs leading-relaxed text-navy-800">
                  <ArrowRight className="mt-0.5 h-3 w-3 shrink-0 text-saffron-500" />
                  <span>{s}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {hasMeta && (
          <div className="mt-3 flex flex-wrap items-center gap-x-3 gap-y-2 border-t border-navy-900/5 pt-2.5">
            {m.confidence && <ConfidenceDot level={m.confidence} />}
            {m.confidence && m.citations?.length > 0 && (
              <span className="h-3 w-px bg-navy-900/10" />
            )}
            <Evidence citations={m.citations} />
            {m.message_id && (
              <div className="ml-auto">
                <FeedbackButtons messageId={m.message_id} />
              </div>
            )}
          </div>
        )}

        <Warnings items={m.warnings} />
      </div>
    </div>
  )
}

function FeedbackButtons({ messageId }) {
  const [sent, setSent] = useState(null)

  function submit(isHelpful) {
    if (sent) return
    setSent(isHelpful ? 'up' : 'down') // optimistic: a failed vote isn't worth a UI error
    sendFeedback({ messageId, isHelpful }).catch(() => {})
  }

  if (sent) {
    return <span className="text-[11px] text-navy-700/40">Thanks</span>
  }

  return (
    <div className="flex items-center gap-0.5">
      <button
        type="button"
        onClick={() => submit(true)}
        className="rounded-md p-1 text-navy-700/30 transition-colors hover:bg-verified-100 hover:text-verified-600"
        aria-label="Helpful"
        title="Helpful"
      >
        <ThumbsUp className="h-3.5 w-3.5" />
      </button>
      <button
        type="button"
        onClick={() => submit(false)}
        className="rounded-md p-1 text-navy-700/30 transition-colors hover:bg-saffron-100 hover:text-saffron-600"
        aria-label="Not helpful"
        title="Not helpful"
      >
        <ThumbsDown className="h-3.5 w-3.5" />
      </button>
    </div>
  )
}
