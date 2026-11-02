"""
Task Extractor Agent (To-Do List Creator - Case 2).
Scans emails for concrete action items, titles, assignees/owners, due dates,
and urgency levels, then persists them into Microsoft SQL Server Tasks table.
"""
import json
import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.core.config import settings
from app.db.models import TaskModel
from app.adapters.nexus_client import nexus_client

logger = logging.getLogger(__name__)

TASK_EXTRACTOR_SYSTEM_PROMPT = """You are an Enterprise Task & Action Item Extractor for Nexus AI.
Analyze the email to discover any concrete action items or to-do tasks.

For each task found, extract:
- "title": Concise, actionable task name (e.g. "Send the revised budget deck")
- "description": Contextual explanation or instructions
- "owner": Who is responsible (e.g. "Me", "Sarah Connor", or named colleague; default to "Me" if the sender directs it to the recipient)
- "due_date": Extracted due date/time (e.g. "Friday 5 PM", "2026-09-25", or null if not stated)
- "urgency": Urgency level - strictly one of: "low", "medium", "high", "urgent"
- "is_ambiguous": true if critical task information is missing (like missing what to do or unclear who is responsible), else false

Output strictly valid JSON with this exact schema:
{
    "tasks": [
        {
            "title": "string",
            "description": "string",
            "owner": "string",
            "due_date": "string or null",
            "urgency": "low" | "medium" | "high" | "urgent",
            "is_ambiguous": false
        }
    ]
}
"""

class TaskExtractorAgent:
    """Identifies tasks in email content and saves them directly to MSSQL database."""

    def __init__(self):
        self.model = settings.MODEL_EXTRACTOR

    def extract_tasks(self, subject: str, body: str, sender: str) -> List[Dict[str, Any]]:
        """Parses email text for action items using Nexus Generative Engine."""
        prompt = f"Sender: {sender}\nSubject: {subject}\nBody:\n{body}"
        messages = [
            {"role": "system", "content": TASK_EXTRACTOR_SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]

        try:
            resp_text = nexus_client.generate(
                messages=messages,
                model=self.model,
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            parsed = json.loads(resp_text)
            tasks = parsed.get("tasks", [])
            return tasks
        except Exception as e:
            logger.warning(f"Task extraction LLM error: {e}. Applying fallback.")
            return [
                {
                    "title": f"Review action item from {subject}",
                    "description": body[:200],
                    "owner": "Me",
                    "due_date": "Friday",
                    "urgency": "medium",
                    "is_ambiguous": False
                }
            ]

    def save_tasks_to_db(
        self,
        tasks: List[Dict[str, Any]],
        db: Session,
        email_id: Optional[int] = None
    ) -> List[TaskModel]:
        """Saves extracted tasks directly into the MSSQL database."""
        saved_records = []
        for t in tasks:
            title = t.get("title", "Action Item")
            owner = t.get("owner", "Me")
            due_date = t.get("due_date")
            urgency = t.get("urgency", "medium")
            description = t.get("description", "")

            # Check for existing matching task if deduplication is enabled
            existing_task = None
            if settings.TASK_DEDUPLICATION_ENABLED and email_id:
                # Find pending task with exact or normalized title match for this email
                norm_title = title.strip().lower()
                candidates = db.query(TaskModel).filter(
                    TaskModel.email_id == email_id,
                    TaskModel.status == "pending"
                ).all()
                for cand in candidates:
                    if cand.title.strip().lower() == norm_title or norm_title in cand.title.strip().lower():
                        existing_task = cand
                        break

            if existing_task:
                # Smart update existing task rather than creating duplicate
                if due_date:
                    existing_task.due_date = due_date
                if urgency:
                    existing_task.urgency = urgency
                if description and not existing_task.description:
                    existing_task.description = description
                saved_records.append(existing_task)
                logger.info(f"Deduplication: Updated existing Task #{existing_task.id} '{existing_task.title}'")
            else:
                record = TaskModel(
                    email_id=email_id,
                    title=title,
                    description=description,
                    owner=owner,
                    due_date=due_date,
                    urgency=urgency,
                    status="pending"
                )
                db.add(record)
                saved_records.append(record)

        db.commit()
        for r in saved_records:
            db.refresh(r)
            logger.info(f"Persisted Task #{r.id} '{r.title}' (Urgency: {r.urgency}, Owner: {r.owner}) to MSSQL.")

        return saved_records

task_extractor_agent = TaskExtractorAgent()
