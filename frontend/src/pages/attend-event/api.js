import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export const DAYS = [
  { id: 'friday', label: 'Friday', short: 'Fri' },
  { id: 'saturday', label: 'Saturday', short: 'Sat' },
  { id: 'sunday', label: 'Sunday', short: 'Sun' },
]

/** Today's conference day in Lagos time; Friday when it isn't one. */
export function defaultDay() {
  const w = new Date().toLocaleDateString('en-US', { weekday: 'long', timeZone: 'Africa/Lagos' }).toLowerCase()
  return DAYS.some((d) => d.id === w) ? w : 'friday'
}

export function errorMessage(err) {
  return err?.response?.data?.detail?.message || err?.message || 'Something went wrong.'
}

export async function call(method, path, { params, data } = {}) {
  const res = await axios({ method, url: `${API_URL}/attend${path}`, params, data })
  return res.data
}
