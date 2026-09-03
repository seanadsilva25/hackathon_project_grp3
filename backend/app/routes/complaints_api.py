import requests
from flask import Blueprint, request, jsonify
from app.services.notification_service import get_supabase_headers, get_supabase_url, log_complaint_action, create_notification
from app.services.email_service import (
    send_status_in_progress_email, 
    send_resolved_email,
    send_threshold_citizen_email,
    send_threshold_authority_email
)

complaints_api = Blueprint("complaints_api", __name__)

COMMUNITY_THRESHOLD = 10

def _fetch_one(table, column, value):
    url = f"{get_supabase_url()}/rest/v1/{table}?{column}=eq.{value}&select=*"
    try:
        resp = requests.get(url, headers=get_supabase_headers())
        if resp.status_code == 200 and len(resp.json()) > 0:
            return resp.json()[0]
    except Exception as e:
        print(f"Error fetching {table}: {e}")
    return None

def _update(table, id_val, payload):
    url = f"{get_supabase_url()}/rest/v1/{table}?id=eq.{id_val}"
    try:
        resp = requests.patch(url, headers=get_supabase_headers(), json=payload)
        if resp.status_code in [200, 204]:
            # Fetch updated row
            return _fetch_one(table, "id", id_val)
    except Exception as e:
        print(f"Error updating {table}: {e}")
    return None

@complaints_api.route("/<complaint_id>/status", methods=["POST"])
def update_status(complaint_id):
    data = request.json
    new_status = data.get("status")
    authority_id = data.get("authority_id")
    
    if not new_status or not authority_id:
        return jsonify({"error": "status and authority_id required"}), 400
        
    try:
        authority = _fetch_one("authorities", "id", authority_id)
        if not authority:
            return jsonify({"error": "Authority not found"}), 404
        
        complaint = _update("complaints", complaint_id, {"status": new_status})
        if not complaint:
            return jsonify({"error": "Complaint not found or update failed"}), 404
        
        citizen = _fetch_one("citizens", "id", complaint.get("citizen_id")) if complaint.get("citizen_id") else None
                
        msg = f"Complaint moved to {new_status}"
        log_complaint_action(complaint_id, authority_id, "STATUS_CHANGED", msg)
        
        if new_status == "in_progress":
            create_notification(
                title="Complaint In Progress",
                body=f"Your complaint '{complaint['title']}' is now in progress.",
                citizen_id=citizen["id"] if citizen else None
            )
            if citizen:
                send_status_in_progress_email(citizen, complaint, authority.get("department", "Authority"))
                
        elif new_status == "resolved":
            create_notification(
                title="Complaint Resolved",
                body=f"Your complaint '{complaint['title']}' has been resolved.",
                citizen_id=citizen["id"] if citizen else None
            )
            if citizen:
                send_resolved_email(citizen, complaint, authority.get("department", "Authority"))
                
        return jsonify({"success": True, "complaint": complaint})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@complaints_api.route("/<complaint_id>/upvote", methods=["POST"])
def upvote_complaint(complaint_id):
    try:
        complaint = _fetch_one("complaints", "id", complaint_id)
        if not complaint:
            return jsonify({"error": "Complaint not found"}), 404
        
        previous_count = complaint.get("upvote_count", 0)
        new_count = previous_count + 1
        
        updated_complaint = _update("complaints", complaint_id, {"upvote_count": new_count})
        if not updated_complaint:
            return jsonify({"error": "Failed to update upvotes"}), 500
            
        if previous_count < COMMUNITY_THRESHOLD and new_count >= COMMUNITY_THRESHOLD:
            citizen = _fetch_one("citizens", "id", updated_complaint.get("citizen_id")) if updated_complaint.get("citizen_id") else None
            if citizen:
                send_threshold_citizen_email(citizen, updated_complaint)
                create_notification(
                    title="Community Threshold Reached",
                    body=f"Your complaint '{updated_complaint['title']}' has been escalated.",
                    citizen_id=citizen["id"]
                )
            
            authority = _fetch_one("authorities", "id", updated_complaint.get("assigned_authority_id")) if updated_complaint.get("assigned_authority_id") else None
            if authority:
                send_threshold_authority_email(authority, updated_complaint)
                create_notification(
                    title="Critical Threshold Escalation",
                    body=f"Complaint '{updated_complaint['title']}' reached the community threshold.",
                    authority_id=authority["id"]
                )
                    
        return jsonify({"success": True, "upvote_count": new_count})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
