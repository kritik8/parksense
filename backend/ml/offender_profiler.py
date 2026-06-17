"""
Repeat Offender & Fleet Profiling
Owner: backend-ml-analysis branch (Eric)

Groups violations by vehicle_number to identify:
  - Individual repeat offenders (top 100)
  - Fleet operators (vehicles sharing owner prefix patterns)
  - Habitual locations (lat/lng clusters per vehicle)
"""
import pandas as pd


def profile_offenders(df: pd.DataFrame, top_n: int = 100) -> pd.DataFrame:
    """
    Parameters
    ----------
    df : cleaned violations DataFrame with columns:
         vehicle_number, latitude, longitude, cis_score, timestamp

    Returns
    -------
    DataFrame of top_n repeat offenders sorted by total_cis desc.
    """
    grp = df.groupby("vehicle_number").agg(
        violation_count=("vehicle_number", "count"),
        total_cis=("cis_score", "sum"),
        avg_cis=("cis_score", "mean"),
        first_seen=("timestamp", "min"),
        last_seen=("timestamp", "max"),
    ).reset_index()

    grp = grp.sort_values("total_cis", ascending=False).head(top_n)
    grp["offender_rank"] = range(1, len(grp) + 1)
    return grp


def detect_fleets(df: pd.DataFrame) -> pd.DataFrame:
    """
    [OPTIONAL] Naive fleet detection: vehicles sharing the first 6 chars
    of vehicle_number (e.g. KA01AB = same owner prefix).
    Fleet = ≥ 3 distinct vehicle_numbers with same prefix.
    """
    df = df.copy()
    df["fleet_prefix"] = df["vehicle_number"].str[:6]
    prefix_counts = df.groupby("fleet_prefix")["vehicle_number"].nunique()
    fleet_prefixes = prefix_counts[prefix_counts >= 3].index
    fleet_df = df[df["fleet_prefix"].isin(fleet_prefixes)]
    return fleet_df.groupby("fleet_prefix").agg(
        vehicle_count=("vehicle_number", "nunique"),
        total_violations=("vehicle_number", "count"),
        total_cis=("cis_score", "sum"),
    ).reset_index().sort_values("total_cis", ascending=False)
