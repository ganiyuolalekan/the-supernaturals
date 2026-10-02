import { useEffect, useState } from 'react'

/* ── Hash routing (deep links: #ministers/<slug>, #sponsors/<slug>/<n>) ───── */

const readHash = () => window.location.hash.replace(/^#/, '')

export function useHash() {
  const [hash, setHash] = useState(readHash)
  useEffect(() => {
    const on = () => setHash(readHash())
    window.addEventListener('hashchange', on)
    window.addEventListener('popstate', on)
    window.addEventListener('igc-hash', on)
    return () => {
      window.removeEventListener('hashchange', on)
      window.removeEventListener('popstate', on)
      window.removeEventListener('igc-hash', on)
    }
  }, [])
  return hash
}

const urlFor = (hash) => window.location.pathname + window.location.search + (hash ? `#${hash}` : '')

/** Open a dialog: pushes a history entry so the browser Back button closes it. */
export function openHash(hash) {
  window.history.pushState({ igcDialog: true }, '', urlFor(hash))
  window.dispatchEvent(new Event('igc-hash'))
}

/** Move within an open dialog without adding history entries. */
export function replaceHash(hash) {
  window.history.replaceState(window.history.state, '', urlFor(hash))
  window.dispatchEvent(new Event('igc-hash'))
}

/** Close a dialog: go back if we opened it, otherwise land on its section. */
export function closeHash(sectionId) {
  if (window.history.state?.igcDialog) {
    window.history.back()
  } else {
    window.history.replaceState(null, '', urlFor(sectionId))
    window.dispatchEvent(new Event('igc-hash'))
  }
}

/* ── Page <head> ──────────────────────────────────────────────────────────── */

const FONTS_HREF =
  'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Outfit:wght@500;600;700&family=Kaushan+Script&display=swap'

/**
 * Per-page <head> setup: title, description, language, fonts. Restored on leave.
 * `snap` turns on gentle scroll-snapping between full-height slides (desktop only).
 */
export function usePageHead({ title, description, lang }, { snap = false } = {}) {
  useEffect(() => {
    const root = document.documentElement
    const prevTitle = document.title
    const prevLang = root.lang
    const created = []

    const setMeta = (attr, key, content) => {
      let el = document.head.querySelector(`meta[${attr}="${key}"]`)
      if (!el) {
        el = document.createElement('meta')
        el.setAttribute(attr, key)
        document.head.appendChild(el)
        created.push(el)
      }
      const prev = el.getAttribute('content')
      el.setAttribute('content', content)
      return () => prev !== null && el.setAttribute('content', prev)
    }

    document.title = title
    root.lang = lang
    root.classList.add('igc-page')
    if (snap) root.classList.add('igc-snap')
    const restores = [
      setMeta('name', 'description', description),
      setMeta('property', 'og:title', title),
      setMeta('property', 'og:description', description),
      setMeta('property', 'og:type', 'website'),
    ]

    const link = document.createElement('link')
    link.rel = 'stylesheet'
    link.href = FONTS_HREF
    document.head.appendChild(link)
    created.push(link)

    return () => {
      document.title = prevTitle
      root.lang = prevLang
      root.classList.remove('igc-page', 'igc-snap')
      restores.forEach((r) => r())
      created.forEach((el) => el.remove())
    }
  }, [title, description, lang, snap])
}

/* ── Slide visibility ─────────────────────────────────────────────────────── */

/** Sets data-in on each slide the first time it scrolls into view (once). */
export function useRevealOnce(ids) {
  useEffect(() => {
    const els = ids.map((id) => document.getElementById(id)).filter(Boolean)
    if (!('IntersectionObserver' in window)) {
      els.forEach((el) => el.setAttribute('data-in', ''))
      return undefined
    }
    const io = new IntersectionObserver(
      (entries) => {
        entries.forEach((e) => {
          if (e.isIntersecting) {
            e.target.setAttribute('data-in', '')
            io.unobserve(e.target)
          }
        })
      },
      { threshold: 0.15 },
    )
    els.forEach((el) => io.observe(el))
    return () => io.disconnect()
  }, [ids])
}

/** Index of the slide that currently crosses the middle of the viewport. */
export function useActiveSlide(ids) {
  const [active, setActive] = useState(0)
  useEffect(() => {
    const els = ids.map((id) => document.getElementById(id)).filter(Boolean)
    const io = new IntersectionObserver(
      (entries) => {
        entries.forEach((e) => {
          if (e.isIntersecting) setActive(ids.indexOf(e.target.id))
        })
      },
      { rootMargin: '-45% 0px -50% 0px' },
    )
    els.forEach((el) => io.observe(el))
    return () => io.disconnect()
  }, [ids])
  return active
}

/** Gentle wing parallax, capped at 12px. Disabled for reduced motion. */
export function useWingParallax() {
  useEffect(() => {
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return undefined
    let raf = 0
    const update = () => {
      raf = 0
      document.querySelectorAll('[data-parallax]').forEach((el) => {
        const host = el.closest('.igc-slide')
        if (!host) return
        const r = host.getBoundingClientRect()
        const d = (r.top + r.height / 2 - window.innerHeight / 2) / window.innerHeight
        const y = Math.max(-1, Math.min(1, d)) * 12
        el.style.setProperty('--par', `${y.toFixed(1)}px`)
      })
    }
    const onScroll = () => {
      if (!raf) raf = requestAnimationFrame(update)
    }
    update()
    window.addEventListener('scroll', onScroll, { passive: true })
    window.addEventListener('resize', onScroll)
    return () => {
      window.removeEventListener('scroll', onScroll)
      window.removeEventListener('resize', onScroll)
      if (raf) cancelAnimationFrame(raf)
    }
  }, [])
}

/** 'next' | 'prev' depending on how `index` just changed (drives the slide-in animation). */
export function useDirection(index) {
  const [state, setState] = useState({ index, dir: 'next' })
  if (state.index !== index) setState({ index, dir: index >= state.index ? 'next' : 'prev' })
  return state.dir
}

/* ── Small helpers ────────────────────────────────────────────────────────── */

export const telHref = (s) => `tel:${s.replace(/[^\d+]/g, '')}`

const TITLES = /^(pastor|apostle|minister|dr|mrs|mr)\.?\s+/i
export function initialsOf(name) {
  const words = name.replace(TITLES, '').replace(/[^A-Za-z\s]/g, '').split(/\s+/).filter(Boolean)
  return (words[0]?.[0] ?? '') + (words[words.length - 1]?.[0] ?? '')
}
