"""
/api/offenders — offender analysis, fleet profiling, and sensor health audits
Owner: backend-api branch (Kratik)
"""

from fastapi import APIRouter, Query
import pandas as pd
from typing import Optional

from app.data_loader import load_scored_violations

# Import Eric's ML models
from ml.offender_profiler import profile_offenders, detect_fleets
from ml.sensor_audit import audit_sensor_health

router = APIRouter()

_df_scored: pd.DataFrame | None = None

def _get_scored_df() -> pd.DataFrame:
    global _df_scored
    if _df_scored is None:
        _df_scored = load_scored_violations()
    return _df_scored


@router.get("/offenders", summary="Rank repeat offenders by cumulative CIS impact")
def get_offenders(
    limit: int = Query(100, ge=1, le=500, description="Number of offenders to return"),
):
    df = _get_scored_df()
    
    # Run Eric's repeat offender profiler
    offenders_df = profile_offenders(df, top_n=limit)
    
    # Convert dataframe to JSON serializable objects
    records = []
    for _, row in offenders_df.iterrows():
        records.append({
            "offender_rank":    int(row["offender_rank"]),
            "vehicle_number":   row["vehicle_number"],
            "violation_count":  int(row["violation_count"]),
            "total_cis":        round(float(row["total_cis"]), 2),
            "avg_cis":          round(float(row["avg_cis"]), 2),
            "first_seen":       str(row["first_seen"]),
            "last_seen":        str(row["last_seen"]),
        })
        
    return {
        "total_offenders_tracked": len(df["vehicle_number"].unique()),
        "limit": limit,
        "offenders": records
    }


@router.get("/fleets", summary="Profile fleet prefixes with high violation frequencies")
def get_fleets():
    df = _get_scored_df()
    
    # Run Eric's fleet detector
    fleets_df = detect_fleets(df)
    
    records = []
    for _, row in fleets_df.iterrows():
        records.append({
            "fleet_prefix":     row["fleet_prefix"],
            "vehicle_count":    int(row["vehicle_count"]),
            "total_violations": int(row["total_violations"]),
            "total_cis":        round(float(row["total_cis"]), 2),
        })
        
    return {
        "total_fleets_detected": len(records),
        "fleets": records
    }


@router.get("/sensors/audit", summary="Audit validation reliability per police station")
def get_sensor_audit():
    df = _get_scored_df()
    
    # Run Eric's sensor audit function
    audit_df = audit_sensor_health(df)
    
    records = []
    for _, row in audit_df.iterrows():
        records.append({
            "police_station":  row["police_station"],
            "total_reports":   int(row["total_reports"]),
            "rejected_count":  int(row["rejected"]),
            "rejection_rate":  round(float(row["rejection_rate"]), 3),
            "health_flag":     row["health_flag"],  # CRITICAL, WARNING, OK
        })
        
    return {
        "total_stations_audited": len(records),
        "audit": records
    }
