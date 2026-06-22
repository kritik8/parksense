/**
 * CIS Trend Chart — 24-hour violation distribution
 * Data source: stats.hourly_distribution from GET /api/stats
 *
 * Shows: line chart of violation counts by hour of day
 * Color fill gradient changes by CIS intensity of the hour
 */
import React from 'react'
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, ReferenceLine,
} from 'recharts'
import { formatHour } from '../../utils/format'
import { LoadingState, EmptyState } from '../common'

const PEAK_HOUR = 18

function CustomTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null
  return (
    <div style={{
      background: 'var(--bg-secondary, #fff)', border: '1px solid var(--border)',
      borderRadius: 8, padding: '8px 12px', boxShadow: 'var(--shadow)',
      fontSize: 12, fontFamily: 'var(--font), sans-serif',
    }}>
      <div style={{ fontWeight: 700, color: 'var(--text-primary)' }}>{formatHour(label)}</div>
      <div style={{ color: 'var(--blue-600)', marginTop: 2 }}>
        {payload[0]?.value} violations
      </div>
    </div>
  )
}

export function CISTrendChart({ data = [], loading }) {
  if (loading) return <LoadingState compact message="Loading trend…" />
  if (!data.length) return <EmptyState icon="📈" title="No trend data" desc="No hourly data available." />

  const maxCount = Math.max(...data.map(d => d.count), 1)

  return (
    <ResponsiveContainer width="100%" height="100%">
      <AreaChart
        data={data}
        margin={{ top: 8, right: 16, left: -20, bottom: 0 }}
      >
        <defs>
          <linearGradient id="cisGradient" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%"   stopColor="#3b82f6" stopOpacity={0.3} />
            <stop offset="100%" stopColor="#3b82f6" stopOpacity={0.02} />
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
        <XAxis
          dataKey="hour"
          tickFormatter={formatHour}
          tick={{ fontSize: 10, fill: 'var(--text-muted)' }}
          interval={3}
          axisLine={false}
          tickLine={false}
        />
        <YAxis
          tick={{ fontSize: 10, fill: 'var(--text-muted)' }}
          axisLine={false}
          tickLine={false}
          width={32}
        />
        <Tooltip content={<CustomTooltip />} />
        <ReferenceLine
          x={PEAK_HOUR}
          stroke="var(--cis-orange)"
          strokeDasharray="4 2"
          label={{ value: 'Peak', fontSize: 9, fill: 'var(--cis-orange)' }}
        />
        <Area
          type="monotone"
          dataKey="count"
          stroke="#3b82f6"
          strokeWidth={2}
          fill="url(#cisGradient)"
          dot={false}
          activeDot={{ r: 4, fill: '#1d4ed8' }}
        />
      </AreaChart>
    </ResponsiveContainer>
  )
}
