import { useEffect, useRef } from 'react'
import Icon from './Icon'

const FOCUSABLE = 'a[href], button:not([disabled]), [tabindex]:not([tabindex="-1"])'

/**
 * In-page slide set (carousel) shown as a dialog so the visitor keeps their place.
 * Keyboard: ← → move between slides, Esc closes, Tab stays inside.
 */
export default function SlideDialog({ label, kicker, index, total, direction, onPrev, onNext, onClose, children }) {
  const ref = useRef(null)

  useEffect(() => {
    const opener = document.activeElement
    ref.current?.focus()
    document.body.style.overflow = 'hidden'
    return () => {
      document.body.style.overflow = ''
      if (opener && opener.isConnected) opener.focus?.()
    }
  }, [])

  const onKeyDown = (e) => {
    if (e.key === 'Escape') {
      e.preventDefault()
      onClose()
    } else if (e.key === 'ArrowLeft') {
      e.preventDefault()
      onPrev()
    } else if (e.key === 'ArrowRight') {
      e.preventDefault()
      onNext()
    } else if (e.key === 'Tab') {
      const items = [...ref.current.querySelectorAll(FOCUSABLE)]
      if (!items.length) return
      const first = items[0]
      const last = items[items.length - 1]
      if (e.shiftKey && (document.activeElement === first || document.activeElement === ref.current)) {
        e.preventDefault()
        last.focus()
      } else if (!e.shiftKey && document.activeElement === last) {
        e.preventDefault()
        first.focus()
      }
    }
  }

  return (
    <div className="igc-dialog-backdrop" onMouseDown={(e) => e.target === e.currentTarget && onClose()}>
      <div
        ref={ref}
        className="igc-dialog"
        role="dialog"
        aria-modal="true"
        aria-label={label}
        tabIndex={-1}
        onKeyDown={onKeyDown}
      >
        <div className="igc-dialog__bar">
          <p className="igc-dialog__kicker" aria-live="polite">
            {kicker} · Slide {index + 1} of {total}
          </p>
          <button type="button" className="igc-iconbtn" onClick={onClose} aria-label="Close">
            <Icon name="x" />
          </button>
        </div>

        <div className="igc-dialog__body">
          <div key={index} className={`igc-dialog__slide igc-dialog__slide--${direction}`}>
            {children}
          </div>
        </div>

        <div className="igc-dialog__foot">
          <button type="button" className="igc-btn igc-btn--outline igc-btn--sm" onClick={onPrev}>
            <Icon name="chevron-left" size={18} /> Previous
          </button>
          <ol className="igc-dots" aria-hidden="true">
            {Array.from({ length: total }).map((_, i) => (
              <li key={i} className={i === index ? 'is-active' : ''} />
            ))}
          </ol>
          <button type="button" className="igc-btn igc-btn--outline igc-btn--sm" onClick={onNext}>
            Next <Icon name="chevron-right" size={18} />
          </button>
        </div>
      </div>
    </div>
  )
}
