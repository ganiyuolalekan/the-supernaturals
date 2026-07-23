import { useState, useEffect } from 'react'
import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export default function Admin() {
  const [username, setUsername] = useState('admin')
  const [password, setPassword] = useState('')
  const [authed, setAuthed] = useState(false)
  const [submissions, setSubmissions] = useState([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const fetchSubmissions = async (pass) => {
    setLoading(true)
    setError(null)
    try {
      const { data } = await axios.get(`${API_URL}/submissions`, {
        auth: { username: 'admin', password: pass || password },
      })
      setSubmissions(data.submissions)
      setTotal(data.total)
      setAuthed(true)
    } catch (err) {
      if (err.response?.status === 401) {
        setError('Incorrect password.')
        setAuthed(false)
      } else {
        setError('Failed to load submissions.')
      }
    } finally {
      setLoading(false)
    }
  }

  const handleLogin = (e) => {
    e.preventDefault()
    fetchSubmissions(password)
  }

  const handleDelete = async (id) => {
    if (!confirm('Delete this submission?')) return
    try {
      await axios.delete(`${API_URL}/submissions/${id}`, {
        auth: { username: 'admin', password },
      })
      setSubmissions((prev) => prev.filter((s) => s.id !== id))
      setTotal((t) => t - 1)
    } catch {
      alert('Delete failed.')
    }
  }

  if (!authed) {
    return (
      <div className="min-h-dvh flex items-center justify-center px-4">
        <div className="w-full max-w-sm">
          <h1 className="font-display text-2xl font-bold text-white mb-6 text-center">Admin Dashboard</h1>
          <form onSubmit={handleLogin} className="flex flex-col gap-4">
            <input
              type="password"
              placeholder="Admin password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-4 py-3 bg-cosmic-800 border border-slate-700 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:border-divine-500"
            />
            {error && <p className="text-red-400 text-sm">{error}</p>}
            <button
              type="submit"
              disabled={loading}
              className="py-3 bg-divine-500 text-cosmic-950 font-bold rounded-xl"
            >
              {loading ? 'Checking…' : 'Login'}
            </button>
          </form>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-dvh px-4 py-8 max-w-6xl mx-auto">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="font-display text-2xl font-bold text-white">Admin Dashboard</h1>
          <p className="text-slate-400 text-sm mt-1">{total} submission{total !== 1 ? 's' : ''}</p>
        </div>
        <button
          onClick={() => fetchSubmissions()}
          className="px-4 py-2 border border-slate-600 text-slate-300 hover:text-white rounded-lg text-sm transition-colors"
        >
          Refresh
        </button>
      </div>

      {loading && <p className="text-slate-400 text-center py-12">Loading…</p>}
      {error && <p className="text-red-400 text-center py-12">{error}</p>}

      {!loading && submissions.length === 0 && (
        <p className="text-slate-500 text-center py-12">No submissions yet.</p>
      )}

      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
        {submissions.map((s) => (
          <div key={s.id} className="bg-cosmic-800 rounded-xl overflow-hidden border border-slate-700/50">
            <img
              src={s.generated_url}
              alt={s.name}
              className="w-full aspect-square object-cover"
              loading="lazy"
            />
            <div className="p-2">
              <p className="text-white text-sm font-semibold truncate">{s.name}</p>
              <p className="text-slate-500 text-xs">{new Date(s.created_at).toLocaleDateString()}</p>
              <div className="flex gap-1 mt-2">
                <a
                  href={s.generated_url}
                  target="_blank"
                  rel="noreferrer"
                  className="flex-1 text-center py-1 text-xs text-divine-500 border border-divine-500/30 rounded-lg hover:bg-divine-500/10 transition-colors"
                >
                  View
                </a>
                <button
                  onClick={() => handleDelete(s.id)}
                  className="flex-1 py-1 text-xs text-red-400 border border-red-800/40 rounded-lg hover:bg-red-900/20 transition-colors"
                >
                  Delete
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
