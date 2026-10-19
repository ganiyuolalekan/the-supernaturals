import { EVENT } from '../../config/event'
import { useEffect, useState } from 'react'
import Shell from './Shell'
import { DAYS, call, errorMessage } from './api'

const pct = (a, b) => (b ? Math.round((a / b) * 100) : 0)

function Kpi({ label, value, sub }) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white shadow-sm p-4">
      <p className="text-[11px] uppercase tracking-wider text-slate-500">{label}</p>
      <p className="text-3xl font-bold text-slate-900 mt-1">{value}</p>
      {sub && <p className="text-xs text-slate-500 mt-0.5">{sub}</p>}
    </div>
  )
}

/** Gold bar = attended, dim track = registered. */
function Bars({ title, items }) {
  const max = Math.max(1, ...items.map((i) => i.registered))
  return (
    <section className="rounded-2xl border border-slate-200 bg-white shadow-sm p-4">
      <h2 className="text-sm font-semibold text-slate-900 mb-3">{title}</h2>
      <ul className="space-y-3">
        {items.map((i) => (
          <li key={i.label}>
            <div className="flex justify-between gap-3 text-xs text-slate-600 mb-1">
              <span className="break-words">{i.label}</span>
              <span className="shrink-0 tabular-nums">
                <b className="text-slate-900">{i.attended}</b> / {i.registered} · {pct(i.attended, i.registered)}%
              </span>
            </div>
            <div className="h-2.5 rounded-full bg-slate-200" style={{ width: `${(i.registered / max) * 100}%`, minWidth: '6px' }}>
              <div className="h-full rounded-full bg-divine-500" style={{ width: `${pct(i.attended, i.registered)}%` }} />
            </div>
          </li>
        ))}
      </ul>
    </section>
  )
}

function ChartBody() {
  const [day, setDay] = useState('all')
  const [s, setS] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    let live = true
    const load = () => call('get', '/stats', { params: { day } })
      .then((r) => { if (live) { setS(r); setError(null) } })
      .catch((e) => live && setError(errorMessage(e)))
    load()
    const t = setInterval(load, 30_000)
    return () => { live = false; clearInterval(t) }
  }, [day])

  const homeOfAttended = s ? pct(s.home_church, s.attended) : 0
  const maxHour = s ? Math.max(1, ...s.by_hour.map((h) => h.count)) : 1

  return (
    <>
      <div className="flex gap-2 flex-wrap">
        {[{ id: 'all', label: 'All days' }, ...DAYS].map((d) => (
          <button key={d.id} onClick={() => setDay(d.id)}
            className={`px-4 py-2 rounded-xl text-sm font-bold border ${
              day === d.id ? 'bg-divine-500 text-cosmic-950 border-divine-500' : 'bg-white text-slate-600 border-slate-300'}`}>
            {d.label}
          </button>
        ))}
      </div>

      {error && <p className="mt-4 text-sm text-red-600">{error}</p>}
      {!s && !error && <p className="mt-4 text-slate-500 text-sm">Loading…</p>}

      {s && (
        <div className="mt-4 grid gap-4 md:grid-cols-2 xl:grid-cols-3 items-start">
          <div className="grid grid-cols-2 gap-3 md:col-span-2 xl:col-span-3 xl:grid-cols-4">
            <Kpi label={day === 'all' ? 'Attended (any day)' : 'Attended'} value={s.attended}
              sub={`${pct(s.attended, s.registered)}% of ${s.registered} registered`} />
            <Kpi label="First-timers" value={s.first_timers} sub={`${pct(s.first_timers, s.attended)}% of attendees`} />
            <Kpi label={EVENT.homeOrg} value={s.home_church} sub={`${homeOfAttended}% of attendees`} />
            <Kpi label="Other organisations" value={s.other_church} sub={`${100 - homeOfAttended}% of attendees`} />
          </div>

          <section className="rounded-2xl border border-slate-200 bg-white shadow-sm p-4">
            <h2 className="text-sm font-semibold text-slate-900 mb-3">Registered by day</h2>
            <div className="grid grid-cols-3 gap-3 text-center">
              {DAYS.map((d) => (
                <div key={d.id}>
                  <p className="text-2xl font-bold text-slate-900">{s.per_day[d.id]}</p>
                  <p className="text-xs text-slate-500">{d.label}</p>
                </div>
              ))}
            </div>
            {day === 'all' && (
              <p className="mt-3 text-xs text-slate-500 text-center">
                Came on all 3 days: <b className="text-slate-900">{s.days_attended['3']}</b> · 2 days:{' '}
                <b className="text-slate-900">{s.days_attended['2']}</b> · 1 day: <b className="text-slate-900">{s.days_attended['1']}</b>
              </p>
            )}
          </section>

          <Bars title="Age bracket" items={s.age_group} />
          <Bars title="Home vs others" items={s.church} />
          <Bars title="Gender" items={s.gender} />
          <Bars title="Free transport" items={s.transport} />
          <Bars title="Where they came from" items={s.area} />
          <Bars title="How they heard" items={s.source} />

          {s.other_churches.length > 0 && (
            <section className="rounded-2xl border border-slate-200 bg-white shadow-sm p-4">
              <h2 className="text-sm font-semibold text-slate-900 mb-3">Other organisations present</h2>
              <ul className="text-sm text-slate-600 space-y-1">
                {s.other_churches.map((c) => (
                  <li key={c.label} className="flex justify-between gap-3"><span>{c.label}</span><b className="text-slate-900">{c.count}</b></li>
                ))}
              </ul>
            </section>
          )}

          {day !== 'all' && s.by_hour.length > 0 && (
            <section className="rounded-2xl border border-slate-200 bg-white shadow-sm p-4">
              <h2 className="text-sm font-semibold text-slate-900 mb-3">Arrivals by hour</h2>
              <div className="flex items-end gap-1.5 h-28">
                {s.by_hour.map((h) => (
                  <div key={h.hour} className="flex-1 flex flex-col items-center justify-end h-full">
                    <span className="text-[10px] text-slate-600">{h.count}</span>
                    <div className="w-full rounded-t bg-divine-500" style={{ height: `${(h.count / maxHour) * 80}%` }} />
                    <span className="text-[10px] text-slate-400 mt-1">{String(h.hour).padStart(2, '0')}</span>
                  </div>
                ))}
              </div>
            </section>
          )}
        </div>
      )}
    </>
  )
}

export default function Chart() {
  return (
    <Shell title="Attendance chart">
      <ChartBody />
    </Shell>
  )
}
