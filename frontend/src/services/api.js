import axios from 'axios'

// VITE_API_URL is set per environment (.env for local dev, build args for
// Docker/production). Falls back to localhost so `npm run dev` works with
// zero config against a locally running backend.
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Once auth exists (Phase 3), a request interceptor attaches the JWT here:
// api.interceptors.request.use((config) => {
//   const token = localStorage.getItem('token')
//   if (token) config.headers.Authorization = `Bearer ${token}`
//   return config
// })

export default api
