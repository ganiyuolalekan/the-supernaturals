import Photo from '../components/Photo'
import Icon from '../components/Icon'
import Wings from '../components/Wings'
import { Button, SectionHead } from '../components/Bits'
import { telHref } from '../hooks'
import data from '../../../data/igc/conference.json'

const { event, visit } = data
const { social } = event

export default function Visit({ registerHref }) {
  return (
    <section id="visit" className="igc-slide igc-slide--navy" aria-labelledby="visit-h">
      <Wings className="igc-watermark" parallax />
      <div className="igc-wrap">
        <SectionHead id="visit-h" eyebrow="See you there" title={visit.heading} align="center" />

        <ul className="igc-days">
          {visit.days.map((d, i) => (
            <li key={d.label} className="igc-day igc-rise" style={{ '--i': i + 1 }}>
              <p className="igc-day__k">{d.label}</p>
              <p className="igc-day__v">{d.date}</p>
            </li>
          ))}
        </ul>

        <div className="igc-visit__grid">
          <article className="igc-venue igc-rise" style={{ '--i': 2 }}>
            <p className="igc-venue__k"><Icon name="pin" size={18} /> Venue</p>
            <h3 className="igc-h3">{event.venue.name}</h3>
            <p>{event.venue.place} ({event.venue.landmark})</p>
            <Photo
              src={visit.venuePhoto.image}
              alt={visit.venuePhoto.alt}
              label={visit.venuePhoto.label}
              ratio="16 / 9"
            />
          </article>

          <article className="igc-infocard igc-rise" style={{ '--i': 3 }}>
            <p className="igc-infocard__k"><Icon name="bus" size={18} /> Getting there</p>
            <h3 className="igc-h3">{event.transport}</h3>
            <p>Questions? Call us on {event.phone}.</p>
            <Button href={telHref(event.phone)} variant="outline" icon="phone">Call {event.phone}</Button>
          </article>

          <article id="register" className="igc-register igc-rise" style={{ '--i': 4 }}>
            <p className="igc-infocard__k">Register</p>
            <div
              className="igc-qr"
              role="img"
              aria-label="Registration QR code placeholder"
            >
              {visit.qr.image ? (
                <img src={visit.qr.image} alt="Registration QR code" />
              ) : (
                <span>{visit.qr.label}</span>
              )}
            </div>
            <Button href={registerHref}>Register</Button>
            {social.whatsappUrl ? (
              <Button href={social.whatsappUrl} variant="outline" icon="chat">Join the WhatsApp Community</Button>
            ) : (
              <p className="igc-note">WhatsApp Community link coming soon.</p>
            )}
          </article>
        </div>

        <p className="igc-connect__row igc-rise" style={{ '--i': 5 }}>
          Follow us {social.handle}
          {' · '}
          <a href={social.tiktokUrl} target="_blank" rel="noopener noreferrer">TikTok</a>
          {' · '}
          <a href={social.instagramUrl} target="_blank" rel="noopener noreferrer">Instagram</a>
        </p>

        <p className="igc-sign igc-rise" style={{ '--i': 6 }}>{visit.closingLine}</p>
      </div>
    </section>
  )
}
