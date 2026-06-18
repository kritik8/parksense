"""
CIS Batch Scorer
Owner: backend-api branch (Kratik)

Applies compute_cis() from engine/cis_scorer.py to an entire DataFrame.

road_criticality strategy (Day 2 fallback — until Aditi's OSM graph is ready):
  - Named junctions ("No Junction" = False) → higher criticality
  - Police station zone proxy: busy stations → higher base
  - Latitude/longitude position used as a simple proxy for area centrality

cascade_multiplier strategy (Day 2 fallback):
  - Uses bpr_delay() from cis_scorer with a v/c ratio estimated from
    local violation density (violations per 0.01° cell).
  - When Aditi's road_graph.py graph is available, swap this with the
    real cascade_propagation() call.

This module is the integration glue between backend-api and backend-geo-engine.
When Aditi merges her branch, only this file needs updating — all route files stay the same.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from engine.cis_scorer import (
    compute_cis,
    blockage_factor,
    temporal_weight,
    bpr_delay,
    BLOCKAGE_FACTOR,
)


# ---------------------------------------------------------------------------
# Busy police station zones → proxy for road criticality
# Derived from the stats: top stations have more violations → busier roads
# ---------------------------------------------------------------------------
STATION_CRITICALITY = {
    "koramangala": 0.85,
    "mg road":     0.90,
    "brigade":     0.88,
    "bellandur":   0.75,
    "hsr":         0.72,
    "whitefield":  0.68,
    "indiranagar": 0.80,
    "jayanagar":   0.70,
    "madiwala":    0.74,
    "hebbal":      0.65,
    "yelahanka":   0.55,
    "electronic city": 0.60,
}

def _road_criticality_proxy(row: pd.Series) -> float:
    """
    Estimate road criticality from available metadata (no OSM graph yet).

    Priority:
    1. Named junction (not 'No Junction') → higher centrality
    2. Police station zone name match
    3. Latitude offset from Bengaluru centre (12.97°N, 77.59°E)
       — central roads are more critical
    """
    # Junction bonus
    junction_bonus = 0.0
    jn = str(row.get("junction_name", "No Junction")).strip().lower()
    if jn not in ("no junction", "nan", "none", ""):
        junction_bonus = 0.20

    # Station-zone proxy
    station = str(row.get("police_station", "")).lower()
    station_rc = 0.50  # default
    for key, val in STATION_CRITICALITY.items():
        if key in station:
            station_rc = val
            break

    # Geographic centrality: Bengaluru CBD is ~12.97°N, 77.59°E
    # Normalise distance from CBD into a 0-1 score (closer = higher)
    lat = row.get("latitude", 12.97)
    lng = row.get("longitude", 77.59)
    dist_deg = ((lat - 12.97) ** 2 + (lng - 77.59) ** 2) ** 0.5
    geo_rc = max(0.0, 1.0 - dist_deg * 5)   # ~0 at 0.2° from centre

    # Weighted blend
    rc = 0.35 * station_rc + 0.40 * geo_rc + 0.25 * junction_bonus
    return round(min(max(rc, 0.05), 1.0), 4)


def _cascade_multiplier_proxy(lat: float, lng: float, density_map: dict) -> float:
    """
    BPR-style cascade multiplier estimated from local violation density.

    density_map: dict mapping (lat_bin, lng_bin) → violation_count
    A 0.01° bin ≈ 1 km². High density → high v/c ratio → high BPR delay.
    Max = 3.0, min = 1.0 (from cis_scorer spec).
    """
    lat_bin = round(lat, 2)
    lng_bin = round(lng, 2)
    count = density_map.get((lat_bin, lng_bin), 1)

    # Scale: 1 violation → v/c = 0.1,  50+ violations → v/c ≈ 1.2
    vc_ratio = min(count / 40.0, 1.5)
    delay = bpr_delay(vc_ratio)  # BPR function from cis_scorer

    # Map BPR delay [1.0, ~1.15+] → cascade multiplier [1.0, 3.0]
    cm = 1.0 + (delay - 1.0) * 15.0
    return round(min(max(cm, 1.0), 3.0), 3)


def score_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply CIS scoring to every row in the violations DataFrame.
    Adds columns: cis_score, road_criticality, cascade_multiplier, cis_label

    Returns a new DataFrame with all original columns + CIS columns.
    Uses vectorised operations where possible; row-wise only where needed.
    """
    df = df.copy()

    # ── 1. Build density map for cascade proxy ──────────────────────────────
    df["_lat_bin"] = df["latitude"].round(2)
    df["_lng_bin"] = df["longitude"].round(2)
    density = df.groupby(["_lat_bin", "_lng_bin"]).size().to_dict()

    # ── 2. Blockage factor (vectorised) ────────────────────────────────────
    df["_bf"] = df["vehicle_type"].apply(
        lambda v: BLOCKAGE_FACTOR.get(str(v).upper().strip(), 0.20)
    )

    # ── 3. Temporal weight (vectorised) ────────────────────────────────────
    hour_series = df["hour"].fillna(12).astype(int)
    tw_map = {h: temporal_weight(h) for h in range(24)}
    df["_tw"] = hour_series.map(tw_map)

    # ── 4. Road criticality proxy (row-wise) ───────────────────────────────
    df["road_criticality"] = df.apply(_road_criticality_proxy, axis=1)

    # ── 5. Cascade multiplier proxy (vectorised via density_map) ───────────
    df["cascade_multiplier"] = df.apply(
        lambda r: _cascade_multiplier_proxy(r["latitude"], r["longitude"], density),
        axis=1,
    )

    # ── 6. CRF: assume secondary road (2 lanes) as default ─────────────────
    # When Aditi's graph is ready, replace with real per-edge CRF
    CRF_DEFAULT = 0.5   # 1/2 lanes = secondary road default

    # ── 7. Compute raw scores ───────────────────────────────────────────────
    raw = df["_bf"] * CRF_DEFAULT * df["road_criticality"] * df["_tw"] * df["cascade_multiplier"]

    # ── 8. Percentile-based normalization to 0-100 ─────────────────────────
    # Using 99th percentile as the ceiling gives a realistic spread:
    #   - Top 1% of violations → CIS near 100  (Critical)
    #   - Median violation     → CIS ~30-50    (Low/Moderate)
    #   - Nighttime scooter    → CIS near 0    (Clear)
    # Recalibrates automatically when Aditi's real graph values arrive.
    p99 = float(raw.quantile(0.99))
    if p99 <= 0:
        p99 = float(raw.max()) or 1.0

    df["cis_score"] = (raw / p99 * 100).clip(0, 100).round(2)

    # ── 9. CIS label ───────────────────────────────────────────────────────
    def _label(s: float) -> str:
        if s >= 81: return "Critical"
        if s >= 61: return "High"
        if s >= 41: return "Moderate"
        if s >= 21: return "Low"
        return "Clear"

    df["cis_label"] = df["cis_score"].apply(_label)

    # Drop scratch columns
    df.drop(columns=["_lat_bin", "_lng_bin", "_bf", "_tw"], inplace=True)

    return df
