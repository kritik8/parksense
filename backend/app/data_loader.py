"""
Data loader — reads cleaned Parquet or falls back to mock CSV.
Shared by all backend branches.
"""
import os
import pandas as pd

PROCESSED_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", "processed")
MOCK_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "mock", "violations_mock.csv")


def load_violations() -> pd.DataFrame:
    """
    Load violation data. Priority order:
    1. data/processed/violations_clean.parquet  (fast, produced by EDA notebook)
    2. data/mock/violations_mock.csv            (500 rows, always available)
    """
    parquet_path = os.path.join(PROCESSED_DIR, "violations_clean.parquet")
    if os.path.exists(parquet_path):
        df = pd.read_parquet(parquet_path)
        print(f"[INFO] Loaded {len(df):,} violations from Parquet.")
        return df

    print("[WARN] Parquet not found — loading mock data (500 rows).")
    df = pd.read_csv(MOCK_PATH)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df
