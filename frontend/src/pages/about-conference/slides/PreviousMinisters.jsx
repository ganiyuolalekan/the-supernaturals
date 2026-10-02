import Photo from '../components/Photo'
import { SectionHead } from '../components/Bits'
import data from '../../../data/igc/conference.json'

const { previous } = data

export default function PreviousMinisters() {
  return (
    <section id="previous-ministers" className="igc-slide igc-slide--navy" aria-labelledby="previous-h">
      <div className="igc-wrap">
        <div className="igc-split igc-split--wide-left">
          <div>
            <SectionHead id="previous-h" eyebrow="With gratitude" title={previous.heading} />
            <p className="igc-lead igc-lead--italic igc-rise" style={{ '--i': 1 }}><em>{previous.intro}</em></p>

            <ul className="igc-groups">
              {previous.groups.map((g, i) => (
                <li key={g.number} className="igc-group igc-rise" style={{ '--i': i + 2 }}>
                  <p className="igc-group__n" aria-hidden="true">{g.number}</p>
                  <h3 className="igc-group__name">{g.name}</h3>
                  <ul className="igc-chips">
                    {g.people.map((p) => (
                      <li key={p} className="igc-chip">{p}</li>
                    ))}
                  </ul>
                </li>
              ))}
            </ul>
          </div>

          <div className="igc-grid2 igc-grid2--tight igc-rise" style={{ '--i': 3 }}>
            {previous.photos.map((p) => (
              <Photo key={p.label} src={p.image} alt={p.alt} label={p.label} ratio="4 / 5" />
            ))}
          </div>
        </div>

        <p className="igc-closing igc-rise" style={{ '--i': 6 }}><em>{previous.closing}</em></p>
      </div>
    </section>
  )
}
