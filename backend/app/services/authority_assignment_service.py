import requests
from app.services.notification_service import get_supabase_headers, get_supabase_url, log_complaint_action, create_notification

# Exact category -> department mapping as requested
POLICE_CATEGORIES = [
    "Theft", "Assault", "Suspicious Activity", "Traffic", 
    "Women Safety", "Illegal Parking", "Robbery", "Harassment", 
    "Eve-Teasing", "Violence", "Child Safety", "Stray Animal"
]

BMC_CATEGORIES = [
    "Road Damage", "Garbage", "Waste", "Streetlight", "Street Lights",
    "Drainage", "Water Supply", "Encroachment", "Public Sanitation",
    "Potholes", "Water Logging", "Prolonged Road Work",
    "Public Washroom", "Green Area", "Landscape", "Plants",
    "Pest", "Insect", "Vegetation", "Tree", "Manholes", "Footpath",
    "Fire Hazard", "Electrical Hazard", "Exposed Wires"
]

def determine_department(category):
    if not category:
        return None
        
    # Handle exact matches or basic substring matches safely
    category_lower = category.lower()
    
    if any(p.lower() in category_lower for p in POLICE_CATEGORIES):
        return "Police"
    elif any(b.lower() in category_lower for b in BMC_CATEGORIES):
        return "BMC"
        
    return None

def fetch_oldest_matching_authority(department, jurisdiction):
    """
    Finds a matching authority based on department and jurisdiction.
    Falls back to deterministic 'oldest matching' if multiple exist.
    """
    if not department or not jurisdiction:
        return None
        
    url = f"{get_supabase_url()}/rest/v1/authorities"
    params = {
        "department": f"eq.{department}",
        "jurisdiction": f"eq.{jurisdiction}",
        "order": "created_at.asc",
        "limit": 1,
        "select": "*"
    }
    try:
        resp = requests.get(url, headers=get_supabase_headers(), params=params)
        if resp.status_code == 200 and len(resp.json()) > 0:
            return resp.json()[0]
    except Exception as e:
        print(f"Error fetching matching authority: {e}")
    
    return None

def update_complaint_assigned_authority(complaint_id, authority_id):
    url = f"{get_supabase_url()}/rest/v1/complaints?id=eq.{complaint_id}"
    payload = {"assigned_authority_id": authority_id}
    try:
        resp = requests.patch(url, headers=get_supabase_headers(), json=payload)
        if resp.status_code in [200, 204]:
            return True
    except Exception as e:
        print(f"Error updating complaint assigned authority: {e}")
    return False

def assign_complaint_authority(complaint):
    """
    Executes the automated assignment workflow for a given complaint.
    Expects `complaint` as a dictionary containing 'id', 'category', 'jurisdiction', 'title'.
    """
    complaint_id = complaint.get("id")
    category = complaint.get("category")
    jurisdiction = complaint.get("jurisdiction")
    
    if not complaint_id or not category or not jurisdiction:
        return {"assigned": False, "reason": "Missing required complaint fields (id, category, jurisdiction)"}
        
    department = determine_department(category)
    if not department:
        return {"assigned": False, "reason": f"Category '{category}' does not map to a supported department"}
        
    authority = fetch_oldest_matching_authority(department, jurisdiction)
    
    if not authority:
        return {"assigned": False, "reason": f"No authority found for department '{department}' and jurisdiction '{jurisdiction}'"}
        
    authority_id = authority.get("id")
    
    success = update_complaint_assigned_authority(complaint_id, authority_id)
    if not success:
        return {"assigned": False, "reason": "Failed to update complaint in database"}
        
    # Create logs and notifications
    log_complaint_action(
        complaint_id=complaint_id,
        authority_id=authority_id,
        action="ASSIGNED",
        message=f"Complaint automatically assigned to {authority.get('name', 'Authority')}"
    )
    
    create_notification(
        title="New complaint assigned",
        body=f"'{complaint.get('title', 'A new complaint')}' has been assigned to your jurisdiction.",
        authority_id=authority_id
    )
    
    # Notify if it's a high risk category
    high_risk_categories = ["Assault", "Violence", "Robbery", "Fire Hazard", "Electrical Hazard", "Exposed Wires"]
    if any(h.lower() in (category or '').lower() for h in high_risk_categories):
        create_notification(
            title="Critical/High-Risk Complaint",
            body=f"URGENT: A high-risk complaint '{complaint.get('title', 'Complaint')}' requires immediate attention.",
            authority_id=authority_id
        )
    
    return {
        "assigned": True,
        "department": department,
        "authority_id": authority_id,
        "authority_name": authority.get("name")
    }
