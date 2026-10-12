import { useEffect, useRef, useState } from 'react'
import Shell from './Shell'
import { DAYS, call, defaultDay, errorMessage } from './api'

const AGE_GROUPS = ['Youth (13-17)', 'Young Adult (18-35)', 'Adult (35+)']
const HOME_CHURCH = 'RCCG Praise Assembly'
const POLL_MS = 15_000

// "🚶🏽‍♂️: 12:54 ✅" — show just the time
const timeOf = (stamp) => (stamp || '').match(/\d{1,2}:\d{2}/)?.[0] || stamp

const fieldCls =
  'w-full px-3 py-2.5 bg-white border border-slate-300 rounded-xl text-slate-900 placeholder-slate-400 text-sm focus:outline-none focus:border-divine-500'

/** A row of mutually exclusive buttons. `value` is null until the agent picks. */
function Choice({ options, value, onChange }) {
  return (
    <div className="flex gap-2 flex-wrap">
      {options.map((o) => (
        <button
          key={String(o.value)} type="button" onClick={() => onChange(o.value)}
          className={`flex-1 min-w-[7rem] py-2 rounded-xl text-sm font-semibold border ${
            value === o.value ? 'bg-amber-100 border-amber-500 text-amber-800' : 'bg-white border-slate-300 text-slate-600'}`}
        >
          {o.label}
        </button>
      ))}
    </div>
  )
}

const FIRST_TIME_OPTIONS = [
  { value: true, label: 'Yes, first time' },
  { value: false, label: 'No, returning' },
]

function PersonCard({ person, day, onChange }) {
  const [phone, setPhone] = useState('')
  // null = the agent hasn't asked yet; never defaulted, so it can't be sent by accident
  const [firstTimer, setFirstTimer] = useState(null)
  const [pending, setPending] = useState(false) // registering — shown at once, confirmed when the sheet answers
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState(null)

  const checkIn = async () => {
    setPending(true)
    setError(null)
    try {
      const res = await call('post', '/check-in', {
        data: { row: person.row, day, phone, first_timer: person.first_timer ? null : firstTimer },
      })
      onChange(res.person, res.day_checked_in)
    } catch (err) {
      setPending(false) // roll the card back and say why
      setError(errorMessage(err))
    }
  }

  const undo = async () => {
    setBusy(true)
    setError(null)
    try {
      const res = await call('post', '/undo', { data: { row: person.row, day } })
      setPhone('')
      onChange(res.person, res.day_checked_in)
    } catch (err) {
      setError(errorMessage(err))
    } finally {
      setBusy(false)
    }
  }

  const ready = person.first_timer || firstTimer !== null
  const done = person.checked_in || pending

  return (
    <li className={`rounded-2xl border p-4 ${
      pending ? 'border-amber-400 bg-amber-50'
        : person.checked_in ? 'border-emerald-400 bg-emerald-50'
          : 'border-slate-200 bg-white shadow-sm'}`}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <p className="font-semibold text-slate-900 break-words">{person.name}</p>
          <p className="text-xs text-slate-500 mt-0.5">
            {[person.gender, person.age_group].filter(Boolean).join(' · ')}
          </p>
          <p className="text-xs mt-1">
            <span className={person.home_church ? 'text-amber-700 font-semibold' : 'text-slate-600'}>
              {person.home_church ? '★ ' : ''}{person.church || 'No church given'}
            </span>
          </p>
        </div>
        <p className="font-mono text-sm text-slate-600 shrink-0">{person.phone_masked || 'no number'}</p>
      </div>

      {done ? (
        <div className="mt-3 flex items-center justify-between gap-3">
          {pending ? (
            <p className="text-sm text-amber-800 font-semibold">⏳ Registering…</p>
          ) : (
            <>
              <p className="text-sm text-emerald-700 font-semibold">
                ✓ Registered {timeOf(person.attended[day])}{person.first_timer ? ' · First-timer' : ''}
              </p>
              <button onClick={undo} disabled={busy} className="text-xs text-slate-500 underline disabled:opacity-50">
                Undo
              </button>
            </>
          )}
        </div>
      ) : (
        <div className="mt-3 space-y-3">
          {person.first_timer ? (
            <p className="text-xs text-slate-500">Already marked as a first-timer on an earlier day.</p>
          ) : (
            <div>
              <p className="text-sm text-slate-700 mb-1.5">Is this their first time at IGC?</p>
              <Choice options={FIRST_TIME_OPTIONS} value={firstTimer} onChange={setFirstTimer} />
            </div>
          )}
          {person.phone_on_file && (
            <input
              type="tel" inputMode="numeric" value={phone} onChange={(e) => setPhone(e.target.value)}
              placeholder="Last 4 digits of their number (optional)"
              className={fieldCls}
            />
          )}
          {error && <p className="text-sm text-red-600">{error}</p>}
          <button
            onClick={checkIn} disabled={!ready}
            className="w-full py-3 bg-divine-500 hover:bg-divine-400 disabled:bg-slate-200 disabled:text-slate-500 text-cosmic-950 font-bold text-sm rounded-xl"
          >
            Mark as registered
          </button>
        </div>
      )}
    </li>
  )
}

function WalkInForm({ day, initialName, onDone, onCancel }) {
  const [name, setName] = useState(initialName)
  const [phone, setPhone] = useState('')
  const [gender, setGender] = useState(null)
  const [ageGroup, setAgeGroup] = useState(null)
  const [church, setChurch] = useState('')
  const [firstTimer, setFirstTimer] = useState(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState(null)
  const [existing, setExisting] = useState(null)

  const phoneOk = phone.replace(/\D/g, '').length >= 7
  const ready = name.trim().length >= 2 && phoneOk && gender && ageGroup && firstTimer !== null
  const dayLabel = DAYS.find((d) => d.id === day).label

  const submit = async (e) => {
    e.preventDefault()
    setBusy(true)
    setError(null)
    setExisting(null)
    try {
      const res = await call('post', '/walk-in', {
        data: { day, name, phone, gender, age_group: ageGroup, church, first_timer: firstTimer },
      })
      onDone(res.person, res)
    } catch (err) {
      setError(errorMessage(err))
      setExisting(err?.response?.data?.detail?.person || null)
      setBusy(false)
    }
  }

  return (
    <form onSubmit={submit} className="mt-4 rounded-2xl border border-amber-300 bg-amber-50/60 p-4 space-y-3 max-w-xl">
      <p className="font-semibold text-slate-900">Walk-in — not on the list</p>

      <input className={fieldCls} value={name} onChange={(e) => setName(e.target.value)} placeholder="Full name" autoFocus />
      <input
        className={fieldCls} type="tel" inputMode="numeric" value={phone} onChange={(e) => setPhone(e.target.value)}
        placeholder="Phone number"
      />

      <div>
        <p className="text-sm text-slate-700 mb-1.5">Gender</p>
        <Choice
          options={[{ value: 'Male', label: 'Male' }, { value: 'Female', label: 'Female' }]}
          value={gender} onChange={setGender}
        />
      </div>
      <div>
        <p className="text-sm text-slate-700 mb-1.5">Age group</p>
        <Choice options={AGE_GROUPS.map((a) => ({ value: a, label: a }))} value={ageGroup} onChange={setAgeGroup} />
      </div>
      <div>
        <p className="text-sm text-slate-700 mb-1.5">Church or fellowship</p>
        <input className={fieldCls} value={church} onChange={(e) => setChurch(e.target.value)} placeholder="Church name" />
        <button type="button" onClick={() => setChurch(HOME_CHURCH)} className="mt-1.5 text-xs text-amber-700 underline">
          Use “{HOME_CHURCH}”
        </button>
      </div>
      <div>
        <p className="text-sm text-slate-700 mb-1.5">Is this their first time at IGC?</p>
        <Choice options={FIRST_TIME_OPTIONS} value={firstTimer} onChange={setFirstTimer} />
      </div>

      {error && (
        <p className="text-sm text-red-600">
          {error}
          {existing && (
            <button type="button" onClick={() => onDone(existing, null)} className="ml-2 underline">Show them</button>
          )}
        </p>
      )}

      <div className="flex gap-3">
        <button
          type="submit" disabled={!ready || busy}
          className="flex-1 py-3 bg-divine-500 hover:bg-divine-400 disabled:bg-slate-200 disabled:text-slate-500 text-cosmic-950 font-bold text-sm rounded-xl"
        >
          {busy ? 'Saving…' : `Register walk-in for ${dayLabel}`}
        </button>
        <button type="button" onClick={onCancel} className="px-4 text-sm text-slate-500 underline">Cancel</button>
      </div>
    </form>
  )
}

function AttendEventBody() {
  const [day, setDay] = useState(defaultDay)
  const [q, setQ] = useState('')
  const [results, setResults] = useState([])
  const [counts, setCounts] = useState({ day_checked_in: null, registered: null })
  const [demo, setDemo] = useState(false)
  const [error, setError] = useState(null)
  const [settled, setSettled] = useState('')   // the query the shown results belong to
  const [walkIn, setWalkIn] = useState(false)
  const seq = useRef(0)
  const latest = useRef({ q, day })
  latest.current = { q, day }

  const refresh = (query, d, { quiet = false } = {}) => {
    const mine = ++seq.current
    call('get', '/search', { params: { day: d, q: query } })
      .then((res) => {
        if (mine !== seq.current) return
        setResults(res.results)
        setCounts({ day_checked_in: res.day_checked_in, registered: res.registered })
        setDemo(!!res.demo)
        setSettled(`${d}|${query}`)
        setError(null)
      })
      .catch((err) => { if (!quiet && mine === seq.current) setError(errorMessage(err)) })
  }

  useEffect(() => {
    const t = setTimeout(() => refresh(q, day), 250)
    return () => clearTimeout(t)
  }, [q, day])

  // Other agents are registering people on other phones: pick their changes up
  // quietly while this tab is open. Cheap — the backend answers from memory.
  useEffect(() => {
    const t = setInterval(() => {
      if (document.visibilityState === 'visible') refresh(latest.current.q, latest.current.day, { quiet: true })
    }, POLL_MS)
    return () => clearInterval(t)
  }, [])

  const replace = (person, dayCount) => {
    setResults((rs) => rs.map((r) => (r.row === person.row ? person : r)))
    if (dayCount != null) setCounts((c) => ({ ...c, day_checked_in: dayCount }))
  }

  const walkInDone = (person, res) => {
    setWalkIn(false)
    seq.current += 1 // drop any search still in flight
    setQ(person.name)
    setResults([person])
    setSettled(`${day}|${person.name}`)
    if (res) setCounts({ day_checked_in: res.day_checked_in, registered: res.registered })
  }

  return (
    <>
      {demo && (
        <p className="mb-3 rounded-xl border border-amber-400 bg-amber-50 px-4 py-2.5 text-sm text-amber-900">
          <b>Demo mode</b> — check-ins are kept in memory only and are <b>not</b> being written to the Google Sheet.
        </p>
      )}
      <div className="flex gap-2">
        {DAYS.map((d) => (
          <button
            key={d.id} onClick={() => setDay(d.id)}
            className={`flex-1 py-2.5 rounded-xl text-sm font-bold border ${
              day === d.id ? 'bg-divine-500 text-cosmic-950 border-divine-500' : 'bg-white text-slate-600 border-slate-300'
            }`}
          >
            {d.label}
          </button>
        ))}
      </div>

      <p className="text-xs text-slate-500 mt-3">
        {counts.registered === null ? 'Loading…' : (
          <><span className="text-slate-900 font-semibold">{counts.day_checked_in}</span> registered on {DAYS.find((d) => d.id === day).label} · {counts.registered} on the list</>
        )}
      </p>

      <div className="mt-3 flex gap-2">
        <input
          type="search" autoFocus value={q} onChange={(e) => setQ(e.target.value)}
          placeholder="Search name or phone…"
          className="flex-1 min-w-0 px-4 py-3.5 bg-white border border-slate-300 rounded-xl text-slate-900 placeholder-slate-400 focus:outline-none focus:border-divine-500 focus:ring-1 focus:ring-divine-500"
        />
        <button
          onClick={() => setWalkIn(true)}
          className="shrink-0 px-4 rounded-xl border border-amber-500 bg-amber-100 text-amber-800 text-sm font-bold"
        >
          + Walk-in
        </button>
      </div>

      {walkIn && (
        <WalkInForm
          day={day}
          initialName={/\d{4}/.test(q) ? '' : q.trim()}
          onDone={walkInDone}
          onCancel={() => setWalkIn(false)}
        />
      )}

      {error && <p className="mt-4 text-sm text-red-600">{error}</p>}
      {!error && !walkIn && q.trim().length >= 2 && settled === `${day}|${q}` && results.length === 0 && (
        <p className="mt-6 text-center text-slate-500 text-sm">
          No one found. Try fewer letters, or the phone number.{' '}
          <button onClick={() => setWalkIn(true)} className="text-amber-700 underline font-semibold">
            Register as a walk-in
          </button>
        </p>
      )}

      <ul className="mt-4 grid gap-3 sm:grid-cols-2 xl:grid-cols-3 items-start">
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
