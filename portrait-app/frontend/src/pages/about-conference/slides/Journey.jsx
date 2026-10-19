import Ornament from '../components/Ornament'
import Photo from '../components/Photo'
import Icon from '../components/Icon'
import { SectionHead } from '../components/Bits'
import data from '../../../data/event/conference.json'

const { journey } = data

export default function Journey() {
  return (
    <section id="journey" className="ev-slide ev-slide--cream" aria-labelledby="journey-h">
      <Ornament className="ev-watermark ev-watermark--right" parallax />
      <div className="ev-wrap">
        <div className="ev-journey__top">
          <SectionHead id="journey-h" eyebrow="Our theme journey" title={journey.heading}>
            <p className="ev-lead ev-rise" style={{ '--i': 1 }}>{journey.intro}</p>
          </SectionHead>
          <Photo
            className="ev-journey__photo ev-rise"
            src={journey.photo.image}
            alt={journey.photo.alt}
            label={journey.photo.label}
            ratio="16 / 9"
          />
        </div>

        <ol className="ev-timeline">
          {journey.steps.map((s, i) => {
            const last = i === journey.steps.length - 1
            return (
              <li
                key={s.title}
                className={`ev-step ev-rise${s.current ? ' is-now' : ''}`}
                style={{ '--i': i + 1 }}
                aria-current={s.current ? 'step' : undefined}
              >
                <div className="ev-step__card">
                  <div className="ev-step__head">
                    <span className="ev-step__n" aria-hidden="true">{i + 1}</span>
                    <h3 className="ev-h3">{s.title}</h3>
                    {s.current && <span className="ev-step__now">Now</span>}
                  </div>
                  <p>{s.text}</p>
                </div>
                {!last && (
                  <span className="ev-step__arrow" style={{ '--i': i }} aria-hidden="true">
                    <Icon name="arrow-right" size={20} className="ev-step__arrow-r" />
                    <Icon name="arrow-down" size={20} className="ev-step__arrow-d" />
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
