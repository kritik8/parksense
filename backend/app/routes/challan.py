"""
/api/challan — dynamic fine recommendations based on CIS
Owner: backend-api branch (Kratik)
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
import pandas as pd

from app.data_loader import load_scored_violations

router = APIRouter()

# Bengaluru standard traffic fine lookup based on violation type
VIOLATION_BASE_FINES = {
    "WRONG PARKING": 500.0,
    "PARKING NEAR ROAD CROSSING": 1000.0,
    "NO PARKING": 500.0,
    "PARKING IN BUS LANES": 1500.0,
    "FOOTPATH PARKING": 1000.0,
    "DOUBLE PARKING": 1000.0,
    "OBSTRUCTING TRAFFIC": 1000.0,
    "PARKING NEAR FIRE HYDRANT": 1000.0,
    "PARKING ON BRIDGE": 1000.0,
    "UNKNOWN": 500.0,
}

_df_scored: pd.DataFrame | None = None

def _get_scored_df() -> pd.DataFrame:
    global _df_scored
    if _df_scored is None:
        _df_scored = load_scored_violations()
    return _df_scored


@router.get("/challan/recommend", summary="Calculate dynamic fine recommendation")
def recommend_challan(
    violation_id: str = Query(..., description="ID of the violation record"),
    override_base_fine: Optional[float] = Query(None, ge=100.0, description="Override standard base fine"),
):
    df = _get_scored_df()
    row = df[df["violation_id"] == violation_id]
    
    if row.empty:
        raise HTTPException(
            status_code=404, 
            detail=f"Violation with ID {violation_id!r} not found."
        )
        
    r = row.iloc[0]
    
    # Resolve base fine
    vtype = str(r["violation_type"]).upper().strip()
    base_fine = VIOLATION_BASE_FINES.get(vtype, 500.0)
    if override_base_fine is not None:
        base_fine = override_base_fine
        
    # CIS and multiplier calculation
    cis = float(r.get("cis_score", 0.0))
    # Formula: base_fine * (1 + CIS/100 * 4) -> multiplier range [1.0, 5.0]
    multiplier = round(1.0 + (cis / 100.0 * 4.0), 3)
    recommended_fine = round(base_fine * multiplier, 2)
    
    # Build breakdown details
    breakdown = {
        "base_fine": base_fine,
        "cis_score": cis,
        "multiplier": multiplier,
        "formula": "base_fine * (1 + (cis_score / 100) * 4)",
        "traffic_impact_factor": f"{multiplier}x multiplier applied due to traffic interference score of {cis}/100",
        "details": {
            "road_criticality": float(r.get("road_criticality", 0.5)),
            "cascade_multiplier": float(r.get("cascade_multiplier", 1.0)),
            "police_station": r.get("police_station", "Unknown"),
            "junction_name": r.get("junction_name", "No Junction"),
        }
    }
    
    return {
        "violation_id": r["violation_id"],
        "vehicle_number": r["vehicle_number"],
        "vehicle_type": r["vehicle_type"],
        "violation_type": r["violation_type"],
        "timestamp": str(r["timestamp"]),
        "base_fine": base_fine,
        "cis_score": cis,
        "multiplier": multiplier,
        "recommended_fine": recommended_fine,
        "breakdown": breakdown,
    }
