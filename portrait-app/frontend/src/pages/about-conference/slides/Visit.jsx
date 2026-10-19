import Photo from '../components/Photo'
import Icon from '../components/Icon'
import Ornament from '../components/Ornament'
import { Button, SectionHead } from '../components/Bits'
import { telHref } from '../hooks'
import data from '../../../data/event/conference.json'

const { event, visit } = data
const { social } = event

export default function Visit({ registerHref }) {
  return (
    <section id="visit" className="ev-slide ev-slide--navy" aria-labelledby="visit-h">
      <Ornament className="ev-watermark" parallax />
      <div className="ev-wrap">
        <SectionHead id="visit-h" eyebrow="See you there" title={visit.heading} align="center" />

        <ul className="ev-days">
          {visit.days.map((d, i) => (
            <li key={d.label} className="ev-day ev-rise" style={{ '--i': i + 1 }}>
              <p className="ev-day__k">{d.label}</p>
              <p className="ev-day__v">{d.date}</p>
            </li>
          ))}
        </ul>

        <div className="ev-visit__grid">
          <article className="ev-venue ev-rise" style={{ '--i': 2 }}>
            <p className="ev-venue__k"><Icon name="pin" size={18} /> Venue</p>
            <h3 className="ev-h3">{event.venue.name}</h3>
            <p>{event.venue.place} ({event.venue.landmark})</p>
            <Photo
              src={visit.venuePhoto.image}
              alt={visit.venuePhoto.alt}
              label={visit.venuePhoto.label}
              ratio="16 / 9"
            />
          </article>

          <article className="ev-infocard ev-rise" style={{ '--i': 3 }}>
            <p className="ev-infocard__k"><Icon name="bus" size={18} /> Getting there</p>
            <h3 className="ev-h3">{event.transport}</h3>
            <p>Questions? Call us on {event.phone}.</p>
            <Button href={telHref(event.phone)} variant="outline" icon="phone">Call {event.phone}</Button>
          </article>

          <article id="register" className="ev-register ev-rise" style={{ '--i': 4 }}>
            <p className="ev-infocard__k">Register</p>
            <div
              className="ev-qr"
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
              <p className="ev-note">WhatsApp Community link coming soon.</p>
            )}
          </article>
        </div>

        <p className="ev-connect__row ev-rise" style={{ '--i': 5 }}>
          Follow us {social.handle}
          {' · '}
          <a href={social.tiktokUrl} target="_blank" rel="noopener noreferrer">TikTok</a>
          {' · '}
          <a href={social.instagramUrl} target="_blank" rel="noopener noreferrer">Instagram</a>
        </p>

        <p className="ev-sign ev-rise" style={{ '--i': 6 }}>{visit.closingLine}</p>
      </div>
    </section>
  )
}
