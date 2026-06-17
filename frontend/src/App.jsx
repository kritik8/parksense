/**
 * ParkSense AI — Root App Component
 * Owner: frontend-dashboard branch (Mayank)
 *
 * Placeholder shell — wire up real components in frontend-dashboard branch.
 * Components to build:
 *   src/components/MapView.jsx        ← Leaflet map + heatmap
 *   src/components/HotspotPanel.jsx   ← Right sidebar, ranked hotspots
 *   src/components/FilterPanel.jsx    ← Left sidebar, filters
 *   src/components/StatsBar.jsx       ← Bottom stats bar
 *   src/components/AnalyticsPanel.jsx ← Charts (Recharts)
 *   src/components/ChalllanPanel.jsx  ← Dynamic challan UI
 *   src/components/ParkFlowSim.jsx    ← What-if simulation UI (OPTIONAL)
 *   src/components/OffendersTable.jsx ← Repeat offenders page
 */

import React, { useState, useEffect } from 'react'
import './App.css'

const API_BASE = '/api'

function App() {
  const [stats, setStats] = useState(null)

  useEffect(() => {
    fetch(`${API_BASE}/stats`)
      .then(r => r.json())
      .then(setStats)
      .catch(() => setStats({ message: 'API not running — start backend first.' }))
  }, [])

  return (
    <div className="app-shell">
      <header className="app-header">
        <div className="header-logo">
          <span className="logo-icon">🅿️</span>
          <span className="logo-text">ParkSense <strong>AI</strong></span>
        </div>
        <div className="header-subtitle">Bengaluru Traffic Command Center</div>
        <div className="header-status">
          <span className="status-dot" />
          Live
        </div>
      </header>

      <main className="app-main">
        {/* TODO (Mayank): Replace this placeholder with real components */}
        <div className="placeholder-dashboard">
          <div className="placeholder-map">
            🗺️ Leaflet Map — build in MapView.jsx
          </div>
          <div className="placeholder-sidebar">
            <div className="card" style={{ marginBottom: 12 }}>
              <h3>🔥 Hotspot Rankings</h3>
              <p style={{ color: 'var(--text-secondary)', fontSize: 13, marginTop: 6 }}>
                Build in HotspotPanel.jsx
              </p>
            </div>
            <div className="card">
              <h3>📊 API Status</h3>
              <pre style={{ fontSize: 12, marginTop: 8, color: 'var(--accent-cyan)', whiteSpace: 'pre-wrap' }}>
                {JSON.stringify(stats, null, 2)}
              </pre>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}

export default App
