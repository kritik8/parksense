/**
 * RepeatOffendersTable
 * Data: GET /api/offenders → offenders[]
 * Fields: offender_rank, vehicle_number, violation_count, total_cis, avg_cis, first_seen, last_seen
 *
 * Vehicle numbers are masked for privacy: KA01AB1234 → KA01···1234
 */
import React from 'react'
import { maskVehicleNumber, formatNumber, formatDecimal, formatDate } from '../../utils/format'
import { getCISClass, getCISHex } from '../../utils/cis'
import { LoadingState, EmptyState } from '../common'

export function RepeatOffendersTable({ offenders = [], loading }) {
  if (loading) return <LoadingState compact message="Loading offenders…" />
  if (!offenders.length) return (
    <EmptyState icon="👮" title="No repeat offenders" desc="No data available." />
  )

  return (
    <div style={{ height: '100%', display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
      <div style={{ flex: 1, overflowY: 'auto' }}>
        <table className="offenders-table" aria-label="Repeat offenders">
          <thead>
            <tr>
              <th>#</th>
              <th>Vehicle (Masked)</th>
              <th>Violations</th>
              <th>Total CIS</th>
              <th>Avg CIS</th>
              <th>Last Seen</th>
            </tr>
          </thead>
          <tbody>
            {offenders.map((o, i) => {
              const cisColor = getCISHex(o.avg_cis)
              return (
                <tr key={o.vehicle_number ?? i} id={`offender-row-${o.offender_rank}`}>
                  <td style={{ fontWeight: 700, color: 'var(--text-muted)', width: 28 }}>
                    {o.offender_rank}
                  </td>
                  <td>
                    <code className="vehicle-tag">{maskVehicleNumber(o.vehicle_number)}</code>
                  </td>
                  <td style={{ fontWeight: 700, color: 'var(--text-primary)' }}>
                    {formatNumber(o.violation_count)}
                  </td>
                  <td style={{ fontWeight: 600, color: 'var(--text-secondary)' }}>
                    {formatDecimal(o.total_cis, 0)}
                  </td>
                  <td>
                    <span style={{
                      fontWeight: 800, color: cisColor,
                      fontSize: 12,
                    }}>
                      {formatDecimal(o.avg_cis, 1)}
                    </span>
                  </td>
                  <td style={{ color: 'var(--text-muted)', fontSize: 11 }}>
                    {formatDate(o.last_seen)}
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
      <div style={{ fontSize: 10, color: 'var(--text-muted)', padding: '6px 10px', borderTop: '1px solid var(--border)', flexShrink: 0 }}>
        Vehicle numbers masked for privacy · Sorted by violation count
      </div>
    </div>
  )
}
