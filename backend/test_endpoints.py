"""
Integration test script for ParkSense AI FastAPI server
Owner: backend-api branch (Kratik)
"""

import urllib.request
import json
import sys

BASE_URL = "http://127.0.0.1:8000"

def make_request(path: str) -> dict:
    url = f"{BASE_URL}{path}"
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as response:
            return {
                "status": response.status,
                "data": json.loads(response.read().decode())
            }
    except Exception as e:
        print(f"[FAIL] Error requesting {url}: {e}")
        return {"status": 500, "data": None}

def run_tests():
    print("=" * 60)
    print("PARKSENSE AI API INTEGRATION TESTS")
    print("=" * 60)
    
    # 1. Health Check
    print("1. Health Check...")
    res = make_request("/")
    if res["status"] == 200 and res["data"].get("status") == "ok":
        print("[PASS] Health Check")
    else:
        print(f"[FAIL] Health Check: {res}")
        sys.exit(1)
        
    # 2. Stats
    print("\n2. Summary Statistics (/api/stats)...")
    res = make_request("/api/stats")
    if res["status"] == 200 and "total_violations" in res["data"]:
        print(f"[PASS] stats: total_violations={res['data']['total_violations']}")
    else:
        print(f"[FAIL] stats: {res}")
        
    # 3. Violations (with page limit)
    print("\n3. List Violations (/api/violations)...")
    res = make_request("/api/violations?limit=5")
    violation_id = None
    if res["status"] == 200 and len(res["data"]["data"]) > 0:
        violation_id = res["data"]["data"][0]["violation_id"]
        print(f"[PASS] violations: retrieved {len(res['data']['data'])} records. Sample ID: {violation_id}")
    else:
        print(f"[FAIL] violations: {res}")
        
    # 4. Heatmap
    print("\n4. Spatial Heatmap (/api/heatmap)...")
    res = make_request("/api/heatmap?top_n=3")
    if res["status"] == 200 and "cells" in res["data"]:
        print(f"[PASS] heatmap: returned {len(res['data']['cells'])} cell clusters.")
    else:
        print(f"[FAIL] heatmap: {res}")

    # 5. Hotspots
    print("\n5. DBSCAN Hotspots (/api/hotspots)...")
    res = make_request("/api/hotspots?limit=3")
    if res["status"] == 200 and "hotspots" in res["data"]:
        print(f"[PASS] hotspots: returned {len(res['data']['hotspots'])} hotspots.")
    else:
        print(f"[FAIL] hotspots: {res}")

    # 6. Offenders
    print("\n6. Repeat Offenders (/api/offenders)...")
    res = make_request("/api/offenders?limit=5")
    if res["status"] == 200 and "offenders" in res["data"]:
        print(f"[PASS] offenders: returned {len(res['data']['offenders'])} offenders.")
    else:
        print(f"[FAIL] offenders: {res}")

    # 7. Fleets
    print("\n7. Fleet Operator Profiling (/api/fleets)...")
    res = make_request("/api/fleets")
    if res["status"] == 200 and "fleets" in res["data"]:
        print(f"[PASS] fleets: returned {len(res['data']['fleets'])} suspected fleets.")
    else:
        print(f"[FAIL] fleets: {res}")

    # 8. Sensor Audit
    print("\n8. Sensor Health Audit (/api/sensors/audit)...")
    res = make_request("/api/sensors/audit")
    if res["status"] == 200 and "audit" in res["data"]:
        print(f"[PASS] sensor audit: audited {len(res['data']['audit'])} stations.")
    else:
        print(f"[FAIL] sensor audit: {res}")

    # 9. Forecasting
    print("\n9. LightGBM Hotspot Forecasting (/api/predict)...")
    res = make_request("/api/predict?limit=3")
    if res["status"] == 200 and "predictions" in res["data"]:
        print(f"[PASS] predict: generated {len(res['data']['predictions'])} forecasts.")
    else:
        print(f"[FAIL] predict: {res}")

    # 10. Challan Dynamic calculator
    if violation_id:
        print(f"\n10. Challan Calculation (/api/challan/recommend) for violation: {violation_id}...")
        res = make_request(f"/api/challan/recommend?violation_id={violation_id}")
        if res["status"] == 200 and "recommended_fine" in res["data"]:
            print(f"[PASS] challan: dynamic recommended fine is {res['data']['recommended_fine']}")
        else:
            print(f"[FAIL] challan: {res}")
    else:
        print("\n[SKIP] challan: No violation ID available to test.")

    # 11. Simulation
    print("\n11. What-If Simulation (/api/parkflow/simulate)...")
    res = make_request("/api/parkflow/simulate?latitude=12.9785&longitude=77.5912&radius_meters=500")
    if res["status"] == 200 and "cis_score_reduction" in res["data"]:
        print(f"[PASS] simulate: simulated CIS reduction of {res['data']['cis_score_reduction']} points ({res['data']['percentage_reduction']}% drop)")
    else:
        print(f"[FAIL] simulate: {res}")

    print("=" * 60)
    print("TEST SUITE RUN COMPLETED")
    print("=" * 60)

if __name__ == "__main__":
    run_tests()
