# Sensor Audit & POI Bias Summary (Demo Reference)
Owner: backend-ml-analysis branch (Eric)

This document provides ready-to-use figures and analysis points for the team's presentation slides and demo.

## 1. Device & Sensor Health Audit
Using the validation records, we analyzed the ratio of rejected reports to identify low-performing device clusters or station jurisdictions:

* **Madiwala PS**: **23.1% Rejection Rate** (WARNING) - High volume (78 reports) but 18 rejections. Recommend device calibration or reporting training.
* **Bellandur PS**: **21.7% Rejection Rate** (WARNING) - 83 reports, 18 rejections.
* **HSR Layout PS**: **17.4% Rejection Rate** (WARNING) - 92 reports, 16 rejections.
* **Koramangala PS**: **14.1% Rejection Rate** (OK) - 78 reports, 11 rejections.
* **Indiranagar PS**: **11.1% Rejection Rate** (OK) - 81 reports, 9 rejections.

*Key Takeaway:* Focus QA audits on reporting sensors/devices operating within Madiwala and Bellandur sectors.

## 2. Spatial POI Bias Mitigation
High-density commercial zones (shopping hubs) artificially inflate violation counts, creating false-alarm congestion hotspots. 

* **Mechanism**: The system cross-references H3 spatial bins with commercial POI locations (shopping malls, marketplaces, restaurants) using OpenStreetMap data.
* **Mitigation**: Applies a dynamic `recommended_normalization_factor` (up to 1.4x divisor) to scale down raw violation counts based on proximity to commercial POIs:
  $$\text{Adjusted CIS} = \frac{\text{Raw CIS}}{1.0 + 0.4 \times \text{POI Proximity Ratio}}$$
* **Result**: Ensures enforcement is prioritized on actual traffic bottlenecks rather than consumer parking areas.
