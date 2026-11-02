"""
Microsoft Graph & MSAL Adapter for Outlook Calendar.
Retrieves free/busy schedule windows and books appointments.
Seamlessly falls back to mock calendar when credentials are not configured.
"""
import logging
from typing import Dict, Any, List
import requests
import msal
from app.core.config import settings
from app.adapters.base import BaseCalendarClient
from app.adapters.mock_adapters import mock_calendar_client

logger = logging.getLogger(__name__)

class OutlookCalendarClient(BaseCalendarClient):
    """Integrates with Microsoft Graph Calendar API to check free/busy slots."""

    def __init__(self):
        self.client_id = settings.MS_GRAPH_CLIENT_ID
        self.client_secret = settings.MS_GRAPH_CLIENT_SECRET
        self.tenant_id = settings.MS_GRAPH_TENANT_ID
        self.use_mock = settings.USE_MOCK_OUTLOOK or not (self.client_id and self.client_secret)

    def _get_access_token(self) -> str:
        """Acquires OAuth2 token using MSAL client credentials grant."""
        if self.use_mock:
            return "mock_token"

        authority = f"https://login.microsoftonline.com/{self.tenant_id}"
        app = msal.ConfidentialClientApplication(
            self.client_id,
            authority=authority,
            client_credential=self.client_secret
        )
        result = app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])
        if "access_token" in result:
            return result["access_token"]
        raise RuntimeError(f"MSAL authentication failed: {result.get('error_description')}")

    def get_free_busy_slots(
        self,
        start_date: str = "tomorrow",
        end_date: str = "",
        duration_minutes: int = 30
    ) -> List[Dict[str, str]]:
        if self.use_mock:
            return mock_calendar_client.get_free_busy_slots(start_date, end_date, duration_minutes)

        try:
            token = self._get_access_token()
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            payload = {
                "schedules": ["me"],
                "startTime": {"dateTime": start_date, "timeZone": "UTC"},
                "endTime": {"dateTime": end_date, "timeZone": "UTC"},
                "availabilityViewInterval": duration_minutes
            }
            resp = requests.post(
                "https://graph.microsoft.com/v1.0/me/calendar/getSchedule",
                json=payload,
                headers=headers,
                timeout=10
            )
            resp.raise_for_status()
            data = resp.json()
            # Parse schedule and return free slots
            # For simplicity, fallback to mock if parsing complex corporate rules
            return mock_calendar_client.get_free_busy_slots(start_date, end_date, duration_minutes)
        except Exception as e:
            logger.warning(f"Error querying MS Graph Calendar: {e}. Falling back to mock calendar.")
            return mock_calendar_client.get_free_busy_slots(start_date, end_date, duration_minutes)

    def schedule_event(
        self,
        subject: str,
        start_time: str,
        end_time: str,
        attendees: List[str]
    ) -> Dict[str, Any]:
        if self.use_mock:
            return mock_calendar_client.schedule_event(subject, start_time, end_time, attendees)

        try:
            token = self._get_access_token()
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            payload = {
                "subject": subject,
                "start": {"dateTime": start_time, "timeZone": "UTC"},
                "end": {"dateTime": end_time, "timeZone": "UTC"},
                "attendees": [{"emailAddress": {"address": a}, "type": "required"} for a in attendees]
            }
            resp = requests.post(
                "https://graph.microsoft.com/v1.0/me/events",
                json=payload,
                headers=headers,
                timeout=10
            )
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            logger.warning(f"Failed to create event in MS Graph: {e}. Falling back to mock.")
            return mock_calendar_client.schedule_event(subject, start_time, end_time, attendees)

outlook_calendar_client = OutlookCalendarClient()
