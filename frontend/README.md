# ParkSense AI — Frontend Dashboard

> **Bengaluru Traffic Command Center** — A polished light-theme dashboard for analyzing illegal parking violations and their Congestion Impact Score (CIS).

---

## Quick Start

```bash
cd parksense/frontend
npm install
npm run dev
# → Opens at http://localhost:3000
```

> The Vite dev server proxies all `/api/*` calls to `http://localhost:8000`.
> Start the FastAPI backend first for live data, or use without backend for demo mode (mock data).

---

## Stack

| Layer       | Technology                        |
|-------------|-----------------------------------|
| Framework   | React 18 + Vite 5                 |
| Map         | Leaflet 1.9 + react-leaflet 4     |
| Heatmap     | leaflet.heat 0.2 (CDN via HTML)   |
| Charts      | Recharts 2.12                     |
| HTTP client | Axios 1.7                         |
| Styling     | Vanilla CSS (light theme)         |
| Icons       | Emoji (no icon library needed)    |

---

## Environment Variables

Copy `.env.example` → `.env` if you need overrides:

```bash
# Only needed when frontend is deployed separately from backend
VITE_API_BASE=http://localhost:8000/api
```

The dev server proxy (`vite.config.js`) already handles this for local development — no `.env` needed.

---

## API Integration

| Component              | Endpoint                      | Status               |
|------------------------|-------------------------------|----------------------|
| StatsBar               | `GET /api/stats`              | ✅ Connected          |
| HeatmapLayer (map)     | `GET /api/heatmap`            | ✅ Connected          |
| ViolationMarkers (map) | `GET /api/violations`         | ✅ Connected          |
| HotspotList + markers  | `GET /api/hotspots`           | ✅ Connected          |
| CISTrendChart          | `GET /api/stats` (`hourly_distribution`) | ✅ Connected |
| VehicleDistChart       | `GET /api/stats` (`top_vehicle_types`) | ✅ Connected   |
| PredictionList         | `GET /api/predict`            | ✅ Connected          |
| RepeatOffendersTable   | `GET /api/offenders`          | ✅ Connected          |
| ChallanPanel           | `GET /api/challan/recommend`  | ✅ Connected          |
| FilterSidebar options  | `GET /api/stats` (`top_police_stations`) | ✅ Connected |

**No unavailable endpoints.** All 8 backend routes are used.

**Not implemented**: `/api/timeseries` does not exist in the backend — the CIS Trend chart uses `hourly_distribution` from `/api/stats` instead.

---

## Fallback / Mock Data

All mock data is isolated in a **single file**: [`src/data/mockData.js`](src/data/mockData.js).

When an API call fails (backend offline), hooks automatically fall back to mock data and a **"Demo Mode"** banner is shown in the header.

To disable mock data entirely (fail hard when API is down): remove the `fallback` parameter from each `useApi` call in `src/hooks/useDashboard.js`.

---

## Folder Structure

```
src/
  services/api.js          ← All API calls (Axios)
  data/mockData.js         ← ALL fallback mock data
  utils/
    cis.js                 ← CIS label, color, enforcement helpers
    format.js              ← Number, date, currency formatters
  hooks/
    useApi.js              ← Generic fetch hook
    useDashboard.js        ← Domain-specific hooks (useStats, useHotspots…)
  components/
    common/index.jsx       ← LoadingState, EmptyState, ErrorState, CISBadge
    layout/
      DashboardHeader.jsx
      StatsBar.jsx
    filters/
      FilterSidebar.jsx
    map/
      TrafficMap.jsx       ← Main Leaflet map + heatmap + markers
      CISLegend.jsx
      TimeSlider.jsx
    hotspots/
      HotspotList.jsx
    charts/
      CISTrendChart.jsx
      VehicleDistChart.jsx
    predictions/
      PredictionList.jsx
    offenders/
      RepeatOffendersTable.jsx
    challan/
      ChallanPanel.jsx
  App.jsx                  ← Root layout + filter state
  App.css                  ← Dashboard grid + all component CSS
  index.css                ← Design system tokens + utilities
  main.jsx                 ← Vite entry point
```

---

## CIS Color Scale

| Score | Color      | Label       | Meaning                          |
|-------|------------|-------------|----------------------------------|
| 81–100 | 🔴 Red    | Critical    | Immediate tow + fine             |
| 61–80  | 🟠 Orange | High Impact | Deploy officer within 15 minutes |
| 41–60  | 🟡 Yellow | Moderate    | Issue challan, monitor           |
| 21–40  | 🟢 Lime   | Low Impact  | Challan, low priority            |
| 0–20   | 🟢 Green  | Clear       | Monitor only                     |

---

## Dynamic Challan

The **Challan panel** (Analytics → ⚖️ Challan tab) lets you enter any violation ID and see:
- Base statutory fine (by violation type)
- CIS score of that violation
- Impact multiplier: `1 + (CIS/100) × 4` → range 1.0× – 5.0×
- Recommended fine = base × multiplier

> **Disclaimer**: Recommended fines are a policy tool for decision-makers. Not automatically issued. Requires officer approval per the Motor Vehicles Act.

---

## Git Branch

All frontend work is committed on the `local-workspace` branch only.

---

## Running Without Backend

```bash
npm run dev
# Open http://localhost:3000
# All panels show realistic Bengaluru mock data
# Banner: "Demo Mode — start backend for live data"
```

## Running With Backend

```bash
# Terminal 1: Start FastAPI
cd parksense/backend
uvicorn app.main:app --reload --port 8000

# Terminal 2: Start Frontend
cd parksense/frontend
npm run dev
```
