import os
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# TODO: Connect an actual email provider (e.g. SendGrid, Resend, or AWS SES)
# Currently, this service logs the email payloads to the console to fulfill the
# backend notification architecture without failing due to missing credentials.

def send_email(to_email, subject, body):
    """
    Mock email sending function.
    """
    logger.info("========== EMAIL DISPATCH ==========")
    logger.info(f"TO: {to_email}")
    logger.info(f"SUBJECT: {subject}")
    logger.info("BODY:")
    logger.info(body)
    logger.info("====================================")
    
    # Returning True indicates successful processing by the mock provider
    return True

def send_threshold_authority_email(authority, complaint):
    subject = "UniSafe - Complaint Threshold Reached"
    body = f"""Hello {authority.get('name', 'Authority')},

A complaint in your jurisdiction has reached the UniSafe community reporting threshold and requires attention.

Complaint:
{complaint.get('title', 'Unknown')}

Category:
{complaint.get('category', 'Unknown')}

Location:
{complaint.get('address', 'Unknown')}

Community Support:
{complaint.get('upvote_count', 0)}

Priority:
Escalated

Multiple citizens have reported or supported this issue.

Please review the complaint in the UniSafe Authority Dashboard.

UniSafe Team
"""
    # Assuming authority has an email in a future schema.
    # Currently Authorities don't have email column natively, fallback to a dummy
    to_email = authority.get('email', 'authority_demo@unisafe.local')
    return send_email(to_email, subject, body)

def send_threshold_citizen_email(citizen, complaint):
    subject = "UniSafe - Your Complaint Has Reached the Community Threshold"
    body = f"""Hello {citizen.get('name', 'Citizen')},

Your complaint:
"{complaint.get('title', 'Unknown')}"

has received significant support from the community.

Community Support:
{complaint.get('upvote_count', 0)}

Status:
Escalated

The issue has been flagged for increased attention from the responsible authority.
You can track its progress from your UniSafe dashboard.

UniSafe Team
"""
    to_email = citizen.get('email', 'citizen_demo@unisafe.local')
    return send_email(to_email, subject, body)

def send_complaint_assigned_email(authority, complaint):
    subject = "UniSafe - New Complaint Assigned"
    body = f"""Hello {authority.get('name', 'Authority')},

A new complaint has been assigned to your department/jurisdiction.

Complaint:
{complaint.get('title', 'Unknown')}

Category:
{complaint.get('category', 'Unknown')}

Location:
{complaint.get('address', 'Unknown')}

Submitted:
{complaint.get('created_at', 'Unknown')}

Please review the complaint and update its status.

UniSafe Team
"""
    to_email = authority.get('email', 'authority_demo@unisafe.local')
    return send_email(to_email, subject, body)

def send_status_in_progress_email(citizen, complaint, department):
    subject = "UniSafe - Your Complaint Is Now In Progress"
    body = f"""Hello {citizen.get('name', 'Citizen')},

Your complaint "{complaint.get('title', 'Unknown')}" is now being reviewed by:
{department}

Status:
In Progress

You can track the progress from your UniSafe dashboard.
"""
    to_email = citizen.get('email', 'citizen_demo@unisafe.local')
    return send_email(to_email, subject, body)

def send_resolved_email(citizen, complaint, department):
    subject = "UniSafe - Your Complaint Has Been Resolved"
    body = f"""Hello {citizen.get('name', 'Citizen')},

Your complaint "{complaint.get('title', 'Unknown')}" has been marked as Resolved.

Resolved By:
{department}

Please open UniSafe to review the resolution and verify whether the issue has been resolved satisfactorily.

UniSafe Team
"""
    to_email = citizen.get('email', 'citizen_demo@unisafe.local')
    return send_email(to_email, subject, body)
