import Icon from '../components/Icon'
import Wings from '../components/Wings'
import { RichText, SectionHead } from '../components/Bits'
import data from '../../../data/igc/conference.json'

const { story, event } = data
const { social } = event

function ConnectItem({ href, icon, children }) {
  const inner = (
    <>
      <Icon name={icon} size={18} />
      <span>{children}</span>
    </>
  )
  return href ? (
    <a className="igc-pill" href={href} target="_blank" rel="noopener noreferrer">{inner}</a>
  ) : (
    <span className="igc-pill">{inner}</span>
  )
}

export default function WhoWeAre() {
  return (
    <section id="who-we-are" className="igc-slide igc-slide--navy" aria-labelledby="who-h">
      <Wings className="igc-watermark" parallax />
      <div className="igc-wrap">
        <div className="igc-split">
          <div>
            <SectionHead id="who-h" eyebrow="The Issachar Generation" title={story.heading} />
            <div className="igc-prose igc-rise" style={{ '--i': 1 }}>
              {story.paragraphs.map((p, i) => (
                <p key={i}><RichText text={p} /></p>
              ))}
            </div>

            <div className="igc-transition igc-rise" style={{ '--i': 2 }} aria-label={`${story.transition.from} became ${story.transition.to}`}>
              <span className="igc-chip igc-chip--ghost">{story.transition.from}</span>
              <Icon name="arrow-right" size={22} />
              <span className="igc-chip igc-chip--gold">{story.transition.to}</span>
            </div>
          </div>

          <div className="igc-stack">
            <figure className="igc-quote igc-rise" style={{ '--i': 2 }}>
              <blockquote>“{story.scripture.text}”</blockquote>
              <figcaption>{story.scripture.reference}</figcaption>
            </figure>
            <div className="igc-mission igc-rise" style={{ '--i': 3 }}>
              <p className="igc-mission__k">{story.mission.label}</p>
              <p className="igc-mission__v"><em>{story.mission.text}</em></p>
            </div>
          </div>
        </div>

        <div className="igc-connect igc-rise" style={{ '--i': 4 }}>
          <p className="igc-connect__k">Connect</p>
          <ConnectItem href={social.tiktokUrl} icon="link">TikTok {social.handle}</ConnectItem>
          <ConnectItem href={social.instagramUrl} icon="link">Instagram {social.handle}</ConnectItem>
          <ConnectItem href={social.youtubeUrl} icon="link">YouTube {social.youtube}</ConnectItem>
          <ConnectItem href={social.facebookUrl} icon="link">Facebook {social.facebook}</ConnectItem>
          <ConnectItem href={social.whatsappUrl} icon="chat">WhatsApp Community</ConnectItem>
        </div>
      </div>
    </section>
  )
}
