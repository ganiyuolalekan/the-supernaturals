import { useEffect, useMemo, useState } from 'react'
import Shell from './Shell'
import { DAYS, call, errorMessage } from './api'

function csvCell(v) {
  const s = String(v ?? '')
  return /[",\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s
}

function FirstTimersBody() {
  const [people, setPeople] = useState(null)
  const [error, setError] = useState(null)
  const [q, setQ] = useState('')

  useEffect(() => {
    call('get', '/first-timers').then((r) => setPeople(r.people)).catch((e) => setError(errorMessage(e)))
  }, [])

  const shown = useMemo(() => {
    const needle = q.trim().toLowerCase()
    return (people || []).filter((p) => !needle || p.name.toLowerCase().includes(needle) || p.phone.includes(needle))
  }, [people, q])

  const daysOf = (p) => DAYS.filter((d) => p.attended[d.id]).map((d) => d.short).join(', ') || '—'

  const download = () => {
    const head = ['Name', 'Phone', 'Gender', 'Age group', 'Church', 'Days attended']
    const lines = [head, ...shown.map((p) => [p.name, p.phone, p.gender, p.age_group, p.church, daysOf(p)])]
    const blob = new Blob([lines.map((l) => l.map(csvCell).join(',')).join('\n')], { type: 'text/csv' })
    const a = document.createElement('a')
    a.href = URL.createObjectURL(blob)
    a.download = 'first-timers.csv'
    a.click()
    URL.revokeObjectURL(a.href)
  }

  return (
    <>
      {error && <p className="text-sm text-red-600">{error}</p>}
      {!people && !error && <p className="text-slate-500 text-sm">Loading…</p>}
      {people && (
        <>
          <div className="flex items-center justify-between gap-3">
            <p className="text-sm text-slate-600">
              <span className="text-slate-900 font-semibold">{people.length}</span> first-timer{people.length === 1 ? '' : 's'} to reach out to
            </p>
            <button onClick={download} disabled={!shown.length}
              className="px-3 py-2 text-xs font-bold rounded-lg bg-divine-500 text-cosmic-950 disabled:bg-slate-200 disabled:text-slate-500">
              Download CSV
            </button>
          </div>
          <input
            type="search" value={q} onChange={(e) => setQ(e.target.value)} placeholder="Filter by name or number…"
            className="mt-3 w-full px-4 py-3 bg-white border border-slate-300 rounded-xl text-slate-900 placeholder-slate-400 text-sm focus:outline-none focus:border-divine-500"
          />
          {people.length === 0 && (
            <p className="mt-6 text-center text-slate-500 text-sm">No first-timers ticked yet. They appear here as agents tick the box at the door.</p>
          )}
          <ul className="mt-4 grid gap-3 sm:grid-cols-2 xl:grid-cols-3 items-start">
            {shown.map((p) => (
              <li key={p.row} className="rounded-2xl border border-slate-200 bg-white shadow-sm p-4">
                <div className="flex items-start justify-between gap-3">
                  <div className="min-w-0">
                    <p className="font-semibold text-slate-900 break-words">{p.name}</p>
                    <p className="text-xs text-slate-500 mt-0.5">{[p.gender, p.age_group].filter(Boolean).join(' · ')}</p>
                    <p className="text-xs mt-1 text-slate-600">{p.home_church ? '★ ' : ''}{p.church || 'No church given'}</p>
                    <p className="text-xs mt-1 text-slate-500">Attended: {daysOf(p)}</p>
                  </div>
                  <div className="text-right shrink-0">
                    <a href={`tel:${p.phone}`} className="font-mono text-sm text-amber-700">{p.phone}</a>
                    {p.whatsapp && (
                      <a href={p.whatsapp} target="_blank" rel="noreferrer"
                        className="block mt-2 text-xs font-semibold text-emerald-700 underline">WhatsApp</a>
                    )}
                  </div>
                </div>
              </li>
            ))}
          </ul>
        </>
      )}
    </>
  )
}

export default function FirstTimers() {
  return (
    <Shell title="First-timers">
      <FirstTimersBody />
    </Shell>
  )
}
