import { WORD_STYLES, MUSIC_STYLES } from '../data/ministerStyles'

export default function StylePicker({ category, selected, onChange }) {
  const styles = category === 'word' ? WORD_STYLES : MUSIC_STYLES

  return (
    <div>
      <label className="block text-sm font-semibold text-slate-300 mb-3">
        Poster Style
      </label>
      <div className="flex flex-col gap-3">
        {styles.map((style) => {
          const isSelected = selected?.id === style.id
          return (
            <button
              key={style.id}
              type="button"
              onClick={() => onChange(style)}
              className={`
                w-full text-left rounded-xl border-2 p-4 transition-all duration-200
                ${isSelected
                  ? 'border-divine-500 bg-divine-500/10 glow-gold-sm'
                  : 'border-slate-700 bg-cosmic-800 hover:border-slate-500'
                }
              `}
            >
              <div className="flex items-start gap-3">
                <span className="text-2xl shrink-0 mt-0.5">{style.icon}</span>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className={`font-bold text-sm ${isSelected ? 'text-divine-400' : 'text-white'}`}>
                      {style.name}
                    </span>
                    <span className={`
                      text-[10px] font-bold tracking-widest uppercase px-2 py-0.5 rounded-full
                      ${isSelected ? 'bg-divine-500/20 text-divine-400' : 'bg-slate-700 text-slate-400'}
                    `}>
                      {style.mood}
                    </span>
                  </div>
                  <p className={`text-xs mt-0.5 font-medium ${isSelected ? 'text-divine-500' : 'text-slate-500'}`}>
                    {style.subtitle}
                  </p>
                  <p className="text-xs text-slate-400 mt-1.5 leading-relaxed">
                    {style.description}
                  </p>
                </div>
                {isSelected && (
                  <div className="shrink-0 w-5 h-5 rounded-full bg-divine-500 flex items-center justify-center">
                    <svg className="w-3 h-3 text-cosmic-950" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd"/>
                    </svg>
                  </div>
                )}
              </div>
            </button>
          )
        })}
      </div>
    </div>
  )
}
