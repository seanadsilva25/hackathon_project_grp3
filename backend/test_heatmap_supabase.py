import os
import sys
import pandas as pd

# Ensure backend directory is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.supabase_client import get_supabase_client
from app.heatmap import process_heatmap_pipeline

def run_supabase_heatmap_integration_test():
    print("=" * 60)
    print(" UNISAFE SUPABASE -> HEATMAP ML PIPELINE INTEGRATION TEST")
    print("=" * 60)

    try:
        # 1. Reuse existing Supabase client
        print("1. Initializing Supabase client...")
        supabase = get_supabase_client()

        # 2. Fetch records from public.complaints
        print("2. Fetching records from Supabase 'complaints' table...")
        response = supabase.table('complaints').select('*').execute()
        raw_records = response.data if response and hasattr(response, 'data') else []

        fetched_count = len(raw_records)
        print(f"   Fetched {fetched_count} complaints from Supabase.")

        if fetched_count == 0:
            print("[WARNING] Table 'complaints' is empty. No records to process.")
            return

        # 3. Convert to pandas DataFrame
        df = pd.DataFrame(raw_records)

        # 4. Handle null/missing fields safely without crashing
        df['latitude'] = pd.to_numeric(df.get('latitude'), errors='coerce')
        df['longitude'] = pd.to_numeric(df.get('longitude'), errors='coerce')
        if 'upvote_count' in df.columns:
            df['upvote_count'] = pd.to_numeric(df['upvote_count'], errors='coerce').fillna(0)
        else:
            df['upvote_count'] = 0

        if 'status' in df.columns:
            df['status'] = df['status'].fillna('open')
        else:
            df['status'] = 'open'

        if 'category' in df.columns:
            df['category'] = df['category'].fillna('general')
        else:
            df['category'] = 'general'

        # 5. Execute existing ML Pipeline
        print("3. Executing existing Heatmap ML Pipeline (DBSCAN + Severity Scoring)...")
        pipeline_result = process_heatmap_pipeline(df, radius_meters=500, min_samples=3)

        summary = pipeline_result['summary']
        zones = pipeline_result['heatmap_zones']
        data_points = pipeline_result['heatmap_data_points']
        noise = pipeline_result['noise_complaints']

        # 6. Report Summary & Hotspots
        print("-" * 60)
        print("PIPELINE INTEGRATION RESULTS:")
        print(f"  • Complaints fetched from Supabase : {fetched_count}")
        print(f"  • Valid geographic coordinates    : {summary['valid_coordinates']}")
        print(f"  • Geographical clusters detected   : {summary['clusters_detected']}")
        print(f"  • DBSCAN noise points (isolated)   : {summary['noise_complaints']}")
        print(f"  • Mapped zone data points          : {len(data_points)}")
        print("=" * 60)

        print("\nDETECTED SUPABASE HOTSPOT ZONES:")
        print("=" * 60)

        for idx, zone in enumerate(zones):
            print(f"Cluster {idx} (Zone ID: {zone['id'][:8]}...)")
            print(f"  • Dominant Category: {zone['zone_type'].upper()}")
            print(f"  • Complaint Count  : {zone['complaint_count']}")
            print(f"  • Centroid         : ({zone['latitude']}, {zone['longitude']})")
            print(f"  • Approx Radius    : {zone['radius_meters']} meters")
            print(f"  • Risk Score       : {zone['risk_score']} / 100")
            print(f"  • Severity Level   : {zone['severity']}")
            print(f"  • Score Breakdown  : {zone['breakdown']}")
            print("-" * 60)

        if noise:
            print("\nDBSCAN NOISE / ISOLATED POINTS (Not clustered):")
            print("=" * 60)
            for nc in noise[:5]:
                print(f"  • ID: {nc.get('id')} | Category: {nc.get('category')} | Lat/Lon: ({nc.get('latitude')}, {nc.get('longitude')})")
            if len(noise) > 5:
                print(f"  ... and {len(noise) - 5} more noise points.")
            print("=" * 60)

        print("\n[SUCCESS] SUPABASE -> HEATMAP ML PIPELINE INTEGRATION PASSED!")

    except Exception as e:
        print("\n[ERROR] Supabase -> Heatmap ML Pipeline Integration Failed!")
        print(f"Details: {type(e).__name__}: {e}")
        sys.exit(1)

if __name__ == '__main__':
    run_supabase_heatmap_integration_test()
