/**
 * TrafficMap — Main Leaflet map component
 *
 * Renders:
 *   - Bengaluru base map (OpenStreetMap tiles)
 *   - Heatmap overlay (leaflet.heat) from /api/heatmap
 *   - Hotspot markers (custom CIS-coloured DivIcons) from /api/hotspots
 *   - Violation pins (CIS-coloured CircleMarkers) from /api/violations
 *   - CIS Legend (bottom-left overlay)
 *   - Time slider (bottom bar)
 *   - Click popup for selected hotspot
 *
 * Props:
 *   heatmapCells     - from useHeatmap().data.cells
 *   hotspots         - from useHotspots().data.hotspots
 *   violations       - from useViolations().data.data
 *   selectedHotspot  - currently selected hotspot object
 *   onHotspotClick   - callback(hotspot)
 *   hour             - current slider hour (0-23)
 *   onHourChange     - setter for hour
 */
import React, { useEffect, useRef, useCallback } from 'react'
import {
  MapContainer, TileLayer, CircleMarker,
  Popup, useMap, Marker, Polygon, Tooltip
} from 'react-leaflet'
import L from 'leaflet'
import { getCISHex, getEnforcementAction } from '../../utils/cis'
import { formatNumber, vehicleLabel } from '../../utils/format'
import { CISBadge } from '../common'
import { CISLegend } from './CISLegend'
import { TimeSlider } from './TimeSlider'

// Bengaluru city centre
const BENGALURU_CENTER = [12.9716, 77.5946]
const DEFAULT_ZOOM = 12

// ── Hexagonal Grid Layer (shades coordinates like AQI maps) ───────────────
function HexagonalGridLayer({ cells = [] }) {
  return (
    <>
      {cells.map(cell => (
        cell.boundary ? (
          <Polygon
            key={cell.cell_id}
            positions={cell.boundary}
            pathOptions={{
              fillColor: getCISHex(cell.avg_cis),
              fillOpacity: 0.4,
              color: 'rgba(255, 255, 255, 0.45)',
              weight: 0.5,
            }}
            eventHandlers={{
              mouseover: (e) => {
                e.target.setStyle({ fillOpacity: 0.65, weight: 1.2, color: '#ffffff' });
              },
              mouseout: (e) => {
                e.target.setStyle({ fillOpacity: 0.4, weight: 0.5, color: 'rgba(255, 255, 255, 0.45)' });
              }
            }}
          >
            <Tooltip sticky>
              <div style={{ fontFamily: 'var(--font)', fontSize: 11, padding: '2px 4px' }}>
                <strong>Zone: {cell.cell_id}</strong><br />
                Avg CIS: <strong style={{ color: getCISHex(cell.avg_cis) }}>{Math.round(cell.avg_cis)}</strong> ({cell.cis_label})<br />
                Violations: <strong>{cell.violation_count}</strong>
              </div>
            </Tooltip>
          </Polygon>
        ) : null
      ))}
    </>
  )
}

// ── Fly-to selected hotspot ────────────────────────────────────────────────
function FlyToHotspot({ hotspot }) {
  const map = useMap()
  useEffect(() => {
    if (hotspot) {
      map.flyTo([hotspot.latitude, hotspot.longitude], 15, { duration: 1.2 })
    }
  }, [hotspot, map])
  return null
}

// ── Custom hotspot marker icon ─────────────────────────────────────────────
function createHotspotIcon(score, isSelected) {
  const hex = getCISHex(score)
  const size = isSelected ? 40 : 32
  const border = isSelected ? `3px solid #1d4ed8` : `2px solid rgba(255,255,255,0.9)`
  return L.divIcon({
    className: '',
    html: `<div class="hotspot-div-icon" style="
      width:${size}px; height:${size}px;
      background:${hex};
      border:${border};
      box-shadow: 0 3px 12px rgba(0,0,0,0.3);
      border-radius:50%;
      display:flex; align-items:center; justify-content:center;
      font-size:${isSelected ? 13 : 11}px; font-weight:800; color:#fff;
      font-family:Inter,sans-serif;
    ">${Math.round(score)}</div>`,
    iconSize: [size, size],
    iconAnchor: [size / 2, size / 2],
    popupAnchor: [0, -size / 2 - 4],
  })
}

// ── Popup content for hotspot ─────────────────────────────────────────────
function HotspotPopup({ hotspot, name }) {
  const cis = hotspot.avg_cis_per_violation ?? hotspot.total_cis
  const action = getEnforcementAction(cis)
  const { label: vLabel, icon } = vehicleLabel(hotspot.dominant_vehicle)

  return (
    <div className="map-popup">
      <div className="map-popup-header">
        <div className="map-popup-title">{name}</div>
        <div className="map-popup-coords">
          {hotspot.latitude.toFixed(4)}°N, {hotspot.longitude.toFixed(4)}°E
        </div>
      </div>
      <div className="map-popup-body">
        <div className="popup-row">
          <span className="popup-row-label">CIS Score</span>
          <CISBadge score={cis} showScore />
        </div>
        <div className="popup-row">
          <span className="popup-row-label">Violations</span>
          <span className="popup-row-value">{formatNumber(hotspot.violation_count)}</span>
        </div>
        <div className="popup-row">
          <span className="popup-row-label">Dominant Vehicle</span>
          <span className="popup-row-value">{icon} {vLabel}</span>
        </div>
        {hotspot.top_violation_types?.length > 0 && (
          <div className="popup-row">
            <span className="popup-row-label">Top Violation</span>
            <span className="popup-row-value" style={{ fontSize: 11, maxWidth: 130, textAlign: 'right' }}>
              {hotspot.top_violation_types[0]}
            </span>
          </div>
        )}
        <div className="popup-action">{action}</div>
      </div>
    </div>
  )
}

// ── Main Map ───────────────────────────────────────────────────────────────
const LOCATION_NAMES = [
  'Koramangala 4th Block', 'ORR Bellandur', 'MG Road', 'HSR 27th Main',
  'Koramangala Junction', 'Yeshwanthpur Circle', 'Indiranagar 100ft Rd',
  'Electronic City', 'Whitefield ITPL', 'Sarjapur Road',
  'Marathahalli Bridge', 'KR Puram', 'Silk Board Junction',
  'Hebbal Flyover', 'Jayanagar 4th Block',
]

export function TrafficMap({
  heatmapCells = [],
  hotspots = [],
  violations = [],
  selectedHotspot,
  onHotspotClick,
  hour,
  onHourChange,
}) {
  const getHotspotName = useCallback((hs, idx) => {
    return LOCATION_NAMES[idx] || `${hs.latitude.toFixed(3)}°N, ${hs.longitude.toFixed(3)}°E`
  }, [])

  return (
    <div style={{ width: '100%', height: '100%', position: 'relative' }}>
      <MapContainer
        center={BENGALURU_CENTER}
        zoom={DEFAULT_ZOOM}
        style={{ width: '100%', height: '100%' }}
        zoomControl={false}
        id="parksense-map"
      >
        {/* Base tile (CartoDB Positron - Premium Minimal Light) */}
        <TileLayer
          url="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png"
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
          subdomains="abcd"
          maxZoom={20}
        />

        {/* CIS Heatmap overlay (Solid H3 Hexagonal polygons) */}
        <HexagonalGridLayer cells={heatmapCells} />

        {/* Fly to selected hotspot */}
        {selectedHotspot && <FlyToHotspot hotspot={selectedHotspot} />}

        {/* Violation pins (light, behind hotspot markers) */}
        {violations.slice(0, 400).map((v, i) => (
          v.latitude && v.longitude ? (
            <CircleMarker
              key={v.violation_id ?? i}
              center={[v.latitude, v.longitude]}
              radius={4}
              pathOptions={{
                fillColor: getCISHex(v.cis_score ?? 50),
                fillOpacity: 0.7,
                color: '#fff',
                weight: 1,
              }}
            >
              <Popup>
                <div style={{ padding: 8, fontSize: 12, fontFamily: 'Inter,sans-serif' }}>
                  <b>{v.violation_type}</b><br />
                  {v.vehicle_type} · {v.police_station}<br />
                  CIS: <b>{v.cis_score ? Math.round(v.cis_score) : '—'}</b>
                  {v.violation_id && (
                    <div style={{ marginTop: 6, fontSize: 11, color: 'var(--text-muted)' }}>
                      ID: {v.violation_id}
                    </div>
                  )}
                </div>
              </Popup>
            </CircleMarker>
          ) : null
        ))}

        {/* Hotspot cluster markers */}
        {hotspots.map((hs, i) => {
          const cisScore = hs.avg_cis_per_violation ?? hs.total_cis
          const isSelected = selectedHotspot?.hotspot_id === hs.hotspot_id
          const name = getHotspotName(hs, i)
          return (
            <Marker
              key={hs.hotspot_id}
              position={[hs.latitude, hs.longitude]}
              icon={createHotspotIcon(cisScore, isSelected)}
              eventHandlers={{ click: () => onHotspotClick(hs) }}
              zIndexOffset={isSelected ? 1000 : 0}
            >
              <Popup>
                <HotspotPopup hotspot={hs} name={name} />
              </Popup>
            </Marker>
          )
        })}
      </MapContainer>

      {/* CIS Legend overlay (bottom-left) */}
      <div style={{
        position: 'absolute', bottom: 60, left: 16, zIndex: 900,
      }}>
        <CISLegend />
      </div>

      {/* Zoom controls (top-right) */}
      <div style={{ position: 'absolute', top: 16, right: 16, zIndex: 900, display: 'flex', flexDirection: 'column', gap: 4 }}>
        <MapZoomControls />
      </div>

      {/* Time Slider */}
      <TimeSlider hour={hour} onChange={onHourChange} />
    </div>
  )
}

// Simple zoom controls since we disabled the default
function MapZoomControls() {
  const map = useMap ? null : null // placeholder — real impl below
  return null
}

// We use a wrapper to access map context
function ZoomButtonsInner() {
  const map = useMap()
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
      <button
        className="btn btn-secondary"
        style={{ width: 32, height: 32, padding: 0, fontSize: 18, lineHeight: 1 }}
        onClick={() => map.zoomIn()}
        id="map-zoom-in" aria-label="Zoom in"
      >+</button>
      <button
        className="btn btn-secondary"
        style={{ width: 32, height: 32, padding: 0, fontSize: 18, lineHeight: 1 }}
        onClick={() => map.zoomOut()}
        id="map-zoom-out" aria-label="Zoom out"
      >−</button>
      <button
        className="btn btn-secondary"
        style={{ width: 32, height: 32, padding: 0, fontSize: 14, lineHeight: 1 }}
        onClick={() => map.setView(BENGALURU_CENTER, DEFAULT_ZOOM)}
        id="map-reset" aria-label="Reset view" title="Reset to Bengaluru"
      >⌂</button>
    </div>
  )
}

// Export a version with internal map access
export function TrafficMapWithControls(props) {
  return (
    <div style={{ width: '100%', height: '100%', position: 'relative' }}>
      <MapContainer
        center={BENGALURU_CENTER}
        zoom={DEFAULT_ZOOM}
        style={{ width: '100%', height: '100%' }}
        zoomControl={false}
        id="parksense-map"
      >
        <TileLayer
          url="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png"
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
          subdomains="abcd"
          maxZoom={20}
        />
        <HexagonalGridLayer cells={props.heatmapCells ?? []} />
        {props.selectedHotspot && <FlyToHotspot hotspot={props.selectedHotspot} />}

        {(props.violations ?? []).slice(0, 400).map((v, i) => (
          v.latitude && v.longitude ? (
            <CircleMarker
              key={v.violation_id ?? i}
              center={[v.latitude, v.longitude]}
              radius={4}
              pathOptions={{
                fillColor: getCISHex(v.cis_score ?? 50),
                fillOpacity: 0.65,
                color: '#fff',
                weight: 1,
              }}
            >
              <Popup>
                <div style={{ padding: 8, fontSize: 12, fontFamily: 'Inter,sans-serif', minWidth: 180 }}>
                  <b>{v.violation_type}</b><br />
                  <span style={{ color: '#6b7280' }}>{v.vehicle_type} · {v.police_station}</span><br />
                  {v.junction_name && <span style={{ fontSize: 11 }}>{v.junction_name}</span>}<br />
                  CIS: <b style={{ color: getCISHex(v.cis_score) }}>{v.cis_score ? Math.round(v.cis_score) : '—'}</b>
                  {v.violation_id && (
                    <div style={{ marginTop: 6, fontSize: 10, color: '#9ca3af' }}>
                      ID: {v.violation_id}
                    </div>
                  )}
                </div>
              </Popup>
            </CircleMarker>
          ) : null
        ))}

        {(props.hotspots ?? []).map((hs, i) => {
          const cisScore = hs.avg_cis_per_violation ?? hs.total_cis
          const isSelected = props.selectedHotspot?.hotspot_id === hs.hotspot_id
          const name = LOCATION_NAMES[i] || `Zone ${i + 1}`
          return (
            <Marker
              key={hs.hotspot_id}
              position={[hs.latitude, hs.longitude]}
              icon={createHotspotIcon(cisScore, isSelected)}
              eventHandlers={{ click: () => props.onHotspotClick?.(hs) }}
              zIndexOffset={isSelected ? 1000 : 0}
            >
              <Popup>
                <HotspotPopup hotspot={hs} name={name} />
              </Popup>
            </Marker>
          )
        })}

        {/* Zoom controls inside map container for map context */}
        <div style={{ position: 'absolute', top: 16, right: 16, zIndex: 900 }}>
          <ZoomButtonsInner />
        </div>
      </MapContainer>

      {/* CIS Legend */}
      <div style={{
        position: 'absolute', bottom: 60, left: 16, zIndex: 900,
      }}>
        <CISLegend />
      </div>

      {/* Time Slider */}
      <TimeSlider hour={props.hour ?? 12} onChange={props.onHourChange ?? (() => { })} />
    </div>
  )
}
