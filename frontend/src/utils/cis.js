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
  if (score === null || score === undefined) return '#9ca3af'
  if (score >= 81) return '#d50000'
  if (score >= 61) return '#ff6d00'
  if (score >= 41) return '#ffd600'
  if (score >= 21) return '#aeea00'
  return '#00c853'
}

/** Returns a CSS rgba string with the given opacity for backgrounds */
export function getCISBg(score, alpha = 0.12) {
  const hex = getCISHex(score)
  return `${hex}${Math.round(alpha * 255).toString(16).padStart(2, '0')}`
}

/** Returns border color hex */
export function getCISBorder(score) {
  if (score === null || score === undefined) return '#e5e7eb'
  if (score >= 81) return '#fecaca'
  if (score >= 61) return '#fed7aa'
  if (score >= 41) return '#fde047'
  if (score >= 21) return '#d9f99d'
  return '#bbf7d0'
}

/** Returns the Leaflet heatmap gradient config */
export const HEATMAP_GRADIENT = {
  0.0: '#00c853',
  0.2: '#aeea00',
  0.4: '#ffd600',
  0.6: '#ff6d00',
  0.8: '#d50000',
  1.0: '#7b0000',
}

/** CIS legend bands */
export const CIS_LEGEND = [
  { range: '81–100', label: 'Critical',   hex: '#d50000', class: 'critical' },
  { range: '61–80',  label: 'High Impact',hex: '#ff6d00', class: 'high'     },
  { range: '41–60',  label: 'Moderate',   hex: '#ffd600', class: 'moderate' },
  { range: '21–40',  label: 'Low Impact', hex: '#aeea00', class: 'low'      },
  { range: '0–20',   label: 'Clear',      hex: '#00c853', class: 'clear'    },
]

/** Returns recommended enforcement action string */
export function getEnforcementAction(cisScore) {
  if (cisScore >= 81) return '🚨 Immediate tow + fine — critical blockage'
  if (cisScore >= 61) return '⚠️ Deploy traffic officer within 15 minutes'
  if (cisScore >= 41) return '📋 Issue challan — monitor closely'
  if (cisScore >= 21) return '🔔 Issue challan — low priority'
  return '✅ Monitor only — minimal impact'
}
