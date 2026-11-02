"""
Router / Planner Agent.
Classifies email intent into: meeting, task, mixed_intent, or general_inquiry.
Routes execution paths to specialized sub-agents.
"""
import json
import logging
from typing import Dict, Any
from app.core.config import settings
from app.adapters.nexus_client import nexus_client

logger = logging.getLogger(__name__)

ROUTER_SYSTEM_PROMPT = """You are an Enterprise Email Intent Router for Nexus AI.
Analyze the given email and determine the sender's core intent.

Classify the intent into EXACTLY one of these categories:
- "meeting": The sender is asking to schedule a meeting, call, appointment, or sync (e.g. "Let's meet tomorrow afternoon").
- "task": The sender is assigning a task, deliverable, action item, or deadline (e.g. "Send the budget deck by Friday").
- "mixed_intent": The email contains BOTH a meeting request AND a task/action item in the SAME message.
- "general_inquiry": The email is an informational inquiry, status update, or FYI not requiring meeting or task recording.
- "unknown": Unclear or ambiguous intent.

Output strictly valid JSON with this exact schema:
{
    "intent": "meeting" | "task" | "mixed_intent" | "general_inquiry" | "unknown",
    "confidence": 0.0 to 1.0,
    "has_meeting_intent": true | false,
    "has_task_intent": true | false,
    "reasoning": "Brief 1-sentence justification"
}
"""

class RouterAgent:
    """Classifies email messages to route them to the appropriate agent workflow."""

    def __init__(self):
        self.model = settings.MODEL_ROUTER

    def route(self, subject: str, body: str) -> Dict[str, Any]:
        """Classifies intent using Nexus Generative Engine with model fallback."""
        user_prompt = f"Subject: {subject}\n\nEmail Body:\n{body}"

        messages = [
            {"role": "system", "content": ROUTER_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ]

        try:
            response_text = nexus_client.generate(
                messages=messages,
                model=self.model,
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            parsed = json.loads(response_text)

            # Sanity check intent
            intent = parsed.get("intent", "unknown")
            if parsed.get("has_meeting_intent") and parsed.get("has_task_intent"):
                intent = "mixed_intent"

            return {
                "intent": intent,
                "confidence": float(parsed.get("confidence", 0.9)),
                "has_meeting_intent": bool(parsed.get("has_meeting_intent", False)),
                "has_task_intent": bool(parsed.get("has_task_intent", False)),
                "reasoning": parsed.get("reasoning", "")
            }
        except Exception as e:
            logger.warning(f"Router LLM parsing failed: {e}. Applying heuristic fallback.")
            # Heuristic fallback
            body_lower = (subject + " " + body).lower()
            has_meet = any(w in body_lower for w in ["meet", "call", "sync", "schedule", "appointment", "calendar", "catch up"])
            has_task = any(w in body_lower for w in ["send", "submit", "prepare", "deck", "budget", "report", "review", "by friday", "deadline", "task", "action item"])

            if has_meet and has_task:
                return {"intent": "mixed_intent", "confidence": 0.85, "has_meeting_intent": True, "has_task_intent": True, "reasoning": "Heuristic mixed intent"}
            elif has_meet:
                return {"intent": "meeting", "confidence": 0.85, "has_meeting_intent": True, "has_task_intent": False, "reasoning": "Heuristic meeting intent"}
            elif has_task:
                return {"intent": "task", "confidence": 0.85, "has_meeting_intent": False, "has_task_intent": True, "reasoning": "Heuristic task intent"}
            return {"intent": "general_inquiry", "confidence": 0.7, "has_meeting_intent": False, "has_task_intent": False, "reasoning": "Heuristic general inquiry"}

router_agent = RouterAgent()
