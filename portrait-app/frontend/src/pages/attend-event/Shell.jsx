import { EVENT } from '../../config/event'
const BASE = '/attend_event'
const TABS = [
  { href: BASE, label: 'Check-in' },
  { href: `${BASE}/first_timers`, label: 'First-timers' },
  { href: `${BASE}/chart`, label: 'Chart' },
]

/** Header/nav shared by the three attendance pages. */
export default function Shell({ title, children }) {
  const path = window.location.pathname.replace(/\/+$/, '')

  return (
    <div className="min-h-dvh bg-slate-50">
      <header className="sticky top-0 z-10 bg-white/90 backdrop-blur border-b border-slate-200">
        <div className="w-full px-4 sm:px-8 pt-3">
          <p className="text-amber-700 text-[10px] tracking-widest uppercase font-semibold">{EVENT.name} · Attendance</p>
          <h1 className="font-display text-xl font-bold text-slate-900">{title}</h1>
          <nav className="flex gap-1 mt-2 -mb-px">
            {TABS.map((t) => (
              <a
                key={t.href} href={t.href}
                className={`px-3 py-2 text-sm font-semibold border-b-2 ${
                  path === t.href ? 'border-amber-500 text-amber-700' : 'border-transparent text-slate-500 hover:text-slate-900'
                }`}
              >
                {t.label}
              </a>
            ))}
          </nav>
        </div>
      </header>
      <main className="w-full px-4 sm:px-8 py-5">{children}</main>
    </div>
  )
}
