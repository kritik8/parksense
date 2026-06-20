/**
 * CIS Legend — Leaflet custom control overlay
 */
import React from 'react'
import { CIS_LEGEND } from '../../utils/cis'

export function CISLegend() {
  return (
    <div className="cis-legend" id="cis-map-legend">
      <div className="cis-legend-title">Current Parking Violation Impact</div>
      {[...CIS_LEGEND].reverse().map(band => (
        <div key={band.class} className="cis-legend-row">
          <span className="cis-legend-dot" style={{ background: band.hex }} />
          <span className="cis-legend-text">{band.label}</span>
          <span className="cis-legend-range">{band.range}</span>
        </div>
      ))}
    </div>
  )
}
