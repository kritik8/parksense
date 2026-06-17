"""
ParkSense AI — FastAPI Entry Point
Owner: backend-api branch (Kratik)

All route modules are imported here. Engine modules live in
backend-geo-engine and backend-ml-analysis branches, but are
called via shared Python imports from backend/engine/.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="ParkSense AI",
    description="Bengaluru parking violation impact scoring API",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten before production
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"status": "ok", "service": "ParkSense AI API"}


# Route stubs — flesh these out in backend-api branch
@app.get("/api/violations")
def get_violations():
    """Filtered violation list — time, type, police station."""
    return {"message": "stub — implement in backend-api branch"}


@app.get("/api/hotspots")
def get_hotspots():
    """Ranked hotspot clusters with CIS scores."""
    return {"message": "stub — implement in backend-api branch"}


@app.get("/api/heatmap")
def get_heatmap():
    """H3 cell grid with aggregated CIS for map rendering."""
    return {"message": "stub — implement in backend-api branch"}


@app.get("/api/stats")
def get_stats():
    """Summary: total violations, avg CIS, peak hour, enforcement %."""
    return {"message": "stub — implement in backend-api branch"}


@app.get("/api/offenders")
def get_offenders():
    """Repeat offender rankings — implemented in backend-ml-analysis."""
    return {"message": "stub — implement in backend-api branch"}


@app.get("/api/challan/recommend")
def recommend_challan(violation_id: str):
    """Dynamic challan recommendation (policy tool, not automatic fine)."""
    return {"message": "stub — implement in backend-api branch"}


@app.get("/api/predict")
def predict_hotspots():
    """LightGBM forecast of hotspots for next 2 hours."""
    return {"message": "stub — implement in backend-api branch"}


@app.get("/api/parkflow/simulate")
def parkflow_simulate():
    """ParkFlow what-if simulation — what happens if violations drop X%."""
    return {"message": "stub — implement in backend-api branch"}
