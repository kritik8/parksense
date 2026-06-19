import pytest
import os
import networkx as nx
from engine.cis_scorer import (
    blockage_factor,
    capacity_reduction_factor,
    temporal_weight,
    bpr_delay,
    compute_cis
)
from engine.road_graph import (
    _mock_graph,
    cascade_multiplier,
    deterrence_decay,
    build_graph,
    schedule_patrols
)
from engine.hotspot_clustering import cluster_violations


def test_blockage_factor():
    assert blockage_factor("SCOOTER") == 0.05
    assert blockage_factor("car") == 0.25
    assert blockage_factor("BUS") == 0.60
    assert blockage_factor("UNKNOWN_VEHICLE") == 0.20
    # Test type safety fallbacks
    assert blockage_factor(None) == 0.20
    assert blockage_factor(123) == 0.20


def test_capacity_reduction_factor():
    # Test specific lanes
    assert capacity_reduction_factor("motorway", lanes=6) == 1.0 / 6
    assert capacity_reduction_factor("secondary", lanes=2) == 0.5
    # Test fallback lanes
    assert capacity_reduction_factor("motorway") == 1.0 / 6
    assert capacity_reduction_factor("secondary") == 0.5
    assert capacity_reduction_factor("residential") == 1.0
    assert capacity_reduction_factor("unknown_class") == 0.5  # fallback to 2
    # Test invalid string, negative, and null lanes
    assert capacity_reduction_factor("secondary", lanes="invalid") == 0.5
    assert capacity_reduction_factor("secondary", lanes=-5) == 0.5
    assert capacity_reduction_factor("secondary", lanes=0) == 0.5


def test_temporal_weight():
    assert temporal_weight(8) == 1.8
    assert temporal_weight(18) == 2.0
    assert temporal_weight(3) == 0.3
    # Check wrap-around
    assert temporal_weight(24) == temporal_weight(0)
    assert temporal_weight(30) == temporal_weight(6)
    # Test float and string inputs
    assert temporal_weight(8.5) == 1.8
    assert temporal_weight("18") == 2.0
    assert temporal_weight("invalid") == 1.2  # maps to 12 (midday fallback)


def test_bpr_delay():
    # Base BPR: 1 + 0.15 * (v/c)^4
    assert bpr_delay(0.0) == 1.0
    assert bpr_delay(1.0) == 1.15
    assert bpr_delay(2.0) == 1 + 0.15 * 16 == 3.4


def test_compute_cis():
    # Test typical violation
    # vehicle="CAR" (0.25), hour=18 (2.0), RC=0.5, CM=1.5, class="secondary" (2 lanes -> 0.5)
    # raw = 0.25 * 0.5 * 0.5 * 2.0 * 1.5 = 0.1875
    # normalized = (0.1875 / 3.6) * 100 = 5.21
    score = compute_cis(
        vehicle_type="CAR",
        hour=18,
        road_criticality=0.5,
        cascade_multiplier=1.5,
        road_class="secondary"
    )
    assert score == 5.21

    # Test theoretical maximum capping
    score_max = compute_cis(
        vehicle_type="BUS",  # 0.6
        hour=18,  # 2.0
        road_criticality=1.0,
        cascade_multiplier=3.0,
        road_class="residential"  # lanes=1 -> CRF=1.0
    )
    # raw = 0.6 * 1.0 * 1.0 * 2.0 * 3.0 = 3.6
    # normalized = (3.6 / 3.6) * 100 = 100
    assert score_max == 100.0


def test_mock_graph():
    G = _mock_graph()
    assert isinstance(G, nx.DiGraph)
    assert len(G.nodes) == 10
    assert len(G.edges) == 10
    # Check attributes
    for u, v, data in G.edges(data=True):
        assert "betweenness_centrality" in data
        assert "lanes" in data


def test_cascade_multiplier():
    G = _mock_graph()
    # Test cascade multiplier from node 0
    multiplier = cascade_multiplier(G, source_node=0, hops=3)
    # Should be within [1.0, 3.0]
    assert 1.0 <= multiplier <= 3.0


def test_deterrence_decay():
    # Deterrence decay multiplier: 0.0 (full deterrence/visit) to 1.0 (no deterrence)
    assert deterrence_decay(0.0) == 0.0
    # Decays over time
    assert deterrence_decay(6.0) == pytest.approx(0.5, abs=0.05)
    assert deterrence_decay(24.0) > 0.9


def test_build_graph_small_neighborhood(tmp_path):
    # Test download of a small neighborhood to verify OSM download works
    # We will use "Koramangala 1st Block, Bengaluru, India" as a tiny area
    place = "Koramangala 1st Block, Bengaluru, India"
    # Call build_graph with force_rebuild=True
    G = build_graph(force_rebuild=True, place_name=place)
    
    assert isinstance(G, nx.DiGraph)
    assert len(G.nodes) > 0
    # Verify that edge attributes like lanes and betweenness_centrality were added
    for u, v, data in G.edges(data=True):
        assert "betweenness_centrality" in data
        assert "lanes" in data


def test_schedule_patrols():
    hotspots = [
        {"hotspot_id": "HS-0001", "cis_score": 80.0, "last_patrolled": None},
        {"hotspot_id": "HS-0002", "cis_score": 60.0, "last_patrolled": "2026-06-19T11:00:00Z"},
        {"hotspot_id": "HS-0003", "cis_score": 100.0, "last_patrolled": "2026-06-19T16:00:00Z"}
    ]
    
    # Run scheduling at 2026-06-19T17:00:00Z
    scheduled = schedule_patrols(hotspots, "2026-06-19T17:00:00Z")
    
    assert len(scheduled) == 3
    # Check HS-0001 (never patrolled) -> hours_since = 24.0 -> decay ~ 0.9 -> priority high
    # Check HS-0002 (6 hours ago) -> decay ~ 0.5 -> priority ~ 30.0
    # Check HS-0003 (1 hour ago) -> decay ~ 0.1 -> priority ~ 10.0
    
    # Priority order should be HS-0001, then HS-0002, then HS-0003
    assert scheduled[0]["hotspot_id"] == "HS-0001"
    assert scheduled[1]["hotspot_id"] == "HS-0002"
    assert scheduled[2]["hotspot_id"] == "HS-0003"
    
    # Verify extra added fields
    assert "hours_since_patrol" in scheduled[0]
    assert "deterrence_decay_factor" in scheduled[0]
    assert "patrol_priority_score" in scheduled[0]
    assert "needs_revisit" in scheduled[0]


def test_hotspot_clustering_and_polygons():
    # Setup test violations
    # We need at least 3 points in a cluster to get a convex hull polygon
    violations = [
        {"latitude": 12.90, "longitude": 77.60, "cis_score": 20.0, "violation_id": "V1"},
        {"latitude": 12.91, "longitude": 77.60, "cis_score": 30.0, "violation_id": "V2"},
        {"latitude": 12.905, "longitude": 77.61, "cis_score": 40.0, "violation_id": "V3"}
    ]
    
    # Cluster violations with small eps to group them (0.01 radians is ~110km, so 2000m is plenty for these coordinates)
    # Let's use eps_meters = 2000.0, min_samples = 2
    hotspots = cluster_violations(violations, eps_meters=2000.0, min_samples=2)
    
    assert len(hotspots) > 0
    hs = hotspots[0]
    assert hs["violation_count"] == 3
    assert hs["cis_score"] == 90.0
    assert "polygon" in hs
    assert len(hs["polygon"]) >= 3
    # Check that each polygon point is a list of [lat, lng]
    for pt in hs["polygon"]:
        assert len(pt) == 2
        assert isinstance(pt[0], float)
        assert isinstance(pt[1], float)

