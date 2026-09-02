import { useState } from 'react'
import { Send, ShieldCheck, Sparkles } from 'lucide-react'

const suggestions = [
  'I manufacture stainless steel water bottles — which standard applies?',
  'Do I need BIS certification for LED bulbs?',
  'Which form do I need for ISI licensing?',
  'क्या पैकेज्ड पेयजल के लिए BIS प्रमाणन अनिवार्य है?',
]

const seedMessages = [
  { role: 'assistant', text: "Hi, I'm Sarthi — your BIS compliance guide. Describe your product, or ask about a standard, certification, or form to get started." },
]

export default function Chat() {
  const [messages, setMessages] = useState(seedMessages)
  const [input, setInput] = useState('')

  // Placeholder submit — wired to POST /api/chat in the next build step.
  function handleSend(text) {
    const value = text ?? input
    if (!value.trim()) return
    setMessages((m) => [
      ...m,
      { role: 'user', text: value },
      { role: 'assistant', text: "Backend not wired yet — this is a UI preview. Real answers will appear here, with sources.", pending: true },
    ])
    setInput('')
  }

  return (
    <div className="mx-auto flex h-[calc(100vh-4rem)] max-w-5xl flex-col px-6">
      <div className="flex-1 overflow-y-auto py-8">
        <div className="mb-6 flex items-center gap-2 text-xs font-semibold uppercase tracking-wide text-navy-700/50">
          <ShieldCheck className="h-3.5 w-3.5 text-verified-600" /> Answers are grounded in official BIS sources
        </div>

        <div className="space-y-4">
          {messages.map((m, i) => (
            <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div
                className={`max-w-lg rounded-2xl px-4 py-3 text-sm leading-relaxed ${
                  m.role === 'user'
                    ? 'bg-navy-900 text-white'
                    : 'card border-navy-900/5 text-navy-800'
                }`}
              >
                {m.text}
              </div>
            </div>
          ))}
        </div>

        {messages.length === 1 && (
          <div className="mt-8">
            <p className="mb-3 flex items-center gap-1.5 text-xs font-semibold text-navy-700/50">
              <Sparkles className="h-3.5 w-3.5" /> Try asking
            </p>
            <div className="flex flex-wrap gap-2">
              {suggestions.map((s) => (
                <button
                  key={s}
                  onClick={() => handleSend(s)}
                  className="rounded-full border border-navy-900/10 bg-white px-4 py-2 text-xs font-medium text-navy-700 hover:border-saffron-400 hover:text-saffron-600"
                >
                  {s}
                </button>
              ))}
            </div>
          </div>
        )}
      </div>

      <form
        onSubmit={(e) => {
          e.preventDefault()
          handleSend()
        }}
        className="sticky bottom-0 mb-6 flex items-center gap-2 rounded-2xl border border-navy-900/10 bg-white p-2 shadow-lg shadow-navy-900/5"
      >
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask about a standard, certification, or form…"
          className="flex-1 bg-transparent px-3 py-2 text-sm text-navy-900 outline-none placeholder:text-navy-700/40"
        />
        <button
          type="submit"
          className="inline-flex h-10 w-10 items-center justify-center rounded-xl bg-saffron-500 text-white hover:bg-saffron-600"
        >
          <Send className="h-4 w-4" />
        </button>
      </form>
    </div>
  )
}
