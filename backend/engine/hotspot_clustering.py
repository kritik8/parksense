"""
Hotspot clustering — DBSCAN on violation GPS points.
Owner: backend-geo-engine branch (Aditi)
"""
import numpy as np
from sklearn.cluster import DBSCAN
from shapely.geometry import MultiPoint, Point

EARTH_RADIUS_KM = 6371.0


def compute_hotspot_polygon(lats: list[float], lngs: list[float], buffer_degrees: float = 0.001) -> list[list[float]]:
    """
    Computes a boundary polygon (convex hull) for a set of coordinates.
    Falls back to a buffered circle around the centroid if a polygon cannot be formed.
    Returns a list of [latitude, longitude] pairs representing the polygon boundary.
    """
    if not lats or not lngs:
        return []
        
    points = [Point(lng, lat) for lat, lng in zip(lats, lngs)]
    multipoint = MultiPoint(points)
    hull = multipoint.convex_hull
    
    # If the hull is a Polygon, return its coordinates
    if hull.geom_type == 'Polygon':
        # Exterior coords are (x, y) which is (lng, lat)
        return [[round(lat, 6), round(lng, 6)] for lng, lat in hull.exterior.coords]
        
    # If it is a LineString or Point, buffer the centroid instead
    centroid = multipoint.centroid
    buffered = centroid.buffer(buffer_degrees)
    return [[round(lat, 6), round(lng, 6)] for lng, lat in buffered.exterior.coords]


def cluster_violations(violations: list[dict], eps_meters: float = 200.0, min_samples: int = 3) -> list[dict]:
    """
    Groups violations into hotspot clusters using DBSCAN.

    Parameters
    ----------
    violations  : list of dicts, each must have 'latitude', 'longitude', 'cis_score'
    eps_meters  : neighbourhood radius in metres (default 200m)
    min_samples : minimum violations to form a cluster

    Returns
    -------
    List of hotspot dicts: {hotspot_id, centroid_lat, centroid_lng,
                            cis_score, violation_count, violation_ids, polygon}
    """
    if not violations:
        return []

    coords = np.array([[v["latitude"], v["longitude"]] for v in violations])
    coords_rad = np.radians(coords)

    eps_rad = eps_meters / 1000.0 / EARTH_RADIUS_KM

    db = DBSCAN(eps=eps_rad, min_samples=min_samples, algorithm="ball_tree", metric="haversine")
    labels = db.fit_predict(coords_rad)

    hotspots = {}
    for idx, label in enumerate(labels):
        if label == -1:
            continue  # noise point
        if label not in hotspots:
            hotspots[label] = {"violation_ids": [], "lats": [], "lngs": [], "cis_scores": []}
        hotspots[label]["violation_ids"].append(violations[idx].get("violation_id", idx))
        hotspots[label]["lats"].append(violations[idx]["latitude"])
        hotspots[label]["lngs"].append(violations[idx]["longitude"])
        hotspots[label]["cis_scores"].append(violations[idx].get("cis_score", 0))

    result = []
    for label, data in hotspots.items():
        total_cis = sum(data["cis_scores"])
        result.append({
            "hotspot_id": f"HS-{label:04d}",
            "centroid_lat": round(np.mean(data["lats"]), 6),
            "centroid_lng": round(np.mean(data["lngs"]), 6),
            "cis_score": round(total_cis, 2),
            "violation_count": len(data["violation_ids"]),
            "violation_ids": data["violation_ids"],
            "polygon": compute_hotspot_polygon(data["lats"], data["lngs"])
        })

    return sorted(result, key=lambda x: x["cis_score"], reverse=True)
