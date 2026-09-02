import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import { defineConfig } from 'vite'

// Served from https://<user>.github.io/BIS-SARTHI/, so assets need that prefix.
// This MUST match the GitHub repo name exactly or every asset 404s on Pages.
// Local dev stays at "/" — set via the `base` option only for production builds.
export default defineConfig(({ command }) => ({
  base: command === 'build' ? '/BIS-SARTHI/' : '/',
  plugins: [react(), tailwindcss()],
  server: {
    port: 5173,
    proxy: {
      '/api': 'http://127.0.0.1:8000',
    },
  },
}))
