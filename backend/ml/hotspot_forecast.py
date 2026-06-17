"""
Hotspot Forecasting — LightGBM
Owner: backend-ml-analysis branch (Eric)

Predicts violation count per H3 cell for the next 2 hours.
Features: hour_of_day, day_of_week, is_weekend, h3_cell, historical_avg
"""
import os
import pickle
import pandas as pd
import numpy as np

MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "models", "hotspot_lgbm.pkl")


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Feature engineering from cleaned violation DataFrame.
    Expects columns: timestamp (datetime), h3_cell (string), cis_score (float)
    """
    df = df.copy()
    df["hour"] = df["timestamp"].dt.hour
    df["day_of_week"] = df["timestamp"].dt.dayofweek
    df["is_weekend"] = df["day_of_week"].isin([5, 6]).astype(int)
    df["date"] = df["timestamp"].dt.date

    # Rolling historical average per (h3_cell, hour)
    hourly = df.groupby(["h3_cell", "hour"])["cis_score"].mean().reset_index()
    hourly.rename(columns={"cis_score": "hist_avg_cis"}, inplace=True)
    df = df.merge(hourly, on=["h3_cell", "hour"], how="left")

    return df


def train_model(df: pd.DataFrame):
    """
    Train LightGBM to predict violation_count_next_2hr per H3 cell.
    Target = violation count in the next 2-hour window for that cell.
    Saves model to MODEL_PATH.

    [STUB] — wire up full training pipeline in backend-ml-analysis branch.
    """
    try:
        import lightgbm as lgb
    except ImportError:
        print("[ERROR] lightgbm not installed. Run: pip install lightgbm")
        return None

    print("[STUB] train_model — implement full training loop in backend-ml-analysis.")
    # TODO (Eric):
    # 1. Aggregate df into (h3_cell, hour_window) → violation_count
    # 2. Lag features: count_last_1h, count_last_3h, count_last_day_same_hour
    # 3. Train/test split (last 2 weeks as test)
    # 4. lgb.train(...) with RMSE objective
    # 5. Save with pickle to MODEL_PATH
    return None


def predict_next_2h(h3_cells: list[str], current_hour: int, day_of_week: int) -> list[dict]:
    """
    Load trained model and return predicted hotspot probabilities per H3 cell.
    Falls back to mock predictions if model not found.
    """
    if not os.path.exists(MODEL_PATH):
        # Mock fallback — returns random scores for dev
        return [
            {"h3_cell": cell, "predicted_count": np.random.randint(0, 20), "confidence": round(np.random.uniform(0.5, 0.95), 2)}
            for cell in h3_cells[:10]
        ]

    with open(MODEL_PATH, "rb") as f:
        model = pickle.load(f)

    # Build input feature rows for each cell
    X = pd.DataFrame([{
        "h3_cell_hash": abs(hash(cell)) % 10000,
        "hour": current_hour,
        "day_of_week": day_of_week,
        "is_weekend": int(day_of_week in [5, 6]),
        "hist_avg_cis": 50.0,  # placeholder — join real values in implementation
    } for cell in h3_cells])

    preds = model.predict(X)
    return [
        {"h3_cell": cell, "predicted_count": max(0, int(round(pred))), "confidence": 0.75}
        for cell, pred in zip(h3_cells, preds)
    ]
