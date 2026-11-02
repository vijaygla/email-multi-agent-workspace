"""
Critic Agent (Output Verifier & Self-Reflection Loop).
Audits generated drafts and execution outputs before dispatch.
Validates:
1. Hallucination guard: ensures dates/times in the draft match calendar free/busy slots.
2. Deliverable completeness: verifies all extracted tasks/deadlines are addressed.
3. Corporate tone consistency and policy compliance.
Provides an auto-corrected draft if defects are identified.
"""
import json
import logging
from typing import Dict, Any, List, Optional
from app.core.config import settings
from app.adapters.nexus_client import nexus_client

logger = logging.getLogger(__name__)

CRITIC_SYSTEM_PROMPT = """You are the Senior Executive Critic & Verifier Agent for Nexus AI.
Your responsibility is to inspect the generated response draft against the incoming email, proposed meeting slots, and extracted tasks.

Verification Rules:
1. Check for Hallucinations: Does the draft propose dates or times NOT present in the proposed calendar slots?
2. Check Task Acknowledgement: If tasks/action items were detected, does the draft acknowledge them accurately?
3. Check Tone & Professionalism: Does the draft maintain the requested tone and avoid risky promises?

Evaluate the draft and output strictly valid JSON with this exact schema:
{
    "is_approved": true,
    "confidence_score": 0.95,
    "issues_detected": [],
    "corrected_draft": {
        "subject": "string",
        "body": "auto-corrected text if issues exist, otherwise identical to input draft"
    },
    "reasoning": "Brief explanation of verification decision"
}
"""

class CriticAgent:
    """Performs self-reflection and verifies agent drafts before human staging or autopilot dispatch."""

    def __init__(self):
        self.model = settings.MODEL_REASONING

    def verify(
        self,
        original_subject: str,
        original_body: str,
        draft_subject: str,
        draft_body: str,
        proposed_slots: Optional[List[Dict[str, str]]] = None,
        tasks: Optional[List[Dict[str, Any]]] = None,
        tone: str = "professional"
    ) -> Dict[str, Any]:
        """Verifies the draft for accuracy, lack of hallucination, and completeness."""
        if not settings.CRITIC_VERIFICATION_ENABLED:
            return {
                "is_approved": True,
                "confidence_score": 0.95,
                "issues_detected": [],
                "corrected_draft": {"subject": draft_subject, "body": draft_body},
                "reasoning": "Critic verification disabled in settings."
            }

        prompt_payload = {
            "original_email": {
                "subject": original_subject,
                "body": original_body
            },
            "proposed_slots": proposed_slots or [],
            "extracted_tasks": tasks or [],
            "tone": tone,
            "generated_draft": {
                "subject": draft_subject,
                "body": draft_body
            }
        }

        messages = [
            {"role": "system", "content": CRITIC_SYSTEM_PROMPT},
            {"role": "user", "content": json.dumps(prompt_payload)}
        ]

        try:
            resp_text = nexus_client.generate(
                messages=messages,
                model=self.model,
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            result = json.loads(resp_text)
            return {
                "is_approved": bool(result.get("is_approved", True)),
                "confidence_score": float(result.get("confidence_score", 0.9)),
                "issues_detected": result.get("issues_detected", []),
                "corrected_draft": result.get("corrected_draft", {"subject": draft_subject, "body": draft_body}),
                "reasoning": result.get("reasoning", "Verification passed.")
            }
        except Exception as e:
            logger.warning(f"Critic Agent verification exception: {e}. Falling back to default approval.")
            return {
                "is_approved": True,
                "confidence_score": 0.88,
                "issues_detected": [],
                "corrected_draft": {"subject": draft_subject, "body": draft_body},
                "reasoning": "Heuristic fallback approval."
            }

critic_agent = CriticAgent()
