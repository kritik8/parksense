"""
Data loader — reads cleaned Parquet or falls back to raw CSV.
Owner: backend-api branch (Kratik)

Real CSV columns (24 total):
  id, latitude, longitude, location, vehicle_number, vehicle_type,
  description, violation_type (JSON string), offence_code,
  created_datetime, closed_datetime, modified_datetime, device_id,
  created_by_id, center_code, police_station, data_sent_to_scita,
  junction_name, action_taken_timestamp, data_sent_to_scita_timestamp,
  updated_vehicle_number, updated_vehicle_type,
  validation_status, validation_timestamp
"""
import ast
import os
import pandas as pd

BASE_DIR = os.path.join(os.path.dirname(__file__), "..", "..")
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
RAW_PATH     = os.path.join(BASE_DIR, "data", "raw", "violations.csv")
MOCK_PATH    = os.path.join(BASE_DIR, "data", "mock", "violations_mock.csv")


# Columns we actually use — keeps memory lean
USECOLS = [
    "id", "latitude", "longitude",
    "vehicle_number", "vehicle_type",
    "violation_type",          # JSON string → will be parsed
    "created_datetime",        # the main timestamp field
    "police_station",
    "junction_name",
    "validation_status",
    "device_id",
]


def _parse_violation_type(val) -> str:
    """
    violation_type is stored as a JSON array string, e.g.
    '["WRONG PARKING","PARKING NEAR ROAD CROSSING"]'
    Returns the first element as a plain string, or 'UNKNOWN'.
    """
    if pd.isna(val):
        return "UNKNOWN"
    try:
        parsed = ast.literal_eval(str(val))
        if isinstance(parsed, list) and parsed:
            return parsed[0].strip()
    except Exception:
        pass
    return str(val).strip()


def _clean(df: pd.DataFrame) -> pd.DataFrame:
    """Normalise column names and types to a consistent schema."""
    df = df.copy()

    # Rename id → violation_id, created_datetime → timestamp
    df.rename(columns={
        "id": "violation_id",
        "created_datetime": "timestamp",
    }, inplace=True)

    # Parse violation_type JSON → first element string
    df["violation_type"] = df["violation_type"].apply(_parse_violation_type)

    # Parse timestamp
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True, errors="coerce")

    # Fill NULLs
    df["junction_name"]     = df["junction_name"].fillna("No Junction")
    df["police_station"]    = df["police_station"].fillna("Unknown")
    df["validation_status"] = df["validation_status"].fillna("pending")
    df["vehicle_type"]      = df["vehicle_type"].fillna("OTHERS")

    # Derived helpers
    df["hour"]        = df["timestamp"].dt.hour
    df["day_of_week"] = df["timestamp"].dt.dayofweek
    df["is_weekend"]  = df["day_of_week"].isin([5, 6]).astype(int)

    return df


def load_violations(force_raw: bool = False) -> pd.DataFrame:
    """
    Load violation data. Priority order:
    1. data/processed/violations_clean.parquet  (fast — run EDA notebook first)
    2. data/raw/violations.csv                  (full 298K rows, slow first load)
    3. data/mock/violations_mock.csv            (500 rows, always available)

    Args:
        force_raw: if True, skip Parquet cache and load from raw CSV.
    """
    parquet_path = os.path.join(PROCESSED_DIR, "violations_clean.parquet")

    if not force_raw and os.path.exists(parquet_path):
        df = pd.read_parquet(parquet_path)
        print(f"[INFO] Loaded {len(df):,} violations from Parquet cache.")
        return df

    if os.path.exists(RAW_PATH):
        print("[INFO] Loading from raw CSV (first time — this takes ~10s)...")
        df = pd.read_csv(RAW_PATH, usecols=USECOLS, low_memory=False)
        df = _clean(df)
        # Cache to Parquet for next time
        os.makedirs(PROCESSED_DIR, exist_ok=True)
        df.to_parquet(parquet_path, index=False)
        print(f"[INFO] Loaded {len(df):,} violations. Cached to Parquet.")
        return df

    print("[WARN] Raw CSV not found — loading mock data (500 rows).")
    df = pd.read_csv(MOCK_PATH)
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df["hour"]        = df["timestamp"].dt.hour
    df["day_of_week"] = df["timestamp"].dt.dayofweek
    df["is_weekend"]  = df["day_of_week"].isin([5, 6]).astype(int)
    return df
