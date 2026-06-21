/**
 * ParkSense AI — API Service Layer
 * Owner: localWorkspace branch (Mayank)
 *
 * All backend calls are made through this file.
 * API_BASE reads from VITE_API_BASE env var, falling back to the Vite proxy '/api'.
 *
 * Connected endpoints (FastAPI on localhost:8000):
 *   GET /api/stats
 *   GET /api/violations
 *   GET /api/hotspots
 *   GET /api/heatmap
 *   GET /api/predict
 *   GET /api/offenders
 *   GET /api/challan/recommend
 *   GET /api/parkflow/simulate
 *
 * If backend is down, hooks fall back to mockData.js automatically.
 */

import axios from 'axios'

// Vite proxy forwards /api/* → http://localhost:8000
// Override with VITE_API_BASE=http://your-backend.com for production
const API_BASE = import.meta.env.VITE_API_BASE ?? '/api'

const client = axios.create({
  baseURL: API_BASE,
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' },
})

// ── Stats ──────────────────────────────────────────────────────────────────
/**
 * GET /api/stats
 * Returns: { total_violations, approved, peak_hour, avg_cis,
 *            date_range, top_vehicle_types, top_violation_types,
 *            top_police_stations, hourly_distribution }
 */
export async function fetchStats() {
  const { data } = await client.get('/stats')
  return data
}

// ── Violations ─────────────────────────────────────────────────────────────
/**
 * GET /api/violations
 * @param {Object} filters
 * @param {string}  [filters.start_time]     - ISO datetime UTC
 * @param {string}  [filters.end_time]       - ISO datetime UTC
 * @param {number}  [filters.hour_start]     - 0-23
 * @param {number}  [filters.hour_end]       - 0-23
 * @param {string}  [filters.vehicle_type]   - comma-sep: "CAR,SCOOTER"
 * @param {string}  [filters.violation_type] - comma-sep
 * @param {string}  [filters.police_station] - exact match
 * @param {string}  [filters.validation_status] - "approved"|"rejected"|"pending"
 * @param {number}  [filters.limit]          - default 500, max 5000
 * @param {number}  [filters.offset]         - pagination
 */
export async function fetchViolations(filters = {}) {
  const params = stripEmpty(filters)
  const { data } = await client.get('/violations', { params })
  return data
}

// ── Hotspots ───────────────────────────────────────────────────────────────
/**
 * GET /api/hotspots
 * @param {Object} filters
 * @param {number}  [filters.limit]       - max hotspots (default 20)
 * @param {number}  [filters.min_cis]     - minimum avg CIS
 * @param {number}  [filters.min_count]   - minimum violations per cluster
 * @param {number}  [filters.eps_meters]  - DBSCAN radius metres
 * @param {number}  [filters.hour_start]
 * @param {number}  [filters.hour_end]
 * @param {string}  [filters.vehicle_type]
 */
export async function fetchHotspots(filters = {}) {
  const params = stripEmpty({ limit: 20, ...filters })
  const { data } = await client.get('/hotspots', { params })
  return data
}

// ── Heatmap ────────────────────────────────────────────────────────────────
/**
 * GET /api/heatmap
 * Returns cells[] with { latitude, longitude, avg_cis, intensity (0-1), cis_label }
 * @param {Object} filters
 * @param {number}  [filters.resolution] - H3 res 7-10 (default 8)
 * @param {number}  [filters.hour_start]
 * @param {number}  [filters.hour_end]
 * @param {string}  [filters.vehicle_type]
 * @param {number}  [filters.min_count]
 * @param {number}  [filters.top_n]      - limit cells returned
 */
export async function fetchHeatmap(filters = {}) {
  const params = stripEmpty({ resolution: 8, top_n: 300, ...filters })
  const { data } = await client.get('/heatmap', { params })
  return data
}

// ── Predictions ────────────────────────────────────────────────────────────
/**
 * GET /api/predict
 * @param {Object} opts
 * @param {number}  [opts.hour]
 * @param {number}  [opts.day_of_week] - 0=Mon
 * @param {number}  [opts.limit]       - cells to forecast
 * @param {number}  [opts.resolution]
 */
export async function fetchPredictions(opts = {}) {
  const params = stripEmpty({ limit: 15, ...opts })
  const { data } = await client.get('/predict', { params })
  return data
}

// ── Offenders ──────────────────────────────────────────────────────────────
/**
 * GET /api/offenders
 * @param {number} [limit] - number of offenders (default 50)
 */
export async function fetchOffenders(limit = 50) {
  const { data } = await client.get('/offenders', { params: { limit } })
  return data
}

// ── Challan ────────────────────────────────────────────────────────────────
/**
 * GET /api/challan/recommend
 * @param {string} violation_id - required
 * @param {number} [override_base_fine]
 */
export async function fetchChallanRecommendation(violation_id, override_base_fine) {
  const params = { violation_id, ...(override_base_fine ? { override_base_fine } : {}) }
  const { data } = await client.get('/challan/recommend', { params })
  return data
}

// ── Simulation ─────────────────────────────────────────────────────────────
/**
 * GET /api/parkflow/simulate
 * @param {Object} opts
 * @param {number}  opts.latitude
 * @param {number}  opts.longitude
 * @param {number}  [opts.radius_meters]
 * @param {string}  [opts.intervention_type] - "patrol"|"barricade"
 * @param {number}  [opts.efficiency]        - 0.1-1.0
 */
export async function fetchSimulation(opts) {
  const { data } = await client.get('/parkflow/simulate', { params: opts })
  return data
}

// ── Helpers ────────────────────────────────────────────────────────────────
/** Remove null/undefined/empty-string keys so axios doesn't send them as "null" */
function stripEmpty(obj) {
  return Object.fromEntries(
    Object.entries(obj).filter(([, v]) => v !== null && v !== undefined && v !== '')
  )
}
