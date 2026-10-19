import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    host: '0.0.0.0',        // bind to all interfaces so ngrok can reach it
    allowedHosts: true,     // allow any hostname (ngrok, etc.)
  },
})
