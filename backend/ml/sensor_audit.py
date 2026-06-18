"""
Sensor / Device Health Audit
Owner: backend-ml-analysis branch (Eric)

Analyses validation_status patterns to identify low-quality
sensors, users, or devices submitting rejected violations.
"""
import pandas as pd
import numpy as np


def audit_sensor_health(df: pd.DataFrame) -> pd.DataFrame:
    """
    Per police_station / device grouping:
      - rejection_rate = rejected / total
      - flag if rejection_rate > threshold

    Returns DataFrame ranked by rejection_rate desc.
    """
    df = df.copy()
    df["is_rejected"] = (df["validation_status"] == "rejected").astype(int)

    audit = df.groupby("police_station").agg(
        total_reports=("validation_status", "count"),
        rejected=("is_rejected", "sum"),
    ).reset_index()

    audit["rejection_rate"] = (audit["rejected"] / audit["total_reports"]).round(3)
    audit["health_flag"] = audit["rejection_rate"].apply(
        lambda r: "CRITICAL" if r > 0.30 else ("WARNING" if r > 0.15 else "OK")
    )

    return audit.sort_values("rejection_rate", ascending=False)


def poi_bias_report(df: pd.DataFrame) -> dict:
    """
    Spatial POI bias mitigation.
    Checks if violation density near commercial POIs (malls, markets)
    is disproportionate — which could skew hotspot rankings.
    
    Attempts to download live POIs using OSMnx; if it fails or is empty,
    falls back to pre-defined prominent commercial centroid coordinates in Bengaluru.
    """
    # Pre-defined central commercial POIs in Bengaluru
    fallback_pois = [
        {"name": "Forum Mall Koramangala", "latitude": 12.9348, "longitude": 77.6114},
        {"name": "UB City MG Road", "latitude": 12.9716, "longitude": 77.5959},
        {"name": "Indiranagar 100ft Rd", "latitude": 12.9719, "longitude": 77.6412},
        {"name": "HSR Layout Sector 3", "latitude": 12.9105, "longitude": 77.6425},
        {"name": "Bellandur Central Mall", "latitude": 12.9268, "longitude": 77.6762}
    ]
    
    pois = []
    
    # Calculate H3 cell index if not present to find top cells
    import h3
    df_temp = df.copy()
    if "h3_cell" not in df_temp.columns:
        df_temp["h3_cell"] = [h3.latlng_to_cell(lat, lng, 8) for lat, lng in zip(df_temp["latitude"], df_temp["longitude"])]

    # Find top cell by violation count to restrict query size
    cell_counts = df_temp["h3_cell"].value_counts()
    
    # Try using OSMnx to get commercial POIs near the top hotspot cell (with mirror rotation fallback)
    overpass_urls = [
        "https://overpass-api.de/api",
        "https://lz4.overpass-api.de/api/",
        "https://z.overpass-api.de/api/",
        "https://overpass.kumi.systems/api"
    ]
    
    for url in overpass_urls:
        try:
            import osmnx as ox
            import socket
            # Set a fast timeout so we don't hang the process
            ox.settings.requests_timeout = 10
            ox.settings.overpass_url = url
            ox.settings.doh_url_template = None
            ox._http._config_dns = lambda u: None
            if hasattr(ox._http, "_original_getaddrinfo"):
                socket.getaddrinfo = ox._http._original_getaddrinfo
            
            if not cell_counts.empty:
                top_cell = cell_counts.index[0]
                cell_lat, cell_lng = h3.cell_to_latlng(top_cell)
                
                # Fetch high-traffic POIs (malls, supermarkets, marketplaces, transit stations, commercial zones)
                tags = {
                    "shop": ["mall", "supermarket"],
                    "amenity": ["marketplace", "bus_station"],
                    "railway": "station",
                    "landuse": "commercial"
                }
                gdf = ox.features_from_point((cell_lat, cell_lng), tags, dist=2000)
                
                if not gdf.empty:
                    gdf = gdf[gdf.geometry.notnull()]
                    centroids = gdf.geometry.centroid
                    for idx, geom in centroids.items():
                        pois.append({"latitude": geom.y, "longitude": geom.x})
                    print(f"[INFO] Successfully loaded {len(pois)} POIs from OSMnx mirror {url}.")
                    break
            else:
                print("[INFO] No cell data found. Skipping OSMnx fetch.")
                break
        except Exception as e:
            print(f"[WARN] Failed to fetch from OSMnx mirror {url}: {e}")

    if not pois:
        pois = fallback_pois
        print(f"[INFO] Using {len(pois)} fallback commercial POIs.")

    # Calculate distance to nearest POI for each violation
    df = df.copy()
    
    import h3
    if "h3_cell" not in df.columns:
        df["h3_cell"] = [h3.latlng_to_cell(lat, lng, 8) for lat, lng in zip(df["latitude"], df["longitude"])]

    # Compute distances to all POIs
    df_lats = df["latitude"].values
    df_lngs = df["longitude"].values
    
    poi_lats = np.array([p["latitude"] for p in pois])
    poi_lngs = np.array([p["longitude"] for p in pois])
    
    near_poi_flags = []
    threshold_meters = 400.0  # Threshold for proximity
    
    for lat, lng in zip(df_lats, df_lngs):
        r = 6371.0 * 1000.0 # meters
        dlat = np.radians(poi_lats - lat)
        dlon = np.radians(poi_lngs - lng)
        a = np.sin(dlat/2)**2 + np.cos(np.radians(lat)) * np.cos(np.radians(poi_lats)) * np.sin(dlon/2)**2
        c = 2 * np.arcsin(np.sqrt(a))
        distances = r * c
        
        near_poi = np.any(distances < threshold_meters)
        near_poi_flags.append(int(near_poi))
        
    df["near_commercial_poi"] = near_poi_flags
    
    # Aggregate by H3 Cell
    cell_agg = df.groupby("h3_cell").agg(
        total_violations=("violation_id", "count"),
        poi_violations=("near_commercial_poi", "sum"),
        avg_cis=("cis_score", "mean")
    ).reset_index()
    
    cell_agg["poi_violation_ratio"] = (cell_agg["poi_violations"] / cell_agg["total_violations"]).round(3)
    
    # Classify POI Bias
    def classify_bias(row):
        if row["poi_violation_ratio"] > 0.5 and row["total_violations"] > 5:
            return "HIGH"
        elif row["poi_violation_ratio"] > 0.25 and row["total_violations"] > 5:
            return "MODERATE"
        else:
            return "LOW"
            
    cell_agg["poi_bias_level"] = cell_agg.apply(classify_bias, axis=1)
    cell_agg["recommended_normalization_factor"] = (1.0 + 0.4 * cell_agg["poi_violation_ratio"]).round(3)
    
    high_bias_cells = cell_agg[cell_agg["poi_bias_level"] == "HIGH"].sort_values("total_violations", ascending=False)
    
    report = {
        "status": "active",
        "total_commercial_pois_used": len(pois),
        "total_cells_analyzed": len(cell_agg),
        "high_bias_cells_count": len(high_bias_cells),
        "high_bias_cells": high_bias_cells[["h3_cell", "total_violations", "poi_violations", "poi_violation_ratio", "recommended_normalization_factor"]].head(10).to_dict(orient="records"),
        "note": "Normalize CIS scores of high bias cells by dividing by the recommended_normalization_factor to prevent false hotspot inflation near shopping malls."
    }
    
    return report

