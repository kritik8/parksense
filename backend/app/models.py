"""
Pydantic models shared across API and engine layers.
Owner: backend-api branch (Kratik)
"""
from pydantic import BaseModel
from typing import Optional


class ViolationRecord(BaseModel):
    violation_id: str
    latitude: float
    longitude: float
    vehicle_type: str
    violation_type: str
    timestamp: str
    police_station: Optional[str] = None
    junction_name: Optional[str] = None
    validation_status: Optional[str] = None
    cis_score: Optional[float] = None


class HotspotRecord(BaseModel):
    hotspot_id: str
    latitude: float
    longitude: float
    cis_score: float
    violation_count: int
    dominant_vehicle_type: str
    label: str  # "Critical", "High", "Moderate", "Low", "Clear"


class ChallанRecommendation(BaseModel):
    violation_id: str
    base_fine: float
    cis_score: float
    multiplier: float
    recommended_fine: float
    breakdown: dict
