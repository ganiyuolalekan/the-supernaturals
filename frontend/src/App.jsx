import { useState, useEffect } from 'react'
import axios from 'axios'
import Landing from './screens/Landing'
import Upload from './screens/Upload'
import Result from './screens/Result'
import ClosedModal from './components/ClosedModal'
import VaultGate from './components/VaultGate'

const SESSION_KEY = 'supernaturals_session'
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
const STATUS_POLL_MS = 60_000

// SHA-256 of the private owner route's URL fragment. The fragment itself is not
// in the code — only this digest — so reading the source doesn't reveal it.
// The route is a normal-looking deep link; entering it just reveals a key modal.
const VAULT_ROUTE_HASH = '7510d8a0b3a05fd52463ed2cf3285372b70c6e8058c6547eeb9baf2c51d2b64c'

async function sha256Hex(str) {
  const buf = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(str))
  return [...new Uint8Array(buf)].map((b) => b.toString(16).padStart(2, '0')).join('')
}

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
  // Hidden owner route: null = not resolved / not the route; false = on the
  // route but not yet unlocked; a string = the verified key (unlocked).
  const [vaultRoute, setVaultRoute] = useState(null)
  const [vaultKey, setVaultKey] = useState(null)

  // Match the URL fragment against the stored digest, on load and whenever it
  // changes. Async because SubtleCrypto is async — until it resolves the app
  // behaves normally.
  useEffect(() => {
    let cancelled = false
    const check = async () => {
      const onRoute = (await sha256Hex(window.location.hash)) === VAULT_ROUTE_HASH
      if (!cancelled) setVaultRoute(onRoute ? false : null)
    }
    check()
    window.addEventListener('hashchange', check)
    return () => { cancelled = true; window.removeEventListener('hashchange', check) }
  }, [])

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

  // Hidden owner route — a self-contained unlocked flow that ignores every
  // campaign gate. Shown only when the URL fragment matched the digest above.
  if (vaultRoute !== null) {
    return (
      <div className="min-h-dvh bg-cosmic-950 bg-stars">
        {!vaultKey && <VaultGate onUnlock={setVaultKey} />}
        {vaultKey && screen !== 'result' && (
          <Upload
            vault={{ key: vaultKey }}
            onResult={(data) => { setResult(data); setScreen('result') }}
            onBack={() => { setResult(null); setScreen('upload') }}
          />
        )}
        {vaultKey && screen === 'result' && result && (
          <Result
            data={result}
            onReset={() => { setResult(null); setScreen('upload') }}
          />
        )}
      </div>
    )
  }

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
