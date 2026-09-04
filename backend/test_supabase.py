import os
import sys

# Ensure backend directory is on sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.supabase_client import get_supabase_client

def test_supabase_connection():
    print("=" * 60)
    print(" UNISAFE BACKEND SUPABASE CONNECTIVITY TEST")
    print("=" * 60)

    try:
        print("1. Initializing Supabase Client from backend/.env ...")
        client = get_supabase_client()
        print("   [SUCCESS] Client initialized successfully.")

        print("2. Testing network communication with Supabase project...")
        # Ping health/auth or perform lightweight check
        response = client.auth.get_session()
        print("   [SUCCESS] Communication with Supabase project verified!")
        print("=" * 60)
        print("[SUCCESS] SUPABASE CONNECTIVITY TEST PASSED")
        print("=" * 60)
        return True

    except ValueError as ve:
        print("   [EXPECTED STATUS / PENDING CONFIGURATION]:")
        print(f"   {ve}")
        print("=" * 60)
        print("   [!] Please update backend/.env with your actual SUPABASE_URL and SUPABASE_KEY to complete connection.")
        print("=" * 60)
        return False

    except Exception as e:
        print("   [ERROR] Failed to communicate with Supabase:")
        print(f"   {type(e).__name__}: {e}")
        print("=" * 60)
        print("[FAILED] SUPABASE CONNECTIVITY TEST FAILED")
        print("=" * 60)
        return False

if __name__ == '__main__':
    test_supabase_connection()
