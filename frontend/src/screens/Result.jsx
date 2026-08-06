import { useEffect, useRef, useState } from 'react'

// ---------------------------------------------------------------------------
// Campaign links — every shared image carries these three calls to action:
// register for the conference, follow the socials, learn more.
// ---------------------------------------------------------------------------
const REGISTER_URL = 'https://forms.gle/BP3b7uYmj3AsZ49TA'
const INSTAGRAM_URL = 'https://www.instagram.com/rccgpa_tig/'
const ABOUT_URL = 'https://theissachargen.carrd.co/'
const SOCIAL_HANDLE = '@rccgpa_tig'

const SHARE_MESSAGE = [
  '✨ I am Supernatural — IGC 2026',
  `Register: ${REGISTER_URL}`,
  `Follow ${SOCIAL_HANDLE} on Instagram & TikTok`,
  `Learn more: ${ABOUT_URL}`,
  '#TheSuperNaturals2026',
].join('\n')

// ---------------------------------------------------------------------------
// Image loaders — HTMLImageElement + <canvas> instead of createImageBitmap /
// OffscreenCanvas. The latter two are unreliable inside in-app browsers
// (Instagram/WhatsApp/Facebook webviews), which is exactly where most people
// open a shared link. These plain-DOM APIs work everywhere.
// ---------------------------------------------------------------------------
function loadImageFromUrl(url) {
  return new Promise((resolve, reject) => {
    const img = new Image()
    img.onload = () => resolve(img)
    img.onerror = () => reject(new Error(`Failed to load image: ${url}`))
    img.src = url
  })
}

async function loadImageFromBlob(blob) {
  const url = URL.createObjectURL(blob)
  try {
    return await loadImageFromUrl(url)
  } finally {
    URL.revokeObjectURL(url)
  }
}

// Promise wrapper for canvas.toBlob, with a toDataURL fallback for the rare
// engine that lacks toBlob.
function canvasToBlob(canvas, type = 'image/jpeg', quality = 0.93) {
  return new Promise((resolve, reject) => {
    if (canvas.toBlob) {
      canvas.toBlob(
        (blob) => (blob ? resolve(blob) : reject(new Error('canvas.toBlob returned null'))),
        type,
        quality,
      )
      return
    }
    try {
      const dataUrl = canvas.toDataURL(type, quality)
      const [meta, b64] = dataUrl.split(',')
      const mime = meta.match(/:(.*?);/)[1]
      const bin = atob(b64)
      const bytes = new Uint8Array(bin.length)
      for (let i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i)
      resolve(new Blob([bytes], { type: mime }))
    } catch (err) {
      reject(err)
    }
  })
}

// ---------------------------------------------------------------------------
// Watermark helper
// Draws the generated portrait onto a canvas, stamps logo_stamp.png in the
// top-right corner, and adds a "Register here" barcode in the bottom-left.
// ---------------------------------------------------------------------------
async function applyWatermark(imageBlob) {
  // Load the portrait, logo and barcode (logo/barcode served from /public)
  const [img, logoImg, barcodeImg] = await Promise.all([
    loadImageFromBlob(imageBlob),
    loadImageFromUrl('/logo_stamp.png'),
    loadImageFromUrl('/registration_barcode.png'),
  ])

  const W = img.naturalWidth || img.width
  const H = img.naturalHeight || img.height

  // Logo sizing: 28% of image width, preserving aspect ratio
  const logoW = Math.round(W * 0.28)
  const logoH = Math.round(logoW * (logoImg.naturalHeight / logoImg.naturalWidth))

  // Top-right, 2.5% padding from each edge
  const pad = Math.round(W * 0.025)
  const logoX = W - logoW - pad
  const logoY = pad

  // Barcode sizing: 17% of image width, preserving aspect ratio
  const barcodePad = Math.round(W * 0.045)
  const barcodeW = Math.round(W * 0.17)
  const barcodeH = Math.round(barcodeW * (barcodeImg.naturalHeight / barcodeImg.naturalWidth))
  const barcodeX = barcodePad
  const barcodeCenterX = barcodeX + barcodeW / 2
  const fontSize = Math.max(12, Math.round(W * 0.018))
  const labelGap = Math.round(fontSize * 0.6)
  // Bottom edge sits at 82% of image height (between center and bottom) so
  // WhatsApp Status's caption/reply overlay near the very bottom of the
  // image doesn't cover it.
  const barcodeBottomY = Math.round(H * 0.82)
  const barcodeY = barcodeBottomY - barcodeH

  // Composite on a standard canvas element
  const canvas = document.createElement('canvas')
  canvas.width = W
  canvas.height = H
  const ctx = canvas.getContext('2d')

  ctx.drawImage(img, 0, 0, W, H)
  ctx.globalAlpha = 0.93   // 7% transparent
  ctx.drawImage(logoImg, logoX, logoY, logoW, logoH)
  ctx.drawImage(barcodeImg, barcodeX, barcodeY, barcodeW, barcodeH)
  ctx.globalAlpha = 1.0    // reset

  // "REGISTER HERE" label, bold and centered above the barcode
  ctx.font = `800 ${fontSize}px sans-serif`
  ctx.textBaseline = 'bottom'
  ctx.textAlign = 'center'
  ctx.fillStyle = '#ffffff'
  ctx.fillText('REGISTER HERE', barcodeCenterX, barcodeY - labelGap)

  // Export as JPEG (smaller file size for sharing)
  return canvasToBlob(canvas, 'image/jpeg', 0.93)
}

// ---------------------------------------------------------------------------
// Fetch the raw image blob (works for both Cloudinary URLs and data URLs)
// ---------------------------------------------------------------------------
async function fetchImageBlob(url) {
  const res = await fetch(url)
  if (!res.ok) throw new Error(`Failed to fetch image: ${res.status}`)
  return res.blob()
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------
export default function Result({ data, onReset }) {
  const { image_url, name } = data
  const [sharing, setSharing] = useState(false)
  const [downloaded, setDownloaded] = useState(false)
  const [shared, setShared] = useState(false)
  // 'idle' | 'copied' | 'manual' — 'manual' reveals the caption for hand-copying
  // when the browser blocks clipboard writes (common in in-app browsers).
  const [copyState, setCopyState] = useState('idle')
  // The finished, shareable image (watermarked when possible). Prepared up
  // front so the Download/Share taps do NO async work — critical on mobile
  // Safari and in-app browsers, which drop the user-gesture "trust" after any
  // `await`, silently killing downloads and blocking navigator.share.
  const [asset, setAsset] = useState(null)  // { url, file }
  const assetRef = useRef(null)

  useEffect(() => {
    let cancelled = false
    let objectUrl
    setAsset(null)
    assetRef.current = null

    ;(async () => {
      let rawBlob
      try {
        rawBlob = await fetchImageBlob(image_url)
      } catch {
        return  // nothing we can do; buttons stay in "Preparing…"
      }

      // Watermark if the browser can; otherwise fall back to the raw image so
      // download/share still work (just without the stamp) rather than failing.
      let outBlob
      try {
        outBlob = await applyWatermark(rawBlob)
      } catch {
        outBlob = rawBlob
      }
      if (cancelled) return

      objectUrl = URL.createObjectURL(outBlob)
      const type = outBlob.type || 'image/jpeg'
      const ext = type.includes('png') ? 'png' : 'jpg'
      const safeName = name?.replace(/\s+/g, '-') || 'me'
      const file = new File([outBlob], `supernatural-portrait-${safeName}.${ext}`, { type })
      const prepared = { url: objectUrl, file }
      assetRef.current = prepared
      setAsset(prepared)
    })()

    return () => {
      cancelled = true
      if (objectUrl) URL.revokeObjectURL(objectUrl)
    }
  }, [image_url, name])

  const copyShareMessage = async () => {
    try {
      await navigator.clipboard.writeText(SHARE_MESSAGE)
      setCopyState('copied')
      setTimeout(() => setCopyState('idle'), 3000)
    } catch {
      setCopyState('manual')
    }
  }

  // Synchronous — must run inside the tap gesture, no awaits before a.click().
  const handleDownload = () => {
    const ready = assetRef.current
    if (!ready) return
    const a = document.createElement('a')
    a.href = ready.url
    a.download = ready.file.name
    a.rel = 'noopener'
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    setDownloaded(true)
    setTimeout(() => setDownloaded(false), 3000)
  }

  const handleShare = async () => {
    const ready = assetRef.current
    const canShareFile =
      !!ready && navigator.canShare?.({ files: [ready.file] })

    // Native share sheet. Call navigator.share FIRST, with no await ahead of
    // it, so the user gesture is still active (iOS requirement).
    if (navigator.share && canShareFile) {
      setSharing(true)
      try {
        // No `title` — some targets (WhatsApp, Telegram) prepend it to the
        // body, which put an extra headline above the caption.
        await navigator.share({ text: SHARE_MESSAGE, files: [ready.file] })
        setShared(true)
        setTimeout(() => setShared(false), 3000)
      } catch (err) {
        // AbortError = user dismissed the sheet; anything else = save instead.
        if (err.name !== 'AbortError') handleDownload()
      } finally {
        setSharing(false)
      }
      return
    }

    // Text-only share (no file support) — still opens the native sheet.
    if (navigator.share) {
      setSharing(true)
      try {
        await navigator.share({ text: SHARE_MESSAGE })
        setShared(true)
        setTimeout(() => setShared(false), 3000)
      } catch (err) {
        if (err.name !== 'AbortError') {
          await copyShareMessage()
          handleDownload()
        }
      } finally {
        setSharing(false)
      }
      return
    }

    // Desktop fallback — copy the caption (links and all) and save the image,
    // so the post can be assembled by hand.
    await copyShareMessage()
    handleDownload()
  }

  return (
    <div className="min-h-dvh flex flex-col items-center px-4 py-10">
      {/* Header */}
      <div className="w-full max-w-md mb-6 text-center">
        <p className="text-divine-500 text-xs tracking-widest uppercase font-semibold mb-1">The SuperNaturals 2026</p>
        <h2 className="font-display text-3xl font-bold text-white text-glow">
          {name ? `${name}'s Portrait` : 'Your Portrait'}
        </h2>
        <p className="text-slate-400 text-sm mt-1">Your supernatural image is ready. Download and share it!</p>
      </div>

      {/* Image */}
      <div className="w-full max-w-md rounded-2xl overflow-hidden glow-gold mb-6 relative">
        <img
          src={image_url}
          alt="Your supernatural portrait"
          className="w-full object-cover"
          loading="eager"
        />
        {/* Overlay badge */}
        <div className="absolute bottom-3 right-3 bg-black/60 backdrop-blur-sm rounded-lg px-3 py-1.5">
          <p className="text-divine-500 text-xs font-semibold tracking-wide">#TheSuperNaturals2026</p>
        </div>
      </div>

      {/* Action buttons */}
      <div className="w-full max-w-md flex flex-col gap-3">
        {/* Download */}
        <button
          onClick={handleDownload}
          disabled={!asset}
          className="w-full py-4 bg-divine-500 hover:bg-divine-400 text-cosmic-950 font-bold text-base rounded-2xl transition-all duration-200 glow-gold hover:scale-[1.02] active:scale-95 flex items-center justify-center gap-2 disabled:opacity-50 disabled:hover:scale-100"
        >
          {!asset ? 'Preparing…' : downloaded ? '✓ Saved!' : '⬇ Download Image'}
        </button>

        {/* Share */}
        <button
          onClick={handleShare}
          disabled={sharing || !asset}
          className="w-full py-4 bg-transparent border-2 border-divine-500 hover:bg-divine-500/10 text-divine-400 hover:text-divine-300 font-bold text-base rounded-2xl transition-all duration-200 active:scale-95 flex items-center justify-center gap-2 disabled:opacity-50"
        >
          {!asset ? 'Preparing…' : sharing ? 'Sharing…' : shared ? '✓ Shared!' : '↗ Share on Instagram'}
        </button>

        {/* Share CTAs — register, follow, learn more */}
        <div className="bg-cosmic-800/60 border border-slate-700/40 rounded-xl px-4 py-4">
          <p className="text-slate-400 text-xs text-center mb-3">
            When you share, bring someone with you 👇
          </p>

          <a
            href={REGISTER_URL}
            target="_blank"
            rel="noopener noreferrer"
            className="block w-full py-3 mb-2 bg-divine-500/15 border border-divine-500/40 hover:bg-divine-500/25 rounded-xl text-center text-divine-400 font-semibold text-sm transition-colors"
          >
            Register for the conference →
          </a>

          <div className="flex gap-2">
            <a
              href={INSTAGRAM_URL}
              target="_blank"
              rel="noopener noreferrer"
              className="flex-1 py-2.5 border border-slate-700 hover:border-slate-500 rounded-xl text-center text-slate-300 text-xs font-medium transition-colors"
            >
              Follow {SOCIAL_HANDLE}
            </a>
            <a
              href={ABOUT_URL}
              target="_blank"
              rel="noopener noreferrer"
              className="flex-1 py-2.5 border border-slate-700 hover:border-slate-500 rounded-xl text-center text-slate-300 text-xs font-medium transition-colors"
            >
              About us
            </a>
          </div>

          <p className="text-slate-500 text-xs text-center mt-3 leading-relaxed">
            Instagram &amp; TikTok: <span className="text-slate-300 font-medium">{SOCIAL_HANDLE}</span> ·
            Use <span className="text-divine-500 font-semibold">#TheSuperNaturals2026</span>
          </p>

          <button
            onClick={copyShareMessage}
            className="w-full mt-3 py-2 text-slate-400 hover:text-white text-xs font-medium transition-colors"
          >
            {copyState === 'copied' ? '✓ Caption copied' : '⧉ Copy caption with links'}
          </button>

          {copyState === 'manual' && (
            <textarea
              readOnly
              rows={6}
              value={SHARE_MESSAGE}
              onFocus={(e) => e.target.select()}
              className="w-full mt-1 px-3 py-2 bg-cosmic-900 border border-slate-700 rounded-lg text-slate-300 text-xs leading-relaxed resize-none"
            />
          )}
        </div>

        {/* Divider */}
        <div className="flex items-center gap-3 my-2">
          <div className="flex-1 h-px bg-slate-700" />
          <span className="text-slate-600 text-xs">or</span>
          <div className="flex-1 h-px bg-slate-700" />
        </div>

        {/* Generate for someone else */}
        <button
          onClick={onReset}
          className="w-full py-3 text-slate-400 hover:text-white text-sm font-medium transition-colors"
        >
          ← Generate for someone else
        </button>
      </div>
    </div>
  )
}
