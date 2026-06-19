"""
Road Graph Builder + Cascade Propagation
Owner: backend-geo-engine branch (Aditi)

1. Downloads Bengaluru road network from OSM (free).
2. Computes betweenness centrality per edge.
3. Implements 3-hop upstream cascade propagation.
4. Implements patrol deterrence decay / return scheduler.

IMPORTANT: osmnx downloads are large (~200MB for Bengaluru).
           Run build_graph() once and cache to data/processed/blr_graph.pkl
"""

import os
import pickle
import networkx as nx

# osmnx is optional at import time — only needed in geo engine branch
try:
    import osmnx as ox
    OSMNX_AVAILABLE = True
except ImportError:
    OSMNX_AVAILABLE = False

GRAPH_CACHE = os.path.join(
    os.path.dirname(__file__), "..", "..", "data", "processed", "blr_graph.pkl"
)


# ---------------------------------------------------------------------------
# OSM road class → default lanes fallback (same table as cis_scorer.py)
# ---------------------------------------------------------------------------
ROAD_CLASS_LANES = {
    "motorway": 6, "trunk": 4, "primary": 3,
    "secondary": 2, "tertiary": 2, "residential": 1, "unclassified": 1,
}


def build_graph(force_rebuild: bool = False, place_name: str = "Bengaluru, India"):
    """
    Download road network from OSM for a given place and compute edge centrality.
    Saves graph to a cache file for reuse.

    Falls back to a tiny mock graph if osmnx is unavailable or download fails.
    """
    if place_name == "Bengaluru, India":
        cache_path = GRAPH_CACHE
    else:
        safe_place_name = "".join([c if c.isalnum() else "_" for c in place_name])
        cache_path = os.path.join(
            os.path.dirname(__file__), "..", "..", "data", "processed", f"{safe_place_name}_graph.pkl"
        )

    if not force_rebuild and os.path.exists(cache_path):
        with open(cache_path, "rb") as f:
            return pickle.load(f)

    if not OSMNX_AVAILABLE:
        print("[WARN] osmnx not installed — returning mock graph for development.")
        return _mock_graph()

    try:
        print(f"[INFO] Downloading {place_name} road network from OSM...")
        G = ox.graph_from_place(place_name, network_type="drive")
        G = ox.add_edge_speeds(G)
        G = ox.add_edge_travel_times(G)

        # Add lane defaults where OSM tag is missing
        for u, v, data in G.edges(data=True):
            rc = data.get("highway", "unclassified")
            if isinstance(rc, list):
                rc = rc[0]
            if "lanes" not in data:
                data["lanes"] = ROAD_CLASS_LANES.get(rc, 2)

        # Edge betweenness centrality (normalised 0-1)
        print(f"[INFO] Computing edge betweenness centrality for {place_name} (using approximation k=5000)...")
        k_val = min(5000, len(G))
        centrality = nx.edge_betweenness_centrality(G, k=k_val, normalized=True, seed=42)
        nx.set_edge_attributes(G, centrality, "betweenness_centrality")

        os.makedirs(os.path.dirname(cache_path), exist_ok=True)
        with open(cache_path, "wb") as f:
            pickle.dump(G, f)

        print(f"[INFO] Graph cached to {cache_path}")
        return G

    except Exception as e:
        print(f"[ERROR] OSM download failed for {place_name}: {e}\nFalling back to mock graph.")
        return _mock_graph()


def _mock_graph():
    """Tiny 10-node mock for dev/testing without OSM download."""
    G = nx.DiGraph()
    for i in range(10):
        G.add_node(i, x=77.5 + i * 0.01, y=12.9 + i * 0.01)
    edges = [(0,1),(1,2),(2,3),(3,4),(4,5),(5,6),(2,7),(7,8),(8,9),(3,9)]
    for u, v in edges:
        G.add_edge(u, v, length=100, highway="secondary",
                   lanes=2, betweenness_centrality=0.1 * (u + 1))
    return G


def cascade_multiplier(G, source_node: int, hops: int = 3) -> float:
    """
    3-hop BFS from source_node on the road graph.
    Returns a multiplier in [1.0, 3.0] representing congestion spread.

    Formula: sum(1 / hop_distance) for all nodes reachable within `hops`.
    Normalised to [1.0, 3.0].
    """
    reachable_score = 0.0
    visited = {source_node}
    frontier = [(source_node, 1)]

    while frontier:
        next_frontier = []
        for node, depth in frontier:
            if depth > hops:
                continue
            for neighbor in G.successors(node):
                if neighbor not in visited:
                    visited.add(neighbor)
                    reachable_score += 1.0 / depth
                    if depth < hops:
                        next_frontier.append((neighbor, depth + 1))
        frontier = next_frontier

    # Normalise to [1.0, 3.0]
    MAX_SCORE = 30.0  # empirical for 3-hop, adjust after testing
    normalised = 1.0 + (min(reachable_score, MAX_SCORE) / MAX_SCORE) * 2.0
    return round(normalised, 3)


# ---------------------------------------------------------------------------
# Patrol deterrence decay — OPTIONAL
# ---------------------------------------------------------------------------
def deterrence_decay(hours_since_patrol: float, half_life_hours: float = 6.0) -> float:
    """
    Exponential decay of deterrence effect after a patrol visit.
    Returns a multiplier: 0.0 (full deterrence) → 1.0 (no deterrence).
    Use this to schedule return patrols: when decay > 0.5, revisit.

    half_life_hours: time after which deterrence is halved. Default 6h.
    [OPTIONAL] — wire this up in the patrol scheduler if time permits.
    """
    import math
    return 1.0 - math.exp(-0.693 * hours_since_patrol / half_life_hours)


def schedule_patrols(hotspots: list[dict], current_time_str: str = None) -> list[dict]:
    """
    Computes priority score for patrol units based on hotspot CIS score and deterrence decay.
    
    Each hotspot dict should have keys:
      - 'hotspot_id'
      - 'cis_score'
      - 'last_patrolled' (ISO timestamp string or None)
      
    Returns a sorted list of hotspots with 'hours_since_patrol', 'deterrence_decay_factor',
    'patrol_priority_score', and 'needs_revisit'.
    """
    import datetime
    
    if current_time_str:
        try:
            current_time = datetime.datetime.fromisoformat(current_time_str.replace("Z", "+00:00"))
        except ValueError:
            current_time = datetime.datetime.utcnow()
    else:
        current_time = datetime.datetime.utcnow()
        
    scheduled = []
    for hs in hotspots:
        last_patrolled_str = hs.get("last_patrolled")
        if last_patrolled_str:
            try:
                last_time = datetime.datetime.fromisoformat(last_patrolled_str.replace("Z", "+00:00"))
                # Make naive/aware datetimes match
                if current_time.tzinfo != last_time.tzinfo:
                    current_time = current_time.replace(tzinfo=last_time.tzinfo)
                hours_since = (current_time - last_time).total_seconds() / 3600.0
            except ValueError:
                hours_since = 24.0  # fallback
        else:
            hours_since = 24.0  # treat as unpatrolled (full decay)
            
        hours_since = max(0.0, hours_since)
        decay = deterrence_decay(hours_since)
        priority_score = round(hs.get("cis_score", 0.0) * decay, 2)
        
        scheduled.append({
            **hs,
            "hours_since_patrol": round(hours_since, 2),
            "deterrence_decay_factor": round(decay, 3),
            "patrol_priority_score": priority_score,
            "needs_revisit": decay > 0.5
        })
        
    return sorted(scheduled, key=lambda x: x["patrol_priority_score"], reverse=True)
