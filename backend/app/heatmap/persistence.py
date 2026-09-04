import os
import sys
import uuid
from typing import Dict, Any, List
from app.supabase_client import get_supabase_client

# Fixed deterministic namespaces for UniSafe Heatmap UUIDs
NAMESPACE_UNISAFE_ZONE = uuid.UUID('6ba7b810-9dad-11d1-80b4-00c04fd430c8')
NAMESPACE_UNISAFE_DATAPOINT = uuid.UUID('6ba7b811-9dad-11d1-80b4-00c04fd430c8')

def generate_deterministic_zone_id(complaint_ids: List[str]) -> str:
    """Generates a deterministic UUID5 for a zone based on sorted cluster complaint IDs."""
    sorted_ids = sorted([str(cid).strip() for cid in complaint_ids if cid])
    canonical_str = ",".join(sorted_ids)
    return str(uuid.uuid5(NAMESPACE_UNISAFE_ZONE, canonical_str))

def generate_deterministic_datapoint_id(source_type: str, source_id: str) -> str:
    """Generates a deterministic UUID5 for a heatmap_data_point based on source_type and source_id."""
    canonical_str = f"{source_type.strip().lower()}:{str(source_id).strip()}"
    return str(uuid.uuid5(NAMESPACE_UNISAFE_DATAPOINT, canonical_str))

def persist_heatmap_results(pipeline_output: Dict[str, Any], complaint_ids: List[str] = None) -> Dict[str, Any]:
    """
    Idempotent persistence layer for Heatmap results into Supabase.

    Strategy:
    1. Derives deterministic UUIDs (uuid5) for zones based on cluster membership.
    2. Derives deterministic UUIDs (uuid5) for data points based on source_type + source_id.
    3. Performs upsert on heatmap_zones and heatmap_data_points.
    4. Safely removes stale data points or orphan zones scoped ONLY to the processed complaint IDs.

    :param pipeline_output: Dict returned by process_heatmap_pipeline()
    :param complaint_ids: List of source complaint IDs processed
    :return: Summary dictionary
    """
    supabase = get_supabase_client()

    raw_zones = pipeline_output.get('heatmap_zones', [])
    raw_data_points = pipeline_output.get('heatmap_data_points', [])

    # Group raw data points by original zone ID to map cluster membership
    zone_to_complaint_ids = {}
    for dp in raw_data_points:
        z_id = dp.get('heatmap_zone_id')
        s_id = dp.get('source_id')
        if z_id and s_id:
            zone_to_complaint_ids.setdefault(z_id, []).append(s_id)

    # --- Step 1: Compute Deterministic Zone UUIDs & Data Point UUIDs ---
    old_zone_id_to_new_zone_id = {}
    zones_to_upsert = []

    for zone in raw_zones:
        old_id = zone['id']
        c_ids = zone_to_complaint_ids.get(old_id, [])
        det_zone_id = generate_deterministic_zone_id(c_ids)
        old_zone_id_to_new_zone_id[old_id] = det_zone_id

        # Clean authority ID
        auth_id = zone.get('assigned_authority_id')
        if not auth_id or not isinstance(auth_id, str) or len(auth_id.strip()) == 0:
            auth_id = None

        zones_to_upsert.append({
            'id': det_zone_id,
            'zone_type': str(zone['zone_type']),
            'latitude': float(zone['latitude']),
            'longitude': float(zone['longitude']),
            'radius_meters': int(zone['radius_meters']),
            'severity': str(zone['severity']),
            'assigned_authority_id': auth_id
        })

    dps_to_upsert = []
    for dp in raw_data_points:
        old_z_id = dp.get('heatmap_zone_id')
        det_z_id = old_zone_id_to_new_zone_id.get(old_z_id)
        source_type = str(dp.get('source_type', 'complaint'))
        source_id = str(dp['source_id'])

        det_dp_id = generate_deterministic_datapoint_id(source_type, source_id)

        created_at_val = dp.get('created_at')
        if not created_at_val or str(created_at_val).strip() == '':
            created_at_val = None

        dps_to_upsert.append({
            'id': det_dp_id,
            'heatmap_zone_id': det_z_id,
            'source_type': source_type,
            'source_id': source_id,
            'created_at': created_at_val
        })

    # Collect complaint IDs for targeted cleanup
    if complaint_ids is None:
        complaint_ids = list(set([dp['source_id'] for dp in dps_to_upsert]))

    # --- Step 2: Targeted Scoped Cleanup of Stale Records for Processed Complaints ---
    if complaint_ids:
        try:
            existing_dp_res = supabase.table('heatmap_data_points') \
                .select('id, heatmap_zone_id, source_id') \
                .eq('source_type', 'complaint') \
                .in_('source_id', complaint_ids) \
                .execute()

            existing_dps = existing_dp_res.data if existing_dp_res and hasattr(existing_dp_res, 'data') else []

            if existing_dps:
                valid_dp_ids = set([dp['id'] for dp in dps_to_upsert])
                valid_zone_ids = set([z['id'] for z in zones_to_upsert])

                # Identify stale data points for these complaints
                stale_dp_ids = [dp['id'] for dp in existing_dps if dp['id'] not in valid_dp_ids]
                if stale_dp_ids:
                    supabase.table('heatmap_data_points').delete().in_('id', stale_dp_ids).execute()

                # Identify candidate orphan zones for these complaints
                existing_zone_ids = set([dp['heatmap_zone_id'] for dp in existing_dps if dp.get('heatmap_zone_id')])
                stale_candidate_zone_ids = list(existing_zone_ids - valid_zone_ids)

                # Delete orphan zones if no remaining data points reference them
                for candidate_id in stale_candidate_zone_ids:
                    remaining_dp_res = supabase.table('heatmap_data_points') \
                        .select('id') \
                        .eq('heatmap_zone_id', candidate_id) \
                        .limit(1) \
                        .execute()
                    if not (remaining_dp_res and hasattr(remaining_dp_res, 'data') and remaining_dp_res.data):
                        supabase.table('heatmap_zones').delete().eq('id', candidate_id).execute()

        except Exception as e:
            print(f"[WARNING] Scoped stale cleanup notice: {e}")

    # --- Step 3: Upsert Deterministic Heatmap Zones ---
    upserted_zones_count = 0
    if zones_to_upsert:
        chunk_size = 50
        for i in range(0, len(zones_to_upsert), chunk_size):
            chunk = zones_to_upsert[i:i + chunk_size]
            res = supabase.table('heatmap_zones').upsert(chunk, on_conflict='id').execute()
            if res and hasattr(res, 'data'):
                upserted_zones_count += len(res.data)

    # --- Step 4: Upsert Deterministic Heatmap Data Points ---
    upserted_dps_count = 0
    if dps_to_upsert:
        chunk_size = 50
        for i in range(0, len(dps_to_upsert), chunk_size):
            chunk = dps_to_upsert[i:i + chunk_size]
            res = supabase.table('heatmap_data_points').upsert(chunk, on_conflict='id').execute()
            if res and hasattr(res, 'data'):
                upserted_dps_count += len(res.data)

    return {
        'status': 'success',
        'zones_persisted': upserted_zones_count,
        'data_points_persisted': upserted_dps_count,
        'zones': zones_to_upsert
    }
