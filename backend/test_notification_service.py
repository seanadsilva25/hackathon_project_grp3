import sys
import os

# Ensure backend directory is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.supabase_client import get_supabase_client
from app.notifications.service import create_notification


def run_integration_test():
    print("=== UniSafe Notification Service Integration Test ===")

    supabase = get_supabase_client()

    # Step 1: Fetch an existing citizen from Supabase 'citizens' table
    print("Fetching an existing citizen from Supabase...")
    citizens_res = supabase.table("citizens").select("id").limit(1).execute()

    if not citizens_res or not hasattr(citizens_res, "data") or not citizens_res.data:
        raise RuntimeError("No citizens found in the Supabase 'citizens' table. Cannot test notification creation.")

    real_citizen_id = citizens_res.data[0]["id"]
    print(f"Fetched existing citizen_id: {real_citizen_id}")

    # Step 2: Create a notification for the citizen
    print("Calling create_notification()...")
    created_notification = create_notification(
        title="Test Notification",
        body="This is a test notification from the UniSafe backend.",
        citizen_id=real_citizen_id,
        authority_id=None
    )

    print("\nReturned Notification Record:")
    print(created_notification)

    # Step 3: Verifications
    print("\nVerifying created notification record attributes...")
    assert "id" in created_notification and created_notification["id"], "Record must contain a valid ID"
    assert created_notification["citizen_id"] == real_citizen_id, f"Expected citizen_id {real_citizen_id}, got {created_notification.get('citizen_id')}"
    assert created_notification["is_read"] is False, f"Expected is_read False, got {created_notification.get('is_read')}"
    assert created_notification["title"] == "Test Notification", "Title mismatch"
    assert created_notification["body"] == "This is a test notification from the UniSafe backend.", "Body mismatch"

    print("\n[SUCCESS] All assertions passed successfully!")
    print(f"Notification ID created: {created_notification['id']}")
    print("The notification record has been persisted in Supabase for manual inspection.")


if __name__ == "__main__":
    run_integration_test()
