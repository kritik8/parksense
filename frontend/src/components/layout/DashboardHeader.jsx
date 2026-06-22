/**
 * Dashboard Header
 * Shows: Logo | Subtitle | Search bar | Digital Clock | Live badge | Last-updated | Refresh
 */
import React, { useState, useEffect } from 'react'
import { formatLastUpdated } from '../../utils/format'
import logo from '../../assets/logo.png'

function DigitalClock() {
  const [time, setTime] = useState(new Date())

  useEffect(() => {
    const timer = setInterval(() => setTime(new Date()), 1000)
    return () => clearInterval(timer)
  }, [])

  const pad = n => String(n).padStart(2, '0')
  const h = time.getHours()
  const ampm = h >= 12 ? 'PM' : 'AM'
  const h12 = h % 12 || 12

  return (
    <div style={{
      display: 'flex', alignItems: 'center', gap: 6,
      background: 'var(--bg-input)', borderRadius: 8,
      padding: '4px 10px', border: '1px solid var(--border)',
    }}>
      <span style={{ fontSize: 11, color: 'var(--text-muted)', letterSpacing: 0.5 }}>IST</span>
      <span style={{
        fontFamily: "'Courier New', monospace",
        fontSize: 15, fontWeight: 700,
        color: 'var(--text-primary)', letterSpacing: 1,
      }}>
        {pad(h12)}:{pad(time.getMinutes())}:{pad(time.getSeconds())}
      </span>
      <span style={{ fontSize: 10, fontWeight: 600, color: 'var(--blue-600)' }}>{ampm}</span>
    </div>
  )
}

export function DashboardHeader({ lastUpdated, onRefresh, usingMock, theme, onToggleTheme }) {
  return (
    <header className="app-header">
      {/* Logo */}
      <div className="flex items-center gap-8">
        <img
          src={logo}
          alt="ParkSense AI Logo"
          style={{ height: 38, width: 'auto', objectFit: 'contain', flexShrink: 0 }}
        />
        <div>
          <div style={{ fontWeight: 800, fontSize: 14, color: 'var(--text-primary)', lineHeight: 1.2 }}>
            ParkSense <span style={{ color: 'var(--blue-600)' }}>AI</span>
          </div>
          <div style={{ fontSize: 10, color: 'var(--text-secondary)', fontWeight: 500 }}>
            Bengaluru Traffic Command Center
          </div>
        </div>
      </div>

      {/* Search */}
      <div className="header-search" style={{ marginLeft: 24 }}>
        <span className="header-search-icon" style={{ fontSize: 12 }}>&#9906;</span>
        <input
          type="search"
          className="header-search-input"
          placeholder="Search locations, hotspots, violations…"
          aria-label="Search locations and violations"
        />
      </div>

      {/* Right side */}
      <div className="header-right">
        {/* Digital Clock */}
        <DigitalClock />

        {/* <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>
          Updated {formatLastUpdated(lastUpdated)}
        </span> */}

        <button
          className="btn btn-secondary btn-sm"
          onClick={onToggleTheme}
          title={`Switch to ${theme === 'light' ? 'dark' : 'light'} mode`}
          aria-label="Toggle dark mode"
          id="header-theme-btn"
        >
          {theme === 'light' ? '🌙 Dark' : '☀️ Light'}
        </button>

        <button
          className="btn btn-secondary btn-sm"
          onClick={onRefresh}
          title="Refresh all data"
          aria-label="Refresh dashboard data"
          id="header-refresh-btn"
        >
          &#8634; Refresh
        </button>

        {usingMock ? (
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: 5,
            fontSize: 12,
            fontWeight: 600,
            color: 'var(--text-secondary)',
            background: 'var(--bg-input)',
            padding: '4px 10px',
            borderRadius: 20,
            border: '1px solid var(--border)',
          }}>
            <span style={{
              width: 7,
              height: 7,
              borderRadius: '50%',
              background: 'var(--text-secondary)',
            }} />
            Demo Mode
          </div>
        ) : (
          <div className="live-badge">
            <span className="live-dot" />
            Live
          </div>
        )}
      </div>
    </header>
  )
}
