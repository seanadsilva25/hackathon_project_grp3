from typing import Optional, Dict, Any, Union
from app.notifications.service import create_notification


def notify_complaint_submitted(complaint: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Notifies the citizen when their complaint is submitted.

    :param complaint: Complaint record dictionary
    :return: Created notification record or None if citizen_id is missing
    """
    citizen_id = complaint.get("citizen_id")
    if not citizen_id:
        return None

    title_text = complaint.get("title", "Untitled Complaint")
    return create_notification(
        title="Complaint Submitted",
        body=f"Your complaint '{title_text}' has been successfully submitted.",
        citizen_id=citizen_id
    )


def notify_complaint_assigned(complaint: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Notifies the assigned authority when a complaint is assigned to them.

    :param complaint: Complaint record dictionary
    :return: Created notification record or None if assigned_authority_id is missing
    """
    authority_id = complaint.get("assigned_authority_id")
    if not authority_id:
        return None

    title_text = complaint.get("title", "Untitled Complaint")
    return create_notification(
        title="New Complaint Assigned",
        body=f"A new complaint '{title_text}' has been assigned to your jurisdiction.",
        authority_id=authority_id
    )


def notify_status_changed(
    complaint: Dict[str, Any],
    old_status: Optional[str],
    new_status: Optional[str]
) -> Optional[Dict[str, Any]]:
    """
    Notifies the citizen when a complaint status changes.
    Delegates to notify_complaint_resolved if new_status is 'resolved'.

    :param complaint: Complaint record dictionary
    :param old_status: Previous status string
    :param new_status: Updated status string
    :return: Created notification record or None
    """
    old_norm = (old_status or "").strip().lower()
    new_norm = (new_status or "").strip().lower()

    if old_norm == new_norm:
        return None

    if new_norm == "resolved":
        return notify_complaint_resolved(complaint)

    citizen_id = complaint.get("citizen_id")
    if not citizen_id:
        return None

    title_text = complaint.get("title", "Untitled Complaint")
    return create_notification(
        title="Complaint Status Updated",
        body=f"Your complaint '{title_text}' status has been updated to '{new_status}'.",
        citizen_id=citizen_id
    )


def notify_complaint_resolved(complaint: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Notifies the citizen when their complaint is marked as resolved.

    :param complaint: Complaint record dictionary
    :return: Created notification record or None if citizen_id is missing
    """
    citizen_id = complaint.get("citizen_id")
    if not citizen_id:
        return None

    title_text = complaint.get("title", "Untitled Complaint")
    return create_notification(
        title="Complaint Resolved",
        body=f"Your complaint '{title_text}' has been marked as resolved.",
        citizen_id=citizen_id
    )


def notify_threshold_reached(
    complaint: Dict[str, Any],
    previous_upvote_count: int
) -> Optional[Dict[str, Any]]:
    """
    Notifies the assigned authority when a complaint reaches or crosses the 10 upvote threshold.
    Triggers ONLY on threshold transition (previous_upvote_count < 10 and current_upvote_count >= 10).

    :param complaint: Complaint record dictionary
    :param previous_upvote_count: Upvote count prior to increment
    :return: Created notification record or None if criteria not met
    """
    current_upvote_count = complaint.get("upvote_count", 0) or 0

    if not (previous_upvote_count < 10 and current_upvote_count >= 10):
        return None

    authority_id = complaint.get("assigned_authority_id")
    if not authority_id:
        return None

    title_text = complaint.get("title", "Untitled Complaint")
    return create_notification(
        title="Complaint Upvote Threshold Reached",
        body=f"Complaint '{title_text}' has reached 10 upvotes and requires priority review.",
        authority_id=authority_id
    )


def notify_critical_complaint(
    complaint: Dict[str, Any],
    risk_score: float
) -> Optional[Dict[str, Any]]:
    """
    Notifies the assigned authority if a complaint has a high risk_score (>= 60).

    :param complaint: Complaint record dictionary
    :param risk_score: Calculated heatmap risk score
    :return: Created notification record or None if risk_score < 60 or authority_id is missing
    """
    if risk_score < 60:
        return None

    authority_id = complaint.get("assigned_authority_id")
    if not authority_id:
        return None

    title_text = complaint.get("title", "Untitled Complaint")
    return create_notification(
        title="Critical Complaint Alert",
        body=f"Complaint '{title_text}' has been classified as high risk (risk score: {risk_score}).",
        authority_id=authority_id
    )


def notify_complaint_reopened(
    complaint: Dict[str, Any],
    old_status: Optional[str],
    new_status: Optional[str]
) -> Optional[Dict[str, Optional[Dict[str, Any]]]]:
    """
    Notifies both citizen and assigned authority when a resolved complaint is reopened.
    Triggers ONLY when transition is 'resolved' -> 'reopened'.

    :param complaint: Complaint record dictionary
    :param old_status: Previous status string
    :param new_status: Updated status string
    :return: Dict containing citizen and authority notification records, or None if invalid transition
    """
    old_norm = (old_status or "").strip().lower()
    new_norm = (new_status or "").strip().lower()

    if not (old_norm == "resolved" and new_norm == "reopened"):
        return None

    citizen_id = complaint.get("citizen_id")
    authority_id = complaint.get("assigned_authority_id")

    if not citizen_id and not authority_id:
        return None

    title_text = complaint.get("title", "Untitled Complaint")
    body_text = f"Complaint '{title_text}' has been reopened for further investigation."

    citizen_notif = None
    if citizen_id:
        citizen_notif = create_notification(
            title="Complaint Reopened",
            body=body_text,
            citizen_id=citizen_id
        )

    authority_notif = None
    if authority_id:
        authority_notif = create_notification(
            title="Complaint Reopened",
            body=body_text,
            authority_id=authority_id
        )

    return {
        "citizen": citizen_notif,
        "authority": authority_notif
    }
