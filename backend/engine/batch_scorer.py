"""
Batch Scorer & Data Cleaner
Owner: backend-geo-engine branch (Aditi)

Loads raw violations, applies spatial/temporal cleaning, converts timestamps,
computes H3 cells, maps GPS coordinates to the OSM graph, calculates CIS scores,
and exports the final cleaned dataset to Parquet.
"""
import os
import pandas as pd
import numpy as np
import pickle
import osmnx as ox
import networkx as nx
import h3
from engine.cis_scorer import compute_cis
from engine.road_graph import build_graph, cascade_multiplier

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data")
MOCK_CSV = os.path.join(DATA_DIR, "mock", "violations_mock.csv")
RAW_CSV = os.path.join(DATA_DIR, "raw", "violations.csv")
OUTPUT_PARQUET = os.path.join(DATA_DIR, "processed", "violations_clean.parquet")


def clean_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans raw violations exactly as specified by the project guidelines:
    1. Drop null and out-of-bounds coordinates (outside Bengaluru).
    2. Convert created_datetime to Indian Standard Time (IST - Asia/Kolkata).
    3. Clean vehicle types, vehicle numbers, and validation statuses.
    4. Compute Uber H3 spatial indexes (resolution 8).
    """
    print("[INFO] Cleaning raw dataset...")
    
    # 1. Coordinate cleaning (drop nulls and coordinates outside Bengaluru bounding box)
    df = df.dropna(subset=["latitude", "longitude"])
    df = df[(df["latitude"] >= 12.0) & (df["latitude"] <= 14.0)]
    df = df[(df["longitude"] >= 77.0) & (df["longitude"] <= 79.0)]
    
    # 2. Timezone conversion (created_datetime -> timestamp in Asia/Kolkata)
    if "created_datetime" in df.columns:
        df["timestamp"] = pd.to_datetime(df["created_datetime"], format="mixed")
        if df["timestamp"].dt.tz is None:
            df["timestamp"] = df["timestamp"].dt.tz_localize("UTC").dt.tz_convert("Asia/Kolkata")
        else:
            df["timestamp"] = df["timestamp"].dt.tz_convert("Asia/Kolkata")
        df.drop(columns=["created_datetime"], inplace=True, errors="ignore")
    elif "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        
    # 3. Format vehicle type, number, status, and rename ID
    df["vehicle_type"] = df["vehicle_type"].fillna("UNKNOWN").str.upper()
    df["vehicle_number"] = df["vehicle_number"].fillna("UNKNOWN").str.upper().str.replace("-", "", regex=False)
    df["validation_status"] = df["validation_status"].fillna("pending").str.lower()
    
    if "id" in df.columns:
        df.rename(columns={"id": "violation_id"}, inplace=True)
        
    # 4. Generate H3 Spatial index (resolution 8)
    print("[INFO] Generating H3 spatial bins...")
    df["h3_cell"] = [
        h3.latlng_to_cell(lat, lng, 8) 
        for lat, lng in zip(df["latitude"], df["longitude"])
    ]
    
    return df


def run_batch_scoring(violations_df: pd.DataFrame, G: nx.MultiDiGraph) -> pd.DataFrame:
    """
    Computes CIS score for a dataframe of violations.
    Vectorized nearest edge lookup is used for performance.
    """
    print(f"[INFO] Scoring {len(violations_df)} violations...")
    
    # Check if graph has spatial info
    has_spatial = all('x' in G.nodes[n] and 'y' in G.nodes[n] for n in list(G.nodes)[:min(5, len(G))])
    
    criticalities = []
    cascade_mults = []
    road_classes = []
    lanes_list = []
    cis_scores = []
    
    # Vectorized nearest edge lookup if G has spatial info and size
    if has_spatial and len(G) > 10:
        lons = violations_df["longitude"].values
        lats = violations_df["latitude"].values
        
        try:
            print("[INFO] Performing nearest edge lookup on road graph...")
            edges = ox.nearest_edges(G, lons, lats)
        except Exception as e:
            print(f"[WARN] Vectorized nearest edge lookup failed: {e}. Falling back to node-based search.")
            edges = []
            nodes = ox.nearest_nodes(G, lons, lats)
            for n in nodes:
                out_edges = list(G.out_edges(n, keys=True))
                if out_edges:
                    edges.append(out_edges[0])
                else:
                    in_edges = list(G.in_edges(n, keys=True))
                    if in_edges:
                        edges.append((in_edges[0][0], in_edges[0][1], in_edges[0][2]))
                    else:
                        edges.append((n, n, 0))
    else:
        # Simple mock graph lookup by node distance
        edges = []
        for _, row in violations_df.iterrows():
            lat, lon = row["latitude"], row["longitude"]
            min_dist = float('inf')
            nearest_n = None
            for n, data in G.nodes(data=True):
                dist = (data.get("x", 0) - lon)**2 + (data.get("y", 0) - lat)**2
                if dist < min_dist:
                    min_dist = dist
                    nearest_n = n
            out_edges = list(G.out_edges(nearest_n, keys=True))
            if out_edges:
                edges.append(out_edges[0])
            else:
                edges.append((nearest_n, nearest_n, 0))
                
    # Cache cascade multiplier for nodes to speed up computation
    cascade_cache = {}
    
    print("[INFO] Calculating CIS scores...")
    for idx, (u, v, k) in enumerate(edges):
        row = violations_df.iloc[idx]
        
        # Look up edge attributes
        if G.has_edge(u, v, k):
            edge_data = G[u][v][k]
            rc = edge_data.get("betweenness_centrality", 0.05)
            road_class = edge_data.get("highway", "secondary")
            if isinstance(road_class, list):
                road_class = road_class[0]
            lanes = edge_data.get("lanes", None)
            if isinstance(lanes, list):
                lanes = lanes[0]
            try:
                lanes = int(lanes) if lanes is not None else None
            except (ValueError, TypeError):
                lanes = None
        else:
            rc = 0.05
            road_class = "secondary"
            lanes = None
            
        # Calculate cascade multiplier (cached for node u)
        if u not in cascade_cache:
            cascade_cache[u] = cascade_multiplier(G, u, hops=3)
        cm = cascade_cache[u]
        
        # temporal weight (hour of timestamp in local Asia/Kolkata timezone)
        hour = row["timestamp"].hour
        
        # Compute CIS
        cis = compute_cis(
            vehicle_type=row["vehicle_type"],
            hour=hour,
            road_criticality=rc,
            cascade_multiplier=cm,
            road_class=road_class,
            lanes=lanes
        )
        
        criticalities.append(rc)
        cascade_mults.append(cm)
        road_classes.append(road_class)
        lanes_list.append(lanes)
        cis_scores.append(cis)
        
    scored_df = violations_df.copy()
    scored_df["road_criticality"] = criticalities
    scored_df["cascade_multiplier"] = cascade_mults
    scored_df["road_class"] = road_classes
    scored_df["lanes"] = lanes_list
    scored_df["cis_score"] = cis_scores
    
    # Filter columns to only what is required for project schemas
    required_cols = [
        "violation_id", "vehicle_number", "vehicle_type", "violation_type",
        "latitude", "longitude", "timestamp", "police_station", "junction_name",
        "validation_status", "cis_score", "h3_cell"
    ]
    existing_cols = [c for c in required_cols if c in scored_df.columns]
    
    return scored_df[existing_cols]


if __name__ == "__main__":
    if os.path.exists(RAW_CSV):
        input_csv = RAW_CSV
        print(f"[INFO] Found raw dataset at {RAW_CSV}")
    else:
        input_csv = MOCK_CSV
        print(f"[INFO] Raw dataset not found. Falling back to mock dataset at {MOCK_CSV}")
        
    df = pd.read_csv(input_csv)
    
    # Clean the dataset (spatial bounds, types, timestamps, H3)
    df = clean_dataset(df)
    
    # Build or load graph
    G = build_graph()
    
    # Process and score
    scored_df = run_batch_scoring(df, G)
    
    # Save output
    os.makedirs(os.path.dirname(OUTPUT_PARQUET), exist_ok=True)
    scored_df.to_parquet(OUTPUT_PARQUET, index=False)
    print(f"[INFO] Cleaned and scored dataset successfully exported to {OUTPUT_PARQUET}")
