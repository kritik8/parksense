/**
 * Filter Sidebar — Left panel
 * Sends filter changes up to App via onFiltersChange(newFilters)
 *
 * Filter fields:
 *   hour_start, hour_end  (from time slots or slider)
 *   vehicle_type          (comma-separated string for API)
 *   violation_type        (comma-separated string)
 *   police_station        (single string)
 */
import React, { useState, useCallback } from 'react'
import { formatHour } from '../../utils/format'

const TIME_SLOTS = [
  { label: '12 AM – 4 AM',  start: 0,  end: 4,  id: 'night'   },
  { label: '4 AM – 8 AM',   start: 4,  end: 8,  id: 'early'   },
  { label: '8 AM – 12 PM',  start: 8,  end: 12, id: 'morning' },
  { label: '12 PM – 4 PM',  start: 12, end: 16, id: 'noon'    },
  { label: '4 PM – 8 PM ⚡', start: 16, end: 20, id: 'peak'    },
  { label: '8 PM – 12 AM',  start: 20, end: 23, id: 'evening' },
]

const VEHICLE_TYPES = [
  'CAR', 'SCOOTER', 'MOTOR CYCLE', 'PASSENGER AUTO',
  'BUS', 'GOODS AUTO', 'VAN', 'LGV', 'TANKER',
]

const VIOLATION_TYPES = [
  'WRONG PARKING', 'NO PARKING', 'FOOTPATH PARKING',
  'PARKING NEAR ROAD CROSSING', 'DOUBLE PARKING',
  'PARKING IN BUS LANES', 'PARKING ON BRIDGE',
]

const VEHICLE_ICONS = {
  CAR: '🚗', SCOOTER: '🛵', 'MOTOR CYCLE': '🏍️',
  'PASSENGER AUTO': '🛺', BUS: '🚌', 'GOODS AUTO': '🛺',
  VAN: '🚐', LGV: '🚚', TANKER: '🚛',
}

export function FilterSidebar({ filters, onFiltersChange, policeStations = [] }) {
  const [vehiclesOpen, setVehiclesOpen] = useState(true)
  const [violationsOpen, setViolationsOpen] = useState(true)
  const [stationOpen, setStationOpen] = useState(false)

  const selectedSlot = TIME_SLOTS.find(
    s => s.start === filters.hour_start && s.end === filters.hour_end
  )

  const selectedVehicles = filters.vehicle_type
    ? filters.vehicle_type.split(',').map(v => v.trim()).filter(Boolean)
    : []

  const selectedViolations = filters.violation_type
    ? filters.violation_type.split(',').map(v => v.trim()).filter(Boolean)
    : []

  const handleSlot = useCallback((slot) => {
    if (selectedSlot?.id === slot.id) {
      onFiltersChange({ ...filters, hour_start: null, hour_end: null })
    } else {
      onFiltersChange({ ...filters, hour_start: slot.start, hour_end: slot.end })
    }
  }, [filters, onFiltersChange, selectedSlot])

  const toggleVehicle = useCallback((v) => {
    const next = selectedVehicles.includes(v)
      ? selectedVehicles.filter(x => x !== v)
      : [...selectedVehicles, v]
    onFiltersChange({ ...filters, vehicle_type: next.join(',') })
  }, [filters, onFiltersChange, selectedVehicles])

  const toggleViolation = useCallback((v) => {
    const next = selectedViolations.includes(v)
      ? selectedViolations.filter(x => x !== v)
      : [...selectedViolations, v]
    onFiltersChange({ ...filters, violation_type: next.join(',') })
  }, [filters, onFiltersChange, selectedViolations])

  const handleStation = useCallback((e) => {
    onFiltersChange({ ...filters, police_station: e.target.value })
  }, [filters, onFiltersChange])

  const handleClear = useCallback(() => {
    onFiltersChange({ hour_start: null, hour_end: null, vehicle_type: '', violation_type: '', police_station: '' })
  }, [onFiltersChange])

  const hasActiveFilters = filters.hour_start !== null || selectedVehicles.length > 0
    || selectedViolations.length > 0 || filters.police_station

  return (
    <div className="filter-sidebar" role="complementary" aria-label="Filters">
      {/* Header */}
      <div className="sidebar-section" style={{ borderBottom: '2px solid var(--border)' }}>
        <div className="flex items-center justify-between">
          <div style={{ fontWeight: 700, fontSize: 13, color: 'var(--text-primary)' }}>
            🔍 Filters
          </div>
          {hasActiveFilters && (
            <button
              className="btn btn-ghost btn-sm"
              onClick={handleClear}
              id="filter-clear-btn"
              aria-label="Clear all filters"
            >
              Clear all
            </button>
          )}
        </div>
        {hasActiveFilters && (
          <div style={{ marginTop: 6, fontSize: 11, color: 'var(--blue-600)', fontWeight: 600 }}>
            {[
              selectedVehicles.length && `${selectedVehicles.length} vehicle${selectedVehicles.length > 1 ? 's' : ''}`,
              selectedViolations.length && `${selectedViolations.length} violation${selectedViolations.length > 1 ? 's' : ''}`,
              filters.police_station && 'station',
              filters.hour_start !== null && 'time slot',
            ].filter(Boolean).join(' · ')} selected
          </div>
        )}
      </div>

      {/* Time Slots */}
      <div className="sidebar-section">
        <div className="sidebar-section-title" style={{ marginBottom: 10 }}>⏰ Time Range</div>
        <div className="slot-grid">
          {TIME_SLOTS.map(slot => (
            <button
              key={slot.id}
              id={`slot-${slot.id}`}
              className={`slot-btn ${selectedSlot?.id === slot.id ? 'active' : ''}`}
              onClick={() => handleSlot(slot)}
              aria-pressed={selectedSlot?.id === slot.id}
            >
              {slot.label}
            </button>
          ))}
        </div>
        {filters.hour_start !== null && (
          <div style={{ marginTop: 8, fontSize: 11, color: 'var(--text-secondary)', textAlign: 'center' }}>
            {formatHour(filters.hour_start)} – {formatHour(filters.hour_end)}
          </div>
        )}
      </div>

      {/* Vehicle Type */}
      <div className="sidebar-section">
        <div
          className="sidebar-section-header"
          onClick={() => setVehiclesOpen(o => !o)}
          role="button"
          aria-expanded={vehiclesOpen}
        >
          <div className="sidebar-section-title">🚗 Vehicle Type</div>
          <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>{vehiclesOpen ? '▲' : '▼'}</span>
        </div>
        {vehiclesOpen && (
          <div>
            {VEHICLE_TYPES.map(v => (
              <label key={v} className="checkbox-label" id={`vehicle-${v.replace(/\s+/g, '-').toLowerCase()}`}>
                <input
                  type="checkbox"
                  checked={selectedVehicles.includes(v)}
                  onChange={() => toggleVehicle(v)}
                  aria-label={`Filter by ${v}`}
                />
                <span>{VEHICLE_ICONS[v] ?? '🚘'} {titleCase(v)}</span>
              </label>
            ))}
          </div>
        )}
      </div>

      {/* Violation Type */}
      <div className="sidebar-section">
        <div
          className="sidebar-section-header"
          onClick={() => setViolationsOpen(o => !o)}
          role="button"
          aria-expanded={violationsOpen}
        >
          <div className="sidebar-section-title">⚠️ Violation Type</div>
          <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>{violationsOpen ? '▲' : '▼'}</span>
        </div>
        {violationsOpen && (
          <div>
            {VIOLATION_TYPES.map(v => (
              <label key={v} className="checkbox-label" id={`vtype-${v.replace(/\s+/g, '-').toLowerCase()}`}>
                <input
                  type="checkbox"
                  checked={selectedViolations.includes(v)}
                  onChange={() => toggleViolation(v)}
                  aria-label={`Filter by ${v}`}
                />
                <span style={{ fontSize: 12 }}>{titleCase(v)}</span>
              </label>
            ))}
          </div>
        )}
      </div>

      {/* Police Station */}
      <div className="sidebar-section">
        <div
          className="sidebar-section-header"
          onClick={() => setStationOpen(o => !o)}
          role="button"
          aria-expanded={stationOpen}
        >
          <div className="sidebar-section-title">🏢 Police Station</div>
          <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>{stationOpen ? '▲' : '▼'}</span>
        </div>
        {stationOpen && (
          <div>
            <select
              className="input select"
              value={filters.police_station || ''}
              onChange={handleStation}
              id="filter-police-station"
              aria-label="Filter by police station"
            >
              <option value="">All Stations</option>
              {policeStations.map(s => (
                <option key={s.station} value={s.station}>{s.station}</option>
              ))}
            </select>
          </div>
        )}
      </div>

      {/* Footer */}
      <div style={{ padding: '12px 16px', marginTop: 'auto', borderTop: '1px solid var(--border)' }}>
        <div style={{ fontSize: 10, color: 'var(--text-muted)', lineHeight: 1.6 }}>
          Filters update map, hotspots, and charts in real time.
        </div>
      </div>
    </div>
  )
}

function titleCase(str) {
  return str.toLowerCase().replace(/\b\w/g, c => c.toUpperCase())
}
