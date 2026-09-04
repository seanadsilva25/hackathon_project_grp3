from flask import Blueprint, jsonify
from collections import Counter
import pandas as pd
from app.supabase_client import get_supabase_client
from app.heatmap import process_heatmap_pipeline, persist_heatmap_results

heatmap_api = Blueprint("heatmap_api", __name__)

@heatmap_api.route("", methods=["GET"])
def get_heatmap():
    """
    GET /api/heatmap/
    Retrieves persisted heatmap zones from Supabase with contributing complaint counts.
    """
    try:
        supabase = get_supabase_client()

        # 1. Fetch persisted heatmap zones from Supabase
        zones_res = supabase.table("heatmap_zones").select("*").execute()
        zones_data = zones_res.data if zones_res and hasattr(zones_res, "data") else []

        if not zones_data:
            return jsonify({
                "status": "success",
                "count": 0,
                "zones": []
            }), 200

        # 2. Fetch data points to aggregate complaint_count per heatmap_zone_id
        dp_res = supabase.table("heatmap_data_points") \
            .select("heatmap_zone_id") \
            .eq("source_type", "complaint") \
            .execute()
        
        dps_data = dp_res.data if dp_res and hasattr(dp_res, "data") else []

        # Count data points per zone ID
        zone_counts = Counter([dp["heatmap_zone_id"] for dp in dps_data if dp.get("heatmap_zone_id")])

        # 3. Format response zones
        formatted_zones = []
        for zone in zones_data:
            z_id = zone.get("id")
            formatted_zones.append({
                "id": z_id,
                "zone_type": zone.get("zone_type"),
                "latitude": zone.get("latitude"),
                "longitude": zone.get("longitude"),
                "radius_meters": zone.get("radius_meters"),
                "severity": zone.get("severity"),
                "assigned_authority_id": zone.get("assigned_authority_id"),
                "complaint_count": zone_counts.get(z_id, 0)
            })

        return jsonify({
            "status": "success",
            "count": len(formatted_zones),
            "zones": formatted_zones
        }), 200

    except Exception as e:
        print(f"Error fetching heatmap: {e}")
        return jsonify({
            "status": "error",
            "message": "Failed to retrieve heatmap data"
        }), 500

@heatmap_api.route("/refresh", methods=["POST"])
def refresh_heatmap():
    """
    POST /api/heatmap/refresh
    Manually triggers the existing ML pipeline to reprocess all complaints and update heatmap zones.
    Useful for testing and manual recalculation.
    """
    try:
        supabase = get_supabase_client()
        
        # Fetch all complaints
        res = supabase.table("complaints").select("*").execute()
        complaints_data = res.data if res and hasattr(res, "data") else []
        
        if not complaints_data or len(complaints_data) < 3:
            return jsonify({
                "status": "success",
                "message": f"Only {len(complaints_data)} complaints — need >= 3 for DBSCAN clustering",
                "zones_persisted": 0
            }), 200
        
        # Run existing ML pipeline
        df = pd.DataFrame(complaints_data)
        pipeline_result = process_heatmap_pipeline(df)
        
        # Persist using existing deterministic logic
        complaint_ids = [str(c.get("id")) for c in complaints_data if c.get("id")]
        persist_result = persist_heatmap_results(pipeline_result, complaint_ids)
        
        return jsonify({
            "status": "success",
            "summary": pipeline_result.get("summary", {}),
            "zones_persisted": persist_result.get("zones_persisted", 0),
            "data_points_persisted": persist_result.get("data_points_persisted", 0)
        }), 200
        
    except Exception as e:
        print(f"Error refreshing heatmap: {e}")
        return jsonify({
            "status": "error",
            "message": f"Failed to refresh heatmap: {str(e)}"
        }), 500
