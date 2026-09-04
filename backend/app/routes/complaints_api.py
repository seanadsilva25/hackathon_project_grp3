import requests
from flask import Blueprint, request, jsonify
from app.services.notification_service import get_supabase_headers, get_supabase_url, log_complaint_action, create_notification
from app.services.email_service import (
    send_status_in_progress_email, 
    send_resolved_email,
    send_threshold_citizen_email,
    send_threshold_authority_email
)
from app.services.authority_assignment_service import assign_complaint_authority

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

@complaints_api.route("", methods=["POST"])
@complaints_api.route("/", methods=["POST"])
def create_complaint():
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400
        
    # Provide defaults for missing fields from Pranav's map
    payload = {
        "description": data.get("description", ""),
        "category": data.get("category", "General"),
        "latitude": data.get("latitude"),
        "longitude": data.get("longitude"),
        "image_url": data.get("image_url"),
        "status": "pending",
        "upvote_count": 0,
        "jurisdiction": data.get("jurisdiction", "Mumbai North") # Default for hackathon
    }
    
    url = f"{get_supabase_url()}/rest/v1/complaints"
    headers = get_supabase_headers()
    headers["Prefer"] = "return=representation"
    
    try:
        resp = requests.post(url, headers=headers, json=payload)
        if resp.status_code not in [200, 201, 204]:
            return jsonify({"error": f"Failed to insert: {resp.text}"}), 400
            
        complaint = resp.json()[0] if isinstance(resp.json(), list) else resp.json()
        
        # Trigger Assignment Engine automatically!
        assign_result = assign_complaint_authority(complaint)
        print(f"Auto-assignment result: {assign_result}")
        
        # Notify citizen
        create_notification(
            title="Complaint Submitted",
            body=f"Your complaint '{complaint.get('category', 'Complaint')}' has been successfully submitted.",
            citizen_id=complaint.get("citizen_id")
        )
        
        # Return the complaint (Frontend expects this format)
        return jsonify(complaint), 200
        
    except Exception as e:
        print(f"Error creating complaint: {e}")
        return jsonify({"error": str(e)}), 500

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
                body=f"Your complaint '{complaint.get('category', 'Complaint')}' is now in progress.",
                citizen_id=citizen["id"] if citizen else None
            )
            if citizen:
                send_status_in_progress_email(citizen, complaint, authority.get("department", "Authority"))
                
        elif new_status == "resolved":
            create_notification(
                title="Complaint Resolved",
                body=f"Your complaint '{complaint.get('category', 'Complaint')}' has been resolved.",
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
                    body=f"Your complaint '{updated_complaint.get('category', 'Complaint')}' has been escalated.",
                    citizen_id=citizen["id"]
                )
            
            authority = _fetch_one("authorities", "id", updated_complaint.get("assigned_authority_id")) if updated_complaint.get("assigned_authority_id") else None
            if authority:
                send_threshold_authority_email(authority, updated_complaint)
                create_notification(
                    title="Critical Threshold Escalation",
                    body=f"Complaint '{updated_complaint.get('category', 'Complaint')}' reached the community threshold.",
                    authority_id=authority["id"]
                )
                    
        return jsonify({"success": True, "upvote_count": new_count})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@complaints_api.route("/<complaint_id>/assign", methods=["POST"])
def assign_authority(complaint_id):
    try:
        # Fetch the complaint
        complaint = _fetch_one("complaints", "id", complaint_id)
        if not complaint:
            return jsonify({"error": "Complaint not found"}), 404
            
        # Execute assignment logic
        result = assign_complaint_authority(complaint)
        
        return jsonify(result), 200 if result.get("assigned") else 400
        
    except Exception as e:
        print(f"Assignment error: {e}")
        return jsonify({"error": str(e)}), 500
