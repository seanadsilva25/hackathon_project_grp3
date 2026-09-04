import sys
import os
import unittest
from unittest.mock import patch, MagicMock

# Ensure backend directory is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.notifications.events import (
    notify_complaint_submitted,
    notify_complaint_assigned,
    notify_status_changed,
    notify_complaint_resolved,
    notify_threshold_reached,
    notify_critical_complaint,
    notify_complaint_reopened,
)


class TestNotificationEvents(unittest.TestCase):

    def setUp(self):
        self.sample_complaint = {
            "title": "Water Leakage Issue",
            "citizen_id": "c-uuid-1111",
            "assigned_authority_id": "a-uuid-2222",
            "upvote_count": 10,
        }

    # -------------------------------------------------------------------------
    # 1. notify_complaint_submitted
    # -------------------------------------------------------------------------
    @patch("app.notifications.events.create_notification")
    def test_notify_complaint_submitted_valid(self, mock_create):
        mock_create.return_value = {"id": "n-1", "title": "Complaint Submitted"}
        
        result = notify_complaint_submitted(self.sample_complaint)
        
        mock_create.assert_called_once_with(
            title="Complaint Submitted",
            body="Your complaint 'Water Leakage Issue' has been successfully submitted.",
            citizen_id="c-uuid-1111"
        )
        self.assertEqual(result, {"id": "n-1", "title": "Complaint Submitted"})

    @patch("app.notifications.events.create_notification")
    def test_notify_complaint_submitted_missing_citizen_id(self, mock_create):
        complaint = {"title": "No Citizen"}
        result = notify_complaint_submitted(complaint)
        
        mock_create.assert_not_called()
        self.assertIsNone(result)

    # -------------------------------------------------------------------------
    # 2. notify_complaint_assigned
    # -------------------------------------------------------------------------
    @patch("app.notifications.events.create_notification")
    def test_notify_complaint_assigned_valid(self, mock_create):
        mock_create.return_value = {"id": "n-2", "title": "New Complaint Assigned"}
        
        result = notify_complaint_assigned(self.sample_complaint)
        
        mock_create.assert_called_once_with(
            title="New Complaint Assigned",
            body="A new complaint 'Water Leakage Issue' has been assigned to your jurisdiction.",
            authority_id="a-uuid-2222"
        )
        self.assertEqual(result, {"id": "n-2", "title": "New Complaint Assigned"})

    @patch("app.notifications.events.create_notification")
    def test_notify_complaint_assigned_missing_authority_id(self, mock_create):
        complaint = {"title": "Unassigned Complaint"}
        result = notify_complaint_assigned(complaint)
        
        mock_create.assert_not_called()
        self.assertIsNone(result)

    # -------------------------------------------------------------------------
    # 3. notify_status_changed
    # -------------------------------------------------------------------------
    @patch("app.notifications.events.create_notification")
    def test_notify_status_changed_open_to_in_progress(self, mock_create):
        mock_create.return_value = {"id": "n-3", "title": "Complaint Status Updated"}
        
        result = notify_status_changed(self.sample_complaint, "open", "in_progress")
        
        mock_create.assert_called_once_with(
            title="Complaint Status Updated",
            body="Your complaint 'Water Leakage Issue' status has been updated to 'in_progress'.",
            citizen_id="c-uuid-1111"
        )
        self.assertEqual(result, {"id": "n-3", "title": "Complaint Status Updated"})

    @patch("app.notifications.events.create_notification")
    def test_notify_status_changed_same_status(self, mock_create):
        result = notify_status_changed(self.sample_complaint, "open", "OPEN")
        
        mock_create.assert_not_called()
        self.assertIsNone(result)

    @patch("app.notifications.events.create_notification")
    def test_notify_status_changed_to_resolved_delegates(self, mock_create):
        mock_create.return_value = {"id": "n-4", "title": "Complaint Resolved"}
        
        result = notify_status_changed(self.sample_complaint, "in_progress", "resolved")
        
        mock_create.assert_called_once_with(
            title="Complaint Resolved",
            body="Your complaint 'Water Leakage Issue' has been marked as resolved.",
            citizen_id="c-uuid-1111"
        )
        self.assertEqual(result, {"id": "n-4", "title": "Complaint Resolved"})

    # -------------------------------------------------------------------------
    # 4. notify_complaint_resolved
    # -------------------------------------------------------------------------
    @patch("app.notifications.events.create_notification")
    def test_notify_complaint_resolved_valid(self, mock_create):
        mock_create.return_value = {"id": "n-5", "title": "Complaint Resolved"}
        
        result = notify_complaint_resolved(self.sample_complaint)
        
        mock_create.assert_called_once_with(
            title="Complaint Resolved",
            body="Your complaint 'Water Leakage Issue' has been marked as resolved.",
            citizen_id="c-uuid-1111"
        )
        self.assertEqual(result, {"id": "n-5", "title": "Complaint Resolved"})

    @patch("app.notifications.events.create_notification")
    def test_notify_complaint_resolved_missing_citizen_id(self, mock_create):
        complaint = {"title": "No Citizen"}
        result = notify_complaint_resolved(complaint)
        
        mock_create.assert_not_called()
        self.assertIsNone(result)

    # -------------------------------------------------------------------------
    # 5. notify_threshold_reached
    # -------------------------------------------------------------------------
    @patch("app.notifications.events.create_notification")
    def test_notify_threshold_reached_9_to_10(self, mock_create):
        mock_create.return_value = {"id": "n-6", "title": "Complaint Upvote Threshold Reached"}
        complaint = {**self.sample_complaint, "upvote_count": 10}
        
        result = notify_threshold_reached(complaint, previous_upvote_count=9)
        
        mock_create.assert_called_once_with(
            title="Complaint Upvote Threshold Reached",
            body="Complaint 'Water Leakage Issue' has reached 10 upvotes and requires priority review.",
            authority_id="a-uuid-2222"
        )
        self.assertEqual(result, {"id": "n-6", "title": "Complaint Upvote Threshold Reached"})

    @patch("app.notifications.events.create_notification")
    def test_notify_threshold_reached_9_to_11(self, mock_create):
        mock_create.return_value = {"id": "n-7", "title": "Complaint Upvote Threshold Reached"}
        complaint = {**self.sample_complaint, "upvote_count": 11}
        
        result = notify_threshold_reached(complaint, previous_upvote_count=9)
        
        mock_create.assert_called_once()
        self.assertIsNotNone(result)

    @patch("app.notifications.events.create_notification")
    def test_notify_threshold_reached_10_to_11(self, mock_create):
        complaint = {**self.sample_complaint, "upvote_count": 11}
        
        result = notify_threshold_reached(complaint, previous_upvote_count=10)
        
        mock_create.assert_not_called()
        self.assertIsNone(result)

    @patch("app.notifications.events.create_notification")
    def test_notify_threshold_reached_10_to_10(self, mock_create):
        complaint = {**self.sample_complaint, "upvote_count": 10}
        
        result = notify_threshold_reached(complaint, previous_upvote_count=10)
        
        mock_create.assert_not_called()
        self.assertIsNone(result)

    # -------------------------------------------------------------------------
    # 6. notify_critical_complaint
    # -------------------------------------------------------------------------
    @patch("app.notifications.events.create_notification")
    def test_notify_critical_complaint_score_60(self, mock_create):
        mock_create.return_value = {"id": "n-8", "title": "Critical Complaint Alert"}
        
        result = notify_critical_complaint(self.sample_complaint, risk_score=60)
        
        mock_create.assert_called_once_with(
            title="Critical Complaint Alert",
            body="Complaint 'Water Leakage Issue' has been classified as high risk (risk score: 60).",
            authority_id="a-uuid-2222"
        )
        self.assertEqual(result, {"id": "n-8", "title": "Critical Complaint Alert"})

    @patch("app.notifications.events.create_notification")
    def test_notify_critical_complaint_score_75(self, mock_create):
        mock_create.return_value = {"id": "n-9", "title": "Critical Complaint Alert"}
        
        result = notify_critical_complaint(self.sample_complaint, risk_score=75)
        
        mock_create.assert_called_once()
        self.assertIsNotNone(result)

    @patch("app.notifications.events.create_notification")
    def test_notify_critical_complaint_score_59(self, mock_create):
        result = notify_critical_complaint(self.sample_complaint, risk_score=59)
        
        mock_create.assert_not_called()
        self.assertIsNone(result)

    @patch("app.notifications.events.create_notification")
    def test_notify_critical_complaint_missing_authority(self, mock_create):
        complaint = {"title": "Critical Issue", "citizen_id": "c-1"}
        result = notify_critical_complaint(complaint, risk_score=80)
        
        mock_create.assert_not_called()
        self.assertIsNone(result)

    # -------------------------------------------------------------------------
    # 7. notify_complaint_reopened
    # -------------------------------------------------------------------------
    @patch("app.notifications.events.create_notification")
    def test_notify_complaint_reopened_both_recipients(self, mock_create):
        mock_create.side_effect = [
            {"id": "n-c", "title": "Complaint Reopened", "recipient": "citizen"},
            {"id": "n-a", "title": "Complaint Reopened", "recipient": "authority"},
        ]
        
        result = notify_complaint_reopened(self.sample_complaint, "resolved", "reopened")
        
        self.assertEqual(mock_create.call_count, 2)
        self.assertEqual(result, {
            "citizen": {"id": "n-c", "title": "Complaint Reopened", "recipient": "citizen"},
            "authority": {"id": "n-a", "title": "Complaint Reopened", "recipient": "authority"}
        })

    @patch("app.notifications.events.create_notification")
    def test_notify_complaint_reopened_only_citizen(self, mock_create):
        mock_create.return_value = {"id": "n-c", "title": "Complaint Reopened"}
        complaint = {"title": "Water Leakage Issue", "citizen_id": "c-uuid-1111"}
        
        result = notify_complaint_reopened(complaint, "resolved", "reopened")
        
        mock_create.assert_called_once_with(
            title="Complaint Reopened",
            body="Complaint 'Water Leakage Issue' has been reopened for further investigation.",
            citizen_id="c-uuid-1111"
        )
        self.assertEqual(result, {
            "citizen": {"id": "n-c", "title": "Complaint Reopened"},
            "authority": None
        })

    @patch("app.notifications.events.create_notification")
    def test_notify_complaint_reopened_only_authority(self, mock_create):
        mock_create.return_value = {"id": "n-a", "title": "Complaint Reopened"}
        complaint = {"title": "Water Leakage Issue", "assigned_authority_id": "a-uuid-2222"}
        
        result = notify_complaint_reopened(complaint, "resolved", "reopened")
        
        mock_create.assert_called_once_with(
            title="Complaint Reopened",
            body="Complaint 'Water Leakage Issue' has been reopened for further investigation.",
            authority_id="a-uuid-2222"
        )
        self.assertEqual(result, {
            "citizen": None,
            "authority": {"id": "n-a", "title": "Complaint Reopened"}
        })

    @patch("app.notifications.events.create_notification")
    def test_notify_complaint_reopened_invalid_transition(self, mock_create):
        result = notify_complaint_reopened(self.sample_complaint, "open", "reopened")
        
        mock_create.assert_not_called()
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main(verbosity=2)
