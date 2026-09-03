import requests
import json
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend', '.env'))

# Load Supabase config manually since we are running outside the app
# Use the same config from notification_service.py logic
SUPABASE_URL = "https://euvjrdlwhlqqeufyqwjx.supabase.co" # Need to fetch actual URL if missing, let's just import from service

import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app.services.notification_service import get_supabase_headers, get_supabase_url

def simulate():
    print("0. Preparing: Inserting a mock Authority into the DB...")
    # Insert an authority so the assignment engine can find a match
    mock_auth = {
        "id": "e4f8d9b1-7a6c-4b5d-9e3f-1a2b3c4d5e6f",
        "name": "Simulated BMC Official",
        "department": "BMC Civic Operations",
        "jurisdiction": "Mumbai North",
        "role": "authority"
    }
    auth_url = f"{get_supabase_url()}/rest/v1/authorities"
    auth_headers = get_supabase_headers()
    auth_headers["Prefer"] = "resolution=merge-duplicates"
    requests.post(auth_url, headers=auth_headers, json=mock_auth)
    
    print("1. Simulating Citizen submitting a complaint...")
    
    # 1. Insert new complaint into Supabase directly
    new_complaint = {
        "description": "Massive pothole near Main Gate causing traffic jams.",
        "category": "Road Damage",
        "jurisdiction": "Mumbai North",
        "status": "pending",
        "upvote_count": 1,
        # "citizen_id": would normally be here
    }
    
    url = f"{get_supabase_url()}/rest/v1/complaints"
    # Prefer return=representation to get the inserted object back
    headers = get_supabase_headers()
    headers["Prefer"] = "return=representation"
    
    resp = requests.post(url, headers=headers, json=new_complaint)
    
    if resp.status_code not in [200, 201, 204]:
        print(f"[ERROR] Failed to insert complaint: {resp.status_code} {resp.text}")
        return
        
    complaint_data = resp.json()[0] if isinstance(resp.json(), list) else resp.json()
    complaint_id = complaint_data["id"]
    print(f"[SUCCESS] Complaint successfully inserted into Supabase! ID: {complaint_id}")
    
    print("\n2. Simulating Frontend calling the Assignment Engine...")
    
    # 2. Call our local Flask API to trigger assignment
    api_url = f"http://127.0.0.1:5000/api/complaints/{complaint_id}/assign"
    assign_resp = requests.post(api_url)
    
    if assign_resp.status_code == 200:
        result = assign_resp.json()
        print(f"[SUCCESS] Assignment Engine Success!")
        print(f"   Routed to Department: {result.get('department')}")
        print(f"   Assigned to Authority: {result.get('authority_name')} ({result.get('authority_id')})")
        print("\n[INFO] Check your Authority Dashboard! You should see the new notification and the complaint in 'My Assignments'!")
    else:
        print(f"[ERROR] Assignment Engine Failed! Status: {assign_resp.status_code}, Body: {assign_resp.text}")

if __name__ == "__main__":
    simulate()
