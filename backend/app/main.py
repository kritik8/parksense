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
from app.routes.offenders  import router as offenders_router
from app.routes.predict    import router as predict_router
from app.routes.challan    import router as challan_router
from app.routes.simulate   import router as simulate_router

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
app.include_router(offenders_router,  prefix="/api", tags=["Offenders"])
app.include_router(predict_router,    prefix="/api", tags=["Forecast"])
app.include_router(challan_router,    prefix="/api", tags=["Challan"])
app.include_router(simulate_router,   prefix="/api", tags=["Simulation"])


# ── Health check ───────────────────────────────────────────────────────────
@app.get("/", tags=["Health"])
def root():
    return {"status": "running"}
