export default function Landing({ onStart }) {
  return (
    <div className="min-h-dvh flex flex-col items-center justify-center px-6 py-16 relative overflow-hidden">
      {/* Ambient background orbs */}
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-96 h-96 rounded-full bg-indigo-900/30 blur-3xl" />
        <div className="absolute bottom-1/4 left-1/4 w-72 h-72 rounded-full bg-purple-900/20 blur-3xl" />
        <div className="absolute top-1/3 right-1/4 w-64 h-64 rounded-full bg-blue-900/20 blur-3xl" />
      </div>

      {/* Stars layer */}
      <div className="absolute inset-0 pointer-events-none overflow-hidden">
        {Array.from({ length: 60 }).map((_, i) => (
          <div
            key={i}
            className="absolute rounded-full bg-white"
            style={{
              width: Math.random() * 2 + 1 + 'px',
              height: Math.random() * 2 + 1 + 'px',
              top: Math.random() * 100 + '%',
              left: Math.random() * 100 + '%',
              opacity: Math.random() * 0.6 + 0.2,
            }}
          />
        ))}
      </div>

      {/* Content */}
      <div className="relative z-10 flex flex-col items-center text-center max-w-lg gap-6">
        {/* Conference label */}
        <span className="text-divine-500 text-sm tracking-[0.25em] uppercase font-semibold">
          The SuperNaturals 2026
        </span>

        {/* Title */}
        <h1 className="font-display text-5xl sm:text-6xl font-bold text-white text-glow leading-tight">
          I Am<br />Supernatural
        </h1>

        {/* Divider */}
        <div className="flex items-center gap-3 w-full max-w-xs">
          <div className="flex-1 h-px bg-gradient-to-r from-transparent to-divine-500/40" />
          <span className="text-divine-500 text-lg">✦</span>
          <div className="flex-1 h-px bg-gradient-to-l from-transparent to-divine-500/40" />
        </div>

        {/* Scripture */}
        <p className="text-slate-300 text-sm italic leading-relaxed max-w-sm">
          "If the Spirit that raised Jesus from the dead dwells in you, that same Spirit will quicken your mortal body."
          <span className="block mt-1 text-divine-500 not-italic font-semibold">Romans 8:11</span>
        </p>

        {/* Tagline */}
        <p className="text-slate-200 text-lg leading-snug">
          Are you a SuperNatural?<br />
          <span className="text-white font-semibold">Show the world.</span>
        </p>

        <p className="text-slate-400 text-sm">
          Upload your photo. Get your supernatural portrait. Share it.
        </p>

        {/* CTA */}
        <button
          onClick={onStart}
          className="mt-2 px-8 py-4 bg-divine-500 hover:bg-divine-400 text-cosmic-950 font-bold text-lg rounded-2xl transition-all duration-200 glow-gold hover:scale-105 active:scale-95"
        >
          Generate My Image ✦
        </button>

        {/* Sample note */}
        <p className="text-slate-500 text-xs">
          Free to generate · Takes 15–30 seconds · Your original photo is never shared
        </p>
      </div>
    </div>
  )
}
