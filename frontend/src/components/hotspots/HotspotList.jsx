/**
 * HotspotList — Right sidebar showing top hotspots ranked by CIS
 * Data from GET /api/hotspots
 *
 * Each item shows: rank, location name, CIS score pill, violation count,
 * dominant vehicle type. Click → zoom map to hotspot.
 */
import React from 'react'
import { ScorePill, CISBadge, LoadingState, EmptyState } from '../common'
import { formatNumber } from '../../utils/format'
import { vehicleLabel } from '../../utils/format'
import { HOTSPOT_NAMES } from '../../data/mockData'

const LOCATION_NAMES = [
  'Koramangala 4th Block', 'ORR Bellandur', 'MG Road', 'HSR 27th Main',
  'Koramangala Junction', 'Yeshwanthpur Circle', 'Indiranagar 100ft Rd',
  'Electronic City PS', 'Whitefield ITPL', 'Sarjapur Road',
  'Marathahalli Bridge', 'KR Puram', 'Silk Board Junction',
  'Hebbal Flyover', 'Jayanagar 4th Block', 'BTM Layout',
  'Bannerghatta Road', 'Old Airport Road', 'Outer Ring Road',
  'Rajajinagar Circle',
]

function getHotspotName(hotspot, index) {
  // Use mock names lookup first, then fall back to junction coordinate label
  return (
    HOTSPOT_NAMES[hotspot.hotspot_id] ||
    LOCATION_NAMES[index] ||
    `${hotspot.latitude.toFixed(4)}°N, ${hotspot.longitude.toFixed(4)}°E`
  )
}

export function HotspotList({ hotspots = [], loading, selectedId, onSelect }) {
  return (
    <div className="hotspot-sidebar">
      {/* Header */}
      <div className="hotspot-sidebar-header">
        <div className="flex items-center justify-between">
          <div className="hotspot-sidebar-title">🔥 Top Hotspots</div>
          <span className="badge badge-high" style={{ fontSize: 10 }}>
            {hotspots.length} zones
          </span>
        </div>
        <div className="hotspot-sidebar-sort">Sorted by CIS score ▼</div>
      </div>

      {/* List */}
      <div className="scroll-list" role="list" aria-label="Hotspot rankings">
        {loading ? (
          <LoadingState compact message="Loading hotspots…" />
        ) : hotspots.length === 0 ? (
          <EmptyState icon="📍" title="No hotspots found" desc="Try adjusting filters." />
        ) : (
          hotspots.map((hs, i) => (
            <HotspotCard
              key={hs.hotspot_id}
              hotspot={hs}
              rank={i + 1}
              name={getHotspotName(hs, i)}
              isSelected={selectedId === hs.hotspot_id}
              onClick={() => onSelect(hs)}
            />
          ))
        )}
      </div>
    </div>
  )
}

function HotspotCard({ hotspot, rank, name, isSelected, onClick }) {
  const { label } = vehicleLabel(hotspot.dominant_vehicle)
  const cisScore = hotspot.avg_cis_per_violation ?? hotspot.total_cis

  return (
    <div
      className={`hotspot-item ${isSelected ? 'selected' : ''}`}
      onClick={onClick}
      role="listitem"
      tabIndex={0}
      onKeyDown={e => e.key === 'Enter' && onClick()}
      id={`hotspot-card-${hotspot.hotspot_id}`}
      aria-label={`${rank}. ${name}, CIS ${Math.round(cisScore)}`}
    >
      <div className="hotspot-rank">#{rank}</div>

      <div className="hotspot-info">
        <div className="hotspot-name truncate" title={name}>{name}</div>
        <div className="hotspot-meta">
          {formatNumber(hotspot.violation_count)} violations · {label}
        </div>
        <div style={{ marginTop: 4 }}>
          <CISBadge score={cisScore} size="sm" />
        </div>
      </div>

      <ScorePill score={cisScore} />
    </div>
  )
}
