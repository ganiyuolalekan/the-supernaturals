import { useState } from 'react'
import { SCENE_CATEGORIES, findScene } from '../data/scenes'

function formatDateRange(starts, ends) {
  if (!starts || !ends) return ''
  const opts = { month: 'short', day: 'numeric' }
  const startStr = new Date(`${starts}T00:00:00`).toLocaleDateString('en-US', opts)
  const endStr = new Date(`${ends}T00:00:00`).toLocaleDateString('en-US', opts)
  return `${startStr} – ${endStr}`
}

export default function ScenePicker({ selected, onChange, activeSceneId, schedule }) {
  const activeScene = activeSceneId ? findScene(activeSceneId) : null
  const activeEntry = schedule?.find((s) => s.scene_id === activeSceneId)
  const activeWeek = activeEntry?.week

  const [openCategory, setOpenCategory] = useState(() => {
    const cat = SCENE_CATEGORIES.find((c) => c.scenes.some((s) => s.id === activeSceneId))
    return cat?.id ?? null
  })

  const toggleCategory = (id) => {
    setOpenCategory((prev) => (prev === id ? null : id))
  }

  const isLocked = (scene) => activeSceneId && scene.id !== activeSceneId

  const sceneStatus = (scene) => {
    if (!activeSceneId || scene.id === activeSceneId) return 'active'
    if (activeWeek && scene.week < activeWeek) return 'past'
    return 'future'
  }

  const sceneCaption = (scene) => {
    const entry = schedule?.find((s) => s.scene_id === scene.id)
    const dateRange = entry ? formatDateRange(entry.starts, entry.ends) : ''
    const status = sceneStatus(scene)
    if (status === 'active') return `✦ This week's scene${dateRange ? ` · ${dateRange}` : ''}`
    if (status === 'past') return `Completed · Week ${scene.week}${dateRange ? ` · ${dateRange}` : ''}`
    return `Unlocks Week ${scene.week}${dateRange ? ` · ${dateRange}` : ''}`
  }

  const handleSelect = (scene) => {
    if (isLocked(scene)) return
    onChange(selected?.id === scene.id ? null : scene)
  }

  return (
    <div>
      <label className="block text-sm font-semibold text-slate-300 mb-2">
        This Week's Scene{' '}
        <span className="text-divine-500 font-normal">(required)</span>
      </label>

      {activeScene ? (
        <div className="mb-3 px-4 py-3 bg-divine-500/10 border border-divine-500/30 rounded-xl">
          <p className="text-xs text-divine-500 font-semibold mb-0.5">
            ✦ Week {activeWeek}{activeEntry ? ` · ${formatDateRange(activeEntry.starts, activeEntry.ends)}` : ''}
          </p>
          <p className="text-sm text-white font-semibold">{activeScene.title}</p>
          {activeScene.wardrobe && (
            <p className="text-xs text-slate-400 mt-1 leading-relaxed">
              <span className="mr-1">👔</span>
              <span className="text-slate-300 font-semibold">Styling: </span>
              {activeScene.wardrobe}
            </p>
          )}
          <p className="text-xs text-slate-400 mt-0.5 leading-relaxed">
            One scene goes live each week — this is the only scene generating right now.
            Come back next week for the next one.
          </p>
        </div>
      ) : (
        <p className="text-xs text-slate-500 mb-3">
          Pick the biblical moment you want to be placed in. Your face is preserved from your photo;
          the supernatural style is applied automatically.
        </p>
      )}

      {/* Category accordions */}
      <div className="flex flex-col gap-2">
        {SCENE_CATEGORIES.map((category) => {
          const isOpen = openCategory === category.id
          const categorySelected = category.scenes.some((s) => s.id === selected?.id)

          return (
            <div key={category.id} className="border border-slate-700/70 rounded-xl overflow-hidden">
              {/* Category header */}
              <button
                type="button"
                onClick={() => toggleCategory(category.id)}
                className={`w-full flex items-center justify-between px-4 py-3 text-left transition-colors
                  ${isOpen ? 'bg-cosmic-700' : 'bg-cosmic-800 hover:bg-cosmic-700/60'}`}
              >
                <div className="flex items-center gap-2">
                  <span>{category.icon}</span>
                  <span className="text-sm font-semibold text-slate-200">{category.name}</span>
                  {categorySelected && (
                    <span className="text-xs text-divine-500 font-semibold">✓</span>
                  )}
                </div>
                <span className={`text-slate-500 text-xs transition-transform duration-200 ${isOpen ? 'rotate-180' : ''}`}>
                  ▼
                </span>
              </button>

              {/* Scenes list */}
              {isOpen && (
                <div className="border-t border-slate-700/50 divide-y divide-slate-700/30">
                  {category.scenes.map((scene) => {
                    const isSelected = selected?.id === scene.id
                    const locked = isLocked(scene)
                    return (
                      <button
                        key={scene.id}
                        type="button"
                        onClick={() => handleSelect(scene)}
                        disabled={locked}
                        className={`w-full text-left px-4 py-3 transition-all duration-150
                          ${locked
                            ? 'bg-cosmic-800/40 opacity-50 cursor-not-allowed'
                            : isSelected
                              ? 'bg-divine-500/10'
                              : 'bg-cosmic-800/80 hover:bg-cosmic-700/50'
                          }`}
                      >
                        <div className="flex items-start justify-between gap-3">
                          <div className="flex-1 min-w-0">
                            <p className={`text-sm font-semibold flex items-center gap-1.5 ${isSelected ? 'text-divine-400' : 'text-slate-200'}`}>
                              {locked && <span className="text-slate-500">🔒</span>}
                              {scene.title}
                            </p>
                            <p className="text-xs text-slate-500 mt-0.5 leading-relaxed line-clamp-2">
                              {scene.description}
                            </p>
                            {scene.wardrobe && (
                              <p className="text-xs text-slate-500 mt-1 leading-relaxed">
                                <span className="mr-1">👔</span>
                                {scene.wardrobe}
                              </p>
                            )}
                            <p className="text-xs text-divine-600 mt-1">{scene.scripture}</p>
                            <p className={`text-xs mt-1 font-medium ${locked ? 'text-slate-500' : 'text-divine-500'}`}>
                              {sceneCaption(scene)}
                            </p>
                          </div>
                          {!locked && (
                            <div className={`shrink-0 w-5 h-5 rounded-full border-2 flex items-center justify-center mt-0.5
                              ${isSelected ? 'border-divine-500 bg-divine-500' : 'border-slate-600'}`}>
                              {isSelected && <span className="text-cosmic-950 text-xs font-bold">✓</span>}
                            </div>
                          )}
                        </div>
                      </button>
                    )
                  })}
                </div>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}
