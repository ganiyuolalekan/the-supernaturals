import { useState, useEffect } from 'react'
import Landing from './screens/Landing'
import Upload from './screens/Upload'
import Result from './screens/Result'

const SESSION_KEY = 'supernaturals_session'

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
    </div>
  )
}
