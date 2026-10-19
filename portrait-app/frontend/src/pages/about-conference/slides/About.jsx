import Photo from '../components/Photo'
import Icon from '../components/Icon'
import { RichText, SectionHead } from '../components/Bits'
import data from '../../../data/event/conference.json'

const { event, about } = data

export default function About() {
  return (
    <section id="about" className="ev-slide ev-slide--white" aria-labelledby="about-h">
      <div className="ev-wrap">
        <div className="ev-split">
          <div>
            <SectionHead id="about-h" eyebrow={event.name} title={about.heading} />
            <div className="ev-prose ev-rise" style={{ '--i': 1 }}>
              {about.paragraphs.map((p, i) => (
                <p key={i}><RichText text={p} /></p>
              ))}
            </div>
          </div>

          <div className="ev-grid2 ev-rise" style={{ '--i': 2 }}>
            {about.photos.map((p) => (
              <Photo key={p.label} src={p.image} alt={p.alt} label={p.label} ratio="4 / 3" />
            ))}
          </div>
        </div>

        <ul className="ev-facts ev-rise" style={{ '--i': 3 }}>
          <li className="ev-fact">
            <Icon name="calendar" size={24} />
            <div>
              <p className="ev-fact__k">Dates</p>
              <p className="ev-fact__v">{event.dateLong}</p>
            </div>
          </li>
          <li className="ev-fact">
            <Icon name="pin" size={24} />
            <div>
              <p className="ev-fact__k">Venue</p>
              <p className="ev-fact__v">{event.venue.name}, {event.venue.place}</p>
            </div>
          </li>
          <li className="ev-fact">
            <Icon name="bus" size={24} />
            <div>
              <p className="ev-fact__k">Getting there</p>
              <p className="ev-fact__v">{event.transportShort}</p>
            </div>
          </li>
          <li className="ev-fact ev-fact--badge">
            <Icon name="star" size={24} />
            <div>
              <p className="ev-fact__k">Milestone</p>
              <p className="ev-fact__v">{event.edition}</p>
            </div>
          </li>
        </ul>
      </div>
    </section>
  )
}
