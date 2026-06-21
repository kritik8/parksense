/**
 * PredictionList — Upcoming hotspot forecasts
 * Data: GET /api/predict → predictions[]
 * Fields: latitude, longitude, predicted_count, confidence, threat_level
 */
import React from 'react'
import { formatConfidence } from '../../utils/format'
import { LoadingState, EmptyState } from '../common'

const THREAT_COLORS = {
  CRITICAL: '#d50000',
  HIGH:     '#ff6d00',
  MODERATE: '#ffd600',
  LOW:      '#00c853',
}

const THREAT_LABELS = {
  CRITICAL: 'Critical', HIGH: 'High', MODERATE: 'Moderate', LOW: 'Low',
}

const LOCATION_NAMES = [
  'Koramangala 4th Block', 'ORR Bellandur', 'MG Road',
  'HSR Layout', 'Yeshwanthpur Circle', 'Indiranagar',
  'Electronic City', 'Whitefield', 'Sarjapur Road', 'BTM Layout',
]

export function PredictionList({ predictions = [], loading }) {
  if (loading) return <LoadingState compact message="Loading forecast…" />
  if (!predictions.length) return (
    <EmptyState icon="🔮" title="No predictions" desc="Forecast data unavailable." />
  )

  return (
    <div style={{ overflow: 'hidden', height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Table header */}
      <div style={{
        display: 'grid', gridTemplateColumns: '1fr 60px 56px',
        fontSize: 10, fontWeight: 700, textTransform: 'uppercase',
        letterSpacing: '0.06em', color: 'var(--text-muted)',
        padding: '0 0 6px 0', borderBottom: '1px solid var(--border)',
        flexShrink: 0,
      }}>
        <span>Location</span>
        <span style={{ textAlign: 'center' }}>Count</span>
        <span style={{ textAlign: 'right' }}>Conf.</span>
      </div>

      {/* Rows */}
      <div style={{ flex: 1, overflowY: 'auto' }}>
        {predictions.map((p, i) => (
          <div key={p.h3_cell ?? i} className="pred-item" id={`pred-${i}`}>
            <span
              className={`pred-threat pred-threat-${p.threat_level}`}
              title={THREAT_LABELS[p.threat_level]}
            />
            <span style={{ flex: 1, fontSize: 12, color: 'var(--text-primary)', fontWeight: 500 }}>
              {LOCATION_NAMES[i] ?? `${p.latitude?.toFixed(3)}°N`}
            </span>
            <span style={{
              minWidth: 52, textAlign: 'center', fontWeight: 700,
              color: THREAT_COLORS[p.threat_level] ?? '#111',
              fontSize: 12,
            }}>
              +{p.predicted_count}
            </span>
            <span style={{ minWidth: 44, textAlign: 'right', fontSize: 11, color: 'var(--text-secondary)' }}>
              {formatConfidence(p.confidence)}
            </span>
          </div>
        ))}
      </div>

      <div style={{ fontSize: 10, color: 'var(--text-muted)', marginTop: 6, flexShrink: 0 }}>
        Predicted violations in next 2 hours
      </div>
    </div>
  )
}
