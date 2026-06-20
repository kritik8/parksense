"""
/api/predict — hotspot congestion forecasting (LightGBM)
Owner: backend-api branch (Kratik)
"""

from fastapi import APIRouter, Query
from typing import Optional
import pandas as pd
import datetime
import h3

from app.data_loader import load_scored_violations
from ml.hotspot_forecast import predict_next_2h

router = APIRouter()

_df_scored: pd.DataFrame | None = None

def _get_scored_df() -> pd.DataFrame:
    global _df_scored
    if _df_scored is None:
        _df_scored = load_scored_violations()
    return _df_scored


@router.get("/predict", summary="Predict hotspot violation counts for the next 2 hours")
def predict_hotspots(
    resolution: int = Query(8, ge=7, le=10, description="H3 hexagon resolution for prediction"),
    hour: Optional[int] = Query(None, ge=0, le=23, description="Hour of day (0-23) to predict for"),
    day_of_week: Optional[int] = Query(None, ge=0, le=6, description="Day of week (0=Mon, 6=Sun)"),
    limit: int = Query(50, ge=1, le=200, description="Number of top cells to forecast"),
):
    df = _get_scored_df()
    
    # Clean invalid coords
    df_gps = df.dropna(subset=["latitude", "longitude"])
    
    # 1. Assign H3 cell if not done
    df_gps = df_gps.copy()
    df_gps["h3_cell"] = df_gps.apply(
        lambda r: h3.latlng_to_cell(r["latitude"], r["longitude"], resolution),
        axis=1
    )
    
    # 2. Identify top cells by historical activity to run predictions on
    top_cells = df_gps["h3_cell"].value_counts().head(limit).index.tolist()
    
    # 3. Handle default temporal parameters
    now = datetime.datetime.now()
    pred_hour = hour if hour is not None else now.hour
    pred_dow = day_of_week if day_of_week is not None else now.weekday()
    
    # 4. Run Eric's forecasting algorithm
    predictions = predict_next_2h(
        h3_cells=top_cells,
        current_hour=pred_hour,
        day_of_week=pred_dow
    )
    
    # 5. Enrich predictions with GPS coordinates and labels for frontend mapping
    enriched_predictions = []
    for pred in predictions:
        cell = pred["h3_cell"]
        lat, lng = h3.cell_to_latlng(cell)
        
        # Intensity mapping (capped/normalized helper)
        count = pred["predicted_count"]
        intensity = min(1.0, count / 20.0) # arbitrary normalizer for UI weights
        
        enriched_predictions.append({
            "h3_cell":          cell,
            "latitude":         round(lat, 6),
            "longitude":        round(lng, 6),
            "predicted_count":  count,
            "confidence":       pred["confidence"],
            "intensity":        round(intensity, 4),
            "threat_level":     "CRITICAL" if count >= 15 else ("HIGH" if count >= 10 else ("MODERATE" if count >= 5 else "LOW")),
        })
        
    return {
        "resolution": resolution,
        "prediction_hour": pred_hour,
        "prediction_day_of_week": pred_dow,
        "total_cells_predicted": len(enriched_predictions),
        "predictions": enriched_predictions
    }
