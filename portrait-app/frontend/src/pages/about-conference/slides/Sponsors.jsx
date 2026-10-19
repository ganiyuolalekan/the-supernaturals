import Photo from '../components/Photo'
import SlideDialog from '../components/SlideDialog'
import Icon from '../components/Icon'
import { Button, SectionHead } from '../components/Bits'
import { closeHash, openHash, replaceHash, telHref, useDirection } from '../hooks'
import data from '../../../data/event/conference.json'
import sponsors from '../../../data/event/sponsors.json'

const { sponsorsSection } = data

/** Sponsor logo on a clean white tile, never recoloured. */
function LogoTile({ sponsor, size = 'md' }) {
  return (
    <div className={`ev-logotile ev-logotile--${size}`}>
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
    <section id="sponsors" className="ev-slide ev-slide--white" aria-labelledby="sponsors-h">
      <div className="ev-wrap">
        <SectionHead id="sponsors-h" eyebrow="Partners & Sponsors" title={sponsorsSection.heading} align="center">
          <p className="ev-lead ev-rise" style={{ '--i': 1 }}>{sponsorsSection.intro}</p>
        </SectionHead>

        <ul className="ev-sgrid">
          {sponsors.map((s, i) => (
            <li key={s.slug} className="ev-rise" style={{ '--i': (i % 3) + 1 }}>
              <button
                type="button"
                className="ev-scard"
                onClick={() => openHash(`sponsors/${s.slug}`)}
                aria-label={`${s.name}. ${s.tagline} Open slides.`}
              >
                <LogoTile sponsor={s} />
                <span className="ev-scard__name">{s.name}</span>
                <span className="ev-scard__tag">{s.tagline}</span>
                <span className="ev-scard__more">View slides <Icon name="arrow-right" size={16} /></span>
              </button>
            </li>
          ))}
        </ul>

        <p className="ev-cta-line ev-rise" style={{ '--i': 4 }}>{sponsorsSection.cta}</p>
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
    <div className="ev-cover">
      <div className="ev-cover__text">
        <LogoTile sponsor={sponsor} size="lg" />
        <h2 className="ev-h2 ev-h2--sm">{sponsor.name}</h2>
        {sponsor.regNo && <p className="ev-minor-h">{sponsor.regNo}</p>}
        <p className="ev-lead">{sponsor.tagline}</p>
        {sponsor.quote && <p className="ev-quote-inline">“{sponsor.quote}”</p>}
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
    <div className="ev-content">
      <h2 className="ev-h2 ev-h2--sm">{slide.title}</h2>
      {slide.paragraphs && (
        <div className="ev-prose">
          {slide.paragraphs.map((p, i) => <p key={i}>{p}</p>)}
        </div>
      )}
      {slide.pairs && (
        <div className="ev-pairs">
          {slide.pairs.map((p) => (
            <div key={p.label} className="ev-pair">
              <h3 className="ev-h3">{p.label}</h3>
              <p>{p.text}</p>
            </div>
          ))}
        </div>
      )}
      {slide.cards && (
        <ul className="ev-cardgrid">
          {slide.cards.map((c, i) => (
            <li key={c.title} className="ev-minicard">
              <span className="ev-minicard__n" aria-hidden="true">{i + 1}</span>
              <h3 className="ev-h3">{c.title}</h3>
              <p>{c.text}</p>
            </li>
          ))}
        </ul>
      )}
      {slide.chips && (
        <div>
          {slide.chipsTitle && <p className="ev-minor-h">{slide.chipsTitle}</p>}
          <ul className="ev-chips">
            {slide.chips.map((c) => <li key={c} className="ev-chip">{c}</li>)}
          </ul>
        </div>
      )}
    </div>
  )
}

function Gallery({ sponsor, title }) {
  return (
    <div className="ev-content">
      <h2 className="ev-h2 ev-h2--sm">{title}</h2>
      <ul className="ev-gallery">
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
    <div className="ev-content">
      <h2 className="ev-h2 ev-h2--sm">{slide.title}</h2>
      <div className="ev-contact">
        <div className="ev-contact__info">
          {slide.contactPerson && (
            <p><span className="ev-minor-h">Contact</span><br />{slide.contactPerson}</p>
          )}
          {slide.addresses.length > 0 && (
            <div>
              <p className="ev-minor-h">Address</p>
              {slide.addresses.map((a) => (
                <p key={a} className="ev-addr"><Icon name="pin" size={18} /><span>{a}</span></p>
              ))}
            </div>
          )}
          {slide.note && <p className="ev-note">{slide.note}</p>}
          {slide.social.length > 0 && (
            <p><span className="ev-minor-h">Social</span><br />{slide.social.join(' · ')}</p>
          )}
          {slide.pending && <p className="ev-note ev-note--pending">{slide.pending}</p>}
        </div>

        {hasAny > 0 && (
          <div className="ev-contact__actions">
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
