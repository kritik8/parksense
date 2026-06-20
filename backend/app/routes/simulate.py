"""
/api/parkflow/simulate — What-If enforcement simulation
Owner: backend-api branch (Kratik)
"""

from fastapi import APIRouter, Query, HTTPException
from typing import Optional
import pandas as pd
import numpy as np
import h3

from app.data_loader import load_scored_violations

router = APIRouter()

_df_scored: pd.DataFrame | None = None

def _get_scored_df() -> pd.DataFrame:
    global _df_scored
    if _df_scored is None:
        _df_scored = load_scored_violations()
    return _df_scored


def _haversine_distance(lat1, lon1, lat2, lon2):
    """
    Vectorized haversine distance in meters.
    """
    # Convert degrees to radians
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = np.sin(dlat/2.0)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2.0)**2
    c = 2.0 * np.arcsin(np.sqrt(a))
    
    meters = 6371000.0 * c
    return meters


@router.get("/parkflow/simulate", summary="Simulate impact of parking patrols or barriers at a specific coordinate")
def simulate_intervention(
    latitude: float = Query(..., ge=12.0, le=14.0, description="Center latitude for simulation", example=12.9785),
    longitude: float = Query(..., ge=77.0, le=78.0, description="Center longitude for simulation", example=77.5912),
    radius_meters: float = Query(300.0, ge=50.0, le=2000.0, description="Enforcement radius in meters"),
    intervention_type: str = Query("patrol", description="Type: 'patrol' (deterrence) or 'barricade' (physical block)"),
    efficiency: float = Query(0.6, ge=0.1, le=1.0, description="Intervention success efficiency (0.1 - 1.0)"),
):
    df = _get_scored_df()
    
    if df.empty:
        raise HTTPException(status_code=500, detail="Violation database is empty.")
        
    df_gps = df.dropna(subset=["latitude", "longitude"]).copy()
    
    # 1. Compute distance from center coordinate for each violation
    df_gps["distance_m"] = _haversine_distance(
        df_gps["latitude"], df_gps["longitude"], latitude, longitude
    )
    
    # 2. Filter violations inside the intervention boundary
    affected_mask = df_gps["distance_m"] <= radius_meters
    affected_df = df_gps[affected_mask]
    
    total_affected = len(affected_df)
    if total_affected == 0:
        return {
            "center": {"latitude": latitude, "longitude": longitude},
            "radius_meters": radius_meters,
            "total_violations_affected": 0,
            "original_cumulative_cis": 0.0,
            "simulated_cumulative_cis": 0.0,
            "cis_score_reduction": 0.0,
            "percentage_reduction": 0.0,
            "note": "No active violations found within this zone. Impact is zero."
        }
        
    original_cis_sum = affected_df["cis_score"].sum()
    
    # 3. Simulate impact
    # Patrol deterrence decays CIS by up to 50% times efficiency
    # Barricade blocks up to 80% of vehicles but displaces remaining ones
    if intervention_type.lower() == "barricade":
        deterrence_factor = 1.0 - (efficiency * 0.8)
        displacement_count = int(round(total_affected * (efficiency * 0.7)))
    else:  # patrol
        deterrence_factor = 1.0 - (efficiency * 0.5)
        displacement_count = int(round(total_affected * (efficiency * 0.2)))
        
    # Recalculate simulated CIS values for affected records
    simulated_cis_sum = (affected_df["cis_score"] * deterrence_factor).sum()
    cis_reduction = original_cis_sum - simulated_cis_sum
    pct_reduction = (cis_reduction / original_cis_sum) * 100.0
    
    # 4. Predict displacement impact (which adjacent H3 hex cells receive overflow)
    center_cell = h3.latlng_to_cell(latitude, longitude, 8)
    neighbors = h3.grid_disk(center_cell, 1)
    if isinstance(neighbors, set):
        neighbors.discard(center_cell)
    else:
        neighbors = [c for c in neighbors if c != center_cell]
    
    displacement_cells = []
    if displacement_count > 0 and len(neighbors) > 0:
        per_cell_overflow = max(1, displacement_count // len(neighbors))
        for neighbor in neighbors:
            n_lat, n_lng = h3.cell_to_latlng(neighbor)
            displacement_cells.append({
                "h3_cell": neighbor,
                "latitude": round(n_lat, 6),
                "longitude": round(n_lng, 6),
                "potential_overflow_vehicles": per_cell_overflow,
                "overflow_risk": "HIGH" if per_cell_overflow > 5 else "MODERATE"
            })
            
    return {
        "center": {
            "latitude": round(latitude, 6),
            "longitude": round(longitude, 6)
        },
        "radius_meters": radius_meters,
        "intervention_type": intervention_type,
        "efficiency": efficiency,
        "total_violations_affected": total_affected,
        "original_cumulative_cis": round(float(original_cis_sum), 2),
        "simulated_cumulative_cis": round(float(simulated_cis_sum), 2),
        "cis_score_reduction": round(float(cis_reduction), 2),
        "percentage_reduction": round(float(pct_reduction), 2),
        "displaced_vehicles_count": displacement_count,
        "overflow_displacement_zones": displacement_cells
    }
