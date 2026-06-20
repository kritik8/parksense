/**
 * TimeSlider — Bottom bar on the map
 * Shows an hour slider 0–23 with play/pause simulation.
 * When backend supports historical playback, wire play to step through hours.
 * Currently: time-filter only (no auto-playback implemented).
 */
import React, { useState, useEffect, useRef } from 'react'
import { formatHour } from '../../utils/format'

export function TimeSlider({ hour, onChange }) {
  const [playing, setPlaying] = useState(false)
  const intervalRef = useRef(null)

  const togglePlay = () => {
    setPlaying(p => !p)
  }

  useEffect(() => {
    if (playing) {
      intervalRef.current = setInterval(() => {
        onChange(prev => {
          const next = (prev + 1) % 24
          return next
        })
      }, 800)
    } else {
      clearInterval(intervalRef.current)
    }
    return () => clearInterval(intervalRef.current)
  }, [playing, onChange])

  const marks = [0, 6, 12, 18, 23]

  return (
    <div className="time-slider-bar" role="region" aria-label="Time slider">
      {/* Play/Pause */}
      <button
        className="btn btn-ghost btn-icon"
        onClick={togglePlay}
        title={playing ? 'Pause time simulation' : 'Play time simulation (demo)'}
        aria-label={playing ? 'Pause' : 'Play time simulation'}
        id="timeslider-play-btn"
        style={{ flexShrink: 0 }}
      >
        {playing ? '⏸' : '▶'}
      </button>

      {/* Slider track */}
      <div style={{ flex: 1, position: 'relative' }}>
        <input
          type="range"
          min={0}
          max={23}
          step={1}
          value={hour}
          onChange={e => onChange(Number(e.target.value))}
          className="time-slider-input"
          id="timeslider-input"
          aria-label={`Time: ${formatHour(hour)}`}
          style={{ width: '100%' }}
        />
        {/* Hour marks */}
        <div style={{
          display: 'flex', justifyContent: 'space-between',
          padding: '0 2px', marginTop: 2,
        }}>
          {marks.map(m => (
            <span key={m} style={{ fontSize: 10, color: 'var(--text-muted)', userSelect: 'none' }}>
              {formatHour(m)}
            </span>
          ))}
        </div>
      </div>

      {/* Current hour label */}
      <span className="time-label" aria-live="polite">
        {formatHour(hour)}
      </span>

      {playing && (
        <span style={{ fontSize: 10, color: 'var(--blue-600)', fontWeight: 600 }}>
          SIMULATING
        </span>
      )}
    </div>
  )
}
