import Icon from './Icon'
import Wings from './Wings'

/** Renders **bold** markers inside copy stored in the content files. */
export function RichText({ text }) {
  return text.split(/(\*\*[^*]+\*\*)/).map((part, i) =>
    part.startsWith('**') ? <strong key={i}>{part.slice(2, -2)}</strong> : part,
  )
}

/** Slide heading: eyebrow, H2 and a gold underline ornament with a tiny wing divider. */
export function SectionHead({ id, eyebrow, title, children, align = 'left' }) {
  return (
    <div className={`igc-head igc-head--${align} igc-rise`}>
      {eyebrow && <p className="igc-eyebrow">{eyebrow}</p>}
      <h2 id={id} className="igc-h2">{title}</h2>
      <div className="igc-orn" aria-hidden="true">
        <span />
        <Wings className="igc-orn__wings" />
        <span />
      </div>
      {children}
    </div>
  )
}

/** Button or link styled as a button. */
export function Button({ href, variant = 'primary', icon, className = '', children, ...rest }) {
  const cls = `igc-btn igc-btn--${variant} ${className}`.trim()
  const inner = (
    <>
      {icon && <Icon name={icon} size={18} />}
      {children}
    </>
  )
  if (href) {
    const external = /^https?:/.test(href)
    return (
      <a
        className={cls}
        href={href}
        {...(external ? { target: '_blank', rel: 'noopener noreferrer' } : {})}
        {...rest}
      >
        {inner}
      </a>
    )
  }
  return (
    <button type="button" className={cls} {...rest}>
      {inner}
    </button>
  )
}
