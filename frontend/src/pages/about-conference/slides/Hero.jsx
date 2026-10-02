import Wings from '../components/Wings'
import Photo, { Logo } from '../components/Photo'
import Icon from '../components/Icon'
import { Button } from '../components/Bits'
import data from '../../../data/igc/conference.json'

const { event, hero } = data

export default function Hero({ registerHref }) {
  return (
    <section id="hero" className="igc-slide igc-slide--cream igc-hero" aria-label="IGC 2026, The Supernaturals">
      <div className="igc-wrap igc-hero__grid">
        <div className="igc-hero__copy">
          <div className="igc-hero__logos igc-rise" style={{ '--i': 0 }}>
            <Logo logo={event.logos.tig} size="lg" />
            <Logo logo={event.logos.rccg} size="lg" />
          </div>

          <div className="igc-hero__titlewrap">
            <Wings className="igc-hero__wings" parallax />
            <h1 className="igc-title igc-rise" style={{ '--i': 1 }}>{event.theme}</h1>
          </div>

          <p className="igc-hero__sub igc-rise" style={{ '--i': 2 }}>
            {event.name} · {event.fullName} · {event.edition}
          </p>

          <p className="igc-rise" style={{ '--i': 3 }}>
            <span className="igc-chip igc-chip--lg">{event.scripture}</span>
          </p>

          <p className="igc-hero__date igc-rise" style={{ '--i': 4 }}>{event.dateShort}</p>
          <p className="igc-hero__venue igc-rise" style={{ '--i': 5 }}>
            <Icon name="pin" size={18} />
            <span>
              {event.venue.name}, {event.venue.place} ({event.venue.landmark})
            </span>
          </p>

          <div className="igc-hero__cta igc-rise" style={{ '--i': 6 }}>
            <Button href={registerHref}>Register</Button>
            <Button href="#ministers" variant="outline" icon="arrow-down">See the ministers</Button>
          </div>
        </div>

        <div className="igc-collage igc-rise" style={{ '--i': 3 }}>
          {hero.collage.map((p, i) => (
            <Photo key={p.label} src={p.image} alt={p.alt} label={p.label} ratio="4 / 5" eager={i < 2} />
          ))}
        </div>
      </div>
    </section>
  )
}
