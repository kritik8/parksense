/**
 * Vehicle Distribution Chart
 * Data: stats.top_vehicle_types from GET /api/stats
 * Shows: horizontal bar chart of violations per vehicle type
 */
import React from 'react'
import {
  BarChart, Bar, XAxis, YAxis, Tooltip,
  ResponsiveContainer, Cell,
} from 'recharts'
import { formatNumber } from '../../utils/format'
import { LoadingState, EmptyState } from '../common'

const VEHICLE_COLORS = [
  '#3b82f6', '#8b5cf6', '#06b6d4', '#10b981',
  '#f59e0b', '#ef4444', '#ec4899',
]

function CustomTooltip({ active, payload }) {
  if (!active || !payload?.length) return null
  return (
    <div style={{
      background: '#fff', border: '1px solid var(--border)',
      borderRadius: 8, padding: '8px 12px', boxShadow: 'var(--shadow)',
      fontSize: 12,
    }}>
      <b>{payload[0]?.payload?.type}</b>
      <div style={{ color: 'var(--blue-600)' }}>{formatNumber(payload[0]?.value)} violations</div>
    </div>
  )
}

function friendlyType(t) {
  const MAP = {
    'CAR': 'Car', 'SCOOTER': 'Scooter', 'MOTOR CYCLE': 'Motorcycle',
    'PASSENGER AUTO': 'Auto', 'GOODS AUTO': 'Goods Auto',
    'BUS': 'Bus', 'MAXI-CAB': 'Maxi-Cab', 'VAN': 'Van',
    'LGV': 'Light Goods', 'TANKER': 'Tanker', 'OTHERS': 'Others',
  }
  return MAP[t?.toUpperCase()] ?? t
}

export function VehicleDistChart({ data = [], loading }) {
  if (loading) return <LoadingState compact message="Loading distribution…" />
  if (!data.length) return <EmptyState icon="🚗" title="No data" />

  const chartData = data.map(d => ({ ...d, type: friendlyType(d.type) }))

  return (
    <ResponsiveContainer width="100%" height="100%">
      <BarChart
        data={chartData}
        layout="vertical"
        margin={{ top: 4, right: 16, left: 0, bottom: 4 }}
      >
        <XAxis
          type="number"
          tick={{ fontSize: 10, fill: 'var(--text-muted)' }}
          axisLine={false}
          tickLine={false}
        />
        <YAxis
          type="category"
          dataKey="type"
          tick={{ fontSize: 11, fill: 'var(--text-secondary)' }}
          width={72}
          axisLine={false}
          tickLine={false}
        />
        <Tooltip content={<CustomTooltip />} />
        <Bar dataKey="count" radius={[0, 4, 4, 0]} maxBarSize={14}>
          {chartData.map((_, i) => (
            <Cell key={i} fill={VEHICLE_COLORS[i % VEHICLE_COLORS.length]} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  )
}
