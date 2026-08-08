import { useState, useEffect } from 'react'
import axios from 'axios'
import Landing from './screens/Landing'
import Upload from './screens/Upload'
import Result from './screens/Result'
import ClosedModal from './components/ClosedModal'

const SESSION_KEY = 'supernaturals_session'
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
const STATUS_POLL_MS = 60_000

// Restores screen + result across a tab reload — mobile browsers routinely
// discard a backgrounded tab's JS state (e.g. switching to WhatsApp and back),
// which otherwise drops the user back to Landing and loses their generated image.
function loadSession() {
  try {
    const raw = sessionStorage.getItem(SESSION_KEY)
    if (!raw) return { screen: 'landing', result: null }
    const parsed = JSON.parse(raw)
    // A generated image can only be shown if we actually have the result data
    if (parsed.screen === 'result' && !parsed.result) return { screen: 'landing', result: null }
    return parsed
  } catch {
    return { screen: 'landing', result: null }
  }
}

export default function App() {
  const [{ screen, result }, setState] = useState(loadSession)
  // Service availability lives here rather than in Upload so a closed day can
  // lock every screen, and so there's one poll for the whole app.
  const [status, setStatus] = useState(null)

  useEffect(() => {
    const fetchStatus = () => {
      axios.get(`${API_URL}/status`)
        .then(({ data }) => setStatus(data))
        .catch(() => {
          // Leave the last known status in place — the backend still enforces
          // every gate on /generate and returns the reason there.
        })
    }
    fetchStatus()
    // Poll so the app opens and closes on its own at the day boundary, and
    // recovers once the daily cap resets — without anyone reloading.
    const timer = setInterval(fetchStatus, STATUS_POLL_MS)
    return () => clearInterval(timer)
  }, [])

  useEffect(() => {
    try {
      sessionStorage.setItem(SESSION_KEY, JSON.stringify({ screen, result }))
    } catch {
      // Quota exceeded (result images are base64 data URLs and can be a few
      // MB) — session recovery just won't work for this one, non-fatal.
    }
  }, [screen, result])

  const setScreen = (next) => setState((s) => ({ ...s, screen: next }))
  const setResult = (next) => setState((s) => ({ ...s, result: next }))

  return (
    <div className="min-h-dvh bg-cosmic-950 bg-stars">
      {screen === 'landing' && (
        <Landing onStart={() => setScreen('upload')} />
      )}
      {screen === 'upload' && (
        <Upload
          status={status}
          onStatusChange={setStatus}
          onResult={(data) => { setResult(data); setScreen('result') }}
          onBack={() => setScreen('landing')}
        />
      )}
      {screen === 'result' && result && (
        <Result
          data={result}
          onReset={() => { setResult(null); setScreen('landing') }}
        />
      )}

      {/* Closed day — locks the entire app on top of whatever screen is behind */}
      {status?.closed_today && <ClosedModal status={status} />}
    </div>
  )
}
