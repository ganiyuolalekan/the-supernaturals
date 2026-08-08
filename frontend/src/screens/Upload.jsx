import { useState, useRef, useCallback, useEffect } from 'react'
import axios from 'axios'
import ScenePicker from '../components/ScenePicker'
import { findScene } from '../data/scenes'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// Fallback text if /status didn't supply a message but the limit is hit.
const ERROR_MESSAGES_CAPACITY =
  "We've reached today's image limit. The limit resets daily — please come back tomorrow."

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

export default function Upload({ status, onStatusChange, onResult, onBack }) {
  const [imageFile, setImageFile] = useState(null)
  const [preview, setPreview] = useState(null)
  const [dragging, setDragging] = useState(false)
  const [loading, setLoading] = useState(false)
  const [progressIdx, setProgressIdx] = useState(0)
  const [error, setError] = useState(null)
  const [selectedScene, setSelectedScene] = useState(null)
  const [gender, setGender] = useState(null) // 'male' | 'female'
  const [activeScene, setActiveScene] = useState(null) // { active_scene_id, schedule } from /active-scene
  const [quota, setQuota] = useState(null) // { used, limit, remaining, cooldown_remaining } from /quota
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

    axios.get(`${API_URL}/quota`)
      .then(({ data }) => setQuota(data))
      .catch(() => {
        // Quota badge just won't show if this fails — backend still enforces it.
      })

  }, [])

  // Availability is owned by App (one poll for the whole app, so a closed day
  // can lock every screen). Absent status = assume open; the backend still
  // enforces every gate on /generate and explains itself there.
  const serviceAvailable = status ? status.generation_available : true
  const serviceMessage = status?.message
  const outOfQuota = quota && quota.remaining <= 0

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
    if (!serviceAvailable) { setError(serviceMessage || ERROR_MESSAGES_CAPACITY); return }
    if (!imageFile) { setError('Please select a photo.'); return }
    if (!gender) { setError('Please select your gender.'); return }
    if (!selectedScene) { setError('Please select a scene below.'); return }

    setLoading(true)
    setError(null)
    startProgressCycle()

    const formData = new FormData()
    formData.append('image', imageFile)
    formData.append('scene_id', selectedScene.id)
    formData.append('gender', gender)
    if (customPrompt.trim()) {
      formData.append('custom_prompt', customPrompt.trim())
    }

    try {
      const { data } = await axios.post(`${API_URL}/generate`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        timeout: 120_000,
      })
      stopProgressCycle()
      if (data.quota) setQuota(data.quota)
      onResult({ ...data })
    } catch (err) {
      stopProgressCycle()
      const detail = err.response?.data?.detail
      let msg
      if (typeof detail === 'object') {
        msg = detail.message
        // A service-wide gate closed between the last poll and this submit —
        // adopt the status the backend sent back so the UI locks immediately
        // (banner, or the closed-day modal) instead of waiting for the poll.
        if (detail.status) {
          onStatusChange?.(detail.status)
        }
        const debug = detail.debug || ''
        if (debug && import.meta.env.DEV) {
          msg += `\n\nDebug: ${debug}`
        }
        if (detail.quota) setQuota(detail.quota)
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

        {/* Service-wide daily limit banner — shown when Gemini's quota is spent */}
        {!serviceAvailable && (
          <div className="mt-4 flex items-start gap-2.5 rounded-xl border border-amber-700/50 bg-amber-900/20 px-4 py-3">
            <span className="text-lg">🌙</span>
            <div className="flex-1">
              <p className="text-sm font-semibold text-amber-200">Today's limit reached</p>
              <p className="text-xs text-slate-300 mt-0.5 leading-relaxed">
                {serviceMessage || ERROR_MESSAGES_CAPACITY}
              </p>
            </div>
          </div>
        )}

        {/* Daily quota badge */}
        {quota && (
          <div
            className={`mt-4 flex items-center gap-2.5 rounded-xl border px-4 py-3 ${
              outOfQuota
                ? 'border-amber-700/50 bg-amber-900/20'
                : 'border-slate-700/50 bg-cosmic-800/60'
            }`}
          >
            <span className="text-lg">{outOfQuota ? '🌙' : '✨'}</span>
            <div className="flex-1">
              {/* Dot tracker: one filled dot per remaining generation */}
              <div className="flex items-center gap-1.5 mb-0.5">
                {Array.from({ length: quota.limit }).map((_, i) => (
                  <span
                    key={i}
                    className={`h-2 w-2 rounded-full ${
                      i < quota.remaining ? 'bg-divine-500' : 'bg-slate-600'
                    }`}
                  />
                ))}
                <span className="ml-1.5 text-sm font-semibold text-white">
                  {quota.remaining} of {quota.limit} left today
                </span>
              </div>
              <p className="text-xs text-slate-400">
                {outOfQuota
                  ? "You've used all your generations for today — come back tomorrow!"
                  : `Each person can create up to ${quota.limit} portrait${quota.limit === 1 ? '' : 's'} a day.`}
              </p>
            </div>
          </div>
        )}
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

        {/* Gender — women are dressed in a modest flowing gown instead of trousers */}
        <div>
          <label className="block text-sm font-semibold text-slate-300 mb-2">Gender</label>
          <div className="grid grid-cols-2 gap-3">
            {[
              { value: 'male', label: 'Male', icon: '♂' },
              { value: 'female', label: 'Female', icon: '♀' },
            ].map((opt) => (
              <button
                key={opt.value}
                type="button"
                onClick={() => setGender(opt.value)}
                className={`flex items-center justify-center gap-2 py-3 rounded-xl border text-sm font-semibold transition-all duration-200
                  ${gender === opt.value
                    ? 'border-divine-500 bg-divine-500/10 text-white'
                    : 'border-slate-700 bg-cosmic-800 text-slate-300 hover:border-slate-500'}`}
              >
                <span className="text-lg leading-none">{opt.icon}</span>
                {opt.label}
              </button>
            ))}
          </div>
          <p className="text-xs text-slate-500 mt-2 leading-relaxed">
            Women are styled in a modest, free-flowing gown to match the scene (never trousers),
            with a light, natural touch-up — your face and complexion stay exactly as they are.
          </p>
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
            Each scene already dresses you to match it. Ask for a different outfit here and you'll get it —
            a white gown instead of a white shirt, an agbada instead of a suit — styled to still fit the scene.
            You can also add objects, motion, extra people or animals. The scene, the wings and the divine light stay.
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
          disabled={loading || !serviceAvailable || !selectedScene || !imageFile || !gender || outOfQuota}
          className="w-full py-4 bg-divine-500 hover:bg-divine-400 disabled:bg-slate-700 disabled:cursor-not-allowed text-cosmic-950 disabled:text-slate-400 font-bold text-base rounded-2xl transition-all duration-200 glow-gold disabled:shadow-none hover:scale-[1.02] active:scale-95"
        >
          {loading
            ? 'Generating…'
            : !serviceAvailable
              ? "Today's Limit Reached — Come Back Tomorrow"
              : outOfQuota
                ? 'Daily Limit Reached — Come Back Tomorrow'
                : !gender
                  ? 'Select Your Gender to Continue'
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
