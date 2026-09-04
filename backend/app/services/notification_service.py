import os
import requests
from dotenv import load_dotenv

env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'frontend', '.env'))
load_dotenv(env_path)

HACKATHON_URL = "https://wcksscwgeoysnqiluxoh.supabase.co"
HACKATHON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Indja3NzY3dnZW95c25xaWx1eG9oIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODUyMDQ3NzAsImV4cCI6MjEwMDc4MDc3MH0.pkS0lo2a4GGS-wDtwFzQwKMeVF-It6sPMrgooPyU-Do"

def get_supabase_headers():
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("VITE_SUPABASE_ANON_KEY") or HACKATHON_KEY
    return {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }

def get_supabase_url():
    url = os.environ.get("SUPABASE_URL") or os.environ.get("VITE_SUPABASE_URL") or HACKATHON_URL
    return url

def log_complaint_action(complaint_id, authority_id, action, message):
    url = f"{get_supabase_url()}/rest/v1/complaint_logs"
    data = {
        "complaint_id": complaint_id,
        "authority_id": authority_id,
        "action": action,
        "message": message
    }
    try:
        requests.post(url, headers=get_supabase_headers(), json=data)
    except Exception as e:
        print(f"Failed to log complaint action: {e}")

def create_notification(title, body, citizen_id=None, authority_id=None):
    url = f"{get_supabase_url()}/rest/v1/notifications"
    data = {
        "title": title,
        "body": body,
        "is_read": False
    }
    if citizen_id:
        data["citizen_id"] = citizen_id
    if authority_id:
        data["authority_id"] = authority_id
        
    try:
        requests.post(url, headers=get_supabase_headers(), json=data)
    except Exception as e:
        print(f"Failed to create notification: {e}")
