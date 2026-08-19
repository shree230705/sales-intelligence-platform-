import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    // Allows the dev server to be reached from outside the Docker
    // container when running via docker-compose.
    host: '0.0.0.0',
    watch: {
      // Polling is needed for file-change detection to work reliably
      // inside Docker on some host OSes (notably Windows/WSL2 bind mounts).
      usePolling: true,
    },
  },
})
