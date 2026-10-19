import { useId } from 'react'

const petal = (len, w) =>
  `M0 0C${len * 0.25} ${-w} ${len * 0.7} ${-w * 1.1} ${len} 0C${len * 0.7} ${w * 0.9} ${len * 0.25} ${w} 0 0Z`

// A half-sun fan of petals: long rays behind, short ones in front. This is the
// placeholder brand mark. Swap it for your own SVG (keep the viewBox and props),
// or drop an <img> in here.
const ROWS = [
  { count: 13, from: -172, to: -8, min: 190, max: 190, gradient: true, stroke: 0.7 },
  { count: 12, from: -166, to: -14, min: 120, max: 120, gradient: false, stroke: 0.5 },
]

function Fan({ gradId }) {
  return ROWS.map((row, r) =>
    Array.from({ length: row.count }).map((_, i) => {
      const t = i / (row.count - 1)
      const angle = row.from + (row.to - row.from) * t
      return (
        <path
          key={`${r}-${i}`}
          d={petal(row.min, row.min * 0.09)}
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

/** Decorative brand mark (inline SVG, always aria-hidden). */
export default function Ornament({ className = '', parallax = false }) {
  const gradId = `ev-mark-${useId().replace(/:/g, '')}`
  return (
    <svg
      className={`ev-ornament ${className}`}
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
      <g transform="translate(300 250)">
        <Fan gradId={gradId} />
      </g>
    </svg>
  )
}
