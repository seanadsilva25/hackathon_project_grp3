import os
from flask import Blueprint, jsonify, request
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

main = Blueprint("main", __name__)

SUPABASE_URL = os.environ.get("SUPABASE_URL") or os.environ.get("VITE_SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY") or os.environ.get("VITE_SUPABASE_ANON_KEY")

supabase: Client = None
if SUPABASE_URL and SUPABASE_KEY:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

@main.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "message": "Backend is running"
    })

@main.route("/complaints", methods=["GET"])
def get_complaints():
    if not supabase:
        return jsonify({"error": "Supabase not configured"}), 500
    try:
        response = supabase.table("complaints").select("*").execute()
        return jsonify(response.data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@main.route("/kanban/tasks", methods=["GET"])
def get_kanban_tasks():
    if not supabase:
        return jsonify({"error": "Supabase not configured"}), 500
    try:
        response = supabase.table("heatmap_zones").select("*").execute()
        return jsonify(response.data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

from app.services.notification_service import create_notification

@main.route("/kanban/tasks/<zone_id>/status", methods=["PUT"])
def update_task_status(zone_id):
    if not supabase:
        return jsonify({"error": "Supabase not configured"}), 500
    try:
        data = request.json
        status = data.get("status")
        response = supabase.table("heatmap_zones").update({"status": status}).eq("id", zone_id).execute()
        
        zone_data = response.data[0] if response.data else {}
        if zone_data:
            # Look up a citizen_id from complaints linked to this zone
            try:
                dp_res = supabase.table("heatmap_data_points").select("source_id").eq("heatmap_zone_id", zone_id).eq("source_type", "complaint").limit(1).execute()
                citizen_id = None
                if dp_res and dp_res.data:
                    complaint_id = dp_res.data[0].get("source_id")
                    if complaint_id:
                        c_res = supabase.table("complaints").select("citizen_id").eq("id", complaint_id).limit(1).execute()
                        if c_res and c_res.data:
                            citizen_id = c_res.data[0].get("citizen_id")
                
                if citizen_id:
                    if status == "done":
                        create_notification(
                            title="Complaint Resolved",
                            body=f"A complaint in zone {zone_data.get('zone_type')} has been resolved.",
                            citizen_id=citizen_id
                        )
                    else:
                        create_notification(
                            title="Complaint Status Changed",
                            body=f"A complaint in zone {zone_data.get('zone_type')} was moved to {status}.",
                            citizen_id=citizen_id
                        )
            except Exception as notif_err:
                print(f"[KANBAN] Notification error (status update still saved): {notif_err}")

        return jsonify(zone_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@main.route("/kanban/tasks/<zone_id>/resolve", methods=["POST"])
def resolve_task(zone_id):
    if not supabase:
        return jsonify({"error": "Supabase not configured"}), 500
    try:
        data = request.json
        image_url = data.get("authority_image_url")
        response = supabase.table("heatmap_zones").update({
            "status": "in-review",
            "authority_image_url": image_url
        }).eq("id", zone_id).execute()
        
        zone_data = response.data[0] if response.data else {}
        if zone_data:
            # Look up citizen_id from related complaints for notification
            try:
                dp_res = supabase.table("heatmap_data_points").select("source_id").eq("heatmap_zone_id", zone_id).eq("source_type", "complaint").limit(1).execute()
                citizen_id = None
                if dp_res and dp_res.data:
                    complaint_id = dp_res.data[0].get("source_id")
                    if complaint_id:
                        c_res = supabase.table("complaints").select("citizen_id").eq("id", complaint_id).limit(1).execute()
                        if c_res and c_res.data:
                            citizen_id = c_res.data[0].get("citizen_id")
                
                if citizen_id:
                    create_notification(
                        title="Resolution Under Review",
                        body=f"The issue for {zone_data.get('zone_type')} is under review. Please verify the resolution.",
                        citizen_id=citizen_id
                    )
                    # Broadcast for high-risk zones
                    if zone_data.get("severity") == "HIGH":
                        create_notification(
                            title="Alert: High Risk Issue in Review",
                            body=f"A high risk {zone_data.get('zone_type')} issue near your location is under review.",
                            citizen_id=citizen_id
                        )
            except Exception as notif_err:
                print(f"[KANBAN] Notification error (resolve still saved): {notif_err}")
                
        return jsonify(zone_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@main.route("/kanban/tasks/<zone_id>/verify", methods=["POST"])
def verify_task(zone_id):
    if not supabase:
        return jsonify({"error": "Supabase not configured"}), 500
    try:
        data = request.json
        image_url = data.get("image_url")
        
        # Insert verification
        supabase.table("complaint_verifications").insert({
            "zone_id": zone_id,
            "image_url": image_url,
            "is_verified": True
        }).execute()
        
        # Update zone status to done
        response = supabase.table("heatmap_zones").update({
            "status": "done"
        }).eq("id", zone_id).execute()
        
        return jsonify(response.data[0] if response.data else {})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@main.route("/kanban/tasks/<zone_id>/reject", methods=["POST"])
def reject_task(zone_id):
    if not supabase:
        return jsonify({"error": "Supabase not configured"}), 500
    try:
        data = request.json
        image_url = data.get("image_url")
        
        # Insert verification
        supabase.table("complaint_verifications").insert({
            "zone_id": zone_id,
            "image_url": image_url,
            "is_verified": False
        }).execute()
        
        # Update zone status back to in-progress
        response = supabase.table("heatmap_zones").update({
            "status": "in-progress"
        }).eq("id", zone_id).execute()
        
        return jsonify(response.data[0] if response.data else {})
    except Exception as e:
        return jsonify({"error": str(e)}), 500