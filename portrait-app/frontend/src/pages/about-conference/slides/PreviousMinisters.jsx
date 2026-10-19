import Photo from '../components/Photo'
import { SectionHead } from '../components/Bits'
import data from '../../../data/event/conference.json'

const { previous } = data

export default function PreviousMinisters() {
  return (
    <section id="previous-ministers" className="ev-slide ev-slide--navy" aria-labelledby="previous-h">
      <div className="ev-wrap">
        <div className="ev-split ev-split--wide-left">
          <div>
            <SectionHead id="previous-h" eyebrow="With gratitude" title={previous.heading} />
            <p className="ev-lead ev-lead--italic ev-rise" style={{ '--i': 1 }}><em>{previous.intro}</em></p>

            <ul className="ev-groups">
              {previous.groups.map((g, i) => (
                <li key={g.number} className="ev-group ev-rise" style={{ '--i': i + 2 }}>
                  <p className="ev-group__n" aria-hidden="true">{g.number}</p>
                  <h3 className="ev-group__name">{g.name}</h3>
                  <ul className="ev-chips">
                    {g.people.map((p) => (
                      <li key={p} className="ev-chip">{p}</li>
                    ))}
                  </ul>
                </li>
              ))}
            </ul>
          </div>

          <div className="ev-grid2 ev-grid2--tight ev-rise" style={{ '--i': 3 }}>
            {previous.photos.map((p) => (
              <Photo key={p.label} src={p.image} alt={p.alt} label={p.label} ratio="4 / 5" />
            ))}
          </div>
        </div>

        <p className="ev-closing ev-rise" style={{ '--i': 6 }}><em>{previous.closing}</em></p>
      </div>
    </section>
  )
}
