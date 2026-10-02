import Photo from '../components/Photo'
import SlideDialog from '../components/SlideDialog'
import Icon from '../components/Icon'
import { SectionHead } from '../components/Bits'
import { closeHash, initialsOf, openHash, replaceHash, useDirection } from '../hooks'
import data from '../../../data/igc/conference.json'
import ministers from '../../../data/igc/ministers.json'

const { ministersSection } = data

export default function GuestMinisters({ hash }) {
  const [section, slug] = hash.split('/')
  const index = section === 'ministers' && slug ? ministers.findIndex((m) => m.slug === slug) : -1
  const direction = useDirection(index)
  const open = index >= 0
  const go = (i) => replaceHash(`ministers/${ministers[(i + ministers.length) % ministers.length].slug}`)

  return (
    <section id="ministers" className="igc-slide igc-slide--cream" aria-labelledby="ministers-h">
      <div className="igc-wrap">
        <SectionHead id="ministers-h" eyebrow="IGC 2026" title={ministersSection.heading} align="center">
          <p className="igc-lead igc-rise" style={{ '--i': 1 }}>{ministersSection.intro}</p>
        </SectionHead>

        <ul className="igc-mgrid">
          {ministers.map((m, i) => (
            <li key={m.slug} className="igc-rise" style={{ '--i': (i % 4) + 1 }}>
              <button
                type="button"
                className="igc-mcard"
                onClick={() => openHash(`ministers/${m.slug}`)}
                aria-label={`${m.name}, ${m.role}. Open profile.`}
              >
                <Photo src={m.image} alt={`Portrait of ${m.name}`} label="Portrait" initials={initialsOf(m.name)} ratio="4 / 5" />
                <span className="igc-mcard__name">{m.name}</span>
                <span className="igc-mcard__role">{m.role}</span>
              </button>
            </li>
          ))}
        </ul>
      </div>

      {open && (
        <SlideDialog
          label={ministers[index].name}
          kicker="Guest Minister"
          index={index}
          total={ministers.length}
          direction={direction}
          onPrev={() => go(index - 1)}
          onNext={() => go(index + 1)}
          onClose={() => closeHash('ministers')}
        >
          <MinisterSlide m={ministers[index]} />
        </SlideDialog>
      )}
    </section>
  )
}

function MinisterSlide({ m }) {
  return (
    <div className="igc-minister">
      <Photo
        className="igc-minister__photo"
        src={m.image}
        alt={`Portrait of ${m.name}`}
        label="Portrait"
        initials={initialsOf(m.name)}
        ratio="4 / 5"
        eager
      />
      <div className="igc-minister__text">
        <h2 className="igc-h2 igc-h2--sm">{m.name}</h2>
        <p className="igc-minister__role">{m.role}</p>
        <p className="igc-minister__bio">{m.bio}</p>
        <div>
          <p className="igc-minor-h">Ministry emphasis</p>
          <ul className="igc-chips">
            {m.emphasis.map((e) => (
              <li key={e} className="igc-chip">{e}</li>
            ))}
          </ul>
        </div>
        <aside className="igc-callout">
          <p className="igc-callout__k"><Icon name="star" size={16} /> At IGC 2026</p>
          <p>{m.atIgc}</p>
        </aside>
      </div>
    </div>
  )
}
