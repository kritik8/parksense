/**
 * Stats Bar — top-level KPI strip
 * Removed: Peak Violation Hour, Latest Record (unreliable data)
 * Kept: Active Violations, Average CIS Score, Enforcement Coverage
 */
import React from 'react'
import { formatNumber, formatDecimal } from '../../utils/format'
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

  const avgCis   = stats?.avg_cis ?? null
  const cisClass = getCISClass(avgCis)

  return (
    <div className="stats-bar" role="region" aria-label="Dashboard statistics">
      <StatCard
        id="stat-violations"
        value={formatNumber(stats?.total_violations)}
        label="Active Violations"
        accent="var(--cis-orange)"
      />
      <StatCard
        id="stat-avg-cis"
        value={avgCis !== null ? formatDecimal(avgCis, 1) : '—'}
        label="Average CIS Score"
        valueClass={cisClass}
        tooltip="Congestion Impact Score (0–100)"
      />
      <StatCard
        id="stat-approved"
        value={`${approvalRate}%`}
        label="Enforcement Coverage"
        accent="var(--cis-green)"
      />
    </div>
  )
}

function StatCard({ id, value, label, valueClass, accent, tooltip }) {
  return (
    <div className="stat-card" id={id} title={tooltip ?? ''}>
      <div className="stat-label">{label}</div>
      <div
        className={`stat-value ${valueClass ? `cis-${valueClass}` : ''}`}
        style={accent && !valueClass ? { color: accent } : {}}
      >
        {value}
      </div>
    </div>
  )
}
