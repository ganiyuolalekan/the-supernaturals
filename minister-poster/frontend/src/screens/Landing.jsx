import { EVENT } from '../config/event'

export default function Landing({ onStart }) {
  return (
    <div className="min-h-dvh flex flex-col items-center justify-center px-6 py-16 relative overflow-hidden">
      {/* Ambient background orbs */}
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-96 h-96 rounded-full bg-amber-900/20 blur-3xl" />
        <div className="absolute bottom-1/3 left-1/4 w-80 h-80 rounded-full bg-yellow-900/15 blur-3xl" />
        <div className="absolute top-1/2 right-1/4 w-64 h-64 rounded-full bg-orange-900/10 blur-3xl" />
      </div>

      {/* Stars */}
      <div className="absolute inset-0 pointer-events-none overflow-hidden">
        {Array.from({ length: 50 }).map((_, i) => (
          <div
            key={i}
            className="absolute rounded-full bg-white"
            style={{
              width: (Math.sin(i * 7.3) * 0.5 + 1) + 'px',
              height: (Math.sin(i * 7.3) * 0.5 + 1) + 'px',
              top: ((i * 19.7) % 100) + '%',
              left: ((i * 37.1) % 100) + '%',
              opacity: (Math.sin(i * 3.1) * 0.3 + 0.4),
            }}
          />
        ))}
      </div>

      {/* Content */}
      <div className="relative z-10 flex flex-col items-center text-center max-w-lg gap-6">

        {/* Conference badge */}
        <span className="text-divine-500 text-xs tracking-[0.3em] uppercase font-bold">
          {EVENT.name}
        </span>

        {/* CONFIRMED mega stamp */}
        <div className="flex flex-col items-center gap-1">
          <div className="px-6 py-2 border-2 border-divine-500/60 rounded">
            <span className="confirmed-stamp font-mono text-divine-500 text-3xl sm:text-4xl font-black tracking-widest uppercase">
              CONFIRMED
            </span>
          </div>
          <p className="text-slate-500 text-xs tracking-widest uppercase">Official Announcement Portal</p>
        </div>

        {/* Divider */}
        <div className="flex items-center gap-3 w-full max-w-xs">
          <div className="flex-1 h-px bg-gradient-to-r from-transparent to-divine-500/40" />
          <span className="text-divine-500 text-lg">✦</span>
          <div className="flex-1 h-px bg-gradient-to-l from-transparent to-divine-500/40" />
        </div>

        {/* Hero text */}
        <h1 className="font-display text-4xl sm:text-5xl font-bold text-white text-glow leading-tight">
          We've Signed<br />Our {EVENT.guests}.
        </h1>

        <p className="text-slate-300 text-base leading-relaxed max-w-sm">
          Generate an announcement poster for each confirmed {EVENT.guest.toLowerCase()}
          in the transfer-signing style.
          <span className="block mt-2 text-divine-500 font-semibold">
            Portrait. Text overlay. 5-second announcement video.
          </span>
        </p>

        {/* How it works */}
        <div className="w-full max-w-sm grid grid-cols-3 gap-2 text-center">
          {[
            { n: '01', label: 'Upload photo' },
            { n: '02', label: 'Select style' },
            { n: '03', label: 'Get poster + video' },
          ].map(({ n, label }) => (
            <div key={n} className="bg-cosmic-800/60 border border-slate-700/40 rounded-xl px-2 py-3">
              <div className="text-divine-500 font-black text-xs tracking-wider">{n}</div>
              <div className="text-slate-300 text-xs mt-1">{label}</div>
            </div>
          ))}
        </div>

        {/* CTA */}
        <button
          onClick={onStart}
          className="mt-2 px-10 py-4 bg-divine-500 hover:bg-divine-400 text-cosmic-950 font-black text-lg rounded-2xl transition-all duration-200 glow-gold hover:scale-105 active:scale-95 tracking-wide"
        >
          GENERATE ANNOUNCEMENT ✦
        </button>

        <p className="text-slate-500 text-xs">
          {EVENT.dates} · {EVENT.audience}
        </p>
      </div>
    </div>
  )
}
