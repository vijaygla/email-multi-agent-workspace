"""
Master Multi-Agent Orchestrator.
Coordinates the Observe -> Think -> Act lifecycle.
Supports Case 3 concurrent split execution for mixed-intent emails,
Stage 1 draft review / Stage 2 auto coordination, and live WebSocket telemetry broadcasting.
"""
import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional, Set
from fastapi import WebSocket
from sqlalchemy.orm import Session

from app.db.models import EmailModel, MeetingProposalModel
from app.core.config import settings
from app.core.telemetry import AgentSpan
from app.agents.reader import reader_agent
from app.agents.router import router_agent
from app.agents.entity_extractor import entity_extractor_agent
from app.agents.task_extractor import task_extractor_agent
from app.agents.supervisor import supervisor_agent
from app.agents.reply_generator import reply_generator_agent
from app.agents.critic import critic_agent
from app.adapters.outlook_mail import outlook_mail_client
from app.adapters.outlook_calendar import outlook_calendar_client

logger = logging.getLogger(__name__)

class ConnectionManager:
    """Manages real-time WebSocket subscriber connections."""
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info(f"WebSocket client connected. Total active: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.discard(websocket)
        logger.info(f"WebSocket client disconnected. Total active: {len(self.active_connections)}")

    async def broadcast(self, event: Dict[str, Any]):
        """Broadcasts event to all connected dashboard clients."""
        dead_connections = set()
        for connection in self.active_connections:
            try:
                await connection.send_json(event)
            except Exception as e:
                logger.warning(f"Error broadcasting to client: {e}")
                dead_connections.add(connection)
        self.active_connections.difference_update(dead_connections)

ws_manager = ConnectionManager()


class Orchestrator:
    """Master Multi-Agent Controller implementing the Observe -> Think -> Act pattern."""

    async def _emit_event(
        self,
        event_type: str,
        email_id: Optional[int],
        agent_name: str,
        step: str,
        details: Dict[str, Any]
    ):
        """Dispatches real-time event to connected WebSocket clients."""
        event_payload = {
            "event_type": event_type,
            "email_id": email_id,
            "agent_name": agent_name,
            "step": step,
            "details": details,
            "timestamp": datetime.utcnow().isoformat()
        }
        await ws_manager.broadcast(event_payload)

    async def process_email(
        self,
        email_id: int,
        db: Session,
        tone: str = "professional",
        stage: int = 1,
        resolved_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Executes the end-to-end multi-agent workflow on the target email.
        Covers Case 1 (Meeting), Case 2 (Task), Case 3 (Mixed Intent), Case 4 (Reply), Case 5 (Clarification),
        Self-reflection Critic audit, and L1-L3 Autopilot execution.
        """
        # Fetch email from MSSQL
        email = db.query(EmailModel).filter(EmailModel.id == email_id).first()
        if not email:
            raise ValueError(f"Email with ID {email_id} not found in database.")

        email.status = "processing"
        db.commit()

        start_time = datetime.utcnow()

        # Handle thread history context
        thread_history = []
        if settings.THREAD_CONTEXT_ENABLED and email.thread_id:
            prior_emails = db.query(EmailModel).filter(
                EmailModel.thread_id == email.thread_id,
                EmailModel.id != email_id
            ).order_by(EmailModel.received_at.asc()).limit(5).all()
            for p in prior_emails:
                thread_history.append({
                    "id": p.id,
                    "sender": p.sender,
                    "subject": p.subject,
                    "body": p.body[:300]
                })

        # Inject resolved clarification answer if provided
        body_to_process = email.body
        if resolved_context:
            body_to_process = f"{email.body}\n\n[Clarification Resolved Context]: {resolved_context}"

        # Step 1: OBSERVE - Reader Agent
        await self._emit_event("agent_start", email_id, "ReaderAgent", "Observe", {
            "message": f"Ingesting and normalizing email '{email.subject}' from {email.sender}"
        })
        with AgentSpan(db, email_id, "ReaderAgent", "Observe", "Normalize Payload") as span:
            context = reader_agent.process({
                "subject": email.subject,
                "body": body_to_process,
                "sender": email.sender,
                "recipient": email.recipient,
                "received_at": email.received_at,
                "thread_history": thread_history
            })
            span.record_io(input_val={"raw_body_len": len(body_to_process)}, output_val=context)

        # Step 2: THINK - Router Agent (Intent Categorization)
        await self._emit_event("agent_think", email_id, "RouterAgent", "Think", {
            "message": "Analyzing intent: checking for Meeting, Task, or Mixed Intent..."
        })
        with AgentSpan(db, email_id, "RouterAgent", "Think", "Classify Intent") as span:
            route_result = router_agent.route(context["subject"], context["cleaned_body"])
            intent = route_result["intent"]
            confidence = route_result["confidence"]
            span.record_io(input_val=context["cleaned_body"], output_val=route_result)

        email.intent = intent
        email.confidence = confidence
        db.commit()

        await self._emit_event("agent_act", email_id, "RouterAgent", "Act", {
            "intent": intent,
            "confidence": confidence,
            "reasoning": route_result.get("reasoning", "")
        })

        meeting_data = None
        tasks_data = []

        # Step 3: ACT - Execution based on intent
        # Case 3: Mixed Intent -> Concurrent execution of Calendar & Task Agents
        if intent == "mixed_intent":
            await self._emit_event("agent_start", email_id, "Orchestrator", "Act", {
                "message": "Case 3 Mixed Intent detected! Concurrently splitting to Calendar Agent and Task Agent."
            })

            async def _run_calendar():
                with AgentSpan(db, email_id, "EntityExtractorAgent", "Act", "Find Calendar Slots") as s:
                    res = entity_extractor_agent.extract_and_find_slots(
                        context["subject"], context["cleaned_body"], context["sender"]
                    )
                    s.record_io(output_val=res)
                    return res

            async def _run_tasks():
                with AgentSpan(db, email_id, "TaskExtractorAgent", "Act", "Extract and Persist Tasks") as s:
                    raw_tasks = task_extractor_agent.extract_tasks(
                        context["subject"], context["cleaned_body"], context["sender"]
                    )
                    saved = task_extractor_agent.save_tasks_to_db(raw_tasks, db, email_id)
                    s.record_io(output_val=[{"id": t.id, "title": t.title} for t in saved])
                    return raw_tasks

            # Concurrent execution
            meeting_data, tasks_data = await asyncio.gather(_run_calendar(), _run_tasks())

        elif intent == "meeting":
            # Case 1: Meeting scheduling
            await self._emit_event("agent_start", email_id, "EntityExtractorAgent", "Act", {
                "message": "Case 1: Extracting meeting dates & checking Outlook Calendar free/busy slots."
            })
            with AgentSpan(db, email_id, "EntityExtractorAgent", "Act", "Find Calendar Slots") as span:
                meeting_data = entity_extractor_agent.extract_and_find_slots(
                    context["subject"], context["cleaned_body"], context["sender"]
                )
                span.record_io(output_val=meeting_data)

        elif intent == "task":
            # Case 2: Task extraction
            await self._emit_event("agent_start", email_id, "TaskExtractorAgent", "Act", {
                "message": "Case 2: Extracting action items and persisting directly into MSSQL Tasks table."
            })
            with AgentSpan(db, email_id, "TaskExtractorAgent", "Act", "Extract and Persist Tasks") as span:
                tasks_data = task_extractor_agent.extract_tasks(
                    context["subject"], context["cleaned_body"], context["sender"]
                )
                saved = task_extractor_agent.save_tasks_to_db(tasks_data, db, email_id)
                span.record_io(output_val=[{"id": t.id, "title": t.title} for t in saved])

        # Step 4: AUDIT - Supervisor Agent (Case 5: The Double-Checker)
        await self._emit_event("agent_think", email_id, "SupervisorAgent", "Think", {
            "message": "Supervisor Agent auditing extracted parameters for ambiguity or missing information..."
        })
        with AgentSpan(db, email_id, "SupervisorAgent", "Think", "Completeness Audit") as span:
            audit = supervisor_agent.audit(
                context["subject"],
                context["cleaned_body"],
                intent,
                meeting_data,
                tasks_data
            )
            span.record_io(output_val=audit)

        # Case 5: Missing or Ambiguous Details -> Pause automated flow and request clarification
        if audit.get("needs_clarification", False):
            await self._emit_event("agent_act", email_id, "SupervisorAgent", "Act", {
                "message": "Case 5: Workflow paused! Clarification question staged for sender.",
                "clarification": audit
            })
            clarification_record = supervisor_agent.record_clarification_in_db(audit, db, email_id)
            email.status = "clarification_needed"
            db.commit()

            return {
                "email_id": email_id,
                "intent": intent,
                "confidence": confidence,
                "status": "clarification_needed",
                "clarification": {
                    "id": clarification_record.id,
                    "missing_fields": clarification_record.missing_fields,
                    "question": clarification_record.question,
                    "options": json.loads(clarification_record.options_json)
                },
                "execution_time_ms": (datetime.utcnow() - start_time).total_seconds() * 1000.0
            }

        # Save Meeting Proposal to MSSQL if present
        meeting_proposal_obj = None
        if meeting_data and meeting_data.get("proposed_slots"):
            proposal_record = MeetingProposalModel(
                email_id=email_id,
                requested_dates=meeting_data.get("requested_dates"),
                participants=", ".join(meeting_data.get("participants", [])),
                proposed_slots_json=json.dumps(meeting_data.get("proposed_slots")),
                status="staged",
                stage=stage  # Stage 1 (user review) or Stage 2 (auto coordinated)
            )
            db.add(proposal_record)
            db.commit()
            db.refresh(proposal_record)
            meeting_proposal_obj = {
                "id": proposal_record.id,
                "requested_dates": proposal_record.requested_dates,
                "participants": proposal_record.participants,
                "proposed_slots": meeting_data.get("proposed_slots"),
                "stage": proposal_record.stage
            }

        # Step 5: DRAFT - Case 4: Reply Generator Agent (The Smart Replier)
        slots = meeting_data.get("proposed_slots") if meeting_data else None
        await self._emit_event("agent_start", email_id, "ReplyGeneratorAgent", "Act", {
            "message": f"Case 4: Drafting personalized response in '{tone}' tone integrating slots and task confirmations."
        })
        with AgentSpan(db, email_id, "ReplyGeneratorAgent", "Act", "Draft Reply") as span:
            draft_dict = reply_generator_agent.draft_reply(
                subject=context["subject"],
                body=context["cleaned_body"],
                sender=context["sender"],
                recipient=context["recipient"],
                intent=intent,
                meeting_slots=slots,
                tasks=tasks_data,
                tone=tone
            )
            span.record_io(output_val={"subject": draft_dict.get("subject", "")})

        # Step 5b: REFLECT & VERIFY - Critic Agent (Self-Reflection Loop)
        await self._emit_event("agent_think", email_id, "CriticAgent", "Think", {
            "message": "Critic Agent auditing draft against meeting slots and tasks for hallucination and completeness..."
        })
        with AgentSpan(db, email_id, "CriticAgent", "Think", "Audit & Verify Draft") as span:
            critic_review = critic_agent.verify(
                original_subject=context["subject"],
                original_body=context["cleaned_body"],
                draft_subject=draft_dict.get("subject", ""),
                draft_body=draft_dict.get("body", ""),
                proposed_slots=slots,
                tasks=tasks_data,
                tone=tone
            )
            span.record_io(output_val=critic_review)

        if not critic_review.get("is_approved", True):
            corrected = critic_review.get("corrected_draft", {})
            if corrected and corrected.get("body"):
                draft_dict["body"] = corrected.get("body")
                draft_dict["subject"] = corrected.get("subject", draft_dict.get("subject", ""))

        draft_record = reply_generator_agent.save_draft_to_db(
            draft_dict=draft_dict,
            recipient=context["sender"],
            db=db,
            email_id=email_id
        )

        # Step 6: AUTOPILOT EXECUTION (L1 Assisted, L2 Semi-Autonomous, L3 Full Autopilot)
        autopilot_actions = []
        is_autopilot_eligible = (
            settings.AUTONOMY_LEVEL in ["L2", "L3"]
            and confidence >= settings.AUTOPILOT_CONFIDENCE_THRESHOLD
        )

        if is_autopilot_eligible:
            # Auto-approve draft
            draft_record.status = "approved"
            draft_record.approved_at = datetime.utcnow()
            autopilot_actions.append("Draft auto-approved based on confidence threshold.")

            # If meeting proposal exists, auto-confirm to Stage 2
            if meeting_proposal_obj and proposal_record:
                proposal_record.status = "confirmed"
                proposal_record.stage = 2
                meeting_proposal_obj["stage"] = 2
                meeting_proposal_obj["status"] = "confirmed"
                top_slot = meeting_data.get("proposed_slots", [{}])[0]
                outlook_calendar_client.schedule_event(
                    subject=f"Confirmed: {proposal_record.requested_dates or email.subject}",
                    start_time=top_slot.get("start_time", ""),
                    end_time=top_slot.get("end_time", ""),
                    attendees=meeting_data.get("participants", [email.sender])
                )
                autopilot_actions.append("Meeting proposal auto-confirmed to Stage 2 on corporate calendar.")

            # Full Autopilot (L3) or Semi-Auto (L2) routine dispatch
            if settings.AUTONOMY_LEVEL == "L3" or (settings.AUTONOMY_LEVEL == "L2" and intent in ["meeting", "task", "mixed_intent"]):
                send_success = outlook_mail_client.send_email(
                    to=draft_record.recipient,
                    subject=draft_record.subject,
                    body=draft_record.body
                )
                if send_success:
                    draft_record.status = "sent"
                    draft_record.sent_at = datetime.utcnow()
                    autopilot_actions.append("Draft auto-dispatched via corporate Outlook service.")

            db.commit()

            await self._emit_event("autopilot_action", email_id, "Autopilot", "Act", {
                "autonomy_level": settings.AUTONOMY_LEVEL,
                "confidence": confidence,
                "actions": autopilot_actions,
                "draft_status": draft_record.status
            })

        email.status = "processed"
        db.commit()

        await self._emit_event("agent_finish", email_id, "Orchestrator", "Finish", {
            "message": "Email workflow processing completed successfully!",
            "draft_id": draft_record.id,
            "status": "processed",
            "autopilot_actions": autopilot_actions
        })

        return {
            "email_id": email_id,
            "intent": intent,
            "confidence": confidence,
            "status": "processed",
            "meeting_proposal": meeting_proposal_obj,
            "tasks": tasks_data,
            "draft": {
                "id": draft_record.id,
                "subject": draft_record.subject,
                "body": draft_record.body,
                "tone": draft_record.tone,
                "status": draft_record.status
            },
            "autopilot": {
                "level": settings.AUTONOMY_LEVEL,
                "executed": is_autopilot_eligible,
                "actions": autopilot_actions
            },
            "execution_time_ms": (datetime.utcnow() - start_time).total_seconds() * 1000.0
        }

orchestrator = Orchestrator()
