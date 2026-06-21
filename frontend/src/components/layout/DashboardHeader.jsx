/**
 * Dashboard Header
 * Shows: Logo | Subtitle | Search bar | Live badge | Last-updated | Refresh
 */
import React from 'react'
import { formatLastUpdated } from '../../utils/format'

export function DashboardHeader({ lastUpdated, onRefresh }) {
  return (
    <header className="app-header">
      {/* Logo */}
      <div className="flex items-center gap-8">
        <div style={{
          width: 30, height: 30, borderRadius: 8,
          background: 'linear-gradient(135deg, #1d4ed8 0%, #3b82f6 100%)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          fontSize: 15, flexShrink: 0, boxShadow: '0 2px 8px rgba(29,78,216,0.3)',
        }}>
          🅿️
        </div>
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
        <span className="header-search-icon">🔍</span>
        <input
          type="search"
          className="header-search-input"
          placeholder="Search locations, hotspots, violations…"
          aria-label="Search locations and violations"
        />
      </div>

      {/* Right side */}
      <div className="header-right">
        <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>
          Updated {formatLastUpdated(lastUpdated)}
        </span>

        <button
          className="btn btn-secondary btn-sm"
          onClick={onRefresh}
          title="Refresh all data"
          aria-label="Refresh dashboard data"
          id="header-refresh-btn"
        >
          ↺ Refresh
        </button>

        <div className="live-badge">
          <span className="live-dot" />
          Live
        </div>

        {/* Profile placeholder */}
        <div style={{
          width: 32, height: 32, borderRadius: '50%',
          background: 'var(--blue-100)', color: 'var(--blue-600)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          fontSize: 14, fontWeight: 700, cursor: 'pointer',
          border: '2px solid var(--blue-200, #bfdbfe)',
        }}
          title="Profile / Settings"
        >
          TC
        </div>
      </div>
    </header>
  )
}
