"""
Demo Scenarios for ParkSense AI
Owner: backend-ml-analysis branch (Eric)

Provides canned scenario data for morning rush, evening rush, and weekend.
"""

# Major H3 cells for central Bengaluru areas (approximate centroids at resolution 8)
# Koramangala: 8861892e21fffff
# MG Road: 8860145b4bfffff
# Indiranagar: 8861892559fffff
# Madiwala: 8861892441fffff
# Bellandur: 8861892f67fffff
# HSR Layout: 8861892ee3fffff

SCENARIOS = {
    "morning_rush": {
        "description": "Weekday Morning Rush Hour (8:30 AM - 10:30 AM)",
        "timestamp": "2024-01-22 09:00:00",
        "predictions": [
            {"h3_cell": "8860145b4bfffff", "predicted_count": 45, "confidence": 0.92, "primary_cause": "Office commute congestion near UB City"},
            {"h3_cell": "8861892559fffff", "predicted_count": 38, "confidence": 0.89, "primary_cause": "Double parking on Indiranagar 100ft road near transit points"},
            {"h3_cell": "8861892ee3fffff", "predicted_count": 25, "confidence": 0.85, "primary_cause": "Wrong parking near schools and local markets"},
            {"h3_cell": "8861892e21fffff", "predicted_count": 18, "confidence": 0.82, "primary_cause": "Moderate congestion near commercial blocks"}
        ]
    },
    "evening_rush": {
        "description": "Weekday Evening Rush Hour (5:30 PM - 7:30 PM)",
        "timestamp": "2024-01-22 18:30:00",
        "predictions": [
            {"h3_cell": "8861892f67fffff", "predicted_count": 55, "confidence": 0.95, "primary_cause": "Severe bottleneck on Outer Ring Road (Bellandur) near tech parks"},
            {"h3_cell": "8861892441fffff", "predicted_count": 48, "confidence": 0.91, "primary_cause": "Bus/taxi boarding blockages near Madiwala junction"},
            {"h3_cell": "8860145b4bfffff", "predicted_count": 32, "confidence": 0.88, "primary_cause": "High shopping and dining parking demand on MG Road"},
            {"h3_cell": "8861892559fffff", "predicted_count": 29, "confidence": 0.86, "primary_cause": "Footpath obstruction in commercial zones"}
        ]
    },
    "weekend": {
        "description": "Saturday Evening Leisure Peak (6:00 PM - 9:00 PM)",
        "timestamp": "2024-01-20 19:30:00",
        "predictions": [
            {"h3_cell": "8861892e21fffff", "predicted_count": 60, "confidence": 0.94, "primary_cause": "Critical parking shortage near Koramangala Forum Mall / food streets"},
            {"h3_cell": "8861892559fffff", "predicted_count": 42, "confidence": 0.90, "primary_cause": "Pub/restaurant parking spillover in Indiranagar"},
            {"h3_cell": "8860145b4bfffff", "predicted_count": 35, "confidence": 0.87, "primary_cause": "UB City luxury shopping parking rush"},
            {"h3_cell": "8861892ee3fffff", "predicted_count": 22, "confidence": 0.81, "primary_cause": "HSR Layout Sector 3 commercial sector rush"}
        ]
    }
}


def get_demo_scenario(scenario_name: str) -> dict:
    """
    Returns canned predictions and description for the requested demo scenario.
    """
    return SCENARIOS.get(scenario_name, {
        "description": "Unknown Scenario",
        "timestamp": "",
        "predictions": []
    })
