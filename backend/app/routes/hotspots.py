"""
/api/hotspots — DBSCAN hotspot clusters ranked by CIS
Owner: backend-api branch (Kratik)

Calls:
  - load_scored_violations() from data_loader  (CIS pre-computed)
  - cluster_violations() from engine/hotspot_clustering  (DBSCAN)

Performance strategy:
  DBSCAN on 298K points is too slow for a live endpoint (~5 minutes).
  Solution: pre-cluster at module load time using a spatial grid sample,
  cache the result in memory, serve from cache on every request.

  Per-filter re-clustering uses a 10K-row sample (fast ~1-2s).

Query params:
  limit        int, max hotspots to return (default 20)
  min_cis      float, minimum avg CIS per violation to include
  min_count    int, minimum violations per cluster (default 3)
  eps_meters   float, DBSCAN radius in metres (default 200)
  hour_start   int 0-23, filter violations by hour before clustering
  hour_end     int 0-23
  vehicle_type comma-sep string
"""

from __future__ import annotations

from typing import Optional
import pandas as pd
from fastapi import APIRouter, Query

from app.data_loader import load_scored_violations

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from engine.hotspot_clustering import cluster_violations

router = APIRouter()

_scored_df: pd.DataFrame | None = None
_base_clusters: list | None = None   # pre-computed on all data

MAX_DBSCAN_ROWS = 15_000  # cap for live re-clustering with filters


def _get_scored() -> pd.DataFrame:
    global _scored_df
    if _scored_df is None:
        _scored_df = load_scored_violations()
    return _scored_df


def _ensure_base_clusters(eps_meters: float = 200.0, min_count: int = 3):
    """
    Pre-cluster the full dataset once.  Uses top-CIS rows spatially sampled
    to keep DBSCAN fast (<10s).  Result cached in _base_clusters.
    """
    global _base_clusters
    if _base_clusters is not None:
        return _base_clusters

    df = _get_scored()

    # Strategy: take top 15K rows by CIS score — these are the meaningful
    # violations. DBSCAN on 15K rows takes ~2-3s.
    sample = df.nlargest(MAX_DBSCAN_ROWS, "cis_score")
    records = sample[["violation_id", "latitude", "longitude", "cis_score"]].to_dict(orient="records")

    print(f"[INFO] Pre-clustering {len(records):,} violations (top CIS)...")
    _base_clusters = cluster_violations(records, eps_meters=eps_meters, min_samples=min_count)
    print(f"[INFO] Found {len(_base_clusters)} hotspot clusters.")
    return _base_clusters


def _run_filtered_clustering(df: pd.DataFrame, eps_meters: float, min_count: int) -> list:
    """
    Run DBSCAN on a filtered subset — capped at MAX_DBSCAN_ROWS for speed.
    If subset > cap, take top-CIS rows.
    """
    if len(df) > MAX_DBSCAN_ROWS:
        df = df.nlargest(MAX_DBSCAN_ROWS, "cis_score")
    records = df[["violation_id", "latitude", "longitude", "cis_score"]].to_dict(orient="records")
    return cluster_violations(records, eps_meters=eps_meters, min_samples=min_count)


def _dominant_type(violation_ids: list, df: pd.DataFrame) -> str:
    subset = df[df["violation_id"].isin(violation_ids)]
    if subset.empty:
        return "UNKNOWN"
    return subset["vehicle_type"].value_counts().idxmax()


def _top_violation_types(violation_ids: list, df: pd.DataFrame, n: int = 3) -> list:
    subset = df[df["violation_id"].isin(violation_ids)]
    return subset["violation_type"].value_counts().head(n).index.tolist()


def _cluster_label(avg_cis: float) -> str:
    if avg_cis >= 81: return "Critical"
    if avg_cis >= 61: return "High"
    if avg_cis >= 41: return "Moderate"
    if avg_cis >= 21: return "Low"
    return "Clear"


def _enrich(clusters: list, full_df: pd.DataFrame, min_cis: float, limit: int) -> list:
    enriched = []
    for c in clusters:
        avg_cis = round(c["cis_score"] / max(c["violation_count"], 1), 2)
        if avg_cis < min_cis:
            continue
        dom_vehicle = _dominant_type(c["violation_ids"], full_df)
        top_vtypes  = _top_violation_types(c["violation_ids"], full_df)
        enriched.append({
            "hotspot_id":            c["hotspot_id"],
            "latitude":              c["centroid_lat"],
            "longitude":             c["centroid_lng"],
            "total_cis":             c["cis_score"],
            "avg_cis_per_violation": avg_cis,
            "violation_count":       c["violation_count"],
            "label":                 _cluster_label(avg_cis),
            "dominant_vehicle":      dom_vehicle,
            "top_violation_types":   top_vtypes,
            "violation_ids_sample":  c["violation_ids"][:5],
        })
        if len(enriched) >= limit:
            break
    return enriched


@router.get("/hotspots", summary="DBSCAN hotspot clusters ranked by CIS")
def get_hotspots(
    limit: int = Query(20, ge=1, le=200, description="Max hotspots to return"),
    min_cis: float = Query(0.0, ge=0, le=100, description="Minimum avg CIS per violation"),
    min_count: int = Query(3, ge=2, description="Minimum violations per cluster"),
    eps_meters: float = Query(200.0, ge=50, le=1000, description="DBSCAN radius in metres"),
    hour_start: Optional[int] = Query(None, ge=0, le=23),
    hour_end: Optional[int] = Query(None, ge=0, le=23),
    vehicle_type: Optional[str] = Query(None, description="Comma-sep: CAR,SCOOTER"),
):
    full_df = _get_scored()
    has_filter = any(v is not None for v in [hour_start, hour_end, vehicle_type])

    if has_filter:
        # Filtered re-cluster on subset
        df = full_df.copy()
        if hour_start is not None:
            df = df[df["hour"] >= hour_start]
        if hour_end is not None:
            df = df[df["hour"] <= hour_end]
        if vehicle_type:
            types = [v.strip().upper() for v in vehicle_type.split(",")]
            df = df[df["vehicle_type"].str.upper().isin(types)]
        clusters = _run_filtered_clustering(df, eps_meters, min_count)
    else:
        # Use pre-computed base clusters
        clusters = _ensure_base_clusters(eps_meters, min_count)

    enriched = _enrich(clusters, full_df, min_cis, limit)

    return {
        "total_hotspots": len(enriched),
        "note": f"Clustered from top-{MAX_DBSCAN_ROWS:,} violations by CIS" if not has_filter else "Filtered subset clustered",
        "filters": {
            "eps_meters":   eps_meters,
            "min_count":    min_count,
            "min_cis":      min_cis,
            "hour_start":   hour_start,
            "hour_end":     hour_end,
            "vehicle_type": vehicle_type,
        },
        "hotspots": enriched,
    }
