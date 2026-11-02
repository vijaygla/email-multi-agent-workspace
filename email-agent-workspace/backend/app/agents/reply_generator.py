"""
Reply Generator Agent (The Smart Replier - Case 4).
Generates highly personalized, context-aware email drafts integrating Case 1 meeting slots
and Case 2 logged task confirmations under specified corporate tone guidelines.
"""
import json
import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.core.config import settings
from app.db.models import DraftModel
from app.adapters.nexus_client import nexus_client

logger = logging.getLogger(__name__)

REPLY_GENERATOR_SYSTEM_PROMPT = """You are the Senior Executive Communications Assistant for Nexus AI.
Your task is to generate a professional, polished, and context-aware email response.

Context guidelines:
- If meeting slots are provided from the Calendar Finder (Case 1), list them clearly as 2 to 3 convenient bullet points.
- If tasks or deliverables were logged from the To-Do Creator (Case 2), confirm clearly that the item has been officially tracked with its owner and deadline.
- Tone Requirement: Adhere strictly to the requested tone ("professional", "friendly", "concise", or "executive").
- Professional closing with appropriate sign-off.

Output strictly valid JSON with this exact schema:
{
    "subject": "Re: [Subject]",
    "body": "Formatted email body text with greetings, bulleted slots/tasks, and sign-off",
    "tone": "professional" | "friendly" | "concise" | "executive"
}
"""

class ReplyGeneratorAgent:
    """Generates context-rich email responses and saves staged drafts to MSSQL."""

    def __init__(self):
        self.model = settings.MODEL_DRAFTING

    def draft_reply(
        self,
        subject: str,
        body: str,
        sender: str,
        recipient: str,
        intent: str,
        meeting_slots: Optional[List[Dict[str, str]]] = None,
        tasks: Optional[List[Dict[str, Any]]] = None,
        tone: str = "professional"
    ) -> Dict[str, str]:
        """
        Drafts a context-aware email incorporating calendar slots and confirmed tasks.
        """
        slots_str = ""
        if meeting_slots:
            slots_str = "Available Meeting Slots:\n" + "\n".join([f"- {s.get('display', s.get('start_time'))}" for s in meeting_slots])

        tasks_str = ""
        if tasks:
            tasks_str = "Logged Tasks / Deliverables:\n" + "\n".join([
                f"- Task: {t.get('title')} | Owner: {t.get('owner')} | Due: {t.get('due_date', 'N/A')} | Urgency: {t.get('urgency')}"
                for t in tasks
            ])

        user_content = (
            f"Original Subject: {subject}\n"
            f"Original Sender: {sender}\n"
            f"Original Recipient: {recipient}\n"
            f"Original Email Body:\n{body}\n\n"
            f"Intent: {intent}\n"
            f"Requested Tone: {tone}\n\n"
            f"{slots_str}\n\n"
            f"{tasks_str}\n"
        )

        messages = [
            {"role": "system", "content": REPLY_GENERATOR_SYSTEM_PROMPT},
            {"role": "user", "content": user_content}
        ]

        try:
            resp_text = nexus_client.generate(
                messages=messages,
                model=self.model,
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            draft = json.loads(resp_text)
            return {
                "subject": draft.get("subject", f"Re: {subject}"),
                "body": draft.get("body", "Thank you for your email."),
                "tone": tone
            }
        except Exception as e:
            logger.warning(f"Reply generator LLM error: {e}. Generating structured template fallback.")
            return self._generate_fallback_draft(subject, sender, meeting_slots, tasks, tone)

    def _generate_fallback_draft(
        self,
        subject: str,
        sender: str,
        meeting_slots: Optional[List[Dict[str, str]]],
        tasks: Optional[List[Dict[str, Any]]],
        tone: str
    ) -> Dict[str, str]:
        greeting = f"Hi {sender.split('@')[0].title()},"
        content_lines = [greeting, ""]

        if meeting_slots:
            content_lines.append("I would be glad to connect. Here are a few open times on my calendar:")
            for s in meeting_slots:
                content_lines.append(f"  • {s.get('display', s.get('start_time'))}")
            content_lines.append("")

        if tasks:
            content_lines.append("I have also logged the following action items onto our task board:")
            for t in tasks:
                content_lines.append(f"  • {t.get('title')} (Due: {t.get('due_date', 'N/A')}, Urgency: {t.get('urgency', 'medium').capitalize()})")
            content_lines.append("")

        content_lines.append("Please let me know if any of these times work best for you.")
        content_lines.append("\nBest regards,\nNexus Workspace Team")

        return {
            "subject": f"Re: {subject}",
            "body": "\n".join(content_lines),
            "tone": tone
        }

    def save_draft_to_db(
        self,
        draft_dict: Dict[str, str],
        recipient: str,
        db: Session,
        email_id: Optional[int] = None
    ) -> DraftModel:
        """Saves generated email draft into MSSQL ready for human approval."""
        draft_record = DraftModel(
            email_id=email_id,
            recipient=recipient,
            subject=draft_dict.get("subject", "Re: Follow up"),
            body=draft_dict.get("body", ""),
            tone=draft_dict.get("tone", "professional"),
            status="staged"  # Staged for user review
        )
        db.add(draft_record)
        db.commit()
        db.refresh(draft_record)
        logger.info(f"Saved Draft #{draft_record.id} in MSSQL for Email #{email_id}.")
        return draft_record

reply_generator_agent = ReplyGeneratorAgent()
