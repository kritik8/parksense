/**
 * Common reusable components for ParkSense AI
 * LoadingState, EmptyState, ErrorState, CISBadge, Tooltip
 */
import React from 'react'
import { getCISLabel, getCISClass } from '../../utils/cis'

// ── Loading State ──────────────────────────────────────────────────────────
export function LoadingState({ message = 'Loading data…', compact = false }) {
  if (compact) {
    return (
      <div className="flex items-center gap-8" style={{ padding: '16px', color: 'var(--text-secondary)', fontSize: 13 }}>
        <div className="spinner" style={{ width: 18, height: 18, borderWidth: 2 }} />
        <span>{message}</span>
      </div>
    )
  }
  return (
    <div className="state-container">
      <div className="spinner" />
      <div className="state-title">{message}</div>
      <div className="state-desc">Fetching from ParkSense AI backend…</div>
    </div>
  )
}

// ── Empty State ────────────────────────────────────────────────────────────
export function EmptyState({ icon = '🗂️', title = 'No data', desc = 'Try adjusting the filters.' }) {
  return (
    <div className="state-container">
      <div className="state-icon">{icon}</div>
      <div className="state-title">{title}</div>
      <div className="state-desc">{desc}</div>
    </div>
  )
}

// ── Error State ────────────────────────────────────────────────────────────
export function ErrorState({ onRetry, message = 'Failed to load data.' }) {
  return (
    <div className="state-container">
      <div className="state-icon">⚠️</div>
      <div className="state-title">Connection Error</div>
      <div className="state-desc">{message}</div>
      {onRetry && (
        <button className="btn btn-secondary btn-sm" style={{ marginTop: 8 }} onClick={onRetry}>
          ↺ Retry
        </button>
      )}
    </div>
  )
}

// ── Mock Data Banner ──────────────────────────────────────────────────────
export function MockBanner() {
  return (
    <div className="mock-banner" role="status">
      ⚠️ Backend offline — showing demo data. Start backend to see live Bengaluru violations.
    </div>
  )
}

// ── CIS Badge ─────────────────────────────────────────────────────────────
/**
 * @param {number} score   - 0-100
 * @param {boolean} showScore - show numeric score alongside label
 * @param {'sm'|'md'} size
 */
export function CISBadge({ score, showScore = false, size = 'md' }) {
  const label = getCISLabel(score)
  const cls   = getCISClass(score)
  const style = size === 'sm' ? { fontSize: 10, padding: '2px 7px' } : {}
  return (
    <span className={`badge badge-${cls}`} style={style}>
      {showScore ? `${Math.round(score)} · ` : ''}{label}
    </span>
  )
}

// ── Score Pill (coloured number bubble) ───────────────────────────────────
export function ScorePill({ score }) {
  const cls = getCISClass(score)
  return (
    <span className={`score-pill score-${cls}`}>
      {Math.round(score)}
    </span>
  )
}

// ── Tooltip ───────────────────────────────────────────────────────────────
export function Tooltip({ text, children }) {
  return (
    <span className="tooltip-container">
      {children}
      <span className="tooltip-box">{text}</span>
    </span>
  )
}

// ── Section Header ─────────────────────────────────────────────────────────
export function SectionHeader({ title, action }) {
  return (
    <div className="flex items-center justify-between" style={{ marginBottom: 10 }}>
      <span className="section-label">{title}</span>
      {action}
    </div>
  )
}
