import Wings from '../components/Wings'
import Photo from '../components/Photo'
import Icon from '../components/Icon'
import { SectionHead } from '../components/Bits'
import data from '../../../data/igc/conference.json'

const { journey } = data

export default function Journey() {
  return (
    <section id="journey" className="igc-slide igc-slide--cream" aria-labelledby="journey-h">
      <Wings className="igc-watermark igc-watermark--right" parallax />
      <div className="igc-wrap">
        <div className="igc-journey__top">
          <SectionHead id="journey-h" eyebrow="Our theme journey" title={journey.heading}>
            <p className="igc-lead igc-rise" style={{ '--i': 1 }}>{journey.intro}</p>
          </SectionHead>
          <Photo
            className="igc-journey__photo igc-rise"
            src={journey.photo.image}
            alt={journey.photo.alt}
            label={journey.photo.label}
            ratio="16 / 9"
          />
        </div>

        <ol className="igc-timeline">
          {journey.steps.map((s, i) => {
            const last = i === journey.steps.length - 1
            return (
              <li
                key={s.title}
                className={`igc-step igc-rise${s.current ? ' is-now' : ''}`}
                style={{ '--i': i + 1 }}
                aria-current={s.current ? 'step' : undefined}
              >
                <div className="igc-step__card">
                  <div className="igc-step__head">
                    <span className="igc-step__n" aria-hidden="true">{i + 1}</span>
                    <h3 className="igc-h3">{s.title}</h3>
                    {s.current && <span className="igc-step__now">Now</span>}
                  </div>
                  <p>{s.text}</p>
                </div>
                {!last && (
                  <span className="igc-step__arrow" style={{ '--i': i }} aria-hidden="true">
                    <Icon name="arrow-right" size={20} className="igc-step__arrow-r" />
                    <Icon name="arrow-down" size={20} className="igc-step__arrow-d" />
                  </span>
                )}
              </li>
            )
          })}
        </ol>
      </div>
    </section>
  )
}
