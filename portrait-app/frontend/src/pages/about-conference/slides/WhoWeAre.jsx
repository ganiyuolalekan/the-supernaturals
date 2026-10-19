import Icon from '../components/Icon'
import Ornament from '../components/Ornament'
import { RichText, SectionHead } from '../components/Bits'
import data from '../../../data/event/conference.json'

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
    <a className="ev-pill" href={href} target="_blank" rel="noopener noreferrer">{inner}</a>
  ) : (
    <span className="ev-pill">{inner}</span>
  )
}

export default function WhoWeAre() {
  return (
    <section id="who-we-are" className="ev-slide ev-slide--navy" aria-labelledby="who-h">
      <Ornament className="ev-watermark" parallax />
      <div className="ev-wrap">
        <div className="ev-split">
          <div>
            <SectionHead id="who-h" eyebrow={event.hostName} title={story.heading} />
            <div className="ev-prose ev-rise" style={{ '--i': 1 }}>
              {story.paragraphs.map((p, i) => (
                <p key={i}><RichText text={p} /></p>
              ))}
            </div>

            <div className="ev-transition ev-rise" style={{ '--i': 2 }} aria-label={`${story.transition.from} became ${story.transition.to}`}>
              <span className="ev-chip ev-chip--ghost">{story.transition.from}</span>
              <Icon name="arrow-right" size={22} />
              <span className="ev-chip ev-chip--gold">{story.transition.to}</span>
            </div>
          </div>

          <div className="ev-stack">
            <figure className="ev-quote ev-rise" style={{ '--i': 2 }}>
              <blockquote>“{story.quote.text}”</blockquote>
              <figcaption>{story.quote.source}</figcaption>
            </figure>
            <div className="ev-mission ev-rise" style={{ '--i': 3 }}>
              <p className="ev-mission__k">{story.mission.label}</p>
              <p className="ev-mission__v"><em>{story.mission.text}</em></p>
            </div>
          </div>
        </div>

        <div className="ev-connect ev-rise" style={{ '--i': 4 }}>
          <p className="ev-connect__k">Connect</p>
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
