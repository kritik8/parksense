/**
 * ParkSense AI — Root Application Component
 * Owner: localWorkspace branch (Mayank)
 *
 * Layout:
 *   DashboardHeader
 *   StatsBar
 *   ┌─────────────┬─────────────────────────────┬────────────────┐
 *   │ FilterSidebar│ TrafficMap + TimeSlider     │ HotspotList   │
 *   └─────────────┴─────────────────────────────┴────────────────┘
 *   AnalyticsBottom (tabs: CIS Trend | Vehicle Dist | Predictions | Offenders | Challan)
 *
 * Filter state is managed here and flows down to all components.
 * API hooks are called here and data is distributed to children.
 */

import React, { useState, useCallback, useMemo, useRef, useEffect } from 'react'
import './App.css'

// Leaflet CSS is loaded via CDN <link> in index.html
// leaflet.heat is loaded via CDN <script> in index.html

// Layout
import { DashboardHeader } from './components/layout/DashboardHeader'
import { StatsBar }        from './components/layout/StatsBar'

// Panels
import { FilterSidebar }        from './components/filters/FilterSidebar'
import { HotspotList }          from './components/hotspots/HotspotList'
import { TrafficMapWithControls } from './components/map/TrafficMap'

// Analytics bottom tabs
import { CISTrendChart }          from './components/charts/CISTrendChart'
import { VehicleDistChart }       from './components/charts/VehicleDistChart'
import { PredictionList }         from './components/predictions/PredictionList'
import { RepeatOffendersTable }   from './components/offenders/RepeatOffendersTable'
import { ChallanPanel }           from './components/challan/ChallanPanel'

// Hooks
import {
  useStats, useHotspots, useHeatmap, useViolations,
  usePredictions, useOffenders,
} from './hooks/useDashboard'



// ── Initial filter state ───────────────────────────────────────────────────
const DEFAULT_FILTERS = {
  hour_start:     null,
  hour_end:       null,
  vehicle_type:   '',
  violation_type: '',
  police_station: '',
}

// ── Analytics tabs ──────────────────────────────────────────────────────────
const TABS = [
  { id: 'trend',       label: 'CIS Trend'        },
  { id: 'vehicles',    label: 'Vehicle Mix'       },
  { id: 'predictions', label: 'Upcoming Hotspots' },
  { id: 'offenders',   label: 'Repeat Offenders'  },
  { id: 'challan',     label: 'Challan'           },
]

// ── Main App ────────────────────────────────────────────────────────────────
export default function App() {
  // Theme state (Lifted up for full app mode)
  const [theme, setTheme] = useState(() => {
    return localStorage.getItem('parksense-theme') || 'light'
  })

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme)
    localStorage.setItem('parksense-theme', theme)
  }, [theme])

  const toggleTheme = useCallback(() => {
    setTheme(prev => prev === 'light' ? 'dark' : 'light')
  }, [])

  // Filter state (lifted up — shared across sidebar, map, hotspots)
  const [filters, setFilters] = useState(DEFAULT_FILTERS)

  // Map state
  const [selectedHotspot, setSelectedHotspot] = useState(null)
  const [sliderHour, setSliderHour]           = useState(new Date().getHours())

  // Analytics tab
  const [activeTab, setActiveTab] = useState('trend')

  // Drag-resize: track analytics panel height
  const ANALYTICS_MIN = 120
  const ANALYTICS_MAX = 420
  const ANALYTICS_DEFAULT = 190
  const [analyticsHeight, setAnalyticsHeight] = useState(ANALYTICS_DEFAULT)
  const dragRef = useRef(null)
  const isDragging = useRef(false)
  const startY = useRef(0)
  const startH = useRef(0)

  useEffect(() => {
    const onMove = (e) => {
      if (!isDragging.current) return
      const delta = startY.current - (e.clientY ?? e.touches?.[0]?.clientY ?? startY.current)
      const newH = Math.min(ANALYTICS_MAX, Math.max(ANALYTICS_MIN, startH.current + delta))
      setAnalyticsHeight(newH)
    }
    const onUp = () => { isDragging.current = false; document.body.style.cursor = '' }
    window.addEventListener('mousemove', onMove)
    window.addEventListener('mouseup', onUp)
    window.addEventListener('touchmove', onMove)
    window.addEventListener('touchend', onUp)
    return () => {
      window.removeEventListener('mousemove', onMove)
      window.removeEventListener('mouseup', onUp)
      window.removeEventListener('touchmove', onMove)
      window.removeEventListener('touchend', onUp)
    }
  }, [])

  const startDrag = useCallback((e) => {
    isDragging.current = true
    startY.current = e.clientY ?? e.touches?.[0]?.clientY
    startH.current = analyticsHeight
    document.body.style.cursor = 'ns-resize'
    e.preventDefault()
  }, [analyticsHeight])

  // Build API filter params from UI filter state + slider hour
  const apiFilters = useMemo(() => ({
    ...(filters.hour_start !== null ? { hour_start: filters.hour_start } : {}),
    ...(filters.hour_end   !== null ? { hour_end:   filters.hour_end   } : {}),
    ...(filters.vehicle_type   ? { vehicle_type:   filters.vehicle_type   } : {}),
    ...(filters.violation_type ? { violation_type: filters.violation_type } : {}),
    ...(filters.police_station ? { police_station: filters.police_station } : {}),
  }), [filters])

  // ── Data hooks ────────────────────────────────────────────────────────────
  const statsResult     = useStats()
  const hotspotsResult  = useHotspots({ ...apiFilters, limit: 20 })
  const heatmapResult   = useHeatmap({ ...apiFilters, top_n: 300 })
  const violationsResult= useViolations({ ...apiFilters, limit: 500 })
  const predictResult   = usePredictions({ hour: sliderHour, limit: 10 })
  const offendersResult = useOffenders(20)

  const stats      = statsResult.data
  const hotspots   = hotspotsResult.data?.hotspots    ?? []
  const heatmapCells = heatmapResult.data?.cells      ?? []
  const violations = violationsResult.data?.data       ?? []
  const predictions= predictResult.data?.predictions   ?? []
  const offenders  = offendersResult.data?.offenders   ?? []

  // Any hook using mock → show banner
  const usingMock = statsResult.usingMock || hotspotsResult.usingMock

  // ── Handlers ──────────────────────────────────────────────────────────────
  const handleFiltersChange = useCallback((newFilters) => {
    setFilters(newFilters)
    setSelectedHotspot(null) // reset selection when filters change
  }, [])

  const handleHotspotSelect = useCallback((hs) => {
    setSelectedHotspot(prev => prev?.hotspot_id === hs.hotspot_id ? null : hs)
  }, [])

  const handleHourChange = useCallback((h) => {
    setSliderHour(typeof h === 'function' ? h(sliderHour) : h)
  }, [sliderHour])

  const handleRefresh = useCallback(() => {
    statsResult.refetch()
    hotspotsResult.refetch()
    heatmapResult.refetch()
    violationsResult.refetch()
  }, [statsResult, hotspotsResult, heatmapResult, violationsResult])

  // ── Render ────────────────────────────────────────────────────────────────
  return (
    <div className="app-shell">
      {/* Header */}
      <DashboardHeader
        lastUpdated={stats?.date_range?.max}
        onRefresh={handleRefresh}
        usingMock={usingMock}
        theme={theme}
        onToggleTheme={toggleTheme}
      />

      {/* Stats Bar */}
      <StatsBar stats={stats} loading={statsResult.loading} />

      {/* Main body: filters | map | hotspots */}
      <div className="app-body">
        {/* Left: Filters */}
        <FilterSidebar
          filters={filters}
          onFiltersChange={handleFiltersChange}
          policeStations={stats?.top_police_stations ?? []}
        />

        {/* Centre: Map + Analytics bottom */}
        <div className="map-analytics-col">
          {/* Map */}
          <div className="map-wrapper" style={{ flex: 1, minHeight: 0 }}>
            <TrafficMapWithControls
              heatmapCells={heatmapCells}
              hotspots={hotspots}
              violations={violations}
              selectedHotspot={selectedHotspot}
              onHotspotClick={handleHotspotSelect}
              hour={sliderHour}
              onHourChange={handleHourChange}
            />
          </div>

          {/* Drag handle */}
          <div
            ref={dragRef}
            onMouseDown={startDrag}
            onTouchStart={startDrag}
            title="Drag to resize map / analytics panel"
            style={{
              height: 6, cursor: 'ns-resize', flexShrink: 0,
              background: 'var(--border)', position: 'relative',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              transition: 'background 0.15s',
            }}
            onMouseEnter={e => e.currentTarget.style.background = 'var(--blue-500)'}
            onMouseLeave={e => e.currentTarget.style.background = 'var(--border)'}
          >
            <div style={{ width: 32, height: 3, borderRadius: 2, background: 'var(--text-muted)', opacity: 0.5 }} />
          </div>

          {/* Analytics tabs — bottom panel */}
          <div className="analytics-bottom" style={{ height: analyticsHeight, flexShrink: 0 }}>
            {/* Tab bar */}
            <div className="tab-nav" role="tablist">
              {TABS.map(tab => (
                <button
                  key={tab.id}
                  id={`tab-${tab.id}`}
                  className={`tab-btn ${activeTab === tab.id ? 'active' : ''}`}
                  onClick={() => setActiveTab(tab.id)}
                  role="tab"
                  aria-selected={activeTab === tab.id}
                  aria-controls={`tabpanel-${tab.id}`}
                >
                  {tab.label}
                </button>
              ))}
            </div>

            {/* Tab content */}
            <div className="analytics-tab-content" role="tabpanel" id={`tabpanel-${activeTab}`}>
              <div style={{ flex: 1, padding: '8px 12px', overflow: 'hidden', overflowY: 'auto', display: 'flex', flexDirection: 'column' }}>
                {activeTab === 'trend' && (
                  <CISTrendChart
                    data={stats?.hourly_distribution ?? []}
                    loading={statsResult.loading}
                  />
                )}
                {activeTab === 'vehicles' && (
                  <VehicleDistChart
                    data={stats?.top_vehicle_types ?? []}
                    loading={statsResult.loading}
                  />
                )}
                {activeTab === 'predictions' && (
                  <PredictionList
                    predictions={predictions}
                    loading={predictResult.loading}
                  />
                )}
                {activeTab === 'offenders' && (
                  <RepeatOffendersTable
                    offenders={offenders}
                    loading={offendersResult.loading}
                  />
                )}
                {activeTab === 'challan' && (
                  <ChallanPanel
                    selectedViolationId={
                      selectedHotspot?.violation_ids_sample?.[0] ?? ''
                    }
                  />
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Right: Hotspot List */}
        <HotspotList
          hotspots={hotspots}
          loading={hotspotsResult.loading}
          selectedId={selectedHotspot?.hotspot_id}
          onSelect={handleHotspotSelect}
        />
      </div>
    </div>
  )
}
