import { useState, useRef, useCallback, useEffect } from 'react'
import axios from 'axios'
import ScenePicker from '../components/ScenePicker'
import { findScene } from '../data/scenes'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const REQUIREMENTS = [
  'Front-facing photo, face clearly visible',
  'Well-lit — no heavy shadows on your face',
  'Single person only (no group photos)',
  'No sunglasses or face masks',
  'JPEG or PNG, under 5 MB',
  'Minimum 512 × 512 pixels',
]

const PROGRESS_MESSAGES = [
  'Uploading your photo…',
  'Sending to the supernatural realm…',
  'Applying divine transformation…',
  'Placing the angelic presence…',
  'Adding the finishing light…',
  'Almost ready…',
]

export default function Upload({ onResult, onBack }) {
  const [imageFile, setImageFile] = useState(null)
  const [preview, setPreview] = useState(null)
  const [dragging, setDragging] = useState(false)
  const [loading, setLoading] = useState(false)
  const [progressIdx, setProgressIdx] = useState(0)
  const [error, setError] = useState(null)
  const [selectedScene, setSelectedScene] = useState(null)
  const [activeScene, setActiveScene] = useState(null) // { active_scene_id, schedule } from /active-scene
  const [customPrompt, setCustomPrompt] = useState('')
  const fileInputRef = useRef(null)
  const progressTimerRef = useRef(null)

  useEffect(() => {
    axios.get(`${API_URL}/active-scene`)
      .then(({ data }) => {
        setActiveScene(data)
        setSelectedScene(findScene(data.active_scene_id))
      })
      .catch(() => {
        // Backend still enforces the active scene — the picker just falls
        // back to showing every scene unlocked if this call fails.
      })
  }, [])

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
    if (file && (file.type.startsWith('image/'))) {
      handleFile(file)
    }
  }, [])

  const onDragOver = (e) => { e.preventDefault(); setDragging(true) }
  const onDragLeave = () => setDragging(false)

  const startProgressCycle = () => {
    let idx = 0
    setProgressIdx(0)
    progressTimerRef.current = setInterval(() => {
      idx = (idx + 1) % PROGRESS_MESSAGES.length
      setProgressIdx(idx)
    }, 4000)
  }

  const stopProgressCycle = () => {
    clearInterval(progressTimerRef.current)
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!imageFile) { setError('Please select a photo.'); return }
    if (!selectedScene) { setError('Please select a scene below.'); return }

    setLoading(true)
    setError(null)
    startProgressCycle()

    const formData = new FormData()
    formData.append('image', imageFile)
    formData.append('scene_id', selectedScene.id)
    if (customPrompt.trim()) {
      formData.append('custom_prompt', customPrompt.trim())
    }

    try {
      const { data } = await axios.post(`${API_URL}/generate`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        timeout: 120_000,
      })
      stopProgressCycle()
      onResult({ ...data })
    } catch (err) {
      stopProgressCycle()
      const detail = err.response?.data?.detail
      let msg
      if (typeof detail === 'object') {
        const debug = detail.debug || ''
        if (debug.includes('BILLING_REQUIRED')) {
          msg = 'Image generation requires billing to be enabled on your Google AI account. Enable it at aistudio.google.com/billing — cost is ~$0.04 per image.'
        } else {
          msg = detail.message
          if (debug && import.meta.env.DEV) {
            msg += `\n\nDebug: ${debug}`
          }
        }
      } else {
        msg = detail || 'Something went wrong. Please try again.'
      }
      setError(msg)
      setLoading(false)
    }
  }

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
        <p className="text-divine-500 text-xs tracking-widest uppercase font-semibold mb-1">The SuperNaturals 2026</p>
        <h2 className="font-display text-3xl font-bold text-white">Create Your Portrait</h2>
        <p className="text-slate-400 text-sm mt-1">Upload your photo and receive your supernatural image.</p>
      </div>

      <form onSubmit={handleSubmit} className="w-full max-w-md flex flex-col gap-5">
        {/* Photo upload */}
        <div>
          <label className="block text-sm font-semibold text-slate-300 mb-2">Your Photo</label>

          {/* Drop zone */}
          <div
            onClick={() => fileInputRef.current?.click()}
            onDrop={onDrop}
            onDragOver={onDragOver}
            onDragLeave={onDragLeave}
            className={`relative cursor-pointer rounded-2xl border-2 border-dashed transition-all duration-200 overflow-hidden
              ${dragging ? 'border-divine-500 bg-divine-500/10' : 'border-slate-600 hover:border-slate-400 bg-cosmic-800'}
              ${preview ? 'h-72' : 'h-48 flex flex-col items-center justify-center'}`}
          >
            {preview ? (
              <>
                <img src={preview} alt="Preview" className="w-full h-full object-cover" />
                <div className="absolute inset-0 bg-black/40 flex items-center justify-center opacity-0 hover:opacity-100 transition-opacity">
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

        {/* Scene picker */}
        <ScenePicker
          selected={selectedScene}
          onChange={setSelectedScene}
          activeSceneId={activeScene?.active_scene_id}
          schedule={activeScene?.schedule}
        />

        {/* Custom prompt */}
        <div>
          <div className="flex items-baseline justify-between mb-2">
            <label className="block text-sm font-semibold text-slate-300">
              Add Your Twist{' '}
              <span className="text-slate-500 font-normal">(optional)</span>
            </label>
            <span className={`text-xs ${customPrompt.length > 450 ? 'text-amber-400' : 'text-slate-600'}`}>
              {customPrompt.length}/500
            </span>
          </div>
          <p className="text-xs text-slate-500 mb-2 leading-relaxed">
            Personalize anything — clothing, objects, motion, extra people, animals, or details in the scene.
            The wings and divine light always stay. Everything else is open to your direction.
            Examples: <em className="text-slate-400">"wearing a traditional Yoruba agbada"</em>, <em className="text-slate-400">"a white dove landing on my shoulder"</em>, <em className="text-slate-400">"my wife standing beside me"</em>, <em className="text-slate-400">"arms raised in worship"</em>.
          </p>
          <textarea
            value={customPrompt}
            onChange={(e) => setCustomPrompt(e.target.value.slice(0, 500))}
            rows={3}
            maxLength={500}
            placeholder="Optional — leave blank to use the scene as-is"
            className="w-full px-4 py-3 bg-cosmic-800 border border-slate-700 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:border-divine-500 focus:ring-1 focus:ring-divine-500 transition-colors resize-none text-sm"
          />
        </div>

        {/* Requirements */}
        <div className="bg-cosmic-800/60 border border-slate-700/50 rounded-xl p-4">
          <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3">Photo Requirements</p>
          <ul className="space-y-1.5">
            {REQUIREMENTS.map((req, i) => (
              <li key={i} className="flex items-start gap-2 text-xs text-slate-400">
                <span className="text-divine-500 mt-0.5 shrink-0">✓</span>
                {req}
              </li>
            ))}
          </ul>
        </div>

        {/* Consent */}
        <p className="text-xs text-slate-500 leading-relaxed">
          Your original photo is processed in memory and immediately deleted — it is never stored or shared.
          Your generated portrait isn't saved anywhere either; download or share it yourself before leaving this page.
        </p>

        {/* Error */}
        {error && (
          <div className="bg-red-900/40 border border-red-700/50 rounded-xl px-4 py-3 text-red-300 text-sm">
            {error}
          </div>
        )}

        {/* Submit */}
        <button
          type="submit"
          disabled={loading || !selectedScene || !imageFile}
          className="w-full py-4 bg-divine-500 hover:bg-divine-400 disabled:bg-slate-700 disabled:cursor-not-allowed text-cosmic-950 disabled:text-slate-400 font-bold text-base rounded-2xl transition-all duration-200 glow-gold disabled:shadow-none hover:scale-[1.02] active:scale-95"
        >
          {loading
            ? 'Generating…'
            : !selectedScene
              ? 'Select a Scene to Continue'
              : 'Generate My Supernatural Image ✦'}
        </button>
      </form>

      {/* Loading overlay */}
      {loading && (
        <div className="fixed inset-0 bg-cosmic-950/90 backdrop-blur-sm z-50 flex flex-col items-center justify-center gap-8 px-6">
          {/* Spinner */}
          <div className="relative w-24 h-24">
            <div className="absolute inset-0 rounded-full border-4 border-slate-700" />
            <div className="absolute inset-0 rounded-full border-4 border-divine-500 border-t-transparent animate-spin" />
            <div className="absolute inset-3 rounded-full border-2 border-divine-500/40 border-b-transparent animate-spin-slow" style={{ animationDirection: 'reverse' }} />
            <div className="absolute inset-0 flex items-center justify-center text-2xl">✨</div>
          </div>

          <div className="text-center">
            <p className="text-divine-500 font-semibold text-lg animate-pulse-slow">
              {PROGRESS_MESSAGES[progressIdx]}
            </p>
            <p className="text-slate-500 text-sm mt-2">This takes 15–30 seconds. Please don't close this page.</p>
          </div>

          {/* Progress bar */}
          <div className="w-64 h-1 bg-slate-800 rounded-full overflow-hidden">
            <div className="h-full bg-gradient-to-r from-divine-600 to-divine-400 rounded-full animate-pulse w-3/4" />
          </div>
        </div>
      )}
    </div>
  )
}
