"""
/api/violations — filtered violation list
Owner: backend-api branch (Kratik)

Filters supported:
  start_time   ISO datetime string (UTC)  e.g. 2024-01-15T08:00:00
  end_time     ISO datetime string (UTC)
  vehicle_type comma-separated list       e.g. CAR,SCOOTER
  violation_type comma-separated list     e.g. WRONG PARKING,NO PARKING
  police_station string                   exact match
  hour_start   int 0-23 (inclusive)
  hour_end     int 0-23 (inclusive)
  limit        int, default 500, max 5000
  offset       int, default 0 (pagination)
"""

from __future__ import annotations

from typing import Optional

import pandas as pd
from fastapi import APIRouter, HTTPException, Query

from app.data_loader import load_scored_violations

router = APIRouter()

# ---------------------------------------------------------------------------
# Load dataset once at module import — cached in memory for the API lifetime.
# On first call this auto-builds data/processed/violations_scored.parquet.
# ---------------------------------------------------------------------------
_df: pd.DataFrame | None = None


def _get_df() -> pd.DataFrame:
    global _df
    if _df is None:
        _df = load_scored_violations()
    return _df


def _cis_label(score: float) -> str:
    if score >= 81:
        return "Critical"
    if score >= 61:
        return "High"
    if score >= 41:
        return "Moderate"
    if score >= 21:
        return "Low"
    return "Clear"


# ---------------------------------------------------------------------------
# GET /api/violations
# ---------------------------------------------------------------------------
@router.get("/violations", summary="List violations with filters")
def get_violations(
    # Time filters
    start_time: Optional[str] = Query(
        None,
        description="ISO datetime (UTC) — e.g. 2024-01-15T08:00:00",
        example="2024-01-15T08:00:00",
    ),
    end_time: Optional[str] = Query(
        None,
        description="ISO datetime (UTC) — e.g. 2024-01-15T20:00:00",
        example="2024-01-15T20:00:00",
    ),
    hour_start: Optional[int] = Query(
        None, ge=0, le=23,
        description="Filter by hour of day start (0-23 inclusive)",
    ),
    hour_end: Optional[int] = Query(
        None, ge=0, le=23,
        description="Filter by hour of day end (0-23 inclusive)",
    ),
    # Category filters
    vehicle_type: Optional[str] = Query(
        None,
        description="Comma-separated vehicle types — e.g. CAR,SCOOTER",
        example="CAR,SCOOTER",
    ),
    violation_type: Optional[str] = Query(
        None,
        description="Comma-separated violation types — e.g. WRONG PARKING,NO PARKING",
        example="WRONG PARKING",
    ),
    police_station: Optional[str] = Query(
        None,
        description="Police station name (exact match, case-insensitive)",
        example="Bellandur",
    ),
    validation_status: Optional[str] = Query(
        None,
        description="approved | rejected | pending",
        example="approved",
    ),
    # Pagination
    limit: int = Query(500, ge=1, le=5000, description="Max records to return"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
):
    df = _get_df().copy()

    # ---- time range filter -----------------------------------------------
    if start_time:
        try:
            ts = pd.to_datetime(start_time, utc=True)
            df = df[df["timestamp"] >= ts]
        except Exception:
            raise HTTPException(status_code=422, detail=f"Invalid start_time: {start_time!r}")

    if end_time:
        try:
            ts = pd.to_datetime(end_time, utc=True)
            df = df[df["timestamp"] <= ts]
        except Exception:
            raise HTTPException(status_code=422, detail=f"Invalid end_time: {end_time!r}")

    # ---- hour-of-day filter -----------------------------------------------
    if hour_start is not None:
        df = df[df["hour"] >= hour_start]
    if hour_end is not None:
        df = df[df["hour"] <= hour_end]

    # ---- vehicle_type filter ----------------------------------------------
    if vehicle_type:
        types = [v.strip().upper() for v in vehicle_type.split(",")]
        df = df[df["vehicle_type"].str.upper().isin(types)]

    # ---- violation_type filter --------------------------------------------
    if violation_type:
        vtypes = [v.strip().upper() for v in violation_type.split(",")]
        df = df[df["violation_type"].str.upper().isin(vtypes)]

    # ---- police_station filter --------------------------------------------
    if police_station:
        df = df[df["police_station"].str.lower().str.contains(
            police_station.lower(), na=False
        )]

    # ---- validation_status filter -----------------------------------------
    if validation_status:
        df = df[df["validation_status"].str.lower() == validation_status.lower()]

    total = len(df)
    page = df.iloc[offset: offset + limit]

    # Build response records
    records = []
    for _, row in page.iterrows():
        records.append({
            "violation_id":      row["violation_id"],
            "latitude":          row["latitude"],
            "longitude":         row["longitude"],
            "vehicle_type":      row["vehicle_type"],
            "violation_type":    row["violation_type"],
            "timestamp":         str(row["timestamp"]),
            "hour":              int(row["hour"]) if pd.notna(row["hour"]) else None,
            "police_station":    row["police_station"],
            "junction_name":     row["junction_name"],
            "validation_status": row["validation_status"],
            "cis_score":         row.get("cis_score", None),
        })

    return {
        "total":   total,
        "offset":  offset,
        "limit":   limit,
        "count":   len(records),
        "filters": {
            "start_time":        start_time,
            "end_time":          end_time,
            "hour_start":        hour_start,
            "hour_end":          hour_end,
            "vehicle_type":      vehicle_type,
            "violation_type":    violation_type,
            "police_station":    police_station,
            "validation_status": validation_status,
        },
        "data": records,
    }


# ---------------------------------------------------------------------------
# GET /api/violations/{violation_id}
# ---------------------------------------------------------------------------
@router.get("/violations/{violation_id}", summary="Get single violation by ID")
def get_violation_by_id(violation_id: str):
    df = _get_df()
    row = df[df["violation_id"] == violation_id]
    if row.empty:
        raise HTTPException(status_code=404, detail=f"Violation {violation_id!r} not found")
    r = row.iloc[0]
    return {
        "violation_id":      r["violation_id"],
        "latitude":          r["latitude"],
        "longitude":         r["longitude"],
        "vehicle_type":      r["vehicle_type"],
        "violation_type":    r["violation_type"],
        "timestamp":         str(r["timestamp"]),
        "hour":              int(r["hour"]) if pd.notna(r["hour"]) else None,
        "police_station":    r["police_station"],
        "junction_name":     r["junction_name"],
        "validation_status": r["validation_status"],
        "cis_score":         r.get("cis_score", None),
    }
