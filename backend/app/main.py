"""
ParkSense AI — FastAPI Entry Point
Owner: backend-api branch (Kratik)

Route files live in app/routes/.
Engine modules (Aditi / Eric) are imported via backend/engine/ and backend/ml/.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.violations import router as violations_router
from app.routes.stats      import router as stats_router
from app.routes.hotspots   import router as hotspots_router
from app.routes.heatmap    import router as heatmap_router

app = FastAPI(
    title="ParkSense AI",
    description="Bengaluru parking violation impact scoring API",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # tighten before production
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Implemented routers ───────────────────────────────────────────────
app.include_router(violations_router, prefix="/api", tags=["Violations"])
app.include_router(stats_router,      prefix="/api", tags=["Stats"])
app.include_router(hotspots_router,   prefix="/api", tags=["Hotspots"])
app.include_router(heatmap_router,    prefix="/api", tags=["Heatmap"])

# ── Stub routers (Day 2-3 work) ────────────────────────────────────────────
from fastapi import APIRouter

_stubs = APIRouter()

@_stubs.get("/offenders",         summary="[STUB] Repeat offender rankings")
def get_offenders():
    return {"message": "stub — implement Day 3 (backend-ml-analysis)"}

@_stubs.get("/predict",           summary="[STUB] LightGBM hotspot forecast")
def predict_hotspots():
    return {"message": "stub — implement Day 3 (backend-ml-analysis)"}

@_stubs.get("/challan/recommend", summary="[STUB] Dynamic challan recommendation")
def recommend_challan(violation_id: str):
    return {"message": "stub — implement Day 3 (backend-api)"}

@_stubs.get("/parkflow/simulate", summary="[STUB] ParkFlow what-if simulation")
def parkflow_simulate():
    return {"message": "stub — implement Day 4 (optional)"}

app.include_router(_stubs, prefix="/api", tags=["Stubs (coming soon)"])


# ── Health check ───────────────────────────────────────────────────────────
@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "service": "ParkSense AI API", "docs": "/docs"}
