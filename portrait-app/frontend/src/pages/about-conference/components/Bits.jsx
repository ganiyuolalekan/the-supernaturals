import Icon from './Icon'
import Ornament from './Ornament'

/** Renders **bold** markers inside copy stored in the content files. */
export function RichText({ text }) {
  return text.split(/(\*\*[^*]+\*\*)/).map((part, i) =>
    part.startsWith('**') ? <strong key={i}>{part.slice(2, -2)}</strong> : part,
  )
}

/** Slide heading: eyebrow, H2 and a gold underline ornament with a tiny ornament divider. */
export function SectionHead({ id, eyebrow, title, children, align = 'left' }) {
  return (
    <div className={`ev-head ev-head--${align} ev-rise`}>
      {eyebrow && <p className="ev-eyebrow">{eyebrow}</p>}
      <h2 id={id} className="ev-h2">{title}</h2>
      <div className="ev-orn" aria-hidden="true">
        <span />
        <Ornament className="ev-orn__mark" />
        <span />
      </div>
      {children}
    </div>
  )
}

/** Button or link styled as a button. */
export function Button({ href, variant = 'primary', icon, className = '', children, ...rest }) {
  const cls = `ev-btn ev-btn--${variant} ${className}`.trim()
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
