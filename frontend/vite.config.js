import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// In development the dev server forwards /api requests to the FastAPI backend,
// so no API URL is needed locally. In production the app uses VITE_API_URL.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: { '/api': 'http://127.0.0.1:8000' },
  },
})
