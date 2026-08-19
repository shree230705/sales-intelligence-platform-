import { useEffect, useState } from 'react'
import api from './services/api'

/**
 * Phase 1 placeholder App.
 *
 * This intentionally does one real thing end-to-end — calling the backend
 * health check — rather than rendering static markup. That way, when you
 * run this for the first time, a green "connected" badge is proof the
 * whole chain (React -> Axios -> Flask -> MongoDB) actually works, not
 * just that each piece was created in isolation.
 *
 * Real pages (Dashboard, Leads, etc.) replace this in later phases via
 * React Router routes defined in src/routes.
 */
function App() {
  const [status, setStatus] = useState('checking')
  const [detail, setDetail] = useState('')

  useEffect(() => {
    api
      .get('/api/health')
      .then((res) => {
        setStatus('connected')
        setDetail(res.data.data.database)
      })
      .catch((err) => {
        setStatus('error')
        setDetail(err.message)
      })
  }, [])

  const badgeColor =
    status === 'connected'
      ? 'bg-green-100 text-green-700 border-green-300'
      : status === 'checking'
        ? 'bg-yellow-100 text-yellow-700 border-yellow-300'
        : 'bg-red-100 text-red-700 border-red-300'

  return (
    <div className="min-h-screen flex items-center justify-center px-4">
      <div className="max-w-md w-full bg-white rounded-xl shadow-sm border border-gray-200 p-8 text-center">
        <h1 className="text-2xl font-semibold text-gray-900 mb-2">
          Sales Intelligence Platform
        </h1>
        <p className="text-gray-500 mb-6">Phase 1 — project scaffold</p>

        <span
          className={`inline-flex items-center gap-2 px-4 py-2 rounded-full border text-sm font-medium ${badgeColor}`}
        >
          <span className="w-2 h-2 rounded-full bg-current" />
          Backend: {status}
          {detail && ` (${detail})`}
        </span>

        <p className="text-xs text-gray-400 mt-6">
          This card calls <code>GET /api/health</code> on load. If it shows
          "connected", the frontend, Flask API, and MongoDB are all wired
          together correctly.
        </p>
      </div>
    </div>
  )
}

export default App
