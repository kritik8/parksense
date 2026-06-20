"""
CIS Scoring Engine
Owner: backend-geo-engine branch (Aditi)

Computes the Congestion Impact Score for a single violation:
    CIS = BF × RC × TW × CM × CRF

Where:
    BF  = Vehicle Blockage Factor (capacity fraction blocked)
    RC  = Road Criticality (betweenness centrality, 0-1)
    TW  = Temporal Weight (rush-hour multiplier)
    CM  = 3-hop Cascade Multiplier (BPR-style downstream delay)
    CRF = Capacity Reduction Factor (adjusted for road class + lanes)
"""

# ---------------------------------------------------------------------------
# Vehicle blockage factors — fraction of a standard lane occupied
# ---------------------------------------------------------------------------
BLOCKAGE_FACTOR = {
    "SCOOTER": 0.05,
    "MOPED": 0.05,
    "MOTOR CYCLE": 0.05,
    "PASSENGER AUTO": 0.15,
    "GOODS AUTO": 0.15,
    "CAR": 0.25,
    "MAXI-CAB": 0.30,
    "VAN": 0.30,
    "LGV": 0.40,
    "TANKER": 0.50,
    "BUS": 0.60,
    "OTHERS": 0.20,
}

# ---------------------------------------------------------------------------
# Road class → default lane count (OSM fallback when tag is missing)
# Standard traffic-engineering defaults for Indian roads
# ---------------------------------------------------------------------------
ROAD_CLASS_LANES = {
    "motorway": 6,
    "trunk": 4,
    "primary": 3,
    "secondary": 2,
    "tertiary": 2,
    "residential": 1,
    "unclassified": 1,
}

# ---------------------------------------------------------------------------
# Temporal weight curve — derived from EDA of violation timestamps
# Adjust after running EDA notebook on the full dataset
# ---------------------------------------------------------------------------
TEMPORAL_WEIGHT = {
    0: 0.3, 1: 0.3, 2: 0.3, 3: 0.3, 4: 0.4, 5: 0.6,
    6: 1.2, 7: 1.6, 8: 1.8, 9: 1.7, 10: 1.4, 11: 1.3,
    12: 1.2, 13: 1.1, 14: 1.0, 15: 1.1, 16: 1.4, 17: 1.8,
    18: 2.0, 19: 1.9, 20: 1.6, 21: 1.3, 22: 0.8, 23: 0.5,
}


def capacity_reduction_factor(road_class: str, lanes: int = None) -> float:
    """
    CRF = 1 / num_lanes
    Represents the fractional capacity removed by ONE blocked lane.
    Falls back to road-class default if OSM lanes tag is missing.
    """
    try:
        n = int(lanes) if lanes else ROAD_CLASS_LANES.get(road_class, 2)
        if n <= 0:
            n = 2
    except (ValueError, TypeError):
        n = ROAD_CLASS_LANES.get(road_class, 2)
    return 1.0 / n


def bpr_delay(volume_capacity_ratio: float, alpha: float = 0.15, beta: float = 4.0) -> float:
    """
    BPR (Bureau of Public Roads) link performance function.
    Returns travel-time increase factor.
        t = t0 × (1 + alpha × (v/c)^beta)
    We use this to scale the cascade multiplier.
    """
    return 1 + alpha * (volume_capacity_ratio ** beta)


def temporal_weight(hour: int) -> float:
    try:
        h = int(hour)
    except (ValueError, TypeError):
        h = 12
    return TEMPORAL_WEIGHT.get(h % 24, 1.0)


def blockage_factor(vehicle_type: str) -> float:
    if not isinstance(vehicle_type, str):
        vehicle_type = str(vehicle_type) if vehicle_type is not None else "UNKNOWN"
    return BLOCKAGE_FACTOR.get(vehicle_type.upper().strip(), 0.20)


def compute_cis(
    vehicle_type: str,
    hour: int,
    road_criticality: float,   # normalised betweenness centrality 0-1
    cascade_multiplier: float, # output of cascade_propagation()
    road_class: str = "secondary",
    lanes: int = None,
) -> float:
    """
    Returns a CIS value in [0, 100].
    Raw = BF × CRF × RC × TW × CM
    Normalise by theoretical maximum (BUS on motorway, peak hour, central junction).
    """
    bf = blockage_factor(vehicle_type)
    crf = capacity_reduction_factor(road_class, lanes)
    tw = temporal_weight(hour)
    raw = bf * crf * road_criticality * tw * cascade_multiplier

    # Theoretical max (approx): 0.60 × 1.0 × 1.0 × 2.0 × 3.0 = 3.6
    RAW_MAX = 3.6
    return min(round((raw / RAW_MAX) * 100, 2), 100.0)
