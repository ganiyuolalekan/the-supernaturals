import Photo from '../components/Photo'
import Icon from '../components/Icon'
import { RichText, SectionHead } from '../components/Bits'
import data from '../../../data/igc/conference.json'

const { event, about } = data

export default function About() {
  return (
    <section id="about" className="igc-slide igc-slide--white" aria-labelledby="about-h">
      <div className="igc-wrap">
        <div className="igc-split">
          <div>
            <SectionHead id="about-h" eyebrow="IGC 2026" title={about.heading} />
            <div className="igc-prose igc-rise" style={{ '--i': 1 }}>
              {about.paragraphs.map((p, i) => (
                <p key={i}><RichText text={p} /></p>
              ))}
            </div>
          </div>

          <div className="igc-grid2 igc-rise" style={{ '--i': 2 }}>
            {about.photos.map((p) => (
              <Photo key={p.label} src={p.image} alt={p.alt} label={p.label} ratio="4 / 3" />
            ))}
          </div>
        </div>

        <ul className="igc-facts igc-rise" style={{ '--i': 3 }}>
          <li className="igc-fact">
            <Icon name="calendar" size={24} />
            <div>
              <p className="igc-fact__k">Dates</p>
              <p className="igc-fact__v">{event.dateLong}</p>
            </div>
          </li>
          <li className="igc-fact">
            <Icon name="pin" size={24} />
            <div>
              <p className="igc-fact__k">Venue</p>
              <p className="igc-fact__v">{event.venue.name}, {event.venue.place}</p>
            </div>
          </li>
          <li className="igc-fact">
            <Icon name="bus" size={24} />
            <div>
              <p className="igc-fact__k">Getting there</p>
              <p className="igc-fact__v">Free transportation</p>
            </div>
          </li>
          <li className="igc-fact igc-fact--badge">
            <Icon name="star" size={24} />
            <div>
              <p className="igc-fact__k">Milestone</p>
              <p className="igc-fact__v">{event.edition}</p>
            </div>
          </li>
        </ul>
      </div>
    </section>
  )
}
