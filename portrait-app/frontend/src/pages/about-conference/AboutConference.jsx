import { useEffect } from 'react'
import './event.css'
import data from '../../data/event/conference.json'
import { Logo } from './components/Photo'
import Icon from './components/Icon'
import { Button } from './components/Bits'
import { useActiveSlide, useHash, usePageHead, useRevealOnce, useParallax } from './hooks'
import Hero from './slides/Hero'
import About from './slides/About'
import WhoWeAre from './slides/WhoWeAre'
import Journey from './slides/Journey'
import PreviousMinisters from './slides/PreviousMinisters'
import GuestMinisters from './slides/GuestMinisters'
import Sponsors from './slides/Sponsors'
import Visit from './slides/Visit'

const { meta, event } = data

const SLIDES = [
  { id: 'hero', label: 'Hero' },
  { id: 'about', label: 'About the Conference' },
  { id: 'who-we-are', label: 'Who We Are' },
  { id: 'journey', label: 'Conference Order' },
  { id: 'previous-ministers', label: 'Previous Ministers' },
  { id: 'ministers', label: 'Guest Ministers 2026' },
  { id: 'sponsors', label: 'Partners & Sponsors' },
  { id: 'visit', label: 'Plan Your Visit' },
]
const IDS = SLIDES.map((s) => s.id)

/** ←/→ (and ↑/↓ when the slide fits the screen) move between slides. */
function useSlideKeys(active) {
  useEffect(() => {
    const onKey = (e) => {
      if (e.defaultPrevented || e.altKey || e.ctrlKey || e.metaKey) return
      if (document.querySelector('.ev-dialog')) return
      const t = e.target
      if (t instanceof HTMLElement && t.closest('input, textarea, select, [contenteditable="true"]')) return

      let dir = 0
      if (e.key === 'ArrowRight') dir = 1
      else if (e.key === 'ArrowLeft') dir = -1
      else if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
        const el = document.getElementById(IDS[active])
        // Only take over vertical arrows when the slide fits on screen; otherwise let it scroll.
        if (el && el.offsetHeight > window.innerHeight + 2) return
        dir = e.key === 'ArrowDown' ? 1 : -1
      }
      if (!dir) return
      const next = IDS[Math.min(Math.max(active + dir, 0), IDS.length - 1)]
      e.preventDefault()
      document.getElementById(next)?.scrollIntoView({ behavior: 'smooth', block: 'start' })
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [active])
}

export default function AboutConference() {
  usePageHead(meta, { snap: true })
  useParallax()
  useRevealOnce(IDS)
  const hash = useHash()
  const active = useActiveSlide(IDS)
  useSlideKeys(active)

  // Deep links (#sponsors/sponsor-1, #journey): scroll to the section once content has mounted.
  useEffect(() => {
    const id = window.location.hash.replace(/^#/, '').split('/')[0]
    if (id && IDS.includes(id)) document.getElementById(id)?.scrollIntoView({ block: 'start' })
  }, [])

  const registerHref = event.registerUrl || '#register'
  const progress = ((active + 1) / SLIDES.length) * 100

  return (
    <div className="ev" lang={meta.lang}>
      <a className="ev-skip" href="#main">Skip to main content</a>

      <header className="ev-header">
        <div className="ev-header__in">
          <a className="ev-header__logos" href="#hero" aria-label={`${event.name}, back to the top`}>
            <Logo logo={event.logos.primary} />
            <Logo logo={event.logos.secondary} />
            <span className="ev-header__name">{event.name}</span>
          </a>
          <Button href={registerHref} className="ev-btn--sm">Register</Button>
        </div>
        <div
          className="ev-progressbar"
          role="progressbar"
          aria-label="Page progress"
          aria-valuemin={1}
          aria-valuemax={SLIDES.length}
          aria-valuenow={active + 1}
          aria-valuetext={`Slide ${active + 1} of ${SLIDES.length}: ${SLIDES[active].label}`}
        >
          <span style={{ width: `${progress}%` }} />
        </div>
      </header>

      <nav className="ev-dotsnav" aria-label="Slides">
        <ol>
          {SLIDES.map((s, i) => (
            <li key={s.id}>
              <a
                href={`#${s.id}`}
                aria-label={`Slide ${i + 1} of ${SLIDES.length}: ${s.label}`}
                aria-current={i === active ? 'true' : undefined}
                className={i === active ? 'is-active' : ''}
              >
                <span className="ev-dotsnav__tip" aria-hidden="true">{s.label}</span>
              </a>
            </li>
          ))}
        </ol>
      </nav>

      <main id="main">
        <Hero registerHref={registerHref} />
        <About />
        <WhoWeAre />
        <Journey />
        <PreviousMinisters />
        <GuestMinisters hash={hash} />
        <Sponsors hash={hash} />
        <Visit registerHref={registerHref} />
      </main>

      <footer className="ev-footer">
        <div className="ev-wrap ev-footer__in">
          <p>
            © 2026 {event.host.split(',')[0]} · {event.social.handle}
          </p>
          <a className="ev-btn ev-btn--ghost ev-btn--sm" href="#hero">
            Back to top <Icon name="arrow-up" size={18} />
          </a>
        </div>
      </footer>
    </div>
  )
}
