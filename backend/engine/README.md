# ParkSense AI — Geo-Engine Documentation
**Owner**: `backend-geo-engine` branch (Aditi)

This directory contains the spatial scoring, clustering, and scheduling engine for ParkSense AI.

---

## 1. Congestion Impact Score (CIS) Formula

The CIS quantifies the traffic impact of a single parked violation:

$$\text{CIS} = \min\left(\frac{\text{Raw Score}}{\text{Raw Max}} \times 100, 100.0\right)$$

Where:
$$\text{Raw Score} = \text{BF} \times \text{CRF} \times \text{RC} \times \text{TW} \times \text{CM}$$

### Formula Factors:
1. **Vehicle Blockage Factor (BF)**:
   Fraction of a standard lane blocked by the vehicle type.
   - Scooter/Motorcycle: `0.05`
   - Car: `0.25`
   - Bus: `0.60`
   - (See `BLOCKAGE_FACTOR` in `cis_scorer.py` for full mapping)

2. **Capacity Reduction Factor (CRF)**:
   $$\text{CRF} = \frac{1}{\text{lanes}}$$
   Represents the fraction of road capacity removed by blocking a single lane. Fallbacks exist for road classes when the OSM `lanes` tag is missing.

3. **Road Criticality (RC)**:
   Normalized edge betweenness centrality from the OpenStreetMap (OSM) drive network graph. Highly central transit corridors have RC close to `1.0`, while quiet residential streets have RC close to `0.0`.

4. **Temporal Weight (TW)**:
   Rush hour multipliers derived from historical violation densities:
   - Peak hours (8-10 AM, 5-8 PM): Up to `2.0x`
   - Late night (12-4 AM): `0.3x`

5. **3-Hop Cascade Multiplier (CM)**:
   A BFS-based downstream ripple multiplier in $[1.0, 3.0]$:
   $$\text{CM} = 1.0 + \left(\frac{\min\left(\sum_{h \in \text{Hops}} \frac{1}{\text{depth}_h}, \text{Max Score}\right)}{\text{Max Score}}\right) \times 2.0$$

---

## 2. API & Usage

Other branches (such as `backend-api` by Kratik) can easily import and call the geo-engine functions:

### Single CIS Calculation
```python
from engine.cis_scorer import compute_cis

score = compute_cis(
    vehicle_type="CAR",
    hour=18,
    road_criticality=0.75,
    cascade_multiplier=2.1,
    road_class="primary"
)
# Returns a float in [0.0, 100.0]
```

### Hotspot Clustering & Polygons
Groups violation coordinates using DBSCAN and returns centroids, stats, and convex hull polygon coordinate bounds for Leaflet map overlays:
```python
from engine.hotspot_clustering import cluster_violations

hotspots = cluster_violations(violations_list, eps_meters=200.0, min_samples=3)
# Returns list of dicts with keys:
# 'hotspot_id', 'centroid_lat', 'centroid_lng', 'cis_score', 'violation_count', 'polygon' (coordinates list)
```

### Patrol Deterrence Scheduler
Prioritizes hotspots for enforcement visits, decaying deterrence exponentially over time:
```python
from engine.road_graph import schedule_patrols

scheduled_hotspots = schedule_patrols(hotspots_list, current_time_str="2026-06-19T18:00:00Z")
# Returns sorted list of hotspots with keys:
# 'patrol_priority_score', 'hours_since_patrol', 'needs_revisit', etc.
```

### Batch Processing Script
To run batch violation scoring on a CSV file and output Parquet:
```bash
python -m engine.batch_scorer
```
- Looks for `data/raw/violations.csv` (or falls back to `data/mock/violations_mock.csv`).
- Outputs to `data/processed/violations_clean.parquet`.
