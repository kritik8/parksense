"""
/api/heatmap — H3 hex grid with aggregated CIS per cell
Owner: backend-api branch (Kratik)

Returns H3 hex cells covering Bengaluru with:
  - cell_id (H3 string)
  - centroid lat/lng
  - total_cis, avg_cis, violation_count
  - cis_label (Clear / Low / Moderate / High / Critical)

Used by Mayank's Leaflet.heat / deck.gl HeatmapLayer to render
the colour-graded congestion map (green → red).

Query params:
  resolution  int 7-9, H3 resolution (7 ≈ 5km², 8 ≈ 0.7km², 9 ≈ 0.1km²)
              Default 8 — good balance for Bengaluru city view
  hour_start  int 0-23
  hour_end    int 0-23
  min_count   int, minimum violations per cell to include (default 1)
  top_n       int, return only top_n cells by CIS (default all)
"""

from __future__ import annotations

from typing import Optional
import pandas as pd
from fastapi import APIRouter, Query

import h3

from app.data_loader import load_scored_violations

router = APIRouter()

_scored_df: pd.DataFrame | None = None


def _get_scored() -> pd.DataFrame:
    global _scored_df
    if _scored_df is None:
        _scored_df = load_scored_violations()
    return _scored_df


def _cis_label(avg_cis: float) -> str:
    if avg_cis >= 81: return "Critical"
    if avg_cis >= 61: return "High"
    if avg_cis >= 41: return "Moderate"
    if avg_cis >= 21: return "Low"
    return "Clear"


@router.get("/heatmap", summary="H3 hex grid with aggregated CIS per cell")
def get_heatmap(
    resolution: int = Query(
        8, ge=7, le=10,
        description="H3 resolution: 7≈5km², 8≈0.7km², 9≈0.1km². Default 8."
    ),
    hour_start: Optional[int] = Query(None, ge=0, le=23, description="Filter by hour of day"),
    hour_end:   Optional[int] = Query(None, ge=0, le=23),
    vehicle_type: Optional[str] = Query(None, description="Comma-sep vehicle types"),
    min_count:  int = Query(1, ge=1, description="Min violations per cell"),
    top_n:      Optional[int] = Query(None, ge=1, description="Return only top N cells by CIS"),
):
    df = _get_scored().copy()

    # Optional filters
    if hour_start is not None:
        df = df[df["hour"] >= hour_start]
    if hour_end is not None:
        df = df[df["hour"] <= hour_end]
    if vehicle_type:
        types = [v.strip().upper() for v in vehicle_type.split(",")]
        df = df[df["vehicle_type"].str.upper().isin(types)]

    # Drop rows with invalid GPS
    df = df.dropna(subset=["latitude", "longitude"])

    # Assign H3 cell to each violation (h3 4.x API)
    df["h3_cell"] = df.apply(
        lambda r: h3.latlng_to_cell(r["latitude"], r["longitude"], resolution),
        axis=1,
    )

    # Aggregate per cell
    agg = df.groupby("h3_cell").agg(
        violation_count=("violation_id", "count"),
        total_cis=("cis_score", "sum"),
        avg_cis=("cis_score", "mean"),
    ).reset_index()

    # Filter by min_count
    agg = agg[agg["violation_count"] >= min_count]

    # Sort by total_cis descending
    agg = agg.sort_values("total_cis", ascending=False)

    if top_n:
        agg = agg.head(top_n)

    # Build response — include cell centroid for map rendering
    cells = []
    for _, row in agg.iterrows():
        cell = row["h3_cell"]
        # h3 4.x: cell_to_latlng returns (lat, lng)
        lat, lng = h3.cell_to_latlng(cell)
        avg = round(float(row["avg_cis"]), 2)
        boundary = [[round(pt[0], 6), round(pt[1], 6)] for pt in h3.cell_to_boundary(cell)]
        cells.append({
            "cell_id":         cell,
            "latitude":        round(lat, 6),
            "longitude":       round(lng, 6),
            "boundary":        boundary,
            "violation_count": int(row["violation_count"]),
            "total_cis":       round(float(row["total_cis"]), 2),
            "avg_cis":         avg,
            "intensity":       round(avg / 100.0, 4),  # 0-1 for Leaflet.heat weight
            "cis_label":       _cis_label(avg),
        })

    return {
        "resolution":   resolution,
        "total_cells":  len(cells),
        "filters": {
            "hour_start":   hour_start,
            "hour_end":     hour_end,
            "vehicle_type": vehicle_type,
            "min_count":    min_count,
        },
        "cells": cells,
    }
