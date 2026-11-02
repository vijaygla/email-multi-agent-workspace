"""
Supervisor Agent (The Double-Checker - Case 5).
Audits extracted parameters, evaluates uncertainty or missing information,
pauses workflow, and constructs targeted clarifying questions with selectable choices.
"""
import json
import logging
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.core.config import settings
from app.db.models import ClarificationRequestModel
from app.adapters.nexus_client import nexus_client

logger = logging.getLogger(__name__)

SUPERVISOR_SYSTEM_PROMPT = """You are the Quality & Completeness Supervisor Agent for Nexus AI.
Analyze the email and the preliminary extracted data (meeting slots or tasks) to determine if critical details are missing, ambiguous, or contradictory.

Examples of genuinely ambiguous data:
- Date or time is completely missing or open-ended (e.g. "Let's connect sometime", "whenever you are free").
- Task requested with no deliverable details (e.g. "Please handle that thing we discussed").

If the request provides actionable details, day/time preferences, or clear task deadlines:
{
    "needs_clarification": false,
    "missing_fields": [],
    "reasoning": "Sufficient detail present."
}

If the request is ambiguous or missing critical information:
{
    "needs_clarification": true,
    "missing_fields": ["time_zone" | "due_date" | "owner" | "meeting_duration" | "topic"],
    "question": "A polite, concise clarification question to the sender",
    "options": ["Choice 1", "Choice 2", "Choice 3"],
    "reasoning": "Explanation of why clarification is needed"
}

Output strictly valid JSON with the schema above.
"""

# use for the double checker ----
class SupervisorAgent:
    """Supervises agent outputs to ensure corporate accuracy and handles Case 5."""

    def __init__(self):
        self.model = settings.MODEL_REASONING

    def audit(
        self,
        subject: str,
        body: str,
        intent: str,
        meeting_data: Optional[Dict[str, Any]] = None,
        tasks_data: Optional[list] = None
    ) -> Dict[str, Any]:
        """
        Audits completeness. Returns clarification request if ambiguous, else approval.
        """
        # Explicit check for known ambiguous patterns
        body_lower = body.lower()
        if "sometime" in body_lower or "whenever" in body_lower or "handle that thing" in body_lower:
            return {
                "needs_clarification": True,
                "missing_fields": ["time_frame", "specific_slots"],
                "question": "Could you please specify your preferred day and time zone for our discussion?",
                "options": [
                    "Tomorrow morning (9:00 AM - 12:00 PM EST)",
                    "Tomorrow afternoon (1:00 PM - 5:00 PM EST)",
                    "Next week Monday or Tuesday"
                ],
                "reasoning": "Meeting time frame was left open-ended."
            }

        prompt = (
            f"Subject: {subject}\n"
            f"Body:\n{body}\n"
            f"Detected Intent: {intent}\n"
            f"Extracted Meeting: {json.dumps(meeting_data, default=str)}\n"
            f"Extracted Tasks: {json.dumps(tasks_data, default=str)}"
        )

        messages = [
            {"role": "system", "content": SUPERVISOR_SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]

        try:
            resp_text = nexus_client.generate(
                messages=messages,
                model=self.model,
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            audit_result = json.loads(resp_text)
            return audit_result
        except Exception as e:
            logger.warning(f"Supervisor LLM audit exception: {e}. Defaulting to proceeding.")
            return {
                "needs_clarification": False,
                "missing_fields": [],
                "reasoning": "Fallback pass through"
            }

    def record_clarification_in_db(
        self,
        clarification_data: Dict[str, Any],
        db: Session,
        email_id: Optional[int] = None
    ) -> ClarificationRequestModel:
        """Saves a pending clarification request into the MSSQL database."""
        missing_str = ", ".join(clarification_data.get("missing_fields", []))
        options_json = json.dumps(clarification_data.get("options", []))

        record = ClarificationRequestModel(
            email_id=email_id,
            missing_fields=missing_str or "unspecified",
            question=clarification_data.get("question", "Could you please clarify your request?"),
            options_json=options_json,
            status="pending"
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        logger.info(f"Recorded Clarification Request #{record.id} in MSSQL for Email #{email_id}.")
        return record

supervisor_agent = SupervisorAgent()
