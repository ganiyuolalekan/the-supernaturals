import { useState } from 'react'

/**
 * Rounded photo frame. Shows the real image when `src` is set, otherwise a
 * labelled placeholder so real photos can be dropped in later.
 */
export default function Photo({ src, alt, label, ratio = '4 / 5', initials, eager = false, className = '' }) {
  const [failed, setFailed] = useState(false)

  if (src && !failed) {
    return (
      <div className={`igc-photo ${className}`} style={{ aspectRatio: ratio }}>
        <img
          src={src}
          alt={alt}
          loading={eager ? 'eager' : 'lazy'}
          decoding="async"
          onError={() => setFailed(true)}
        />
      </div>
    )
  }

  return (
    <div
      className={`igc-photo igc-photo--ph ${className}`}
      style={{ aspectRatio: ratio }}
      role="img"
      aria-label={`Placeholder: ${alt || label}`}
    >
      {initials && <span className="igc-photo__initials" aria-hidden="true">{initials}</span>}
      <span className="igc-photo__label" aria-hidden="true">{label}</span>
    </div>
  )
}

/** Round logo badge: real image when provided, otherwise a labelled placeholder. */
export function Logo({ logo, size = 'sm' }) {
  return (
    <span className={`igc-logo igc-logo--${size}`}>
      {logo.image ? <img src={logo.image} alt={logo.alt} /> : <span role="img" aria-label={`${logo.alt} (placeholder)`}>{logo.label}</span>}
    </span>
  )
}
