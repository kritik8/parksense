/**
 * ParkSense AI — Mock / Fallback Data
 * Owner: localWorkspace branch (Mayank)
 *
 * ALL mock data lives here and ONLY here.
 * To replace with real API data: remove the import of this file
 * and ensure the backend is running. Hooks fall back to these
 * only when the API call throws an error.
 *
 * Bengaluru coordinates reference: center ~12.9716, 77.5946
 */

export const MOCK_STATS = {
  total_violations: 1247,
  approved: 1089,
  rejected: 104,
  pending: 54,
  peak_hour: 18,
  avg_cis: 56.4,
  date_range: { min: '2023-10-01T00:00:00+00:00', max: '2023-10-28T23:59:00+00:00' },
  top_vehicle_types: [
    { type: 'CAR', count: 421 },
    { type: 'SCOOTER', count: 318 },
    { type: 'MOTOR CYCLE', count: 187 },
    { type: 'PASSENGER AUTO', count: 142 },
    { type: 'BUS', count: 98 },
    { type: 'OTHERS', count: 81 },
  ],
  top_violation_types: [
    { type: 'WRONG PARKING', count: 584 },
    { type: 'NO PARKING', count: 312 },
    { type: 'FOOTPATH PARKING', count: 189 },
    { type: 'PARKING NEAR ROAD CROSSING', count: 97 },
    { type: 'DOUBLE PARKING', count: 41 },
    { type: 'PARKING IN BUS LANES', count: 24 },
  ],
  top_police_stations: [
    { station: 'Koramangala', count: 198 },
    { station: 'Bellandur', count: 176 },
    { station: 'HSR Layout', count: 154 },
    { station: 'MG Road', count: 132 },
    { station: 'Madiwala', count: 118 },
    { station: 'Indiranagar', count: 109 },
    { station: 'Electronic City', count: 87 },
    { station: 'Whitefield', count: 76 },
  ],
  hourly_distribution: [
    { hour: 0, count: 12 }, { hour: 1, count: 8 }, { hour: 2, count: 5 },
    { hour: 3, count: 4 }, { hour: 4, count: 7 }, { hour: 5, count: 18 },
    { hour: 6, count: 34 }, { hour: 7, count: 67 }, { hour: 8, count: 98 },
    { hour: 9, count: 87 }, { hour: 10, count: 74 }, { hour: 11, count: 68 },
    { hour: 12, count: 82 }, { hour: 13, count: 78 }, { hour: 14, count: 71 },
    { hour: 15, count: 79 }, { hour: 16, count: 95 }, { hour: 17, count: 118 },
    { hour: 18, count: 134 }, { hour: 19, count: 122 }, { hour: 20, count: 96 },
    { hour: 21, count: 72 }, { hour: 22, count: 48 }, { hour: 23, count: 28 },
  ],
}

export const MOCK_HOTSPOTS = {
  total_hotspots: 10,
  hotspots: [
    {
      hotspot_id: 'h1', latitude: 12.9352, longitude: 77.6245,
      total_cis: 940, avg_cis_per_violation: 94, violation_count: 42,
      label: 'Critical', dominant_vehicle: 'CAR',
      top_violation_types: ['WRONG PARKING', 'NO PARKING'],
      violation_ids_sample: ['V001', 'V002'],
    },
    {
      hotspot_id: 'h2', latitude: 12.9698, longitude: 77.7499,
      total_cis: 870, avg_cis_per_violation: 87, violation_count: 38,
      label: 'Critical', dominant_vehicle: 'MOTOR CYCLE',
      top_violation_types: ['NO PARKING', 'FOOTPATH PARKING'],
      violation_ids_sample: ['V003', 'V004'],
    },
    {
      hotspot_id: 'h3', latitude: 12.9766, longitude: 77.5993,
      total_cis: 720, avg_cis_per_violation: 72, violation_count: 31,
      label: 'High', dominant_vehicle: 'CAR',
      top_violation_types: ['WRONG PARKING'],
      violation_ids_sample: ['V005', 'V006'],
    },
    {
      hotspot_id: 'h4', latitude: 12.9279, longitude: 77.6271,
      total_cis: 720, avg_cis_per_violation: 72, violation_count: 28,
      label: 'High', dominant_vehicle: 'SCOOTER',
      top_violation_types: ['FOOTPATH PARKING', 'WRONG PARKING'],
      violation_ids_sample: ['V007', 'V008'],
    },
    {
      hotspot_id: 'h5', latitude: 12.9352, longitude: 77.6245,
      total_cis: 940, avg_cis_per_violation: 94, violation_count: 22,
      label: 'Critical', dominant_vehicle: 'BUS',
      top_violation_types: ['PARKING IN BUS LANES'],
      violation_ids_sample: ['V009', 'V010'],
    },
    {
      hotspot_id: 'h6', latitude: 13.0124, longitude: 77.5505,
      total_cis: 650, avg_cis_per_violation: 65, violation_count: 20,
      label: 'High', dominant_vehicle: 'PASSENGER AUTO',
      top_violation_types: ['WRONG PARKING'],
      violation_ids_sample: ['V011'],
    },
    {
      hotspot_id: 'h7', latitude: 12.9581, longitude: 77.6477,
      total_cis: 540, avg_cis_per_violation: 54, violation_count: 17,
      label: 'Moderate', dominant_vehicle: 'CAR',
      top_violation_types: ['NO PARKING'],
      violation_ids_sample: ['V012'],
    },
    {
      hotspot_id: 'h8', latitude: 12.9082, longitude: 77.6476,
      total_cis: 480, avg_cis_per_violation: 48, violation_count: 15,
      label: 'Moderate', dominant_vehicle: 'SCOOTER',
      top_violation_types: ['WRONG PARKING'],
      violation_ids_sample: ['V013'],
    },
    {
      hotspot_id: 'h9', latitude: 12.9897, longitude: 77.7471,
      total_cis: 390, avg_cis_per_violation: 39, violation_count: 12,
      label: 'Low', dominant_vehicle: 'MOTOR CYCLE',
      top_violation_types: ['FOOTPATH PARKING'],
      violation_ids_sample: ['V014'],
    },
    {
      hotspot_id: 'h10', latitude: 12.8386, longitude: 77.6779,
      total_cis: 280, avg_cis_per_violation: 28, violation_count: 9,
      label: 'Low', dominant_vehicle: 'CAR',
      top_violation_types: ['NO PARKING'],
      violation_ids_sample: ['V015'],
    },
  ],
}

export const MOCK_HEATMAP = {
  cells: [
    { latitude: 12.9352, longitude: 77.6245, avg_cis: 94, intensity: 0.94, cis_label: 'Critical', violation_count: 42 },
    { latitude: 12.9698, longitude: 77.7499, avg_cis: 87, intensity: 0.87, cis_label: 'Critical', violation_count: 38 },
    { latitude: 12.9766, longitude: 77.5993, avg_cis: 72, intensity: 0.72, cis_label: 'High',     violation_count: 31 },
    { latitude: 12.9279, longitude: 77.6271, avg_cis: 72, intensity: 0.72, cis_label: 'High',     violation_count: 28 },
    { latitude: 13.0124, longitude: 77.5505, avg_cis: 65, intensity: 0.65, cis_label: 'High',     violation_count: 20 },
    { latitude: 12.9581, longitude: 77.6477, avg_cis: 54, intensity: 0.54, cis_label: 'Moderate', violation_count: 17 },
    { latitude: 12.9082, longitude: 77.6476, avg_cis: 48, intensity: 0.48, cis_label: 'Moderate', violation_count: 15 },
    { latitude: 12.9897, longitude: 77.7471, avg_cis: 39, intensity: 0.39, cis_label: 'Low',      violation_count: 12 },
    { latitude: 12.8386, longitude: 77.6779, avg_cis: 28, intensity: 0.28, cis_label: 'Low',      violation_count: 9 },
    { latitude: 12.9900, longitude: 77.5600, avg_cis: 18, intensity: 0.18, cis_label: 'Clear',    violation_count: 4 },
  ],
}

export const MOCK_VIOLATIONS = {
  total: 1247,
  count: 20,
  data: [
    { violation_id: 'V001', latitude: 12.9352, longitude: 77.6244, vehicle_type: 'CAR', violation_type: 'WRONG PARKING', cis_score: 94, police_station: 'Koramangala', junction_name: 'Koramangala 4th Block Junction', hour: 18 },
    { violation_id: 'V002', latitude: 12.9698, longitude: 77.7499, vehicle_type: 'MOTOR CYCLE', violation_type: 'NO PARKING', cis_score: 87, police_station: 'Bellandur', junction_name: 'ORR Bellandur Junction', hour: 17 },
    { violation_id: 'V003', latitude: 12.9766, longitude: 77.5993, vehicle_type: 'CAR', violation_type: 'FOOTPATH PARKING', cis_score: 72, police_station: 'MG Road', junction_name: 'MG Road Metro', hour: 19 },
    { violation_id: 'V004', latitude: 12.9279, longitude: 77.6271, vehicle_type: 'SCOOTER', violation_type: 'WRONG PARKING', cis_score: 72, police_station: 'HSR Layout', junction_name: 'HSR 27th Main', hour: 8 },
    { violation_id: 'V005', latitude: 13.0124, longitude: 77.5505, vehicle_type: 'BUS', violation_type: 'PARKING IN BUS LANES', cis_score: 65, police_station: 'Yeshwanthpur', junction_name: 'Yeshwanthpur Circle', hour: 9 },
  ],
}

export const MOCK_PREDICTIONS = {
  predictions: [
    { h3_cell: 'c1', latitude: 12.9352, longitude: 77.6245, predicted_count: 18, confidence: 0.87, threat_level: 'CRITICAL' },
    { h3_cell: 'c2', latitude: 12.9698, longitude: 77.7499, predicted_count: 14, confidence: 0.79, threat_level: 'HIGH'     },
    { h3_cell: 'c3', latitude: 12.9766, longitude: 77.5993, predicted_count: 11, confidence: 0.74, threat_level: 'HIGH'     },
    { h3_cell: 'c4', latitude: 12.9279, longitude: 77.6271, predicted_count: 7,  confidence: 0.68, threat_level: 'MODERATE' },
    { h3_cell: 'c5', latitude: 13.0124, longitude: 77.5505, predicted_count: 4,  confidence: 0.61, threat_level: 'LOW'      },
  ],
}

export const MOCK_OFFENDERS = {
  total_offenders_tracked: 8241,
  offenders: [
    { offender_rank: 1,  vehicle_number: 'KA01AB1234', violation_count: 120, total_cis: 505.4, avg_cis: 4.2, first_seen: '2023-10-01', last_seen: '2023-10-28' },
    { offender_rank: 2,  vehicle_number: 'KA05CD5678', violation_count: 89,  total_cis: 412.8, avg_cis: 4.6, first_seen: '2023-10-03', last_seen: '2023-10-27' },
    { offender_rank: 3,  vehicle_number: 'KA03EF9012', violation_count: 76,  total_cis: 387.2, avg_cis: 5.1, first_seen: '2023-10-02', last_seen: '2023-10-26' },
    { offender_rank: 4,  vehicle_number: 'KA41GH3456', violation_count: 64,  total_cis: 298.6, avg_cis: 4.7, first_seen: '2023-10-05', last_seen: '2023-10-25' },
    { offender_rank: 5,  vehicle_number: 'KA02IJ7890', violation_count: 58,  total_cis: 254.1, avg_cis: 4.4, first_seen: '2023-10-06', last_seen: '2023-10-24' },
    { offender_rank: 6,  vehicle_number: 'KA50KL2345', violation_count: 51,  total_cis: 218.7, avg_cis: 4.3, first_seen: '2023-10-07', last_seen: '2023-10-23' },
    { offender_rank: 7,  vehicle_number: 'KA04MN6789', violation_count: 45,  total_cis: 196.3, avg_cis: 4.4, first_seen: '2023-10-08', last_seen: '2023-10-22' },
    { offender_rank: 8,  vehicle_number: 'MH12OP3456', violation_count: 39,  total_cis: 174.8, avg_cis: 4.5, first_seen: '2023-10-09', last_seen: '2023-10-21' },
    { offender_rank: 9,  vehicle_number: 'TN09QR7890', violation_count: 34,  total_cis: 152.4, avg_cis: 4.5, first_seen: '2023-10-10', last_seen: '2023-10-20' },
    { offender_rank: 10, vehicle_number: 'KA53ST1234', violation_count: 29,  total_cis: 131.9, avg_cis: 4.6, first_seen: '2023-10-11', last_seen: '2023-10-19' },
  ],
}

export const MOCK_CHALLAN = {
  violation_id: 'V001',
  vehicle_number: 'KA01AB****',
  vehicle_type: 'CAR',
  violation_type: 'WRONG PARKING',
  base_fine: 500,
  cis_score: 94,
  multiplier: 4.76,
  recommended_fine: 2380,
  breakdown: {
    base_fine: 500,
    cis_score: 94,
    multiplier: 4.76,
    formula: 'base_fine × (1 + (cis_score / 100) × 4)',
    road_criticality: 0.92,
    cascade_multiplier: 2.4,
    police_station: 'Koramangala',
    junction_name: 'Koramangala 4th Block Junction',
  },
}

// Hotspot name lookup (lat/lng → readable label)
// Used when backend doesn't return a name field
export const HOTSPOT_NAMES = {
  h1: 'Koramangala 4th Block',
  h2: 'ORR Bellandur',
  h3: 'MG Road',
  h4: 'HSR Layout 27th Main',
  h5: 'Koramangala Junction',
  h6: 'Yeshwanthpur Circle',
  h7: 'Indiranagar 100ft Rd',
  h8: 'Electronic City',
  h9: 'Whitefield ITPL Gate',
  h10: 'Sarjapur Road',
}
