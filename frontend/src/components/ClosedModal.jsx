import { findScene } from '../data/scenes'

/**
 * Full-screen lock shown on the days the campaign is closed (Thursday and
 * Friday by default — the backend decides, via /status.closed_today).
 *
 * Deliberately not dismissible: the whole scene is locked on these days, so
 * there is nothing behind it to go back to. It names the scene that opens next
 * and the day it opens, so the close reads as anticipation rather than an
 * outage.
 */
/** ['Thu'] → 'Thu' · ['Thu','Fri'] → 'Thu and Fri' · 3+ → 'A, B and C' */
function joinDays(days) {
  if (!days?.length) return null
  if (days.length === 1) return days[0]
  return `${days.slice(0, -1).join(', ')} and ${days[days.length - 1]}`
}

export default function ClosedModal({ status }) {
  const nextScene = findScene(status?.next_open_scene_id)
  const restDays = joinDays(status?.closed_weekdays)

  const nextOpenLabel = status?.next_open
    ? new Date(`${status.next_open}T00:00:00`).toLocaleDateString(undefined, {
        weekday: 'long',
        day: 'numeric',
        month: 'long',
      })
    : null

  return (
    <div className="fixed inset-0 z-50 bg-cosmic-950/95 backdrop-blur-md flex items-center justify-center px-5 py-10 overflow-y-auto">
      <div className="w-full max-w-md text-center">
        <div className="rounded-3xl border border-divine-500/30 bg-cosmic-900/80 px-6 py-10 shadow-2xl">
          <div className="text-5xl mb-5" aria-hidden="true">🌙</div>

          <p className="text-divine-500 text-xs tracking-widest uppercase font-semibold mb-2">
            The SuperNaturals 2026
          </p>
          <h2 className="font-display text-2xl font-bold text-white leading-snug">
            This week's scene has closed
          </h2>

          <p className="text-slate-400 text-sm mt-3 leading-relaxed">
            {status?.message ||
              'The scene is closed today. Come back for the next one!'}
          </p>

          {/* What's coming — the reason to come back */}
          {nextScene && (
            <div className="mt-7 rounded-2xl border border-slate-700/60 bg-cosmic-800/60 px-5 py-5 text-left">
              <p className="text-[11px] font-semibold uppercase tracking-wider text-slate-500 mb-2">
                Up next
              </p>
              <p className="font-display text-lg font-bold text-white">
                {nextScene.title}
              </p>
              {nextScene.scripture && (
                <p className="text-divine-500 text-xs font-semibold mt-0.5">
                  {nextScene.scripture}
                </p>
              )}
              <p className="text-slate-400 text-xs mt-2.5 leading-relaxed">
                {nextScene.description}
              </p>
            </div>
          )}

          {nextOpenLabel && (
            <div className="mt-6 inline-flex items-center gap-2 rounded-full border border-divine-500/40 bg-divine-500/10 px-4 py-2">
              <span aria-hidden="true">✦</span>
              <span className="text-sm font-semibold text-divine-500">
                Opens {nextOpenLabel}
              </span>
            </div>
          )}

          <p className="text-slate-600 text-xs mt-7 leading-relaxed">
            {restDays ? `We rest every ${restDays}.` : 'We rest between scenes.'}{' '}
            See you when the next one goes live.
          </p>
        </div>
      </div>
    </div>
  )
}
