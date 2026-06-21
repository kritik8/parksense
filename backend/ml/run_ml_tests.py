"""
Verification Script for backend-ml-analysis tasks.
Loads mock data and tests forecasting, profiling, and sensor audit pipelines.
"""
import os
import sys
import pandas as pd

# Add the parent directory of backend to path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

from app.data_loader import load_violations
from ml.hotspot_forecast import build_features, train_model, predict_next_2h, MODEL_PATH
from ml.offender_profiler import profile_offenders, detect_fleets
from ml.sensor_audit import audit_sensor_health, poi_bias_report


def run_tests():
    print("=" * 60)
    print("Starting ML Pipeline Verification...")
    print("=" * 60)

    # 1. Load Data
    print("\n[STEP 1] Loading violations data...")
    df = load_violations()
    print(f"Loaded {len(df)} rows. Columns: {list(df.columns)}")

    # 2. Build Features
    print("\n[STEP 2] Testing build_features...")
    feat_df = build_features(df)
    print(f"Features built. Columns: {list(feat_df.columns)}")
    print(feat_df[["timestamp", "h3_cell", "hour", "hist_avg_cis"]].head(2))

    # 3. Train Model
    print("\n[STEP 3] Testing train_model...")
    if os.path.exists(MODEL_PATH):
        os.remove(MODEL_PATH)
        print(f"Removed old model file at {MODEL_PATH}")
    
    model = train_model(df)
    if model and os.path.exists(MODEL_PATH):
        print(f"[SUCCESS] Model trained and saved successfully at: {MODEL_PATH}")
    else:
        print("[FAIL] Model training failed or file not written.")
        sys.exit(1)

    # 4. Predict
    print("\n[STEP 4] Testing predict_next_2h...")
    test_cells = list(feat_df["h3_cell"].value_counts().head(5).index)
    print(f"Testing predictions for top 5 active cells: {test_cells}")
    preds = predict_next_2h(test_cells, current_hour=9, day_of_week=0)
    print("Predictions output:")
    for p in preds:
        print(f"  Cell: {p['h3_cell']} -> Predicted Count: {p['predicted_count']}, Confidence: {p['confidence']}")

    # 5. Offender Profiler
    print("\n[STEP 5] Testing Offender Profiling...")
    offenders = profile_offenders(df, top_n=5)
    print("Top 5 Repeat Offenders:")
    print(offenders[["offender_rank", "vehicle_number", "violation_count", "total_cis"]])

    print("\nTesting Fleet Detection...")
    fleets = detect_fleets(df)
    print(f"Detected {len(fleets)} fleets. Top 3 fleets:")
    print(fleets.head(3))

    # 6. Sensor Audit
    print("\n[STEP 6] Testing Sensor Health Audit...")
    audit = audit_sensor_health(df)
    print("Sensor Audit Health Table:")
    print(audit.head(5))

    print("\nTesting POI Bias Report...")
    poi_report = poi_bias_report(df)
    print(f"POI Bias Report status: {poi_report['status']}")
    print(f"Total POIs used: {poi_report['total_commercial_pois_used']}")
    print(f"High bias cells count: {poi_report['high_bias_cells_count']}")
    if poi_report["high_bias_cells"]:
        print("Sample High Bias Cell:")
        print(poi_report["high_bias_cells"][0])
    
    print("\n" + "=" * 60)
    print("Verification Completed Successfully!")
    print("=" * 60)


if __name__ == "__main__":
    run_tests()
