# ParkSense AI — ML Integration Guide (For Kratik / `backend-api`)

This guide explains how to wire the ML analysis backend components from the `backend-ml-analysis` branch into your FastAPI routes in `backend/app/main.py`.

All modules are exposed directly from `backend/ml/__init__.py`.

---

## 1. Import ML Functions

In `backend/app/main.py`, import the ML package:

```python
from ml import (
    predict_next_2h,
    profile_offenders,
    detect_fleets,
    audit_sensor_health,
    poi_bias_report,
    get_demo_scenario
)
from app.data_loader import load_violations
```

---

## 2. Implement API Endpoints

### `/api/predict`

This endpoint returns hotspot predictions for the next 2 hours.
Support a `scenario` parameter (e.g. `?scenario=morning_rush` or `?scenario=evening_rush`) to facilitate frontend demo presentations without requiring full live data.

```python
from fastapi import Query

@app.get("/api/predict")
def predict_hotspots(scenario: str = Query(None, description="morning_rush, evening_rush, or weekend")):
    if scenario:
        # Returns canned scenario predictions for demo presentation
        return get_demo_scenario(scenario)
        
    # Standard inference logic on real H3 cells
    df = load_violations()
    if df.empty:
        return {"status": "error", "message": "No data loaded"}
        
    # Get distinct cells to predict
    if "h3_cell" not in df.columns:
        import h3
        df["h3_cell"] = [h3.latlng_to_cell(lat, lng, 8) for lat, lng in zip(df["latitude"], df["longitude"])]
        
    top_cells = list(df["h3_cell"].unique())[:50]  # predict for top 50 active cells
    
    import datetime
    now = datetime.datetime.now()
    
    predictions = predict_next_2h(
        h3_cells=top_cells,
        current_hour=now.hour,
        day_of_week=now.weekday()
    )
    
    return {
        "status": "success",
        "timestamp": now.isoformat(),
        "predictions": predictions
    }
```

### `/api/offenders`

This endpoint returns repeat offenders ranking and detected fleets.

```python
@app.get("/api/offenders")
def get_offenders(limit: int = 100):
    df = load_violations()
    if df.empty:
        return {"status": "error", "message": "No data loaded"}
        
    # Get repeat offenders list
    offenders_df = profile_offenders(df, top_n=limit)
    offenders_list = offenders_df.to_dict(orient="records")
    
    # Get fleet operators list
    fleets_df = detect_fleets(df)
    fleets_list = fleets_df.to_dict(orient="records")
    
    return {
        "status": "success",
        "repeat_offenders": offenders_list,
        "fleets": fleets_list
    }
```

### `/api/sensor-audit` (New Endpoint / Stats wiring)

This endpoint returns quality audits of reporting devices/stations and POI spatial bias recommendations.

```python
@app.get("/api/sensor-audit")
def get_sensor_audit():
    df = load_violations()
    if df.empty:
        return {"status": "error", "message": "No data loaded"}
        
    # Sensor quality audit table
    audit_df = audit_sensor_health(df)
    audit_list = audit_df.to_dict(orient="records")
    
    # POI spatial bias analysis
    poi_report = poi_bias_report(df)
    
    return {
        "status": "success",
        "device_health": audit_list,
        "poi_bias": poi_report
    }
```

---

## 3. Local Verification

To test that everything imports and works in your local environment, run:

```bash
python ml/run_ml_tests.py
```
