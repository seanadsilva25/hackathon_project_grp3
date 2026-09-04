import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Explicitly resolve path to backend/.env
base_backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(base_backend_dir, '.env')
load_dotenv(dotenv_path=env_path)

_supabase_client = None

def get_supabase_client() -> Client:
    """
    Initializes and returns a singleton Supabase client using environment variables.
    
    :return: Client instance from supabase-py
    :raises ValueError: If SUPABASE_URL or SUPABASE_KEY are missing or unpopulated placeholders
    """
    global _supabase_client

    if _supabase_client is not None:
        return _supabase_client

    supabase_url = os.getenv("SUPABASE_URL", "").strip()
    supabase_key = os.getenv("SUPABASE_KEY", "").strip()

    if not supabase_url or "your_supabase" in supabase_url.lower():
        raise ValueError("SUPABASE_URL environment variable is missing or unconfigured in backend/.env")

    if not supabase_key or "your_supabase" in supabase_key.lower():
        raise ValueError("SUPABASE_KEY environment variable is missing or unconfigured in backend/.env")

    _supabase_client = create_client(supabase_url, supabase_key)
    return _supabase_client
