/**
 * Stats Bar — top-level KPI strip
 * Reads from GET /api/stats
 * Fields: total_violations, approved, avg_cis, peak_hour, date_range
 */
import React from 'react'
import { formatNumber, formatDecimal, formatHour } from '../../utils/format'
import { getCISClass } from '../../utils/cis'
import { LoadingState } from '../common'

export function StatsBar({ stats, loading }) {
  if (loading) {
    return (
      <div className="stats-bar">
        <LoadingState compact message="Loading stats…" />
      </div>
    )
  }

  const approvalRate = stats
    ? Math.round((stats.approved / Math.max(stats.total_violations, 1)) * 100)
    : 0

  const avgCis     = stats?.avg_cis ?? null
  const cisClass   = getCISClass(avgCis)

  return (
    <div className="stats-bar" role="region" aria-label="Dashboard statistics">
      <StatCard
        id="stat-violations"
        value={formatNumber(stats?.total_violations)}
        label="Active Violations"
        icon="🚫"
        accent="var(--cis-orange)"
      />
      <StatCard
        id="stat-avg-cis"
        value={avgCis !== null ? formatDecimal(avgCis, 1) : '—'}
        label="Average CIS Score"
        icon="📊"
        valueClass={cisClass}
        tooltip="Congestion Impact Score (0–100)"
      />
      <StatCard
        id="stat-peak-hour"
        value={formatHour(stats?.peak_hour)}
        label="Peak Violation Hour"
        icon="🕐"
        accent="var(--blue-600)"
      />
      <StatCard
        id="stat-approved"
        value={`${approvalRate}%`}
        label="Enforcement Coverage"
        icon="✅"
        accent="var(--cis-green)"
      />
      <StatCard
        id="stat-date-range"
        value={stats?.date_range?.max ? formatShortDate(stats.date_range.max) : '—'}
        label="Latest Record"
        icon="📅"
      />
    </div>
  )
}

function StatCard({ id, value, label, icon, valueClass, accent, tooltip }) {
  return (
    <div className="stat-card" id={id} title={tooltip ?? ''}>
      <div className="flex items-center gap-6" style={{ marginBottom: 2 }}>
        <span style={{ fontSize: 12 }}>{icon}</span>
        <span className="stat-label" style={{ margin: 0 }}>{label}</span>
      </div>
      <div className={`stat-value ${valueClass ? `cis-${valueClass}` : ''}`}
        style={accent && !valueClass ? { color: accent } : {}}>
        {value}
      </div>
    </div>
  )
}

function formatShortDate(ts) {
  if (!ts) return '—'
  try {
    return new Date(ts).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: '2-digit' })
  } catch { return '—' }
}
