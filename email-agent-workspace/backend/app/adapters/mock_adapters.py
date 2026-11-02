"""
Mock / Disconnected Adapters for local enterprise testing.
Simulates Outlook Inbox and Calendar free/busy slots with realistic corporate schedules.
"""
from datetime import datetime, timedelta
from typing import Dict, Any, List
from app.adapters.base import BaseEmailClient, BaseCalendarClient

class MockEmailClient(BaseEmailClient):
    """Simulated corporate inbox for disconnected or sandbox testing."""

    def __init__(self):
        self._sent_emails: List[Dict[str, Any]] = []

    def fetch_unread_emails(self, limit: int = 10) -> List[Dict[str, Any]]:
        # Returns simulated corporate inbox emails
        return [
            {
                "id": "mock_msg_001",
                "subject": "Q3 Budget Review and Next Steps",
                "sender": "sarah.connor@nexus.ai",
                "recipient": "user@nexus.ai",
                "body": "Hi team, please send the revised budget deck by Friday 5 PM. Also let's meet tomorrow afternoon at 2 PM to sync.",
                "received_at": datetime.utcnow().isoformat()
            }
        ]

    def send_email(self, to: str, subject: str, body: str) -> bool:
        self._sent_emails.append({
            "to": to,
            "subject": subject,
            "body": body,
            "sent_at": datetime.utcnow().isoformat()
        })
        return True


class MockCalendarClient(BaseCalendarClient):
    """Simulated corporate calendar mapping realistic open slots with zero time overlap."""

    def __init__(self):
        self._booked_events: List[Dict[str, Any]] = []

    def _get_confirmed_booked_times(self) -> set:
        """Queries MSSQL for confirmed slots to prevent scheduling collision."""
        booked = set()
        try:
            from app.core.database import SessionLocal
            from app.db.models import MeetingProposalModel
            import json

            with SessionLocal() as db:
                confirmed = db.query(MeetingProposalModel).filter(
                    (MeetingProposalModel.stage == 2) | (MeetingProposalModel.status == "confirmed")
                ).all()
                for p in confirmed:
                    if p.proposed_slots_json:
                        try:
                            slots = json.loads(p.proposed_slots_json)
                            for s in slots:
                                if isinstance(s, dict) and "start_time" in s:
                                    booked.add(s["start_time"])
                        except Exception:
                            pass
        except Exception:
            pass

        for evt in self._booked_events:
            if "start_time" in evt:
                booked.add(evt["start_time"])

        return booked

    def get_free_busy_slots(
        self,
        start_date: str = "tomorrow",
        end_date: str = "",
        duration_minutes: int = 30
    ) -> List[Dict[str, str]]:
        now = datetime.now()
        tomorrow = now + timedelta(days=1)
        booked_times = self._get_confirmed_booked_times()

        # Corporate business candidate slots (2 PM through 5:30 PM, then morning)
        candidate_hours = [
            (14, 0),
            (14, 30),
            (15, 0),
            (15, 30),
            (16, 0),
            (16, 30),
            (17, 0),
            (17, 30),
            (10, 0),
            (10, 30),
            (11, 0),
            (11, 30),
        ]

        free_slots: List[Dict[str, str]] = []
        for hour, minute in candidate_hours:
            slot_start = tomorrow.replace(hour=hour, minute=minute, second=0, microsecond=0)
            start_str = slot_start.strftime("%Y-%m-%d %I:%M %p")

            if start_str in booked_times:
                continue

            slot_end = slot_start + timedelta(minutes=duration_minutes)
            free_slots.append({
                "start_time": start_str,
                "end_time": slot_end.strftime("%I:%M %p"),
                "display": f"{slot_start.strftime('%A, %b %d')} from {slot_start.strftime('%I:%M %p')} - {slot_end.strftime('%I:%M %p')}"
            })

            if len(free_slots) == 3:
                break

        if not free_slots:
            slot1_start = tomorrow.replace(hour=18, minute=0, second=0, microsecond=0)
            slot1_end = slot1_start + timedelta(minutes=duration_minutes)
            free_slots.append({
                "start_time": slot1_start.strftime("%Y-%m-%d %I:%M %p"),
                "end_time": slot1_end.strftime("%I:%M %p"),
                "display": f"{slot1_start.strftime('%A, %b %d')} from {slot1_start.strftime('%I:%M %p')} - {slot1_end.strftime('%I:%M %p')}"
            })

        return free_slots

    def schedule_event(
        self,
        subject: str,
        start_time: str,
        end_time: str,
        attendees: List[str]
    ) -> Dict[str, Any]:
        event = {
            "id": f"evt_{int(datetime.utcnow().timestamp())}",
            "subject": subject,
            "start_time": start_time,
            "end_time": end_time,
            "attendees": attendees,
            "status": "Confirmed",
            "provider": "MockCorporateCalendar"
        }
        self._booked_events.append(event)
        return event

mock_email_client = MockEmailClient()
mock_calendar_client = MockCalendarClient()
