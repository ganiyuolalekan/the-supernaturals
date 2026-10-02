import { useId } from 'react'

const feather = (len, w) =>
  `M0 0C${len * 0.25} ${-w} ${len * 0.7} ${-w * 1.1} ${len} 0C${len * 0.7} ${w * 0.9} ${len * 0.25} ${w} 0 0Z`

// Three overlapping rows of feathers fan out from the shoulder: long primaries
// behind, shorter coverts in front.
const ROWS = [
  { count: 9, from: -74, to: 8, min: 125, max: 255, gradient: true, stroke: 0.7 },
  { count: 9, from: -66, to: 2, min: 80, max: 160, gradient: false, stroke: 0.5 },
  { count: 7, from: -58, to: -6, min: 45, max: 85, gradient: false, stroke: 0.4 },
]

function Wing({ gradId }) {
  return ROWS.map((row, r) =>
    Array.from({ length: row.count }).map((_, i) => {
      const t = i / (row.count - 1)
      const angle = row.from + (row.to - row.from) * t
      const len = row.min + (row.max - row.min) * t
      return (
        <path
          key={`${r}-${i}`}
          d={feather(len, len * 0.1)}
          transform={`rotate(${angle})`}
          fill={row.gradient ? `url(#${gradId})` : '#fff'}
          stroke="#C99A1F"
          strokeWidth="1.1"
          strokeOpacity={row.stroke}
        />
      )
    }),
  )
}

/** Decorative pair of feathered wings (inline SVG, always aria-hidden). */
export default function Wings({ className = '', parallax = false }) {
  const gradId = `igc-wing-${useId().replace(/:/g, '')}`
  return (
    <svg
      className={`igc-wings ${className}`}
      viewBox="0 0 600 300"
      aria-hidden="true"
      focusable="false"
      data-parallax={parallax ? '' : undefined}
    >
      <defs>
        <linearGradient id={gradId} x1="0" y1="0" x2="1" y2="0">
          <stop offset="0" stopColor="#FFFFFF" />
          <stop offset="0.65" stopColor="#FFF1BE" />
          <stop offset="1" stopColor="#F5B800" />
        </linearGradient>
      </defs>
      <g transform="translate(312 215)">
        <Wing gradId={gradId} />
      </g>
      <g transform="translate(288 215) scale(-1 1)">
        <Wing gradId={gradId} />
      </g>
    </svg>
  )
}
