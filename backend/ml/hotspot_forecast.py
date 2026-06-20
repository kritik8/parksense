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
import hashlib

MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "models", "hotspot_lgbm.pkl")


def stable_hash(s: str) -> int:
    """Stable hash function returning an integer between 0 and 9999."""
    return int(hashlib.md5(s.encode()).hexdigest(), 16) % 10000


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Feature engineering from cleaned violation DataFrame.
    Expects columns: timestamp (datetime), h3_cell (string), cis_score (float)
    """
    df = df.copy()
    if "h3_cell" not in df.columns:
        import h3
        df["h3_cell"] = [h3.latlng_to_cell(lat, lng, 8) for lat, lng in zip(df["latitude"], df["longitude"])]

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
    Saves model and necessary lookup data to MODEL_PATH.
    """
    try:
        import lightgbm as lgb
    except ImportError:
        print("[ERROR] lightgbm not installed. Run: pip install lightgbm")
        return None

    if len(df) == 0:
        print("[ERROR] Empty dataframe passed to train_model.")
        return None

    df = df.copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    if "h3_cell" not in df.columns:
        import h3
        df["h3_cell"] = [h3.latlng_to_cell(lat, lng, 8) for lat, lng in zip(df["latitude"], df["longitude"])]

    # Aggregate into 2-hour windows
    df["timestamp_2h"] = df["timestamp"].dt.floor("2h")
    grouped = df.groupby(["h3_cell", "timestamp_2h"]).agg(
        violation_count=("violation_id", "count"),
        avg_cis=("cis_score", "mean")
    ).reset_index()

    # Reindex to fill missing time/cell slots with 0
    all_cells = grouped["h3_cell"].unique()
    if len(all_cells) == 0:
        print("[ERROR] No unique H3 cells found.")
        return None

    min_time = df["timestamp_2h"].min()
    max_time = df["timestamp_2h"].max()
    all_times = pd.date_range(start=min_time, end=max_time, freq="2h")
    
    grid = pd.MultiIndex.from_product([all_cells, all_times], names=["h3_cell", "timestamp_2h"]).to_frame().reset_index(drop=True)
    grid_df = grid.merge(grouped, on=["h3_cell", "timestamp_2h"], how="left")
    grid_df["violation_count"] = grid_df["violation_count"].fillna(0)
    grid_df["avg_cis"] = grid_df["avg_cis"].fillna(0.0)

    # Basic time features
    grid_df["hour"] = grid_df["timestamp_2h"].dt.hour
    grid_df["day_of_week"] = grid_df["timestamp_2h"].dt.dayofweek
    grid_df["is_weekend"] = grid_df["day_of_week"].isin([5, 6]).astype(int)

    # Lag features per cell
    grid_df = grid_df.sort_values(["h3_cell", "timestamp_2h"]).reset_index(drop=True)
    grid_df["count_lag_1"] = grid_df.groupby("h3_cell")["violation_count"].shift(1).fillna(0)
    grid_df["count_lag_2"] = grid_df.groupby("h3_cell")["violation_count"].shift(2).fillna(0)
    grid_df["count_lag_12"] = grid_df.groupby("h3_cell")["violation_count"].shift(12).fillna(0)

    # Historical average CIS per H3 cell and hour of day
    hourly_avg = grid_df.groupby(["h3_cell", "hour"])["avg_cis"].mean().reset_index()
    hourly_avg.rename(columns={"avg_cis": "hist_avg_cis"}, inplace=True)
    grid_df = grid_df.merge(hourly_avg, on=["h3_cell", "hour"], how="left")
    grid_df["hist_avg_cis"] = grid_df["hist_avg_cis"].fillna(0.0)

    # Define target (violation count in NEXT 2 hours)
    grid_df["target"] = grid_df.groupby("h3_cell")["violation_count"].shift(-1)
    grid_df = grid_df.dropna(subset=["target"]).reset_index(drop=True)

    # H3 Cell stable hash feature
    grid_df["h3_cell_hash"] = [stable_hash(c) for c in grid_df["h3_cell"]]

    features = ["h3_cell_hash", "hour", "day_of_week", "is_weekend", "count_lag_1", "count_lag_2", "count_lag_12", "hist_avg_cis"]

    # Determine train/test split
    total_days = (max_time - min_time).days
    split_days = 14 if total_days > 30 else 3
    split_time = max_time - pd.Timedelta(days=split_days)

    train_df = grid_df[grid_df["timestamp_2h"] < split_time]
    test_df = grid_df[grid_df["timestamp_2h"] >= split_time]

    params = {
        "objective": "regression",
        "metric": "rmse",
        "learning_rate": 0.05,
        "num_leaves": 15,
        "verbose": -1,
        "seed": 42
    }

    if len(train_df) == 0 or len(test_df) == 0:
        train_data = lgb.Dataset(grid_df[features], label=grid_df["target"])
        model = lgb.train(params, train_data, num_boost_round=50)
    else:
        train_data = lgb.Dataset(train_df[features], label=train_df["target"])
        test_data = lgb.Dataset(test_df[features], label=test_df["target"], reference=train_data)
        model = lgb.train(
            params,
            train_data,
            num_boost_round=100,
            valid_sets=[test_data],
            callbacks=[lgb.early_stopping(stopping_rounds=10, verbose=False)]
        )

    # Save latest counts and recent histories for inference lookups
    hist_avg_map = hourly_avg.set_index(["h3_cell", "hour"])["hist_avg_cis"].to_dict()
    
    # Store latest 12 slots for each cell to reconstruct lags in predict_next_2h
    recent_history = {}
    for cell, grp in grid_df.groupby("h3_cell"):
        recent_history[cell] = list(grp.tail(12)["violation_count"].values)

    # Create models dir if not exists
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    
    model_data = {
        "model": model,
        "hist_avg_cis": hist_avg_map,
        "recent_history": recent_history
    }

    with open(MODEL_PATH, "wb") as f:
        pickle.dump(model_data, f)
    print(f"[INFO] Model successfully trained and saved to {MODEL_PATH}")
    return model


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

    # Align current_hour to the 2-hour training grid (even hours)
    current_hour = (current_hour // 2) * 2

    with open(MODEL_PATH, "rb") as f:
        model_data = pickle.load(f)

    model = model_data["model"]
    hist_avg_map = model_data["hist_avg_cis"]
    recent_history = model_data["recent_history"]

    rows = []
    for cell in h3_cells:
        cell_hash = stable_hash(cell)
        
        # Format key as tuple for map lookup
        # Note: hist_avg_map key is (h3_cell, hour)
        hist_avg = hist_avg_map.get((cell, current_hour), 0.0)
        
        history = recent_history.get(cell, [])
        # Pad history to ensure we have at least 12 elements
        if len(history) < 12:
            history = [0.0] * (12 - len(history)) + list(history)
            
        lag_1 = history[-1] if history else 0.0
        lag_2 = history[-2] if len(history) >= 2 else 0.0
        lag_12 = history[0] if len(history) >= 12 else 0.0

        rows.append({
            "h3_cell_hash": cell_hash,
            "hour": current_hour,
            "day_of_week": day_of_week,
            "is_weekend": int(day_of_week in [5, 6]),
            "count_lag_1": lag_1,
            "count_lag_2": lag_2,
            "count_lag_12": lag_12,
            "hist_avg_cis": hist_avg
        })

    features = ["h3_cell_hash", "hour", "day_of_week", "is_weekend", "count_lag_1", "count_lag_2", "count_lag_12", "hist_avg_cis"]
    X = pd.DataFrame(rows)[features]
    preds = model.predict(X)
    
    return [
        {"h3_cell": cell, "predicted_count": max(0, int(round(pred))), "confidence": 0.85}
        for cell, pred in zip(h3_cells, preds)
    ]
