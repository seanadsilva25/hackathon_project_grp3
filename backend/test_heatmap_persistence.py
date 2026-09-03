import os
import sys
import pandas as pd
from collections import Counter

# Ensure backend directory is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.supabase_client import get_supabase_client
from app.heatmap import process_heatmap_pipeline, persist_heatmap_results

def run_heatmap_idempotency_test():
    print("=" * 60)
    print("HEATMAP IDEMPOTENCY TEST")
    print("=" * 60)

    try:
        supabase = get_supabase_client()

        # Record Initial DB State
        initial_zones_res = supabase.table('heatmap_zones').select('id', count='exact').execute()
        initial_dps_res = supabase.table('heatmap_data_points').select('id', count='exact').execute()

        initial_zones_count = initial_zones_res.count if hasattr(initial_zones_res, 'count') and initial_zones_res.count is not None else len(initial_zones_res.data or [])
        initial_dps_count = initial_dps_res.count if hasattr(initial_dps_res, 'count') and initial_dps_res.count is not None else len(initial_dps_res.data or [])

        print(f"\nInitial:")
        print(f"  heatmap_zones: {initial_zones_count}")
        print(f"  heatmap_data_points: {initial_dps_count}")

        # 1. Fetch current complaints
        complaints_res = supabase.table('complaints').select('*').execute()
        raw_complaints = complaints_res.data if complaints_res and hasattr(complaints_res, 'data') else []

        if not raw_complaints:
            print("[ERROR] 'complaints' table is empty. Seed complaints first.")
            sys.exit(1)

        df = pd.DataFrame(raw_complaints)
        complaint_ids = [c['id'] for c in raw_complaints if 'id' in c]

        # 2. Run existing ML pipeline
        pipeline_output = process_heatmap_pipeline(df, radius_meters=500, min_samples=3)

        # Separate noise complaint IDs
        noise_complaints = pipeline_output.get('noise_complaints', [])
        noise_ids = set([nc['id'] for nc in noise_complaints if 'id' in nc])

        # --- RUN 1 ---
        persist_heatmap_results(pipeline_output, complaint_ids=complaint_ids)
        r1_zones = supabase.table('heatmap_zones').select('*').execute().data or []
        r1_dps = supabase.table('heatmap_data_points').select('*').execute().data or []

        print(f"\nAfter Run 1:")
        print(f"  heatmap_zones: {len(r1_zones)}")
        print(f"  heatmap_data_points: {len(r1_dps)}")

        # --- RUN 2 ---
        persist_heatmap_results(pipeline_output, complaint_ids=complaint_ids)
        r2_zones = supabase.table('heatmap_zones').select('*').execute().data or []
        r2_dps = supabase.table('heatmap_data_points').select('*').execute().data or []

        print(f"\nAfter Run 2:")
        print(f"  heatmap_zones: {len(r2_zones)}")
        print(f"  heatmap_data_points: {len(r2_dps)}")

        # --- RUN 3 ---
        persist_heatmap_results(pipeline_output, complaint_ids=complaint_ids)
        r3_zones = supabase.table('heatmap_zones').select('*').execute().data or []
        r3_dps = supabase.table('heatmap_data_points').select('*').execute().data or []

        print(f"\nAfter Run 3:")
        print(f"  heatmap_zones: {len(r3_zones)}")
        print(f"  heatmap_data_points: {len(r3_dps)}")

        # --- VALIDATIONS ---
        # 1. Duplicate data points check (source_type + source_id)
        source_pairs = [(dp.get('source_type'), dp.get('source_id')) for dp in r3_dps]
        duplicate_dps_count = len(source_pairs) - len(set(source_pairs))

        # 2. Check if any noise complaints were linked to data points
        noise_dps_count = sum(1 for dp in r3_dps if dp.get('source_id') in noise_ids)

        # 3. Verify data points reference existing zones
        zone_ids_set = set([z['id'] for z in r3_zones])
        orphan_dps_count = sum(1 for dp in r3_dps if dp.get('heatmap_zone_id') not in zone_ids_set)

        # 4. Severity & Category counts
        severities = dict(Counter([z['severity'] for z in r3_zones if 'severity' in z]))
        categories = dict(Counter([z['zone_type'] for z in r3_zones if 'zone_type' in z]))

        print(f"\nDuplicate data points: {duplicate_dps_count}")
        print(f"Noise complaints linked: {noise_dps_count}")
        print(f"Orphan data points: {orphan_dps_count}")

        print(f"\nSeverity:")
        print(f"  LOW: {severities.get('LOW', 0)}")
        print(f"  MEDIUM: {severities.get('MEDIUM', 0)}")
        print(f"  HIGH: {severities.get('HIGH', 0)}")

        print(f"\nCategories:")
        for cat, cnt in sorted(categories.items()):
            print(f"  {cat}: {cnt}")

        # --- ASSERTIONS ---
        assert len(r1_zones) == 5, f"Expected 5 zones after Run 1, got {len(r1_zones)}"
        assert len(r1_dps) == 90, f"Expected 90 data points after Run 1, got {len(r1_dps)}"

        assert len(r2_zones) == 5, f"Expected 5 zones after Run 2, got {len(r2_zones)}"
        assert len(r2_dps) == 90, f"Expected 90 data points after Run 2, got {len(r2_dps)}"

        assert len(r3_zones) == 5, f"Expected 5 zones after Run 3, got {len(r3_zones)}"
        assert len(r3_dps) == 90, f"Expected 90 data points after Run 3, got {len(r3_dps)}"

        assert duplicate_dps_count == 0, f"Expected 0 duplicate data points, got {duplicate_dps_count}"
        assert noise_dps_count == 0, f"Expected 0 noise data points, got {noise_dps_count}"
        assert orphan_dps_count == 0, f"Expected 0 orphan data points, got {orphan_dps_count}"

        assert severities.get('LOW') == 1, f"Expected 1 LOW severity zone, got {severities.get('LOW')}"
        assert severities.get('MEDIUM') == 1, f"Expected 1 MEDIUM severity zone, got {severities.get('MEDIUM')}"
        assert severities.get('HIGH') == 3, f"Expected 3 HIGH severity zones, got {severities.get('HIGH')}"

        print("\n" + "=" * 60)
        print("[SUCCESS] HEATMAP IDEMPOTENCY TEST PASSED!")
        print("=" * 60)

    except Exception as e:
        print("\n" + "=" * 60)
        print("[FAILED] HEATMAP IDEMPOTENCY TEST FAILED")
        print(f"Details: {type(e).__name__}: {e}")
        print("=" * 60)
        sys.exit(1)

if __name__ == '__main__':
    run_heatmap_idempotency_test()
