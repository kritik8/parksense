/**
 * Domain-specific API hooks for ParkSense AI
 * Each hook wraps useApi with the right fetch function + mock fallback.
 *
 * Returns: { data, loading, error, refetch, usingMock }
 */
import { useMemo } from 'react'
import { useApi } from './useApi'
import {
  fetchStats, fetchHotspots, fetchHeatmap,
  fetchPredictions, fetchOffenders, fetchViolations,
} from '../services/api'
import {
  MOCK_STATS, MOCK_HOTSPOTS, MOCK_HEATMAP,
  MOCK_PREDICTIONS, MOCK_OFFENDERS, MOCK_VIOLATIONS,
} from '../data/mockData'

// ── Stats ──────────────────────────────────────────────────────────────────
export function useStats() {
  return useApi(fetchStats, [], MOCK_STATS)
}

// ── Hotspots ───────────────────────────────────────────────────────────────
/**
 * @param {Object} filters - hour_start, hour_end, vehicle_type, limit
 */
export function useHotspots(filters = {}) {
  const fetchFn = useMemo(
    () => () => fetchHotspots(filters),
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [JSON.stringify(filters)]
  )
  return useApi(fetchFn, [JSON.stringify(filters)], MOCK_HOTSPOTS)
}

// ── Heatmap ────────────────────────────────────────────────────────────────
export function useHeatmap(filters = {}) {
  const fetchFn = useMemo(
    () => () => fetchHeatmap(filters),
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [JSON.stringify(filters)]
  )
  return useApi(fetchFn, [JSON.stringify(filters)], MOCK_HEATMAP)
}

// ── Predictions ────────────────────────────────────────────────────────────
export function usePredictions(opts = {}) {
  const fetchFn = useMemo(
    () => () => fetchPredictions(opts),
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [JSON.stringify(opts)]
  )
  return useApi(fetchFn, [JSON.stringify(opts)], MOCK_PREDICTIONS)
}

// ── Offenders ──────────────────────────────────────────────────────────────
export function useOffenders(limit = 50) {
  const fetchFn = useMemo(
    () => () => fetchOffenders(limit),
    [limit]
  )
  return useApi(fetchFn, [limit], MOCK_OFFENDERS)
}

// ── Violations (map markers) ───────────────────────────────────────────────
export function useViolations(filters = {}) {
  const fetchFn = useMemo(
    () => () => fetchViolations({ limit: 500, ...filters }),
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [JSON.stringify(filters)]
  )
  return useApi(fetchFn, [JSON.stringify(filters)], MOCK_VIOLATIONS)
}
