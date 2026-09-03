from typing import Optional, Dict, Any
from app.supabase_client import get_supabase_client


def create_notification(
    title: str,
    body: Optional[str] = None,
    citizen_id: Optional[str] = None,
    authority_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Creates and inserts a notification record into the Supabase 'notifications' table.

    A notification must be assigned to exactly one recipient: either a citizen or an authority.

    :param title: Title of the notification (required)
    :param body: Body content/message of the notification (optional)
    :param citizen_id: UUID of the target citizen (optional)
    :param authority_id: UUID of the target authority (optional)
    :return: Created notification record dictionary from Supabase
    :raises ValueError: If both citizen_id and authority_id are provided, or if neither is provided
    :raises RuntimeError: If the insert operation fails or returns no data
    """
    # Validation: Exactly one recipient ID must be provided
    if citizen_id and authority_id:
        raise ValueError("A notification cannot be assigned to both citizen_id and authority_id.")

    if not citizen_id and not authority_id:
        raise ValueError("Either citizen_id or authority_id must be provided.")

    supabase = get_supabase_client()

    payload = {
        "title": title,
        "body": body,
        "citizen_id": citizen_id,
        "authority_id": authority_id,
        "is_read": False
    }

    response = supabase.table("notifications").insert(payload).execute()

    if not response or not hasattr(response, "data") or not response.data:
        raise RuntimeError("Failed to create notification.")

    return response.data[0]
