# 🅿️ ParkSense AI — Bengaluru Traffic Command Center

**AI-powered parking violation impact scoring engine that quantifies congestion caused by illegal parking.**

---

## What It Does

ParkSense AI scores every parking violation in Bengaluru using a **Congestion Impact Score (CIS)** that factors in:
- **Vehicle blockage factor** — how much lane capacity the parked vehicle blocks
- **Road criticality** — betweenness centrality of the road segment (OSMnx)
- **Temporal weight** — rush hour multiplier derived from historical data
- **3-hop cascade propagation** — BPR-style delay ripple to downstream junctions

It then surfaces:
- Live colour-graded heatmap (green → red, like AQI)
- Ranked hotspot list with CIS breakdown
- Repeat offender & fleet profiling
- Dynamic challan **recommendation** (not an automatic fine — a policy tool)
- ParkFlow what-if simulation
- Predicted hotspots for the next 2 hours (LightGBM)

---

## Branches

| Branch | Owner | Responsibility |
|--------|-------|---------------|
| `main` | All | Stable integration target — no direct commits |
| `frontend-dashboard` | Mayank | React + Leaflet UI |
| `backend-api` | Me (Kratik) | FastAPI core + all endpoints |
| `backend-geo-engine` | Aditi | CIS scorer, graph, clustering, BPR, cascade |
| `backend-ml-analysis` | Eric | Forecasting, repeat offenders, sensor audit, POI bias |

---

## Quick Start

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

---

## Tech Stack

| Layer | Tool |
|-------|------|
| Frontend | React + Vite + Leaflet.js + Recharts |
| Backend API | Python 3.11 + FastAPI + Uvicorn |
| Geo/Graph | OSMnx + NetworkX + Shapely + H3 |
| ML | scikit-learn (DBSCAN) + LightGBM + Prophet |
| Data | Pandas + SQLite + Parquet |
| Maps | OpenStreetMap (free) — NO paid map APIs |

---

## Data

- `data/raw/` — original CSV (298K violation records, gitignored if >50MB)
- `data/processed/` — cleaned Parquet files, pre-computed CIS, centrality cache
- `data/mock/` — small mock dataset (500 rows) for development without the full CSV

> All data sources are free / open. No Google Maps, TomTom, or paid traffic APIs.

---

## Team

- **Mayank** — Frontend dashboard
- **Kratik** — Backend API
- **Aditi** — Geo / scoring engine
- **Eric** — ML / analysis engine

---

## API Endpoints Documentation

The backend exposes the following endpoints (default host `http://localhost:8000`).

### 1. System Health
*   **`GET /`**
    *   *Description*: System health check. Returns API details and docs path.
    *   *Response*: `{"status": "ok", "service": "ParkSense AI API", "docs": "/docs"}`

### 2. Violations Core
*   **`GET /api/violations`**
    *   *Description*: Fetch paginated lists of violations with spatial and temporal filters.
    *   *Query Parameters*:
        *   `start_time`, `end_time` (ISO datetime string, e.g., `2024-01-15T08:00:00`)
        *   `hour_start`, `hour_end` (0-23)
        *   `vehicle_type` (comma-separated, e.g., `CAR,SCOOTER`)
        *   `violation_type` (comma-separated, e.g., `WRONG PARKING`)
        *   `police_station` (exact match, case-insensitive)
        *   `limit` (default 500, max 5000), `offset` (default 0)
*   **`GET /api/violations/{violation_id}`**
    *   *Description*: Fetch details of a single violation by its unique ID.

### 3. Dashboard Statistics
*   **`GET /api/stats`**
    *   *Description*: Computes aggregate metrics for dashboard counters and trend graphs.
    *   *Response Keys*: `total_violations`, `approved`, `rejected`, `pending`, `peak_hour`, `avg_cis`, `top_vehicle_types`, `top_violation_types`, `top_police_stations`, `hourly_distribution`.

### 4. Congestion Hotspots & Heatmaps
*   **`GET /api/hotspots`**
    *   *Description*: Runs DBSCAN spatial clustering over the top-15,000 CIS violations to find primary congestion centers.
    *   *Query Parameters*: `limit` (max hotspots to return), `min_cis`, `min_count` (min violations to form cluster), `eps_meters` (search radius).
*   **`GET /api/heatmap`**
    *   *Description*: Groups violation counts and impact scores into H3 hexagons at a selected resolution.
    *   *Query Parameters*: `resolution` (7-10, default 8), `hour_start`, `hour_end`, `top_n` (return top N cells by impact).

### 5. Repeat Offenders & Fleets
*   **`GET /api/offenders`**
    *   *Description*: Ranks repeat vehicle numbers based on cumulative CIS impact.
    *   *Query Parameters*: `limit` (default 100).
*   **`GET /api/fleets`**
    *   *Description*: Groups vehicles sharing license plate owner patterns (first 6 characters) to identify commercial fleets with high violation counts.

### 6. Sensor Audit & Health
*   **`GET /api/sensors/audit`**
    *   *Description*: Audits reporting validation rates per police station to flag faulty cameras or biased report patterns. Returns `rejection_rate` and `health_flag` (`OK`, `WARNING`, `CRITICAL`).

### 7. H3 Predictive Forecasting (LightGBM)
*   **`GET /api/predict`**
    *   *Description*: Returns predicted violation count and confidence probability for H3 hex cells over the next 2 hours.
    *   *Query Parameters*: `resolution`, `hour`, `day_of_week`, `limit`.

### 8. Dynamic Challan Recommendation
*   **`GET /api/challan/recommend`**
    *   *Description*: Calculates progressive fines for violation entries based on road centrality and impact congestion multiplier.
    *   *Query Parameters*: `violation_id` (required), `override_base_fine` (optional).
    *   *Calculation*: `recommended_fine = base_fine * (1 + (cis_score / 100) * 4)`

### 9. What-If Traffic Simulation
*   **`GET /api/parkflow/simulate`**
    *   *Description*: Runs a spatial what-if model simulating the traffic impact (CIS reduction and spatial overflow displacement) of placing patrols or barricades.
    *   *Query Parameters*: `latitude` (required), `longitude` (required), `radius_meters`, `intervention_type` (`patrol` / `barricade`), `efficiency` (0.1 - 1.0).

