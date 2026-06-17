# ParkSense AI — Full Implementation Plan

## 1. Core Idea Analysis

Your [core_idea.md](file:///c:/IIIT Academics/Hustle/GLH_R2/core_idea.md) is solid. Here's what works, what needs tightening, and what I'd add:

### ✅ What's Strong

| Aspect | Why It Works |
|--------|-------------|
| **CIS Formula** | `vehicle_blockage_factor × road_criticality × temporal_weight × cascade_multiplier` — this is genuinely novel. No existing system quantifies parking impact this way. |
| **"Congestion Contagion" concept** | Modeling the ripple effect of one violation across downstream junctions is academically defensible and practically useful. Judges will love this. |
| **6-layer architecture** | Ingestion → Clustering → Graph → Scoring → Ranking → Prediction is clean and logical. |
| **Scalability claim** | "Any city with CCTV/GPS data" is realistic because the architecture is city-agnostic (just swap the road network graph). |

### ⚠️ What Needs Sharpening

| Gap | Problem | Fix |
|-----|---------|-----|
| **No ground-truth for congestion** | The dataset has violations but no actual traffic speed data. How do you *validate* that your CIS actually correlates with real congestion? | Use Google Maps Distance Matrix API or TomTom Traffic Flow API to pull historical/real-time travel times for road segments. Compare CIS predictions against actual speed drops. Even a simple correlation analysis adds massive credibility. |
| **Road width data assumption** | You say "pulled from OpenStreetMap" but OSM's `lanes` and `width` tags are missing for ~40-60% of Bengaluru roads. | Use a fallback hierarchy: OSM tag → road class default (trunk=4 lanes, primary=3, secondary=2, residential=1). This is standard in traffic modeling. |
| **Cascade multiplier is vague** | "How many downstream junctions are affected" — but HOW do you compute this? | Define it clearly: Run BFS/DFS from the violation's nearest graph edge. For each downstream junction within k hops, compute the capacity reduction propagated. The multiplier = sum of (1/distance × capacity_reduction) for all reachable junctions. |
| **Prediction layer underspecified** | "Prophet/LSTM" is mentioned but no feature design. | Define features: `hour_of_day`, `day_of_week`, `is_weekend`, `police_station_zone`, `nearby_commercial_density`, `historical_violation_count_same_slot`. This makes it concrete for judges. |

### 🔥 What I'd Add (Differentiators)

1. **Repeat Offender Intelligence**: The dataset has `vehicle_number`. Group violations by vehicle → identify fleets/individuals who park illegally repeatedly at the same spots. This is a goldmine for "targeted enforcement" narrative.

2. **Police Station Performance Scoring**: The dataset has `police_station` and `validation_status` (approved/rejected). Score each police station's enforcement efficiency. "Madiwala PS clears violations 3x faster than Bellandur PS" — this is politically powerful.

3. **Validation Pipeline Health**: ~15-20% of violations are `rejected`. Analyze rejection patterns → identify which devices/users submit low-quality reports. This shows system thinking, not just ML.

---

## 2. Color-Graded Congestion Map — Deep Design

Your AQI-style color grading idea is excellent. Here's exactly how to implement it:

### Color Scale Definition

| CIS Range | Color | Hex | Label | Meaning |
|-----------|-------|-----|-------|---------|
| 0-20 | 🟢 Green | `#00C853` | Clear | Few or no violations, road flowing normally |
| 21-40 | 🟡 Yellow-Green | `#AEEA00` | Low Impact | Some violations but minimal congestion effect |
| 41-60 | 🟠 Yellow | `#FFD600` | Moderate | Noticeable lane reduction, slowing traffic |
| 61-80 | 🔴 Orange | `#FF6D00` | High Impact | Significant congestion, enforcement needed soon |
| 81-100 | ⛔ Red | `#D50000` | Critical | Severe bottleneck, immediate action required |

### Map Layers (Bottom to Top)

```
Layer 5: Markers — Individual violation pins (clickable for details)
Layer 4: Hotspot Labels — CIS score badges on hotspot clusters  
Layer 3: Heatmap — Color-graded intensity overlay (the AQI layer)
Layer 2: Road Network — Highlighted road segments colored by impact
Layer 1: Base Map — Dark-themed Mapbox/Leaflet basemap
```

### How It Actually Works Technically

1. **Grid the city**: Divide Bengaluru into ~500m × 500m hex cells (H3 indexing from Uber)
2. **Per-cell CIS**: For each cell, sum up CIS of all active violations within it
3. **Interpolation**: Smooth the cell values using IDW (Inverse Distance Weighting) for a fluid heatmap effect, not blocky squares
4. **Render**: Use `deck.gl HeatmapLayer` or `Leaflet.heat` with the color scale above
5. **Real-time update**: WebSocket pushes new violation data → recalculates cell CIS → re-renders heatmap every 5 minutes

### Dashboard Layout Around the Map

```
┌──────────────────────────────────────────────────────────┐
│  🅿️ ParkSense AI — Bengaluru Traffic Command Center      │
├──────────┬───────────────────────────────┬───────────────┤
│          │                               │  TOP HOTSPOTS │
│ FILTERS  │                               │  ┌─────────┐ │
│          │                               │  │ #1 Kora- │ │
│ □ Time   │      🗺️ BENGALURU MAP          │  │ mangala  │ │
│   Range  │      (Color-graded heatmap)   │  │ CIS: 94  │ │
│          │                               │  ├─────────┤ │
│ □ Vehicle│                               │  │ #2 ORR   │ │
│   Type   │                               │  │ Bellan-  │ │
│          │                               │  │ dur      │ │
│ □ Viola- │                               │  │ CIS: 87  │ │
│   tion   │                               │  ├─────────┤ │
│   Type   │                               │  │ #3 MG    │ │
│          │                               │  │ Road     │ │
│ □ Police │                               │  │ CIS: 72  │ │
│   Station│                               │  └─────────┘ │
├──────────┴───────────────────────────────┴───────────────┤
│  📊 STATS BAR                                            │
│  Active Violations: 1,247 │ Avg CIS: 56 │ Peak Hour: 6PM│
├──────────────────────┬───────────────────────────────────┤
│  📈 CIS Trend (24hr) │  🔮 Predicted Hotspots (next 2hr) │
│  [Line Chart]        │  [List of upcoming hotspots]      │
└──────────────────────┴───────────────────────────────────┘
```

> [!TIP]
> The key visual impact for judges: When you demo, show the map at 6 AM (all green), then slide the time to 6 PM and watch it turn red across Koramangala, ORR, MG Road. This "city waking up" animation is a **killer demo moment**.

---

## 3. Dynamic Challan — My Honest View

### The Concept
Instead of a flat fine (e.g., ₹500 for wrong parking everywhere), the challan amount scales with the **congestion impact** your specific violation causes.

- Scooter parked in a residential lane at 3 AM → Low CIS → ₹200
- Truck parked on ORR near Bellandur junction at 6 PM → Critical CIS → ₹5,000

### Is It Fair? ⚖️

**Yes, but with important caveats:**

#### ✅ Arguments FOR (Strong)

| Argument | Reasoning |
|----------|-----------|
| **Proportional justice** | A violation causing 1,000 people a 15-minute delay is objectively worse than one causing 5 people a 1-minute delay. The punishment should match the societal harm. This is the same principle as pollution-based fines, carbon taxes, or congestion pricing (London, Stockholm, Singapore). |
| **Behavioral deterrence** | Flat fines become a "cost of doing business" for delivery fleets and commercial vehicles. Dynamic fines make high-impact zones genuinely expensive to violate, creating real behavioral change where it matters most. |
| **Resource-efficient enforcement** | Officers prioritize high-CIS zones → maximum congestion relief per enforcement hour. The fine revenue from critical zones also funds better enforcement. |
| **International precedent** | Singapore's Electronic Road Pricing charges more during peak hours on congested roads. Stockholm's congestion tax varies by time of day. Dynamic parking fines are the same principle applied to violations. |

#### ⚠️ Arguments AGAINST / Risks

| Risk | Mitigation |
|------|------------|
| **Equity concern**: A poor auto-rickshaw driver on ORR gets a ₹5,000 fine while a rich car owner in a residential area gets ₹200. Is this fair? | Cap the maximum multiplier at 3-5x the base fine. Set a floor AND ceiling. Also: the auto driver chose to park illegally at a critical spot — the fine reflects the impact, not the person. |
| **Transparency problem**: If people don't understand WHY their fine is higher, they'll feel it's arbitrary. | Every challan must show: "Your violation at [location] at [time] had a Congestion Impact Score of [X/100]. Base fine: ₹[Y]. Impact multiplier: [Z]x. Total: ₹[Y×Z]." Full transparency. |
| **Gaming risk**: People might move their illegal parking 50 meters to a lower-CIS zone. | Good! That's exactly the desired behavior. Moving violations from critical to non-critical locations IS the goal. The system adapts — if the new location becomes a hotspot, its CIS rises too. |
| **Legal feasibility**: Current Motor Vehicles Act has fixed fine slabs. Dynamic fines may need regulatory approval. | Present it as a "policy recommendation engine" for the hackathon. The system RECOMMENDS dynamic fines; actual implementation requires policy change. This is a safer framing for judges. |

### 🎯 My Recommendation

> **Include dynamic challan as a feature, but frame it carefully.**

- In the dashboard, show it as **"Recommended Fine"** alongside the standard fine
- Show the calculation transparently: base fine × impact multiplier
- Present it as a **policy tool for decision makers**, not an automatic system
- This gives you a powerful differentiator without the legal controversy
- The multiplier formula:
  ```
  recommended_fine = base_fine × (1 + CIS_normalized × max_multiplier_factor)
  
  Example: base_fine = ₹500, CIS = 85/100, max_multiplier = 4
  recommended_fine = ₹500 × (1 + 0.85 × 4) = ₹500 × 4.4 = ₹2,200
  ```

---

## 4. Five-Day Gameplan (June 16-20)

> [!IMPORTANT]
> **Deadline**: Submit by June 20 EOD. June 21 is for PPT/video only.
> **Today is June 16 (evening).** You have effectively 4.5 working days.

### Team Assumptions
Assuming 2-3 people. Adjust if different.

---

### 📅 Day 1 — June 16 (Mon) Evening + Night
**Goal: Data Pipeline + EDA + Project Setup**

- [ ] **Project scaffold**: Init a Python + FastAPI backend, React/Next.js frontend
- [ ] **Data cleaning script**: 
  - Load 298K records from CSV
  - Parse violation_type JSON strings
  - Parse timestamps to proper datetime
  - Handle NULLs in `junction_name`, `police_station`, `validation_status`
  - Deduplicate same vehicle_number at same GPS within 5 minutes
- [ ] **EDA notebook**: 
  - Violation count by type (bar chart)
  - Violations by hour of day (line chart — find peak hours)
  - Violations by police station (ranking)
  - Geographic spread (scatter plot on map)
  - Vehicle type distribution
  - Approval vs rejection rates
- [ ] **Store cleaned data**: Into SQLite/PostgreSQL with PostGIS extension (or just a clean Parquet file for now)

---

### 📅 Day 2 — June 17 (Tue)
**Goal: CIS Engine (Core ML/Logic)**

- [ ] **Road network graph**: 
  - Download Bengaluru road network via `osmnx.graph_from_place("Bengaluru, India", network_type="drive")`
  - Add edge attributes: `road_class`, `estimated_lanes`, `estimated_capacity`
  - Compute betweenness centrality for each edge → this becomes `road_criticality`
- [ ] **Vehicle blockage factor table**:
  ```python
  BLOCKAGE = {
      "SCOOTER": 0.05, "MOPED": 0.05, "MOTOR CYCLE": 0.05,
      "PASSENGER AUTO": 0.15, "GOODS AUTO": 0.15,
      "CAR": 0.25, "MAXI-CAB": 0.30, "VAN": 0.30,
      "LGV": 0.40, "TANKER": 0.50, "BUS": 0.60,
      "OTHERS": 0.20
  }
  ```
- [ ] **Temporal weight model**: 
  - From EDA, derive rush hour multiplier curve (e.g., 8-10 AM = 1.8x, 5-8 PM = 2.0x, 2-4 AM = 0.3x)
- [ ] **Cascade multiplier**: 
  - For each violation's nearest edge in the graph, run BFS outward 3 hops
  - Sum 1/hop_distance for each reachable junction
  - Normalize to 1.0-3.0 range
- [ ] **CIS calculation function**:
  ```python
  def compute_cis(violation):
      bf = BLOCKAGE[violation.vehicle_type]
      rc = edge_centrality[nearest_edge(violation.lat, violation.lng)]
      tw = temporal_weight(violation.hour)
      cm = cascade_multiplier(violation.lat, violation.lng)
      return bf * rc * tw * cm
  ```
- [ ] **DBSCAN clustering**: Cluster violations by (lat, lng) with eps=200m → each cluster = one "hotspot"
- [ ] **Hotspot CIS**: Sum individual CIS within each cluster → sort → enforcement priority ranking

---

### 📅 Day 3 — June 18 (Wed)
**Goal: Prediction Model + API Backend**

- [ ] **Prediction model (Hotspot Forecasting)**:
  - Feature engineering from historical data:
    - `hour_of_day`, `day_of_week`, `is_weekend`
    - `police_station_zone` (one-hot)
    - `h3_cell_index` (spatial binning)
    - `historical_violation_count_same_hour_same_cell` (rolling avg)
    - `num_violations_last_1hr_same_cell`
  - Train LightGBM/XGBoost: predict `violation_count_next_2hr` per H3 cell
  - Evaluate with RMSE + MAE on held-out test data (last 2 weeks)
- [ ] **Repeat offender detection**:
  - Group by `vehicle_number` → count violations → sort
  - Top 100 repeat offenders with their frequent locations
- [ ] **FastAPI backend endpoints**:
  - `GET /api/violations` — filtered by time range, type, police station
  - `GET /api/hotspots` — current hotspot clusters ranked by CIS
  - `GET /api/heatmap` — H3 cell grid with CIS values for map rendering
  - `GET /api/predict` — predicted hotspots for next 2 hours
  - `GET /api/stats` — summary statistics (total violations, avg CIS, peak hour, etc.)
  - `GET /api/offenders` — repeat offender rankings
  - `GET /api/challan/recommend` — dynamic challan calculation for a given violation
- [ ] **Dynamic challan API**:
  ```python
  @app.get("/api/challan/recommend")
  def recommend_challan(violation_id: str):
      violation = get_violation(violation_id)
      cis = compute_cis(violation)
      base_fine = BASE_FINES[violation.violation_type]
      multiplier = 1 + (cis / 100) * MAX_MULTIPLIER
      return {
          "base_fine": base_fine,
          "cis_score": cis,
          "multiplier": round(multiplier, 2),
          "recommended_fine": round(base_fine * multiplier),
          "breakdown": { ... }
      }
  ```

---

### 📅 Day 4 — June 19 (Thu)
**Goal: Frontend Dashboard**

- [ ] **Map component** (Leaflet or Mapbox GL JS):
  - Bengaluru basemap (dark theme)
  - Heatmap layer with CIS color grading (green → red)
  - Click on hotspot → popup with CIS breakdown, violation list, recommended actions
  - Time slider to see historical heatmap evolution
- [ ] **Sidebar — Filters**:
  - Time range picker
  - Vehicle type multi-select
  - Violation type multi-select
  - Police station dropdown
- [ ] **Right panel — Hotspot Ranking**:
  - Top 10 hotspots ranked by CIS
  - Each card shows: location, CIS score (with color badge), violation count, dominant vehicle type
  - Click → zooms map to that hotspot
- [ ] **Bottom panel — Analytics**:
  - CIS trend chart (24hr line graph)
  - Violation type distribution (donut chart)
  - Predicted hotspots for next 2 hours (list with confidence %)
- [ ] **Dynamic challan panel**:
  - Select a violation → shows base fine, CIS, multiplier, recommended fine
  - Visual breakdown showing each CIS component's contribution
- [ ] **Stats bar**: 
  - Total active violations, avg CIS, peak hour, enforcement coverage %
- [ ] **Repeat offender page**: 
  - Table of top offenders with violation count, locations, total estimated congestion caused

---

### 📅 Day 5 — June 20 (Fri)
**Goal: Integration, Testing, Polish, Documentation**

- [ ] **Integration testing**: 
  - End-to-end: data loads → CIS computes → API returns → map renders correctly
  - Edge cases: no violations in a cell, single violation hotspot, midnight data
- [ ] **Performance optimization**:
  - Pre-compute CIS for historical data (batch)
  - Cache hotspot rankings (Redis or in-memory)
  - Ensure map renders smoothly with 298K points (use clustering/aggregation)
- [ ] **Documentation**:
  - README.md with project overview, setup instructions, architecture
  - Screenshots of dashboard for submission
- [ ] **Demo data preparation**:
  - Prepare 3 demo scenarios: morning rush, evening rush, weekend
  - Record a 2-minute screen recording of the dashboard
- [ ] **Final code cleanup + submission prep**

---

### 📅 Day 6 — June 21 (Sat)
**Goal: PPT, Video, Submission (NO CODE)**

- [ ] PPT (10-15 slides): Problem → Solution → Architecture → Demo Screenshots → Impact → Scalability
- [ ] Video recording of live demo
- [ ] Final submission on portal

---

## 5. System Architecture

### High-Level Data Flow

```
  ┌─────────────────────────────────────────────────────────────┐
  │                     ParkSense AI                             │
  │                                                              │
  │  "AI-powered parking violation impact scoring engine         │
  │   that quantifies congestion caused by illegal parking"      │
  └──────────────────────────┬──────────────────────────────────┘
                             │
         ┌───────────────────┼───────────────────┐
         ▼                   ▼                   ▼
  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
  │  DATA IN    │    │  BRAIN      │    │  DATA OUT   │
  │  (Sources)  │    │  (Engine)   │    │  (Users)    │
  └──────┬──────┘    └──────┬──────┘    └──────┬──────┘
         │                  │                  │
         ▼                  ▼                  ▼
  Violation CSV       CIS Scoring        Dashboard Map
  Road Network        Clustering         Hotspot Rankings
  Traffic API         Prediction         Challan Engine
  (optional)          Offender           Analytics
                      Analysis           API Endpoints
```

### Detailed Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND                                  │
│                     (React / Next.js)                            │
│                                                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────────────┐  │
│  │  Map     │  │ Hotspot  │  │Analytics │  │Dynamic Challan │  │
│  │ (Leaflet │  │ Ranking  │  │ Charts   │  │ Calculator     │  │
│  │  + Heat- │  │ Panel    │  │ (Recharts│  │                │  │
│  │  map)    │  │          │  │  /D3)    │  │                │  │
│  └──────────┘  └──────────┘  └──────────┘  └────────────────┘  │
│                                                                  │
└───────────────────────────┬──────────────────────────────────────┘
                            │ REST API calls
                            ▼
┌───────────────────────────────────────────────────────────────────┐
│                      BACKEND (FastAPI)                            │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │                    API LAYER                               │   │
│  │  /violations  /hotspots  /heatmap  /predict  /challan     │   │
│  │  /stats       /offenders /timeseries                      │   │
│  └────────────────────────────┬───────────────────────────────┘   │
│                               │                                   │
│  ┌────────────────────────────▼───────────────────────────────┐   │
│  │                  CORE ENGINE                               │   │
│  │                                                            │   │
│  │  ┌─────────────┐  ┌──────────────┐  ┌─────────────────┐  │   │
│  │  │ CIS Scorer  │  │  DBSCAN      │  │  Prediction     │  │   │
│  │  │             │  │  Clusterer   │  │  Model          │  │   │
│  │  │ Computes:   │  │              │  │                 │  │   │
│  │  │ • blockage  │  │ Groups       │  │ LightGBM that   │  │   │
│  │  │   factor    │  │ nearby       │  │ forecasts       │  │   │
│  │  │ • road      │  │ violations   │  │ violation count │  │   │
│  │  │   critical- │  │ into         │  │ per H3 cell     │  │   │
│  │  │   ity       │  │ "hotspots"   │  │ for next 2 hrs  │  │   │
│  │  │ • temporal  │  │ (eps=200m)   │  │                 │  │   │
│  │  │   weight    │  │              │  │                 │  │   │
│  │  │ • cascade   │  │              │  │                 │  │   │
│  │  │   multi-    │  │              │  │                 │  │   │
│  │  │   plier     │  │              │  │                 │  │   │
│  │  └─────────────┘  └──────────────┘  └─────────────────┘  │   │
│  │                                                            │   │
│  │  ┌─────────────┐  ┌──────────────┐                        │   │
│  │  │ Dynamic     │  │  Repeat      │                        │   │
│  │  │ Challan     │  │  Offender    │                        │   │
│  │  │ Engine      │  │  Detector    │                        │   │
│  │  │             │  │              │                        │   │
│  │  │ base_fine × │  │ Groups by    │                        │   │
│  │  │ (1 + CIS ×  │  │ vehicle_no   │                        │   │
│  │  │  multiplier)│  │ to find      │                        │   │
│  │  │             │  │ habitual     │                        │   │
│  │  │             │  │ violators    │                        │   │
│  │  └─────────────┘  └──────────────┘                        │   │
│  └────────────────────────────────────────────────────────────┘   │
│                               │                                   │
│  ┌────────────────────────────▼───────────────────────────────┐   │
│  │                  DATA LAYER                                │   │
│  │                                                            │   │
│  │  ┌──────────┐  ┌──────────────┐  ┌─────────────────────┐  │   │
│  │  │ Cleaned  │  │ Road Network │  │ Pre-computed        │  │   │
│  │  │ Violation│  │ Graph        │  │ Results             │  │   │
│  │  │ Data     │  │ (OSMnx)      │  │                     │  │   │
│  │  │          │  │              │  │ • CIS per violation  │  │   │
│  │  │ 298K     │  │ Bengaluru    │  │ • Hotspot clusters   │  │   │
│  │  │ records  │  │ road graph   │  │ • Edge centrality    │  │   │
│  │  │ (SQLite/ │  │ with         │  │ • H3 cell aggregates │  │   │
│  │  │ Parquet) │  │ centrality   │  │                     │  │   │
│  │  └──────────┘  └──────────────┘  └─────────────────────┘  │   │
│  └────────────────────────────────────────────────────────────┘   │
└───────────────────────────────────────────────────────────────────┘
```

### CIS Scoring Pipeline (Zoomed In)

```
 Single Violation Record
 (lat, lng, vehicle_type, violation_type, time)
          │
          ▼
 ┌─────────────────────────────────┐
 │ Step 1: Vehicle Blockage Factor │
 │                                 │
 │ SCOOTER → 0.05  (5% of lane)   │
 │ CAR     → 0.25  (25% of lane)  │
 │ TRUCK   → 0.50  (50% of lane)  │
 └────────────┬────────────────────┘
              │
              ▼
 ┌─────────────────────────────────┐
 │ Step 2: Road Criticality       │
 │                                 │
 │ Find nearest road edge to       │
 │ violation GPS point.            │
 │                                 │
 │ Look up pre-computed            │
 │ betweenness centrality          │
 │ (normalized 0-1).               │
 │                                 │
 │ MG Road → 0.92 (critical)      │
 │ Residential lane → 0.08 (low)  │
 └────────────┬────────────────────┘
              │
              ▼
 ┌─────────────────────────────────┐
 │ Step 3: Temporal Weight        │
 │                                 │
 │ Rush hour? → High multiplier    │
 │ Late night? → Low multiplier    │
 │                                 │
 │ 8 AM  → 1.8x                   │
 │ 6 PM  → 2.0x                   │
 │ 3 AM  → 0.3x                   │
 └────────────┬────────────────────┘
              │
              ▼
 ┌─────────────────────────────────┐
 │ Step 4: Cascade Multiplier     │
 │                                 │
 │ From violation's road edge,     │
 │ do 3-hop BFS on road graph.     │
 │                                 │
 │ Count reachable junctions.      │
 │ Weight by inverse distance.     │
 │                                 │
 │ Near junction → 2.5x           │
 │ Middle of road → 1.2x          │
 └────────────┬────────────────────┘
              │
              ▼
 ┌─────────────────────────────────┐
 │ Final CIS = BF × RC × TW × CM │
 │                                 │
 │ Example:                        │
 │ CAR on MG Road at 6 PM near    │
 │ junction:                       │
 │ 0.25 × 0.92 × 2.0 × 2.5       │
 │ = 1.15 (raw)                   │
 │ Normalized to 0-100: → 82      │
 │ Label: "High Impact" 🔴         │
 └─────────────────────────────────┘
```

### Tech Stack Summary

| Layer | Technology | Why |
|-------|-----------|-----|
| **Frontend** | React + Leaflet/MapboxGL + Recharts | Free, fast, great map rendering. Leaflet is simpler; Mapbox is prettier. |
| **Backend** | Python + FastAPI | Fast async API, great for ML integration, easy to demo |
| **ML Models** | scikit-learn (DBSCAN), LightGBM (prediction), NetworkX (graph) | Lightweight, no GPU needed, fast training |
| **Spatial** | OSMnx + H3 (Uber's hex grid) + Shapely | Industry-standard geospatial stack |
| **Data** | Pandas + SQLite (or just Parquet files) | Simple enough for a hackathon, no DB server needed |
| **Charts** | Recharts or Chart.js | Easy React integration |

> [!IMPORTANT]  
> **Keep it simple.** For a hackathon, SQLite + Parquet files >> PostgreSQL. No Docker, no Redis, no Kafka. Just Python scripts and a React app. Deploy on Vercel (frontend) + Railway/Render (backend) if needed for demo.

---

## Open Questions

> [!IMPORTANT]
> 1. **How many team members?** This affects task distribution on the gameplan.
> 2. **Do you want to deploy online for the demo**, or is a localhost demo with screen recording sufficient?
> 3. **Do you have access to Google Maps API key?** The TomTom/Google traffic API would add real traffic speed validation of CIS, but it's optional — the project stands strong without it.
> 4. **Shall I start building the project now** (data cleaning script + backend + frontend), or do you want to review and tweak this plan first?
