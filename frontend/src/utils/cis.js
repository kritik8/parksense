/**
 * CIS (Congestion Impact Score) helpers
 * Score 0-100 → label, color class, hex color, background color
 */

/** @param {number|null} score */
export function getCISLabel(score) {
  if (score === null || score === undefined) return 'Unknown'
  if (score >= 81) return 'Critical'
  if (score >= 61) return 'High'
  if (score >= 41) return 'Moderate'
  if (score >= 21) return 'Low'
  return 'Clear'
}

/** Returns CSS class suffix: 'clear' | 'low' | 'moderate' | 'high' | 'critical' */
export function getCISClass(score) {
  return getCISLabel(score).toLowerCase().replace(' ', '-')
}

/** Returns the map hex color for the CIS score (for Leaflet markers / heatmap) */
export function getCISHex(score) {
  if (score === null || score === undefined) return '#8e8e93' // iOS Gray
  if (score >= 81) return '#ff3b30' // iOS Red
  if (score >= 61) return '#ff9500' // iOS Orange
  if (score >= 41) return '#ffcc00' // iOS Yellow
  if (score >= 21) return '#a6e22e' // Pastel Lime
  return '#34c759' // iOS Green
}

/** Returns a CSS rgba string with the given opacity for backgrounds */
export function getCISBg(score, alpha = 0.12) {
  const hex = getCISHex(score)
  return `${hex}${Math.round(alpha * 255).toString(16).padStart(2, '0')}`
}

/** Returns border color hex */
export function getCISBorder(score) {
  if (score === null || score === undefined) return '#e5e7eb'
  if (score >= 81) return '#ffb3b0'
  if (score >= 61) return '#ffd1a4'
  if (score >= 41) return '#ffeaa7'
  if (score >= 21) return '#d3f2d3'
  return '#c2eed0'
}

/** Returns the Leaflet heatmap gradient config */
export const HEATMAP_GRADIENT = {
  0.0: '#34c759',
  0.2: '#a6e22e',
  0.4: '#ffcc00',
  0.6: '#ff9500',
  0.8: '#ff3b30',
  1.0: '#bf261f',
}

/** CIS legend bands */
export const CIS_LEGEND = [
  { range: '81–100', label: 'Critical',   hex: '#ff3b30', class: 'critical' },
  { range: '61–80',  label: 'High Impact',hex: '#ff9500', class: 'high'     },
  { range: '41–60',  label: 'Moderate',   hex: '#ffcc00', class: 'moderate' },
  { range: '21–40',  label: 'Low Impact', hex: '#a6e22e', class: 'low'      },
  { range: '0–20',   label: 'Clear',      hex: '#34c759', class: 'clear'    },
]

/** Returns recommended enforcement action string */
export function getEnforcementAction(cisScore) {
  if (cisScore >= 81) return '🚨 Immediate tow + fine — critical blockage'
  if (cisScore >= 61) return '⚠️ Deploy traffic officer within 15 minutes'
  if (cisScore >= 41) return '📋 Issue challan — monitor closely'
  if (cisScore >= 21) return '🔔 Issue challan — low priority'
  return '✅ Monitor only — minimal impact'
}
