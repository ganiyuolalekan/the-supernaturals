import Photo from '../components/Photo'
import SlideDialog from '../components/SlideDialog'
import Icon from '../components/Icon'
import { SectionHead } from '../components/Bits'
import { closeHash, initialsOf, openHash, replaceHash, useDirection } from '../hooks'
import data from '../../../data/event/conference.json'
import ministers from '../../../data/event/ministers.json'

const { event, ministersSection } = data

export default function GuestMinisters({ hash }) {
  const [section, slug] = hash.split('/')
  const index = section === 'ministers' && slug ? ministers.findIndex((m) => m.slug === slug) : -1
  const direction = useDirection(index)
  const open = index >= 0
  const go = (i) => replaceHash(`ministers/${ministers[(i + ministers.length) % ministers.length].slug}`)

  return (
    <section id="ministers" className="ev-slide ev-slide--cream" aria-labelledby="ministers-h">
      <div className="ev-wrap">
        <SectionHead id="ministers-h" eyebrow={event.name} title={ministersSection.heading} align="center">
          <p className="ev-lead ev-rise" style={{ '--i': 1 }}>{ministersSection.intro}</p>
        </SectionHead>

        <ul className="ev-mgrid">
          {ministers.map((m, i) => (
            <li key={m.slug} className="ev-rise" style={{ '--i': (i % 4) + 1 }}>
              <button
                type="button"
                className="ev-mcard"
                onClick={() => openHash(`ministers/${m.slug}`)}
                aria-label={`${m.name}, ${m.role}. Open profile.`}
              >
                <Photo src={m.image} alt={`Portrait of ${m.name}`} label="Portrait" initials={initialsOf(m.name)} ratio="4 / 5" />
                <span className="ev-mcard__name">{m.name}</span>
                <span className="ev-mcard__role">{m.role}</span>
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
    <div className="ev-minister">
      <Photo
        className="ev-minister__photo"
        src={m.image}
        alt={`Portrait of ${m.name}`}
        label="Portrait"
        initials={initialsOf(m.name)}
        ratio="4 / 5"
        eager
      />
      <div className="ev-minister__text">
        <h2 className="ev-h2 ev-h2--sm">{m.name}</h2>
        <p className="ev-minister__role">{m.role}</p>
        <p className="ev-minister__bio">{m.bio}</p>
        <div>
          <p className="ev-minor-h">Ministry emphasis</p>
          <ul className="ev-chips">
            {m.emphasis.map((e) => (
              <li key={e} className="ev-chip">{e}</li>
            ))}
          </ul>
        </div>
        <aside className="ev-callout">
          <p className="ev-callout__k"><Icon name="star" size={16} /> At {event.name}</p>
          <p>{m.atEvent}</p>
        </aside>
      </div>
    </div>
  )
}
