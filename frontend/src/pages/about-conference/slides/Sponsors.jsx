import Photo from '../components/Photo'
import SlideDialog from '../components/SlideDialog'
import Icon from '../components/Icon'
import { Button, SectionHead } from '../components/Bits'
import { closeHash, openHash, replaceHash, telHref, useDirection } from '../hooks'
import data from '../../../data/igc/conference.json'
import sponsors from '../../../data/igc/sponsors.json'

const { sponsorsSection } = data

/** Sponsor logo on a clean white tile, never recoloured. */
function LogoTile({ sponsor, size = 'md' }) {
  return (
    <div className={`igc-logotile igc-logotile--${size}`}>
      {sponsor.logo ? (
        <img src={sponsor.logo} alt={`${sponsor.name} logo`} loading="lazy" />
      ) : (
        <span role="img" aria-label={`${sponsor.name} logo (placeholder)`}>Logo</span>
      )}
    </div>
  )
}

export default function Sponsors({ hash }) {
  const [section, slug, n] = hash.split('/')
  const sIndex = section === 'sponsors' && slug ? sponsors.findIndex((s) => s.slug === slug) : -1
  const sponsor = sIndex >= 0 ? sponsors[sIndex] : null
  const slideIndex = sponsor ? Math.min(Math.max((parseInt(n, 10) || 1) - 1, 0), sponsor.slides.length - 1) : -1
  const direction = useDirection(slideIndex)

  const go = (i) => {
    const total = sponsor.slides.length
    replaceHash(`sponsors/${sponsor.slug}/${((i + total) % total) + 1}`)
  }

  return (
    <section id="sponsors" className="igc-slide igc-slide--white" aria-labelledby="sponsors-h">
      <div className="igc-wrap">
        <SectionHead id="sponsors-h" eyebrow="Partners & Sponsors" title={sponsorsSection.heading} align="center">
          <p className="igc-lead igc-rise" style={{ '--i': 1 }}>{sponsorsSection.intro}</p>
        </SectionHead>

        <ul className="igc-sgrid">
          {sponsors.map((s, i) => (
            <li key={s.slug} className="igc-rise" style={{ '--i': (i % 3) + 1 }}>
              <button
                type="button"
                className="igc-scard"
                onClick={() => openHash(`sponsors/${s.slug}`)}
                aria-label={`${s.name}. ${s.tagline} Open slides.`}
              >
                <LogoTile sponsor={s} />
                <span className="igc-scard__name">{s.name}</span>
                <span className="igc-scard__tag">{s.tagline}</span>
                <span className="igc-scard__more">View slides <Icon name="arrow-right" size={16} /></span>
              </button>
            </li>
          ))}
        </ul>

        <p className="igc-cta-line igc-rise" style={{ '--i': 4 }}>{sponsorsSection.cta}</p>
      </div>

      {sponsor && (
        <SlideDialog
          label={sponsor.name}
          kicker={sponsor.name}
          index={slideIndex}
          total={sponsor.slides.length}
          direction={direction}
          onPrev={() => go(slideIndex - 1)}
          onNext={() => go(slideIndex + 1)}
          onClose={() => closeHash('sponsors')}
        >
          <SponsorSlide sponsor={sponsor} slide={sponsor.slides[slideIndex]} />
        </SlideDialog>
      )}
    </section>
  )
}

function SponsorSlide({ sponsor, slide }) {
  if (slide.type === 'cover') return <Cover sponsor={sponsor} />
  if (slide.type === 'images') return <Gallery sponsor={sponsor} title={slide.title} />
  if (slide.type === 'contact') return <Contact sponsor={sponsor} slide={slide} />
  return <Content slide={slide} />
}

function Cover({ sponsor }) {
  return (
    <div className="igc-cover">
      <div className="igc-cover__text">
        <LogoTile sponsor={sponsor} size="lg" />
        <h2 className="igc-h2 igc-h2--sm">{sponsor.name}</h2>
        {sponsor.regNo && <p className="igc-minor-h">{sponsor.regNo}</p>}
        <p className="igc-lead">{sponsor.tagline}</p>
        {sponsor.quote && <p className="igc-quote-inline">“{sponsor.quote}”</p>}
      </div>
      <Photo
        src={sponsor.heroImage}
        alt={`${sponsor.name}, featured image`}
        label="Hero image"
        ratio="4 / 3"
        eager
      />
    </div>
  )
}

function Content({ slide }) {
  return (
    <div className="igc-content">
      <h2 className="igc-h2 igc-h2--sm">{slide.title}</h2>
      {slide.paragraphs && (
        <div className="igc-prose">
          {slide.paragraphs.map((p, i) => <p key={i}>{p}</p>)}
        </div>
      )}
      {slide.pairs && (
        <div className="igc-pairs">
          {slide.pairs.map((p) => (
            <div key={p.label} className="igc-pair">
              <h3 className="igc-h3">{p.label}</h3>
              <p>{p.text}</p>
            </div>
          ))}
        </div>
      )}
      {slide.cards && (
        <ul className="igc-cardgrid">
          {slide.cards.map((c, i) => (
            <li key={c.title} className="igc-minicard">
              <span className="igc-minicard__n" aria-hidden="true">{i + 1}</span>
              <h3 className="igc-h3">{c.title}</h3>
              <p>{c.text}</p>
            </li>
          ))}
        </ul>
      )}
      {slide.chips && (
        <div>
          {slide.chipsTitle && <p className="igc-minor-h">{slide.chipsTitle}</p>}
          <ul className="igc-chips">
            {slide.chips.map((c) => <li key={c} className="igc-chip">{c}</li>)}
          </ul>
        </div>
      )}
    </div>
  )
}

function Gallery({ sponsor, title }) {
  return (
    <div className="igc-content">
      <h2 className="igc-h2 igc-h2--sm">{title}</h2>
      <ul className="igc-gallery">
        {sponsor.images.map((img) => (
          <li key={img.caption}>
            <figure>
              <Photo src={img.image} alt={`${sponsor.name}: ${img.caption}`} label="Photo" ratio="4 / 3" />
              <figcaption>{img.caption}</figcaption>
            </figure>
          </li>
        ))}
      </ul>
    </div>
  )
}

function Contact({ sponsor, slide }) {
  const hasAny = slide.phones.length || slide.emails.length
  return (
    <div className="igc-content">
      <h2 className="igc-h2 igc-h2--sm">{slide.title}</h2>
      <div className="igc-contact">
        <div className="igc-contact__info">
          {slide.contactPerson && (
            <p><span className="igc-minor-h">Contact</span><br />{slide.contactPerson}</p>
          )}
          {slide.addresses.length > 0 && (
            <div>
              <p className="igc-minor-h">Address</p>
              {slide.addresses.map((a) => (
                <p key={a} className="igc-addr"><Icon name="pin" size={18} /><span>{a}</span></p>
              ))}
            </div>
          )}
          {slide.note && <p className="igc-note">{slide.note}</p>}
          {slide.social.length > 0 && (
            <p><span className="igc-minor-h">Social</span><br />{slide.social.join(' · ')}</p>
          )}
          {slide.pending && <p className="igc-note igc-note--pending">{slide.pending}</p>}
        </div>

        {hasAny > 0 && (
          <div className="igc-contact__actions">
            {slide.phones.map((p) => (
              <Button key={p} href={telHref(p)} icon="phone">Call {p}</Button>
            ))}
            {slide.emails.map((e) => (
              <Button key={e} href={`mailto:${e}`} variant="outline" icon="mail">{e}</Button>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
