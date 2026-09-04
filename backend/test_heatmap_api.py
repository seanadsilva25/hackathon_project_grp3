import os
import sys
import json
from collections import Counter

# Ensure backend directory is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app

def run_heatmap_api_test():
    print("=" * 60)
    print(" UNISAFE HEATMAP FLASK API ENDPOINT TEST (GET /api/heatmap)")
    print("=" * 60)

    app = create_app()
    client = app.test_client()

    print("1. Sending GET request to /api/heatmap ...")
    response = client.get("/api/heatmap")

    print(f"   HTTP Status Code: {response.status_code}")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"

    data = response.get_json()
    print("   [SUCCESS] Received HTTP 200 with valid JSON response.")

    # Validate JSON structure
    assert data.get("status") == "success", f"Expected status 'success', got '{data.get('status')}'"
    assert "zones" in data, "Response JSON missing 'zones' key"

    zones = data["zones"]
    zone_count = len(zones)
    print(f"   Returned {zone_count} heatmap zones.")
    assert zone_count == 5, f"Expected 5 heatmap zones, got {zone_count}"

    required_fields = [
        "id", "zone_type", "latitude", "longitude",
        "radius_meters", "severity", "assigned_authority_id", "complaint_count"
    ]

    print("\n2. Validating zone schema fields and values:")
    severities = []
    categories = []
    total_complaints_in_zones = 0

    for idx, zone in enumerate(zones):
        for field in required_fields:
            assert field in zone, f"Zone #{idx} missing required field '{field}'"

        severities.append(zone["severity"])
        categories.append(zone["zone_type"])
        total_complaints_in_zones += zone["complaint_count"]

        print(f"  • Zone {idx+1}: [{zone['zone_type'].upper()}] - Severity: {zone['severity']} | Radius: {zone['radius_meters']}m | Complaints: {zone['complaint_count']} | Centroid: ({zone['latitude']}, {zone['longitude']})")

    severity_dist = dict(Counter(severities))
    category_dist = dict(Counter(categories))

    print("-" * 60)
    print("SUMMARY RESULTS:")
    print(f"  • Endpoint URL                : GET /api/heatmap")
    print(f"  • HTTP Status                : 200 OK")
    print(f"  • Total Zones Returned       : {zone_count}")
    print(f"  • Total Clustered Complaints : {total_complaints_in_zones}")
    print(f"  • Severity Distribution      : {severity_dist}")
    print(f"  • Categories Breakdown       : {category_dist}")
    print("=" * 60)

    # Verify expected count & distribution assertions
    assert severity_dist.get("LOW") == 1, f"Expected 1 LOW severity zone, got {severity_dist.get('LOW')}"
    assert severity_dist.get("MEDIUM") == 1, f"Expected 1 MEDIUM severity zone, got {severity_dist.get('MEDIUM')}"
    assert severity_dist.get("HIGH") == 3, f"Expected 3 HIGH severity zones, got {severity_dist.get('HIGH')}"
    assert total_complaints_in_zones == 90, f"Expected 90 total clustered complaints, got {total_complaints_in_zones}"

    print("\n[SUCCESS] HEATMAP FLASK API ENDPOINT TEST PASSED!")

if __name__ == "__main__":
    run_heatmap_api_test()
