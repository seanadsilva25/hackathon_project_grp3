import os
import sys
import pandas as pd

# Ensure backend app directory is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.heatmap import process_heatmap_pipeline

def run_test():
    # Resolve CSV filepath
    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(base_dir, 'app', 'data', 'test_complaints_100.csv')

    if not os.path.exists(csv_path):
        # Fallback check for root backend/data/ directory
        csv_path = os.path.join(base_dir, 'data', 'test_complaints_100.csv')

    print("=" * 60)
    print(" UNISAFE HEATMAP ML PIPELINE TEST (DBSCAN + SEVERITY SCORING)")
    print("=" * 60)
    print(f"Loading test dataset from: {csv_path}")

    if not os.path.exists(csv_path):
        print(f"ERROR: Dataset file not found at {csv_path}")
        return

    df = pd.read_csv(csv_path)
    print(f"Loaded {len(df)} complaints successfully.")
    print("-" * 60)

    # Execute pipeline
    result = process_heatmap_pipeline(df, radius_meters=500, min_samples=3)

    summary = result['summary']
    zones = result['heatmap_zones']
    data_points = result['heatmap_data_points']
    noise = result['noise_complaints']

    print(f"PIPELINE SUMMARY:")
    print(f"  • Total complaints processed : {summary['total_complaints']}")
    print(f"  • Valid coordinates          : {summary['valid_coordinates']}")
    print(f"  • Geographical clusters      : {summary['clusters_detected']}")
    print(f"  • Noise / Isolated complaints: {summary['noise_complaints']}")
    print(f"  • Mapped data points         : {len(data_points)}")
    print("=" * 60)

    print("\nDETECTED HOTSPOT ZONES (HEATMAP ZONES):")
    print("=" * 60)

    for idx, zone in enumerate(zones):
        # Find mapped complaints for this zone
        mapped_ids = [dp['source_id'] for dp in data_points if dp['heatmap_zone_id'] == zone['id']]
        
        print(f"Cluster {idx} (Zone ID: {zone['id'][:8]}...)")
        print(f"  • Zone Type      : {zone['zone_type'].upper()}")
        print(f"  • Complaints Count: {zone['complaint_count']}")
        print(f"  • Centroid       : ({zone['latitude']}, {zone['longitude']})")
        print(f"  • Approx Radius  : {zone['radius_meters']} meters")
        print(f"  • Risk Score     : {zone['risk_score']} / 100")
        print(f"  • Severity Level : {zone['severity']}")
        print(f"  • Score Breakdown: {zone['breakdown']}")
        print(f"  • Contributing Complaint IDs ({len(mapped_ids)}):")
        for cid in mapped_ids[:5]:
            print(f"      - {cid}")
        if len(mapped_ids) > 5:
            print(f"      ... and {len(mapped_ids) - 5} more")
        print("-" * 60)

    if noise:
        print("\nNOISE / ISOLATED COMPLAINTS (Not part of any cluster):")
        print("=" * 60)
        for nc in noise[:5]:
            print(f"  • ID: {nc.get('id')} | Category: {nc.get('category')} | Lat/Lon: ({nc.get('latitude')}, {nc.get('longitude')}) | Title: {nc.get('title')}")
        if len(noise) > 5:
            print(f"  ... and {len(noise) - 5} more noise complaints.")
        print("=" * 60)

    print("\n[SUCCESS] TEST COMPLETED SUCCESSFULLY!")

if __name__ == '__main__':
    run_test()
