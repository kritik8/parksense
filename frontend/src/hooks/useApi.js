/**
 * Generic data-fetching hook with loading / error / retry states.
 * Used as the base for all domain-specific hooks.
 *
 * Usage:
 *   const { data, loading, error, refetch } = useApi(fetchStats, [])
 *
 * @param {Function} fetchFn   - async function that returns data
 * @param {Array}    deps      - dependency array (re-fetches when these change)
 * @param {*}        fallback  - value returned while loading or on error
 * @param {Function} [onError] - optional callback when error occurs
 */
import { useState, useEffect, useCallback, useRef } from 'react'

export function useApi(fetchFn, deps = [], fallback = null, onError = null) {
  const [data, setData] = useState(fallback)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [usingMock, setUsingMock] = useState(false)
  const mountedRef = useRef(true)

  const fetch_ = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const result = await fetchFn()
      if (mountedRef.current) {
        setData(result)
        setUsingMock(false)
      }
    } catch (err) {
      if (mountedRef.current) {
        setError(err)
        setUsingMock(true)
        if (onError) onError(err)
        // fallback stays as-is; caller should set it to mock data
      }
    } finally {
      if (mountedRef.current) setLoading(false)
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps)

  useEffect(() => {
    mountedRef.current = true
    fetch_()
    return () => { mountedRef.current = false }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [fetch_])

  return { data, loading, error, refetch: fetch_, usingMock }
}
