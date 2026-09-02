import axios from 'axios'

// Dev goes through the Vite proxy (see vite.config.js) so there is no CORS hop.
// In production the API lives elsewhere, so VITE_API_BASE_URL points at it.
const baseURL = import.meta.env.VITE_API_BASE_URL || '/api'

export const api = axios.create({ baseURL, timeout: 60000 })

/** Stable per-browser id so a refresh keeps the same conversation. */
export function getSessionId() {
  const KEY = 'bis-sarthi-session'
  let id = null
  try {
    id = localStorage.getItem(KEY)
  } catch {
    // Private mode or blocked storage — fall through to an in-memory id.
  }
  if (!id) {
    id = (crypto.randomUUID?.() ?? `s-${Date.now()}-${Math.random().toString(36).slice(2)}`)
    try {
      localStorage.setItem(KEY, id)
    } catch {
      /* not fatal: the session just won't survive a reload */
    }
  }
  return id
}

export async function sendChat({ sessionId, message, language }) {
  const { data } = await api.post('/chat', {
    session_id: sessionId,
    message,
    language,
  })
  return data
}

export async function fetchHistory(sessionId) {
  const { data } = await api.get(`/chat/${sessionId}/history`)
  return data.messages ?? []
}

export async function sendFeedback({ messageId, isHelpful, reason }) {
  await api.post('/feedback', {
    message_id: messageId,
    is_helpful: isHelpful,
    reason: reason ?? null,
  })
}

/** Turn an axios failure into something worth showing a user. */
export function describeError(err) {
  if (err?.response?.status === 429) {
    return 'Too many questions in a short time. Wait a moment and try again.'
  }
  if (err?.code === 'ECONNABORTED') {
    return 'That took too long. Try asking again, or rephrase it more specifically.'
  }
  if (!err?.response) {
    return 'Could not reach the Sarthi backend. Is it running on port 8000?'
  }
  return err.response.data?.detail || 'Something went wrong answering that question.'
}
