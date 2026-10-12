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
    <div className="min-h-dvh bg-cosmic-950 bg-stars">
      <header className="sticky top-0 z-10 bg-cosmic-950/90 backdrop-blur border-b border-slate-800">
        <div className="max-w-3xl mx-auto px-4 pt-3">
          <p className="text-divine-500 text-[10px] tracking-widest uppercase font-semibold">IGC 2026 · Attendance</p>
          <h1 className="font-display text-xl font-bold text-white">{title}</h1>
          <nav className="flex gap-1 mt-2 -mb-px">
            {TABS.map((t) => (
              <a
                key={t.href} href={t.href}
                className={`px-3 py-2 text-sm font-semibold border-b-2 ${
                  path === t.href ? 'border-divine-500 text-divine-400' : 'border-transparent text-slate-400 hover:text-white'
                }`}
              >
                {t.label}
              </a>
            ))}
          </nav>
        </div>
      </header>
      <main className="max-w-3xl mx-auto px-4 py-5">{children}</main>
    </div>
  )
}
