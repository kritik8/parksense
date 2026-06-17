"""
Sensor / Device Health Audit
Owner: backend-ml-analysis branch (Eric)

Analyses validation_status patterns to identify low-quality
sensors, users, or devices submitting rejected violations.
"""
import pandas as pd


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
    [OPTIONAL] Spatial POI bias mitigation.
    Checks if violation density near commercial POIs (malls, markets)
    is disproportionate — which could skew hotspot rankings.

    Placeholder: returns a stub report. Wire up real H3 + POI join in
    backend-ml-analysis branch using OSM Overpass API (free).
    """
    return {
        "status": "stub",
        "note": (
            "Compare violation H3 cell density with OSM commercial POI density. "
            "Cells with high POI density should have their CIS normalized by a "
            "poi_density_factor to avoid false hotspot inflation. "
            "Implement using osmnx.geometries_from_place() for POI polygons."
        ),
    }
