/**
 * ChallanPanel — Dynamic Challan Recommendation
 * API: GET /api/challan/recommend?violation_id=...
 *
 * Shows:
 *   - violation_id input
 *   - Transparent calculation breakdown
 *   - Base fine, CIS score, multiplier, Recommended Fine
 *   - Disclaimer: policy recommendation, not automated fine
 */
import React, { useState } from 'react'
import { fetchChallanRecommendation } from '../../services/api'
import { formatINR, formatDecimal } from '../../utils/format'
import { getCISHex, getCISLabel } from '../../utils/cis'
import { LoadingState, CISBadge } from '../common'
import { MOCK_CHALLAN } from '../../data/mockData'

export function ChallanPanel({ selectedViolationId }) {
  const [inputId, setInputId]     = useState(selectedViolationId ?? '')
  const [result, setResult]       = useState(null)
  const [loading, setLoading]     = useState(false)
  const [error, setError]         = useState(null)
  const [usingMock, setUsingMock] = useState(false)

  const handleLookup = async () => {
    if (!inputId.trim()) return
    setLoading(true)
    setError(null)
    setUsingMock(false)
    try {
      const data = await fetchChallanRecommendation(inputId.trim())
      setResult(data)
    } catch (err) {
      if (err.response?.status === 404) {
        setError(`Violation ID "${inputId}" not found.`)
        setResult(null)
      } else {
        // API down — show mock
        setResult(MOCK_CHALLAN)
        setUsingMock(true)
        setError(null)
      }
    } finally {
      setLoading(false)
    }
  }

  const handleKey = (e) => {
    if (e.key === 'Enter') handleLookup()
  }

  return (
    <div style={{ height: '100%', display: 'flex', flexDirection: 'column', overflow: 'hidden', padding: '2px 0' }}>
      {/* Input row */}
      <div className="flex items-center gap-6" style={{ flexShrink: 0, marginBottom: 10 }}>
        <input
          type="text"
          className="input"
          value={inputId}
          onChange={e => setInputId(e.target.value)}
          onKeyDown={handleKey}
          placeholder="Enter Violation ID…"
          id="challan-violation-input"
          aria-label="Violation ID for challan lookup"
          style={{ flex: 1, fontSize: 12 }}
        />
        <button
          className="btn btn-primary btn-sm"
          onClick={handleLookup}
          disabled={!inputId.trim() || loading}
          id="challan-lookup-btn"
          aria-label="Look up challan recommendation"
        >
          Calculate
        </button>
      </div>

      {/* Loading */}
      {loading && <LoadingState compact message="Calculating…" />}

      {/* Error */}
      {error && !loading && (
        <div style={{
          background: 'var(--cis-red-bg)', border: '1px solid var(--cis-red-border)',
          borderRadius: 6, padding: '8px 12px', fontSize: 12, color: 'var(--cis-red)',
        }}>
          {error}
        </div>
      )}

      {/* Mock banner */}
      {usingMock && result && !loading && (
        <div style={{
          background: '#fef9c3', border: '1px solid #fde047', color: '#854d0e',
          fontSize: 11, padding: '4px 10px', borderRadius: 6, marginBottom: 8,
        }}>
          ⚠️ Demo data — backend offline
        </div>
      )}

      {/* Result */}
      {result && !loading && !error && (
        <div style={{ flex: 1, overflowY: 'auto' }}>
          {/* Recommended Fine headline */}
          <div className="challan-total">
            {formatINR(result.recommended_fine)}
          </div>
          <div style={{ textAlign: 'center', fontSize: 11, color: 'var(--text-secondary)', marginBottom: 10 }}>
            Recommended Fine
          </div>

          {/* Breakdown */}
          <div className="challan-breakdown">
            <div className="challan-row">
              <span>Violation</span>
              <span style={{ fontWeight: 600, fontSize: 11 }}>{result.violation_type}</span>
            </div>
            <div className="challan-row">
              <span>Vehicle</span>
              <span style={{ fontWeight: 600 }}>{result.vehicle_type}</span>
            </div>
            <div className="challan-row">
              <span>Base Fine</span>
              <span style={{ fontWeight: 700 }}>{formatINR(result.base_fine)}</span>
            </div>
            <div className="challan-row">
              <span>CIS Score</span>
              <CISBadge score={result.cis_score} showScore size="sm" />
            </div>
            <div className="challan-row">
              <span>Impact Multiplier</span>
              <span style={{ fontWeight: 800, color: getCISHex(result.cis_score), fontSize: 13 }}>
                ×{formatDecimal(result.multiplier, 2)}
              </span>
            </div>
            {result.breakdown?.road_criticality !== undefined && (
              <div className="challan-row">
                <span style={{ color: 'var(--text-muted)' }}>Road Criticality</span>
                <span style={{ color: 'var(--text-secondary)' }}>{formatDecimal(result.breakdown.road_criticality, 2)}</span>
              </div>
            )}
            {result.breakdown?.cascade_multiplier !== undefined && (
              <div className="challan-row">
                <span style={{ color: 'var(--text-muted)' }}>Cascade Multiplier</span>
                <span style={{ color: 'var(--text-secondary)' }}>{formatDecimal(result.breakdown.cascade_multiplier, 2)}×</span>
              </div>
            )}
            <div className="challan-row" style={{ borderTop: '1px solid var(--border)', paddingTop: 6, marginTop: 2 }}>
              <span style={{ fontWeight: 700 }}>Formula</span>
              <span style={{ fontSize: 10, color: 'var(--text-muted)' }}>
                {result.breakdown?.formula ?? 'base × (1 + CIS/100 × 4)'}
              </span>
            </div>
          </div>

          <div className="challan-disclaimer">
            ⚖️ This is a <b>policy recommendation</b> for traffic authorities.
            Not an automatically issued fine. Requires officer approval per Motor Vehicles Act.
          </div>
        </div>
      )}

      {/* Default state */}
      {!result && !loading && !error && (
        <div style={{
          flex: 1, display: 'flex', flexDirection: 'column',
          alignItems: 'center', justifyContent: 'center', gap: 6,
          color: 'var(--text-muted)', textAlign: 'center',
        }}>
          <span style={{ fontSize: 24 }}>⚖️</span>
          <span style={{ fontSize: 12 }}>Enter a violation ID to calculate the recommended challan based on CIS impact.</span>
        </div>
      )}
    </div>
  )
}
