/**
 * CIS Legend — Collapsible overlay on the map
 */
import React, { useState } from 'react'
import { CIS_LEGEND } from '../../utils/cis'

export function CISLegend() {
  const [open, setOpen] = useState(false)

  return (
    <div className="cis-legend" id="cis-map-legend">
      <button
        onClick={() => setOpen(o => !o)}
        style={{
          display: 'flex', alignItems: 'center', justifyContent: 'space-between',
          width: '100%', background: 'none', border: 'none', cursor: 'pointer',
          padding: 0, gap: 8,
        }}
        aria-expanded={open}
        aria-controls="cis-legend-body"
      >
        <span className="cis-legend-title" style={{ margin: 0 }}>
          Parking Violation Impact
        </span>
        <span style={{ fontSize: 10, color: 'var(--text-muted)', flexShrink: 0 }}>
          {open ? '▲' : '▼'}
        </span>
      </button>

      {open && (
        <div id="cis-legend-body" style={{ marginTop: 8 }}>
          {[...CIS_LEGEND].reverse().map(band => (
            <div key={band.class} className="cis-legend-row">
              <span className="cis-legend-dot" style={{ background: band.hex }} />
              <span className="cis-legend-text">{band.label}</span>
              <span className="cis-legend-range">{band.range}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
