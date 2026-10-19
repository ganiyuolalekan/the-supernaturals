import Ornament from '../components/Ornament'
import Photo, { Logo } from '../components/Photo'
import Icon from '../components/Icon'
import { Button } from '../components/Bits'
import data from '../../../data/event/conference.json'

const { event, hero } = data

export default function Hero({ registerHref }) {
  return (
    <section id="hero" className="ev-slide ev-slide--cream ev-hero" aria-label={`${event.name}, ${event.theme}`}>
      <div className="ev-wrap ev-hero__grid">
        <div className="ev-hero__copy">
          <div className="ev-hero__logos ev-rise" style={{ '--i': 0 }}>
            <Logo logo={event.logos.primary} size="lg" />
            <Logo logo={event.logos.secondary} size="lg" />
          </div>

          <div className="ev-hero__titlewrap">
            <Ornament className="ev-hero__mark" parallax />
            <h1 className="ev-title ev-rise" style={{ '--i': 1 }}>{event.theme}</h1>
          </div>

          <p className="ev-hero__sub ev-rise" style={{ '--i': 2 }}>
            {event.name} · {event.fullName} · {event.edition}
          </p>

          <p className="ev-rise" style={{ '--i': 3 }}>
            <span className="ev-chip ev-chip--lg">{event.motto}</span>
          </p>

          <p className="ev-hero__date ev-rise" style={{ '--i': 4 }}>{event.dateShort}</p>
          <p className="ev-hero__venue ev-rise" style={{ '--i': 5 }}>
            <Icon name="pin" size={18} />
            <span>
              {event.venue.name}, {event.venue.place} ({event.venue.landmark})
            </span>
          </p>

          <div className="ev-hero__cta ev-rise" style={{ '--i': 6 }}>
            <Button href={registerHref}>Register</Button>
            <Button href="#ministers" variant="outline" icon="arrow-down">See the ministers</Button>
          </div>
        </div>

        <div className="ev-collage ev-rise" style={{ '--i': 3 }}>
          {hero.collage.map((p, i) => (
            <Photo key={p.label} src={p.image} alt={p.alt} label={p.label} ratio="4 / 5" eager={i < 2} />
          ))}
        </div>
      </div>
    </section>
  )
}
