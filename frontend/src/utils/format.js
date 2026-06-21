/**
 * General formatting utilities for ParkSense AI
 */

/** Format integer with comma separators: 1247 → "1,247" */
export function formatNumber(n) {
  if (n === null || n === undefined) return '—'
  return Number(n).toLocaleString('en-IN')
}

/** Format a float to N decimal places */
export function formatDecimal(n, places = 1) {
  if (n === null || n === undefined) return '—'
  return Number(n).toFixed(places)
}

/** Format hour as 12h string: 18 → "6 PM", 8 → "8 AM" */
export function formatHour(hour) {
  if (hour === null || hour === undefined) return '—'
  const h = Number(hour)
  if (h === 0)  return '12 AM'
  if (h === 12) return '12 PM'
  if (h < 12)   return `${h} AM`
  return `${h - 12} PM`
}

/** Format hour range: (8, 10) → "8 AM – 10 AM" */
export function formatHourRange(start, end) {
  return `${formatHour(start)} – ${formatHour(end)}`
}

/**
 * Mask vehicle number for privacy.
 * Shows state code + last 3 chars: "KA01AB1234" → "KA01 ···1234"
 * @param {string} vehicleNumber
 */
export function maskVehicleNumber(vehicleNumber) {
  if (!vehicleNumber) return '—'
  const v = vehicleNumber.trim()
  if (v.length <= 6) return v
  const state = v.slice(0, 4)
  const tail  = v.slice(-4)
  return `${state}···${tail}`
}

/**
 * Format ISO timestamp to readable date+time
 * "2023-10-18T18:30:00+00:00" → "18 Oct, 6:30 PM"
 */
export function formatTimestamp(ts) {
  if (!ts) return '—'
  try {
    const d = new Date(ts)
    return d.toLocaleString('en-IN', {
      day: 'numeric', month: 'short',
      hour: 'numeric', minute: '2-digit', hour12: true,
    })
  } catch {
    return ts
  }
}

/** Format date only: "2023-10-18T..." → "18 Oct 2023" */
export function formatDate(ts) {
  if (!ts) return '—'
  try {
    return new Date(ts).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' })
  } catch {
    return ts
  }
}

/** Format INR currency: 2380 → "₹2,380" */
export function formatINR(amount) {
  if (amount === null || amount === undefined) return '—'
  return `₹${Number(amount).toLocaleString('en-IN')}`
}

/** Format confidence as percentage: 0.87 → "87%" */
export function formatConfidence(c) {
  if (c === null || c === undefined) return '—'
  return `${Math.round(Number(c) * 100)}%`
}

/** Truncate long text: "Koramangala 4th Block Junction" → "Koramangala 4th B…" */
export function truncate(str, max = 24) {
  if (!str) return '—'
  return str.length > max ? str.slice(0, max - 1) + '…' : str
}

/** Last-updated string: relative to now */
export function formatLastUpdated(date) {
  if (!date) return 'Unknown'
  const diff = Math.floor((Date.now() - new Date(date).getTime()) / 1000)
  if (diff < 60)    return 'Just now'
  if (diff < 3600)  return `${Math.floor(diff / 60)}m ago`
  return `${Math.floor(diff / 3600)}h ago`
}

/** Vehicle type → friendly label + icon */
export function vehicleLabel(type) {
  const MAP = {
    'CAR': { label: 'Car', icon: '🚗' },
    'SCOOTER': { label: 'Scooter', icon: '🛵' },
    'MOTOR CYCLE': { label: 'Motorcycle', icon: '🏍️' },
    'PASSENGER AUTO': { label: 'Auto', icon: '🛺' },
    'GOODS AUTO': { label: 'Goods Auto', icon: '🛺' },
    'BUS': { label: 'Bus', icon: '🚌' },
    'MAXI-CAB': { label: 'Maxi-Cab', icon: '🚐' },
    'VAN': { label: 'Van', icon: '🚐' },
    'LGV': { label: 'Light Goods', icon: '🚚' },
    'TANKER': { label: 'Tanker', icon: '🚛' },
    'OTHERS': { label: 'Other', icon: '🚘' },
  }
  return MAP[type?.toUpperCase()] ?? { label: type ?? 'Unknown', icon: '🚘' }
}
