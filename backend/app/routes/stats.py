"""
/api/stats — summary statistics for the dashboard stats bar
Owner: backend-api branch (Kratik)

Returns:
  total_violations, approved_count, rejected_count, pending_count,
  top_vehicle_types, top_violation_types, top_police_stations,
  peak_hour, avg_cis (None until CIS scores computed),
  date_range { min, max }
"""

from fastapi import APIRouter
import pandas as pd

from app.data_loader import load_scored_violations

router = APIRouter()

_df: pd.DataFrame | None = None


def _get_df() -> pd.DataFrame:
    global _df
    if _df is None:
        _df = load_scored_violations()
    return _df


@router.get("/stats", summary="Dashboard summary statistics")
def get_stats():
    df = _get_df()

    total = len(df)

    # Validation breakdown
    vc = df["validation_status"].value_counts().to_dict()

    # Top vehicle types (top 6)
    top_vehicles = (
        df["vehicle_type"]
        .value_counts()
        .head(6)
        .reset_index()
        .rename(columns={"vehicle_type": "type", "count": "count"})
        .to_dict(orient="records")
    )

    # Top violation types (top 6)
    top_violations = (
        df["violation_type"]
        .value_counts()
        .head(6)
        .reset_index()
        .rename(columns={"violation_type": "type", "count": "count"})
        .to_dict(orient="records")
    )

    # Top police stations (top 8)
    top_stations = (
        df["police_station"]
        .value_counts()
        .head(8)
        .reset_index()
        .rename(columns={"police_station": "station", "count": "count"})
        .to_dict(orient="records")
    )

    # Peak hour (mode of hour column, drop NaT rows)
    hour_series = df["hour"].dropna()
    peak_hour = int(hour_series.mode().iloc[0]) if not hour_series.empty else None

    # Hourly distribution (for the 24h trend chart)
    hourly_dist = (
        df.groupby("hour")
        .size()
        .reset_index(name="count")
        .sort_values("hour")
        .to_dict(orient="records")
    )

    # Date range
    ts = df["timestamp"].dropna()
    date_range = {
        "min": str(ts.min()) if not ts.empty else None,
        "max": str(ts.max()) if not ts.empty else None,
    }

    # Avg CIS — only if column exists and has values
    avg_cis = None
    if "cis_score" in df.columns:
        cis_vals = df["cis_score"].dropna()
        if not cis_vals.empty:
            avg_cis = round(float(cis_vals.mean()), 2)

    return {
        "total_violations":   total,
        "approved":           int(vc.get("approved", 0)),
        "rejected":           int(vc.get("rejected", 0)),
        "pending":            int(vc.get("pending", 0)),
        "peak_hour":          peak_hour,
        "avg_cis":            avg_cis,
        "date_range":         date_range,
        "top_vehicle_types":  top_vehicles,
        "top_violation_types": top_violations,
        "top_police_stations": top_stations,
        "hourly_distribution": hourly_dist,
    }
