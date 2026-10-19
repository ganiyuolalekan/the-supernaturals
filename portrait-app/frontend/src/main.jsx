import { StrictMode, Suspense, lazy } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'

// Standalone pages with isolated styles. Each is lazy-loaded so the portrait
// app's bundle is unchanged; any other path renders the app.
const PAGES = {
  '/about-conference': lazy(() => import('./pages/about-conference/AboutConference.jsx')),
  '/our-sponsors': lazy(() => import('./pages/our-sponsors/OurSponsors.jsx')),
  '/attend_event': lazy(() => import('./pages/attend-event/AttendEvent.jsx')),
  '/attend_event/first_timers': lazy(() => import('./pages/attend-event/FirstTimers.jsx')),
  '/attend_event/chart': lazy(() => import('./pages/attend-event/Chart.jsx')),
}
const Page = PAGES[window.location.pathname.replace(/\/+$/, '')]

createRoot(document.getElementById('root')).render(
  <StrictMode>
    {Page ? (
      <Suspense fallback={null}>
        <Page />
      </Suspense>
    ) : (
      <App />
    )}
  </StrictMode>,
)
