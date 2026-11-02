"""
Entity Extractor Agent (Calendar Finder - Case 1).
Extracts meeting details (dates, times, participants, duration) and connects
to Outlook Calendar to identify 2-3 optimal open slots.
"""
import json
import logging
from typing import Dict, Any, List
from app.core.config import settings
from app.adapters.nexus_client import nexus_client
from app.adapters.outlook_calendar import outlook_calendar_client

logger = logging.getLogger(__name__)

MEETING_EXTRACTOR_SYSTEM_PROMPT = """You are an Enterprise Meeting Entity Extractor.
Extract meeting scheduling details from the provided email.
Identify:
1. "requested_dates": Dates or relative terms (e.g. "tomorrow afternoon", "next Monday", "Wednesday").
2. "preferred_time_range": Time range if mentioned (e.g. "afternoon", "2 PM", "morning", "between 3 and 5").
3. "duration_minutes": Duration in minutes (default 30 if unspecified).
4. "participants": List of email addresses or names mentioned.
5. "topic": Meeting topic or subject.
6. "is_ambiguous": true if the time or date is completely missing or critically vague (e.g. "let's meet sometime"), false if specific enough.

Output strictly valid JSON with this exact schema:
{
    "requested_dates": "string",
    "preferred_time_range": "string",
    "duration_minutes": 30,
    "participants": ["name or email"],
    "topic": "string",
    "is_ambiguous": false
}
"""

class EntityExtractorAgent:
    """Extracts meeting parameters and queries calendar for free/busy availability."""

    def __init__(self):
        self.model = settings.MODEL_EXTRACTOR

    def extract_and_find_slots(self, subject: str, body: str, sender: str) -> Dict[str, Any]:
        """
        Parses meeting entities and finds open slots using the corporate Calendar adapter.
        """
        prompt = f"Sender: {sender}\nSubject: {subject}\nBody:\n{body}"
        messages = [
            {"role": "system", "content": MEETING_EXTRACTOR_SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]

        try:
            resp_text = nexus_client.generate(
                messages=messages,
                model=self.model,
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            extracted = json.loads(resp_text)
        except Exception as e:
            logger.warning(f"Entity extraction failed: {e}. Using rule fallback.")
            extracted = {
                "requested_dates": "tomorrow afternoon",
                "preferred_time_range": "afternoon",
                "duration_minutes": 30,
                "participants": [sender],
                "topic": subject,
                "is_ambiguous": False
            }

        # Ensure sender is in participants
        participants = extracted.get("participants", [])
        if sender and sender not in participants:
            participants.append(sender)

        # Check calendar free/busy slots via Outlook Calendar adapter
        open_slots = outlook_calendar_client.get_free_busy_slots(
            start_date=extracted.get("requested_dates", "tomorrow"),
            duration_minutes=int(extracted.get("duration_minutes", 30))
        )

        return {
            "requested_dates": extracted.get("requested_dates", ""),
            "preferred_time_range": extracted.get("preferred_time_range", ""),
            "duration_minutes": extracted.get("duration_minutes", 30),
            "participants": participants,
            "topic": extracted.get("topic", subject),
            "is_ambiguous": extracted.get("is_ambiguous", False),
            "proposed_slots": open_slots,
            "stage": 1  # Stage 1: Hand draft to user for review
        }

entity_extractor_agent = EntityExtractorAgent()
