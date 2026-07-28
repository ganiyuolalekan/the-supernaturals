import { useState } from 'react'

// ---------------------------------------------------------------------------
// Watermark helper
// Draws the generated portrait onto a canvas, stamps logo_stamp.png in the
// top-right corner, and adds a "Register here" barcode in the bottom-left.
// ---------------------------------------------------------------------------
async function applyWatermark(imageBlob) {
  // 1. Load the source image
  const imgBitmap = await createImageBitmap(imageBlob)

  // 2. Load the logo and barcode (served from /public)
  const logoRes = await fetch('/logo_stamp.png')
  const logoBitmap = await createImageBitmap(await logoRes.blob())

  const barcodeRes = await fetch('/registration_barcode.png')
  const barcodeBitmap = await createImageBitmap(await barcodeRes.blob())

  const W = imgBitmap.width
  const H = imgBitmap.height

  // Logo sizing: 28% of image width, preserving aspect ratio
  const logoW = Math.round(W * 0.28)
  const logoH = Math.round(logoW * (logoBitmap.height / logoBitmap.width))

  // Top-right, 2.5% padding from each edge
  const pad = Math.round(W * 0.025)
  const logoX = W - logoW - pad
  const logoY = pad

  // Barcode sizing: 17% of image width, preserving aspect ratio
  const barcodePad = Math.round(W * 0.045)
  const barcodeW = Math.round(W * 0.17)
  const barcodeH = Math.round(barcodeW * (barcodeBitmap.height / barcodeBitmap.width))
  const barcodeX = barcodePad
  const barcodeCenterX = barcodeX + barcodeW / 2
  const fontSize = Math.max(12, Math.round(W * 0.018))
  const labelGap = Math.round(fontSize * 0.6)
  const barcodeY = H - barcodePad - barcodeH

  // 3. Composite on an off-screen canvas
  const canvas = new OffscreenCanvas(W, H)
  const ctx = canvas.getContext('2d')

  ctx.drawImage(imgBitmap, 0, 0, W, H)
  ctx.globalAlpha = 0.93   // 7% transparent
  ctx.drawImage(logoBitmap, logoX, logoY, logoW, logoH)
  ctx.drawImage(barcodeBitmap, barcodeX, barcodeY, barcodeW, barcodeH)
  ctx.globalAlpha = 1.0    // reset

  // "REGISTER HERE" label, bold and centered above the barcode
  ctx.font = `800 ${fontSize}px sans-serif`
  ctx.textBaseline = 'bottom'
  ctx.textAlign = 'center'
  ctx.fillStyle = '#ffffff'
  ctx.fillText('REGISTER HERE', barcodeCenterX, barcodeY - labelGap)

  // 4. Export as JPEG (smaller file size for sharing)
  return canvas.convertToBlob({ type: 'image/jpeg', quality: 0.93 })
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

  const isDataUrl = image_url?.startsWith('data:')

  const handleDownload = async () => {
    try {
      const rawBlob = await fetchImageBlob(image_url)
      const watermarked = await applyWatermark(rawBlob)

      const url = URL.createObjectURL(watermarked)
      const a = document.createElement('a')
      a.href = url
      a.download = `supernatural-portrait-${name?.replace(/\s+/g, '-') || 'me'}.jpg`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)

      setDownloaded(true)
      setTimeout(() => setDownloaded(false), 3000)
    } catch {
      // Fallback: open in new tab without watermark
      window.open(image_url, '_blank')
    }
  }

  const handleShare = async () => {
    setSharing(true)
    try {
      let file
      try {
        const rawBlob = await fetchImageBlob(image_url)
        const watermarked = await applyWatermark(rawBlob)
        file = new File([watermarked], 'supernatural-portrait.jpg', { type: 'image/jpeg' })
      } catch {
        // Can't watermark — will fall back to URL share
      }

      if (navigator.share) {
        const shareData = {
          title: 'My Supernatural Portrait — The SuperNaturals 2026',
          text: '✨ I am Supernatural! Tag us @TheSuperNaturals2026 and use #TheSuperNaturals2026',
          ...(file && navigator.canShare?.({ files: [file] }) ? { files: [file] } : {}),
        }
        await navigator.share(shareData)
        setShared(true)
        setTimeout(() => setShared(false), 3000)
      } else {
        // Desktop fallback — copy URL or download watermarked file
        if (!isDataUrl) {
          await navigator.clipboard.writeText(image_url)
          alert('Image URL copied to clipboard! Paste it to share.')
        } else {
          handleDownload()
        }
      }
    } catch (err) {
      if (err.name !== 'AbortError') {
        handleDownload()
      }
    } finally {
      setSharing(false)
    }
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
          className="w-full py-4 bg-divine-500 hover:bg-divine-400 text-cosmic-950 font-bold text-base rounded-2xl transition-all duration-200 glow-gold hover:scale-[1.02] active:scale-95 flex items-center justify-center gap-2"
        >
          {downloaded ? '✓ Saved!' : '⬇ Download Image'}
        </button>

        {/* Share */}
        <button
          onClick={handleShare}
          disabled={sharing}
          className="w-full py-4 bg-transparent border-2 border-divine-500 hover:bg-divine-500/10 text-divine-400 hover:text-divine-300 font-bold text-base rounded-2xl transition-all duration-200 active:scale-95 flex items-center justify-center gap-2 disabled:opacity-50"
        >
          {sharing ? 'Preparing…' : shared ? '✓ Shared!' : '↗ Share on Instagram'}
        </button>

        {/* Tag instruction */}
        <div className="bg-cosmic-800/60 border border-slate-700/40 rounded-xl px-4 py-3 text-center">
          <p className="text-slate-300 text-sm">
            Tag us <span className="text-divine-500 font-semibold">@TheSuperNaturals2026</span> and use{' '}
            <span className="text-divine-500 font-semibold">#TheSuperNaturals2026</span>
          </p>
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
