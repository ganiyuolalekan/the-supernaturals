import { useState, useEffect, useRef } from 'react'
import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8001'

// ---------------------------------------------------------------------------
// Watermark helper — stamps logo_stamp.png onto the poster
// ---------------------------------------------------------------------------
async function applyWatermark(imageBlob) {
  const imgBitmap  = await createImageBitmap(imageBlob)
  const logoRes    = await fetch('/logo_stamp.png')
  if (!logoRes.ok) return imageBlob   // no stamp file — return clean

  const logoBitmap = await createImageBitmap(await logoRes.blob())
  const W = imgBitmap.width
  const H = imgBitmap.height

  const logoW = Math.round(W * 0.26)
  const logoH = Math.round(logoW * (logoBitmap.height / logoBitmap.width))
  const pad   = Math.round(W * 0.025)
  const logoX = W - logoW - pad
  const logoY = pad

  const canvas = new OffscreenCanvas(W, H)
  const ctx    = canvas.getContext('2d')
  ctx.drawImage(imgBitmap, 0, 0, W, H)
  ctx.globalAlpha = 0.90
  ctx.drawImage(logoBitmap, logoX, logoY, logoW, logoH)
  ctx.globalAlpha = 1.0

  return canvas.convertToBlob({ type: 'image/jpeg', quality: 0.93 })
}

async function fetchBlob(url) {
  const res = await fetch(url)
  if (!res.ok) throw new Error(`fetch failed: ${res.status}`)
  return res.blob()
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------
export default function Result({ data, onReset }) {
  const { poster_url, submission_id, ministerName, ministerTitle, style_id, category } = data

  const [posterDownloaded, setPosterDownloaded] = useState(false)
  const [videoDownloaded,  setVideoDownloaded]  = useState(false)
  const [sharing,          setSharing]          = useState(false)
  const [shared,           setShared]           = useState(false)

  const [videoStatus,  setVideoStatus]  = useState('idle')  // 'idle' | 'generating' | 'ready' | 'failed'
  const [videoUrl,     setVideoUrl]     = useState(null)
  const pollRef = useRef(null)

  // ── Poll for video (only after generation is triggered) ─────────────────
  const startPolling = () => {
    if (pollRef.current) return
    const poll = async () => {
      try {
        const { data: job } = await axios.get(`${API_URL}/video-status/${submission_id}`)
        if (job.status === 'ready') {
          setVideoStatus('ready')
          setVideoUrl(job.video_url)
          clearInterval(pollRef.current)
          pollRef.current = null
        } else if (job.status === 'failed') {
          setVideoStatus('failed')
          clearInterval(pollRef.current)
          pollRef.current = null
        }
      } catch {
        // non-fatal
      }
    }
    poll()
    pollRef.current = setInterval(poll, 6000)
  }

  useEffect(() => () => clearInterval(pollRef.current), [])

  // ── Trigger video generation ─────────────────────────────────────────────
  const handleGenerateVideo = async () => {
    if (!submission_id || videoStatus === 'generating' || videoStatus === 'ready') return
    setVideoStatus('generating')
    try {
      await axios.post(`${API_URL}/generate-video/${submission_id}`)
      startPolling()
    } catch {
      setVideoStatus('failed')
    }
  }

  // ── Download poster ──────────────────────────────────────────────────────
  const handleDownloadPoster = async () => {
    try {
      const raw        = await fetchBlob(poster_url)
      const watermarked = await applyWatermark(raw)
      const url  = URL.createObjectURL(watermarked)
      const a    = document.createElement('a')
      a.href     = url
      a.download = `confirmed-${ministerName?.replace(/\s+/g, '-') || 'minister'}-poster.jpg`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
      setPosterDownloaded(true)
      setTimeout(() => setPosterDownloaded(false), 3000)
    } catch {
      window.open(poster_url, '_blank')
    }
  }

  // ── Download video ───────────────────────────────────────────────────────
  const handleDownloadVideo = async () => {
    if (!videoUrl) return
    try {
      const blob = await fetchBlob(videoUrl)
      const url  = URL.createObjectURL(blob)
      const a    = document.createElement('a')
      a.href     = url
      a.download = `confirmed-${ministerName?.replace(/\s+/g, '-') || 'minister'}-video.mp4`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
      setVideoDownloaded(true)
      setTimeout(() => setVideoDownloaded(false), 3000)
    } catch {
      window.open(videoUrl, '_blank')
    }
  }

  // ── Share poster ─────────────────────────────────────────────────────────
  const handleShare = async () => {
    setSharing(true)
    try {
      const raw        = await fetchBlob(poster_url)
      const watermarked = await applyWatermark(raw)
      const file = new File([watermarked], 'minister-confirmed.jpg', { type: 'image/jpeg' })

      if (navigator.share && navigator.canShare?.({ files: [file] })) {
        await navigator.share({
          title: `${ministerName} — CONFIRMED | The SuperNaturals 2026`,
          text: `${ministerName} is confirmed for The SuperNaturals 2026. 16–18 October. #TheSuperNaturals2026`,
          files: [file],
        })
        setShared(true)
        setTimeout(() => setShared(false), 3000)
      } else {
        handleDownloadPoster()
      }
    } catch (err) {
      if (err.name !== 'AbortError') handleDownloadPoster()
    } finally {
      setSharing(false)
    }
  }

  const categoryLabel = category === 'word' ? 'Word Minister' : 'Music Minister'

  return (
    <div className="min-h-dvh flex flex-col items-center px-4 py-10">

      {/* Header */}
      <div className="w-full max-w-md mb-6 text-center">
        <p className="text-divine-500 text-xs tracking-widest uppercase font-bold mb-1">
          The SuperNaturals 2026
        </p>
        <div className="inline-flex items-center gap-2 px-4 py-1.5 border border-divine-500/40 rounded-full mb-3">
          <span className="w-2 h-2 rounded-full bg-divine-500 animate-pulse" />
          <span className="text-divine-400 text-xs font-bold tracking-widest uppercase">
            CONFIRMED · {categoryLabel}
          </span>
        </div>
        <h2 className="font-display text-2xl font-bold text-white text-glow">
          {ministerName || 'Minister'}
        </h2>
        <p className="text-slate-400 text-sm mt-1">{ministerTitle}</p>
      </div>

      {/* ── Poster ──────────────────────────────────────────────────── */}
      <div className="w-full max-w-md rounded-2xl overflow-hidden glow-gold mb-4 relative">
        <img
          src={poster_url}
          alt={`${ministerName} announcement poster`}
          className="w-full object-cover"
          loading="eager"
        />
        <div className="absolute bottom-3 right-3 bg-black/60 backdrop-blur-sm rounded-lg px-3 py-1.5">
          <p className="text-divine-500 text-xs font-bold tracking-wide">#TheSuperNaturals2026</p>
        </div>
      </div>

      {/* ── Video section ────────────────────────────────────────────── */}
      {videoStatus !== 'idle' && (
        <div className="w-full max-w-md mb-6">
          <div className="bg-cosmic-800/80 border border-slate-700/50 rounded-2xl p-4">
            <div className="flex items-center justify-between mb-3">
              <p className="text-sm font-semibold text-slate-300">5-Sec Announcement Video</p>
              {videoStatus === 'generating' && (
                <span className="flex items-center gap-1.5 text-xs text-divine-400">
                  <span className="w-1.5 h-1.5 rounded-full bg-divine-500 animate-pulse" />
                  Generating…
                </span>
              )}
              {videoStatus === 'ready' && (
                <span className="flex items-center gap-1.5 text-xs text-green-400">
                  <span className="w-1.5 h-1.5 rounded-full bg-green-400" />
                  Ready
                </span>
              )}
              {videoStatus === 'failed' && (
                <span className="text-xs text-red-400">Failed</span>
              )}
            </div>

            {videoStatus === 'generating' && (
              <div className="h-1 bg-slate-700 rounded-full overflow-hidden">
                <div className="h-full w-2/3 bg-gradient-to-r from-divine-600 to-divine-400 rounded-full animate-pulse" />
              </div>
            )}

            {videoStatus === 'ready' && videoUrl && (
              <video
                src={videoUrl}
                autoPlay
                loop
                muted
                playsInline
                className="w-full rounded-xl mt-2"
                style={{ maxHeight: '280px', objectFit: 'cover' }}
              />
            )}

            {videoStatus === 'failed' && (
              <p className="text-xs text-slate-500 mt-1">
                Video generation failed. The poster is still available to download.
              </p>
            )}
          </div>
        </div>
      )}

      {/* ── Actions ──────────────────────────────────────────────────── */}
      <div className="w-full max-w-md flex flex-col gap-3">

        {/* Download poster */}
        <button
          onClick={handleDownloadPoster}
          className="w-full py-4 bg-divine-500 hover:bg-divine-400 text-cosmic-950 font-black text-base rounded-2xl transition-all duration-200 glow-gold hover:scale-[1.02] active:scale-95 flex items-center justify-center gap-2 tracking-wide"
        >
          {posterDownloaded ? '✓ Poster Saved!' : '⬇ DOWNLOAD POSTER'}
        </button>

        {/* Generate / Download video */}
        {videoStatus === 'idle' && (
          <button
            onClick={handleGenerateVideo}
            className="w-full py-4 bg-cosmic-800 border-2 border-divine-500 hover:bg-divine-500/10 text-divine-400 hover:text-divine-300 font-bold text-base rounded-2xl transition-all duration-200 active:scale-95 flex items-center justify-center gap-2"
          >
            🎬 Generate Announcement Video
          </button>
        )}

        {videoStatus !== 'idle' && (
          <button
            onClick={handleDownloadVideo}
            disabled={videoStatus !== 'ready' || !videoUrl}
            className="w-full py-4 bg-cosmic-800 border-2 border-divine-500 hover:bg-divine-500/10 text-divine-400 hover:text-divine-300 disabled:border-slate-700 disabled:text-slate-600 disabled:cursor-not-allowed font-bold text-base rounded-2xl transition-all duration-200 active:scale-95 flex items-center justify-center gap-2"
          >
            {videoStatus === 'generating'
              ? '⏳ Video Generating…'
              : videoStatus === 'failed'
                ? 'Video Unavailable'
                : videoDownloaded
                  ? '✓ Video Saved!'
                  : '⬇ Download Video'
            }
          </button>
        )}

        {/* Share */}
        <button
          onClick={handleShare}
          disabled={sharing}
          className="w-full py-4 bg-transparent border border-slate-600 hover:border-divine-500/60 text-slate-400 hover:text-divine-400 font-bold text-base rounded-2xl transition-all duration-200 active:scale-95 flex items-center justify-center gap-2 disabled:opacity-50"
        >
          {sharing ? 'Preparing…' : shared ? '✓ Shared!' : '↗ Share Poster'}
        </button>

        {/* Tag note */}
        <div className="bg-cosmic-800/60 border border-slate-700/40 rounded-xl px-4 py-3 text-center">
          <p className="text-slate-300 text-sm">
            Tag{' '}
            <span className="text-divine-500 font-semibold">@TheSuperNaturals2026</span>
            {' '}and{' '}
            <span className="text-divine-500 font-semibold">#TheSuperNaturals2026</span>
          </p>
        </div>

        <div className="flex items-center gap-3 my-1">
          <div className="flex-1 h-px bg-slate-800" />
          <span className="text-slate-600 text-xs">or</span>
          <div className="flex-1 h-px bg-slate-800" />
        </div>

        <button
          onClick={onReset}
          className="w-full py-3 text-slate-400 hover:text-white text-sm font-medium transition-colors"
        >
          ← Generate for another minister
        </button>
      </div>
    </div>
  )
}
