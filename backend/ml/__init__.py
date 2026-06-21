"""ML analysis package — forecasting, profiling, audit."""
from .hotspot_forecast import build_features, train_model, predict_next_2h
from .offender_profiler import profile_offenders, detect_fleets
from .sensor_audit import audit_sensor_health, poi_bias_report
from .demo_scenarios import get_demo_scenario
