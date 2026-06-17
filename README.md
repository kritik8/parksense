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
