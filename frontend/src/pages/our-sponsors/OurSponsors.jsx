import '../about-conference/igc.css'
import './sponsors.css'
import data from '../../data/igc/our-sponsors.json'
import Icon from '../about-conference/components/Icon'
import Wings from '../about-conference/components/Wings'
import { Button, SectionHead } from '../about-conference/components/Bits'
import { telHref, usePageHead, useRevealOnce } from '../about-conference/hooks'

const { meta, intro, sponsors } = data
const IDS = ['top', ...sponsors.map((s) => s.slug)]

/** Sponsor logo on a clean tile, never recoloured. */
function LogoTile({ sponsor, className = '' }) {
  return (
    <span className={`sp-logo ${className}`} style={sponsor.logoBg ? { '--logo-bg': sponsor.logoBg } : undefined}>
      <img src={sponsor.logo} alt={`${sponsor.name} logo`} loading="lazy" decoding="async" />
    </span>
  )
}

function Block({ block }) {
  switch (block.type) {
    case 'pairs':
      return (
        <div className="sp-pairs">
          {block.items.map((p) => (
            <div key={p.label} className="sp-pair">
              <h3 className="sp-h3">{p.label}</h3>
              <p>{p.text}</p>
            </div>
          ))}
        </div>
      )
    case 'chips':
      return (
        <div className="sp-block">
          <h3 className="sp-h3">{block.title}</h3>
          <ul className="igc-chips">
            {block.items.map((c) => (
              <li key={c} className="igc-chip">{c}</li>
            ))}
          </ul>
        </div>
      )
    case 'cards':
      return (
        <div className="sp-block">
          <h3 className="sp-h3">{block.title}</h3>
          <ul className="sp-cards">
            {block.items.map((c, i) => (
              <li key={c.title} className="sp-card">
                {block.numbered && <span className="sp-card__n" aria-hidden="true">{i + 1}</span>}
                <h4>{c.title}</h4>
                <p>{c.text}</p>
              </li>
            ))}
          </ul>
        </div>
      )
    case 'text':
      return (
        <div className="sp-block">
          <h3 className="sp-h3">{block.title}</h3>
          <p>{block.text}</p>
        </div>
      )
    default:
      return null
  }
}

/** "Find them": only the details that were actually provided are shown. */
function Find({ find }) {
  const { locations = [], note, contactPerson, phones = [], emails = [], social = [] } = find
  return (
    <aside className="sp-find" aria-label="How to reach them">
      <h3 className="sp-find__title">Find them</h3>

      {locations.map((l) => (
        <p key={l} className="sp-line"><Icon name="pin" size={18} /><span>{l}</span></p>
      ))}
      {note && <p className="sp-note">{note}</p>}
      {contactPerson && (
        <p className="sp-line"><Icon name="star" size={18} /><span>{contactPerson}</span></p>
      )}
      {social.length > 0 && (
        <p className="sp-line"><Icon name="link" size={18} /><span>{social.join(' · ')}</span></p>
      )}

      {(phones.length > 0 || emails.length > 0) && (
        <div className="sp-actions">
          {phones.map((p, i) => (
            <Button key={p} href={telHref(p)} variant={i === 0 ? 'primary' : 'outline'} icon="phone">Call {p}</Button>
          ))}
          {emails.map((e) => (
            <Button key={e} href={`mailto:${e}`} variant="outline" icon="mail" className="sp-email">{e}</Button>
          ))}
        </div>
      )}
    </aside>
  )
}

function SponsorSection({ sponsor: s, index }) {
  const total = sponsors.length
  return (
    <section
      id={s.slug}
      className={`sp-section ${index % 2 ? 'sp-section--cream' : 'sp-section--white'}`}
      aria-labelledby={`${s.slug}-h`}
    >
      <div className="igc-wrap">
        <figure className="sp-banner igc-rise">
          <img
            src={s.banner}
            alt={s.bannerAlt}
            width="1800"
            height="1005"
            loading={index === 0 ? 'eager' : 'lazy'}
            decoding="async"
          />
        </figure>

        <header className="sp-id igc-rise" style={{ '--i': 1 }}>
          <LogoTile sponsor={s} className="sp-logo--lg" />
          <div className="sp-id__text">
            <p className="sp-num">{String(index + 1).padStart(2, '0')} / {String(total).padStart(2, '0')}</p>
            <h2 id={`${s.slug}-h`} className="igc-h2 igc-h2--sm">{s.name}</h2>
            {s.regNo && <p className="sp-reg">{s.regNo}</p>}
            {s.tagline && <p className="sp-tagline">{s.tagline}</p>}
            {s.quote && <p className="sp-quote">“{s.quote}”</p>}
          </div>
        </header>

        <div className="sp-body">
          <div className="sp-main igc-rise" style={{ '--i': 2 }}>
            <p className="sp-about">{s.about}</p>
            {s.blocks.map((b, i) => (
              <Block key={i} block={b} />
            ))}
          </div>
          {s.find && (
            <div className="igc-rise" style={{ '--i': 3 }}>
              <Find find={s.find} />
            </div>
          )}
        </div>
      </div>
    </section>
  )
}

export default function OurSponsors() {
  usePageHead(meta)
  useRevealOnce(IDS)

  return (
    <div className="igc sp" lang={meta.lang}>
      <a className="igc-skip" href="#main">Skip to main content</a>

      <header className="igc-header">
        <div className="igc-header__in">
          <a className="sp-brand" href="#top" aria-label="IGC 2026 sponsors, back to the top">
            <Wings className="sp-brand__wings" />
            <span>IGC 2026</span>
          </a>
          {/* TODO: restore once the conference page is linked from here.
          <Button href="/about-conference" variant="outline" className="igc-btn--sm">About the conference</Button>
          */}
        </div>
      </header>

      <main id="main">
        <section id="top" className="sp-section sp-hero" aria-labelledby="sponsors-title">
          <Wings className="igc-watermark igc-watermark--right" parallax />
          <div className="igc-wrap">
            <SectionHead id="sponsors-title" eyebrow={intro.eyebrow} title={intro.title} align="center">
              <p className="igc-lead igc-rise" style={{ '--i': 1 }}>{intro.lead}</p>
            </SectionHead>

            <nav aria-label="Jump to a sponsor" className="igc-rise" style={{ '--i': 2 }}>
              <ul className="sp-jump">
                {sponsors.map((s) => (
                  <li key={s.slug}>
                    <a href={`#${s.slug}`} className="sp-jump__link">
                      <LogoTile sponsor={s} />
                      <span>{s.short}</span>
                    </a>
                  </li>
                ))}
              </ul>
            </nav>
          </div>
        </section>

        {sponsors.map((s, i) => (
          <SponsorSection key={s.slug} sponsor={s} index={i} />
        ))}

      </main>

      <footer className="igc-footer">
        <div className="igc-wrap igc-footer__in">
          <p>© 2026 The Issachar Generation · @rccgpa_tig</p>
        </div>
      </footer>
    </div>
  )
}
