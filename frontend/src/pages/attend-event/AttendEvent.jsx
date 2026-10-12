import { useEffect, useRef, useState } from 'react'
import Shell from './Shell'
import { DAYS, call, defaultDay, errorMessage } from './api'

function PersonCard({ person, day, onChange }) {
  const [phone, setPhone] = useState('')
  const [firstTimer, setFirstTimer] = useState(person.first_timer)
  const [unverified, setUnverified] = useState(!person.phone_on_file)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState(null)

  const run = async (fn) => {
    setBusy(true)
    setError(null)
    try { await fn() } catch (err) { setError(errorMessage(err)) } finally { setBusy(false) }
  }

  const checkIn = () => run(async () => {
    const res = await call('post', '/check-in', {
      data: { row: person.row, day, phone, unverified, first_timer: firstTimer },
    })
    onChange(res.person)
  })
  const undo = () => run(async () => {
    const res = await call('post', '/undo', { data: { row: person.row, day } })
    setPhone('')
    onChange(res.person)
  })

  const ready = unverified || phone.replace(/\D/g, '').length >= 4
  const time = person.attended[day]

  return (
    <li className={`rounded-2xl border p-4 ${person.checked_in ? 'border-emerald-600/60 bg-emerald-950/30' : 'border-slate-700/70 bg-cosmic-800/70'}`}>
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <p className="font-semibold text-white break-words">{person.name}</p>
          <p className="text-xs text-slate-400 mt-0.5">
            {[person.gender, person.age_group].filter(Boolean).join(' · ')}
          </p>
          <p className="text-xs mt-1">
            <span className={person.home_church ? 'text-divine-400 font-semibold' : 'text-slate-300'}>
              {person.home_church ? '★ ' : ''}{person.church || 'No church given'}
            </span>
          </p>
        </div>
        <p className="font-mono text-sm text-slate-300 shrink-0">{person.phone_masked || 'no number'}</p>
      </div>

      {person.checked_in ? (
        <div className="mt-3 flex items-center justify-between gap-3">
          <p className="text-sm text-emerald-400 font-semibold">
            ✓ Registered {time}{person.first_timer ? ' · First-timer' : ''}
          </p>
          <button onClick={undo} disabled={busy} className="text-xs text-slate-400 underline disabled:opacity-50">
            Undo
          </button>
        </div>
      ) : (
        <div className="mt-3 space-y-3">
          {!unverified && (
            <input
              type="tel" inputMode="numeric" value={phone} onChange={(e) => setPhone(e.target.value)}
              placeholder="Their number (or last 4 digits)"
              className="w-full px-3 py-2.5 bg-cosmic-900 border border-slate-700 rounded-xl text-white placeholder-slate-500 text-sm focus:outline-none focus:border-divine-500"
            />
          )}
          <label className="flex items-center gap-2 text-sm text-slate-200">
            <input
              type="checkbox" checked={firstTimer} onChange={(e) => setFirstTimer(e.target.checked)}
              className="h-5 w-5 accent-amber-400"
            />
            First time at IGC?
          </label>
          {error && <p className="text-sm text-red-400">{error}</p>}
          <div className="flex items-center gap-3">
            <button
              onClick={checkIn} disabled={busy || !ready}
              className="flex-1 py-3 bg-divine-500 hover:bg-divine-400 disabled:bg-slate-700 disabled:text-slate-400 text-cosmic-950 font-bold text-sm rounded-xl"
            >
              {busy ? 'Saving…' : 'Mark as registered'}
            </button>
            {person.phone_on_file && (
              <button onClick={() => setUnverified((v) => !v)} className="text-xs text-slate-400 underline w-28 text-left">
                {unverified ? 'Verify number' : "Can't verify number"}
              </button>
            )}
          </div>
        </div>
      )}
    </li>
  )
}

function AttendEventBody() {
  const [day, setDay] = useState(defaultDay)
  const [q, setQ] = useState('')
  const [results, setResults] = useState([])
  const [counts, setCounts] = useState({ day_checked_in: null, registered: null })
  const [error, setError] = useState(null)
  const [settled, setSettled] = useState('')   // the query the shown results belong to
  const seq = useRef(0)

  const refresh = (query = q, d = day) => {
    const mine = ++seq.current
    call('get', '/search', { params: { day: d, q: query } })
      .then((res) => {
        if (mine !== seq.current) return
        setResults(res.results)
        setCounts({ day_checked_in: res.day_checked_in, registered: res.registered })
        setSettled(`${d}|${query}`)
        setError(null)
      })
      .catch((err) => mine === seq.current && setError(errorMessage(err)))
  }

  useEffect(() => {
    const t = setTimeout(() => refresh(q, day), 250)
    return () => clearTimeout(t)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [q, day])

  const replace = (person) => {
    setResults((rs) => rs.map((r) => (r.row === person.row ? person : r)))
    // keep the day counter honest without waiting for the next search
    call('get', '/search', { params: { day, q: '' } }).then((res) =>
      setCounts({ day_checked_in: res.day_checked_in, registered: res.registered })).catch(() => {})
  }

  return (
    <>
      <div className="flex gap-2">
        {DAYS.map((d) => (
          <button
            key={d.id} onClick={() => setDay(d.id)}
            className={`flex-1 py-2.5 rounded-xl text-sm font-bold border ${
              day === d.id ? 'bg-divine-500 text-cosmic-950 border-divine-500' : 'bg-cosmic-800 text-slate-300 border-slate-700'
            }`}
          >
            {d.label}
          </button>
        ))}
      </div>

      <p className="text-xs text-slate-400 mt-3">
        {counts.registered === null ? 'Loading…' : (
          <><span className="text-white font-semibold">{counts.day_checked_in}</span> registered on {DAYS.find((d) => d.id === day).label} · {counts.registered} on the list</>
        )}
      </p>

      <input
        type="search" autoFocus value={q} onChange={(e) => setQ(e.target.value)}
        placeholder="Search name or phone…"
        className="mt-3 w-full px-4 py-3.5 bg-cosmic-900 border border-slate-700 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:border-divine-500 focus:ring-1 focus:ring-divine-500"
      />

      {error && <p className="mt-4 text-sm text-red-400">{error}</p>}
      {!error && q.trim().length >= 2 && settled === `${day}|${q}` && results.length === 0 && (
        <p className="mt-6 text-center text-slate-400 text-sm">No one found. Try fewer letters, or the phone number.</p>
      )}

      <ul className="mt-4 space-y-3">
        {results.map((p) => (
          <PersonCard key={`${p.row}-${day}-${p.checked_in}`} person={p} day={day} onChange={replace} />
        ))}
      </ul>
    </>
  )
}

export default function AttendEvent() {
  return (
    <Shell title="Check-in">
      <AttendEventBody />
    </Shell>
  )
}
