import { useState } from 'react'
import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// Password modal for the hidden owner route. On success it hands the verified
// key up to App, which flips Upload into unlocked mode. The key lives only in
// memory — nothing is persisted, so a reload re-prompts.
export default function VaultGate({ onUnlock }) {
  const [key, setKey] = useState('')
  const [error, setError] = useState(null)
  const [checking, setChecking] = useState(false)

  const submit = async (e) => {
    e.preventDefault()
    if (!key.trim()) return
    setChecking(true)
    setError(null)
    try {
      const form = new FormData()
      form.append('key', key.trim())
      await axios.post(`${API_URL}/vault/unlock`, form)
      onUnlock(key.trim())
    } catch {
      setError('Wrong key.')
      setChecking(false)
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-cosmic-950/95 backdrop-blur-sm px-6">
      <form
        onSubmit={submit}
        className="w-full max-w-sm rounded-2xl border border-slate-700/70 bg-cosmic-800/90 p-6 shadow-2xl"
      >
        <div className="mb-5 text-center">
          <div className="text-4xl mb-2">🔑</div>
          <p className="text-divine-500 text-xs tracking-widest uppercase font-semibold">The SuperNaturals</p>
          <h2 className="font-display text-2xl font-bold text-white mt-1">Enter the key</h2>
        </div>

        <input
          type="password"
          value={key}
          autoFocus
          autoComplete="off"
          onChange={(e) => setKey(e.target.value)}
          placeholder="Key"
          className="w-full px-4 py-3 bg-cosmic-900 border border-slate-700 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:border-divine-500 focus:ring-1 focus:ring-divine-500 transition-colors text-sm"
        />

        {error && (
          <p className="mt-3 text-sm text-red-400">{error}</p>
        )}

        <button
          type="submit"
          disabled={checking || !key.trim()}
          className="mt-5 w-full py-3 bg-divine-500 hover:bg-divine-400 disabled:bg-slate-700 disabled:cursor-not-allowed text-cosmic-950 disabled:text-slate-400 font-bold text-sm rounded-xl transition-all duration-200"
        >
          {checking ? 'Checking…' : 'Unlock'}
        </button>
      </form>
    </div>
  )
}
