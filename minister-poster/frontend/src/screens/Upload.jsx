import { EVENT } from '../config/event'

import { useState, useRef, useCallback } from 'react'
import axios from 'axios'
import StylePicker from '../components/StylePicker'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8001'

const PHOTO_TIPS = [
  'Clear front-facing portrait, face visible',
  'Good lighting — no heavy shadows on face',
  'Single person only',
  'JPEG or PNG, under 5 MB',
  'Minimum 512 × 512 pixels',
]

const PROGRESS_MSGS = [
  'Uploading reference photo…',
  'Reading your reference photo…',
  'Setting the scene…',
  'Composing the announcement portrait…',
  'Adding the CONFIRMED overlay…',
  'Almost ready — polishing the final light…',
]

export default function Upload({ onResult, onBack }) {
  const [ministerName,  setMinisterName]  = useState('')
  const [ministerTitle, setMinisterTitle] = useState('')
  const [category,      setCategory]      = useState(EVENT.groups[0].id)
  const [selectedStyle, setSelectedStyle] = useState(null)
  const [imageFile,     setImageFile]     = useState(null)
  const [preview,       setPreview]       = useState(null)
  const [dragging,      setDragging]      = useState(false)
  const [loading,       setLoading]       = useState(false)
  const [progressIdx,   setProgressIdx]   = useState(0)
  const [error,         setError]         = useState(null)

  const fileInputRef     = useRef(null)
  const progressTimerRef = useRef(null)

  const handleFile = (file) => {
    if (!file) return
    setError(null)
    setImageFile(file)
    const reader = new FileReader()
    reader.onload = (e) => setPreview(e.target.result)
    reader.readAsDataURL(file)
  }

  const onFileChange = (e) => handleFile(e.target.files[0])

  const onDrop = useCallback((e) => {
    e.preventDefault()
    setDragging(false)
    const file = e.dataTransfer.files[0]
    if (file?.type?.startsWith('image/')) handleFile(file)
  }, [])

  const onDragOver  = (e) => { e.preventDefault(); setDragging(true) }
  const onDragLeave = () => setDragging(false)

  const handleCategoryChange = (cat) => {
    setCategory(cat)
    setSelectedStyle(null)  // reset style when switching category
  }

  const startProgress = () => {
    let idx = 0
    setProgressIdx(0)
    progressTimerRef.current = setInterval(() => {
      idx = (idx + 1) % PROGRESS_MSGS.length
      setProgressIdx(idx)
    }, 4500)
  }

  const stopProgress = () => clearInterval(progressTimerRef.current)

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!ministerName.trim())  { setError('Enter the minister\'s name.');   return }
    if (!imageFile)            { setError('Please upload a photo.');        return }
    if (!selectedStyle)        { setError('Please select a poster style.'); return }

    setLoading(true)
    setError(null)
    startProgress()

    const formData = new FormData()
    formData.append('minister_name',  ministerName.trim())
    formData.append('minister_title', ministerTitle.trim())
    formData.append('style_id',       selectedStyle.id)
    formData.append('image',          imageFile)

    try {
      const { data } = await axios.post(`${API_URL}/generate`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        timeout: 180_000,   // 3 min — portrait generation can be slow
      })
      stopProgress()
      onResult({ ...data, ministerName: ministerName.trim(), ministerTitle: ministerTitle.trim() })
    } catch (err) {
      stopProgress()
      const detail = err.response?.data?.detail
      let msg
      if (typeof detail === 'object') {
        const debug = detail.debug || ''
        if (debug.includes('BILLING_REQUIRED')) {
          msg = 'Image generation requires billing on your Google AI account. Enable at aistudio.google.com/billing.'
        } else {
          msg = detail.message
          if (debug && import.meta.env.DEV) msg += `\n\nDebug: ${debug}`
        }
      } else {
        msg = detail || 'Something went wrong. Please try again.'
      }
      setError(msg)
      setLoading(false)
    }
  }

  const canSubmit = !loading && ministerName.trim() && imageFile && selectedStyle

  return (
    <div className="min-h-dvh flex flex-col items-center px-4 py-10">
      {/* Header */}
      <div className="w-full max-w-md mb-8">
        <button
          onClick={onBack}
          className="text-slate-400 hover:text-white text-sm flex items-center gap-1 mb-6 transition-colors"
        >
          ← Back
        </button>
        <p className="text-divine-500 text-xs tracking-widest uppercase font-bold mb-1">
          {EVENT.name}
        </p>
        <h2 className="font-display text-3xl font-bold text-white">
          New Signing
        </h2>
        <p className="text-slate-400 text-sm mt-1">
          Generate the announcement poster and video for a confirmed {EVENT.guest.toLowerCase()}.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="w-full max-w-md flex flex-col gap-6">

        {/* ── Category ─────────────────────────── */}
        <div>
          <label className="block text-sm font-semibold text-slate-300 mb-3">
            Category
          </label>
          <div className="grid grid-cols-2 gap-3">
            {EVENT.groups.map(({ id, label, sub, icon }) => (
              <button
                key={id}
                type="button"
                onClick={() => handleCategoryChange(id)}
                className={`
                  flex flex-col items-center gap-2 py-5 rounded-xl border-2 font-bold transition-all duration-200
                  ${category === id
                    ? 'border-divine-500 bg-divine-500/10 text-divine-400 glow-gold-sm'
                    : 'border-slate-700 bg-cosmic-800 text-slate-400 hover:border-slate-500'
                  }
                `}
              >
                <span className="text-2xl">{icon}</span>
                <span className="text-sm tracking-widest">{label}</span>
                <span className={`text-[10px] font-normal ${category === id ? 'text-divine-500/80' : 'text-slate-600'}`}>{sub}</span>
              </button>
            ))}
          </div>
        </div>

        {/* ── Poster Style ──────────────────────────────── */}
        <StylePicker
          category={category}
          selected={selectedStyle}
          onChange={setSelectedStyle}
        />

        {/* ── Minister Name ─────────────────────────────── */}
        <div>
          <label className="block text-sm font-semibold text-slate-300 mb-2">
            {EVENT.guest} Name
          </label>
          <input
            type="text"
            value={ministerName}
            onChange={(e) => setMinisterName(e.target.value)}
            placeholder="e.g. Jane Doe"
            maxLength={120}
            required
            className="w-full px-4 py-3 bg-cosmic-800 border border-slate-700 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:border-divine-500 focus:ring-1 focus:ring-divine-500 transition-colors"
          />
        </div>

        {/* ── Minister Title ────────────────────────────── */}
        <div>
          <label className="block text-sm font-semibold text-slate-300 mb-2">
            {EVENT.guest} Title / Organisation <span className="text-slate-500 font-normal">(optional)</span>
          </label>
          <input
            type="text"
            value={ministerTitle}
            onChange={(e) => setMinisterTitle(e.target.value)}
            placeholder="e.g. Founder, Example Co."
            maxLength={200}
            className="w-full px-4 py-3 bg-cosmic-800 border border-slate-700 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:border-divine-500 focus:ring-1 focus:ring-divine-500 transition-colors"
          />
        </div>

        {/* ── Photo Upload ──────────────────────────────── */}
        <div>
          <label className="block text-sm font-semibold text-slate-300 mb-2">
            {EVENT.guest}'s Photo
          </label>

          <div
            onClick={() => fileInputRef.current?.click()}
            onDrop={onDrop}
            onDragOver={onDragOver}
            onDragLeave={onDragLeave}
            className={`
              relative cursor-pointer rounded-2xl border-2 border-dashed transition-all duration-200 overflow-hidden
              ${dragging
                ? 'border-divine-500 bg-divine-500/10'
                : 'border-slate-600 hover:border-slate-400 bg-cosmic-800'
              }
              ${preview ? 'h-72' : 'h-48 flex flex-col items-center justify-center'}
            `}
          >
            {preview ? (
              <>
                <img src={preview} alt="Preview" className="w-full h-full object-cover" />
                <div className="absolute inset-0 bg-black/50 flex items-center justify-center opacity-0 hover:opacity-100 transition-opacity">
                  <span className="text-white font-semibold text-sm">Click to change photo</span>
                </div>
              </>
            ) : (
              <>
                <div className="text-4xl mb-2">📷</div>
                <p className="text-slate-300 font-semibold text-sm">Tap to upload or drag & drop</p>
                <p className="text-slate-500 text-xs mt-1">JPEG or PNG, max 5 MB</p>
              </>
            )}
          </div>

          <input
            ref={fileInputRef}
            type="file"
            accept="image/jpeg,image/jpg,image/png"
            className="hidden"
            onChange={onFileChange}
          />
        </div>

        {/* ── Photo tips ────────────────────────────────── */}
        <div className="bg-cosmic-800/60 border border-slate-700/50 rounded-xl p-4">
          <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3">
            Photo Tips
          </p>
          <ul className="space-y-1.5">
            {PHOTO_TIPS.map((tip, i) => (
              <li key={i} className="flex items-start gap-2 text-xs text-slate-400">
                <span className="text-divine-500 mt-0.5 shrink-0">✓</span>
                {tip}
              </li>
            ))}
          </ul>
        </div>

        {/* ── Error ────────────────────────────────────── */}
        {error && (
          <div className="bg-red-900/40 border border-red-700/50 rounded-xl px-4 py-3 text-red-300 text-sm">
            {error}
          </div>
        )}

        {/* ── Submit ───────────────────────────────────── */}
        <button
          type="submit"
          disabled={!canSubmit}
          className="w-full py-4 bg-divine-500 hover:bg-divine-400 disabled:bg-slate-700 disabled:cursor-not-allowed text-cosmic-950 disabled:text-slate-400 font-black text-base rounded-2xl transition-all duration-200 glow-gold disabled:shadow-none hover:scale-[1.02] active:scale-95 tracking-wide"
        >
          {loading
            ? 'Generating…'
            : !selectedStyle
              ? 'Select a Poster Style to Continue'
              : 'GENERATE ANNOUNCEMENT POSTER ⚔'
          }
        </button>
      </form>

      {/* ── Loading overlay ───────────────────────────── */}
      {loading && (
        <div className="fixed inset-0 bg-cosmic-950/92 backdrop-blur-sm z-50 flex flex-col items-center justify-center gap-8 px-6">
          <div className="relative w-24 h-24">
            <div className="absolute inset-0 rounded-full border-4 border-slate-700" />
            <div className="absolute inset-0 rounded-full border-4 border-divine-500 border-t-transparent animate-spin" />
            <div className="absolute inset-3 rounded-full border-2 border-divine-500/40 border-b-transparent animate-spin-slow" style={{ animationDirection: 'reverse' }} />
            <div className="absolute inset-0 flex items-center justify-center text-2xl">⚔</div>
          </div>

          <div className="text-center">
            <div className="confirmed-stamp text-divine-500 text-xl font-black tracking-widest mb-3">
              CONFIRMED
            </div>
            <p className="text-divine-400 font-semibold text-lg animate-pulse-slow">
              {PROGRESS_MSGS[progressIdx]}
            </p>
            <p className="text-slate-500 text-sm mt-2">
              Poster takes 20–40 seconds. Video starts in background after.
            </p>
          </div>

          <div className="w-64 h-1 bg-slate-800 rounded-full overflow-hidden">
            <div className="h-full bg-gradient-to-r from-divine-600 to-divine-400 rounded-full animate-pulse w-3/4" />
          </div>
        </div>
      )}
    </div>
  )
}
