"""
Autonomous Background Polling & Email Ingestion Worker.
Continuously or periodically inspects the corporate inbox (Outlook Graph or Mock adapter),
automatically ingests unread messages into MSSQL, and triggers the multi-agent
orchestrator pipeline autonomously without manual human intervention.
"""
import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, Optional

from app.core.config import settings
from app.core.database import SessionLocal
from app.db.models import EmailModel
from app.adapters.outlook_mail import outlook_mail_client
from app.agents.orchestrator import orchestrator, ws_manager

logger = logging.getLogger("BackgroundWorker")

class AutonomousBackgroundWorker:
    """Manages autonomous polling, ingestion, and background execution loops."""

    def __init__(self):
        self.is_running: bool = False
        self.last_poll_time: Optional[datetime] = None
        self.total_polls_count: int = 0
        self.total_emails_ingested: int = 0
        self.total_emails_processed: int = 0
        self._loop_task: Optional[asyncio.Task] = None

    def get_status(self) -> Dict[str, Any]:
        """Returns the current operational status of the autonomous worker."""
        return {
            "is_running": self.is_running,
            "polling_enabled": settings.BACKGROUND_POLLING_ENABLED,
            "autonomy_level": settings.AUTONOMY_LEVEL,
            "confidence_threshold": settings.AUTOPILOT_CONFIDENCE_THRESHOLD,
            "poll_interval_seconds": settings.BACKGROUND_POLLING_INTERVAL_SECONDS,
            "last_poll_time": self.last_poll_time.isoformat() if self.last_poll_time else None,
            "total_polls_count": self.total_polls_count,
            "total_emails_ingested": self.total_emails_ingested,
            "total_emails_processed": self.total_emails_processed
        }

    async def poll_once(self) -> Dict[str, Any]:
        """
        Executes a single autonomous polling and processing cycle:
        1. Queries Outlook Mail adapter for unread messages.
        2. Ingests new messages into MSSQL database.
        3. Autonomously triggers the multi-agent pipeline for each ingested email.
        """
        self.last_poll_time = datetime.utcnow()
        self.total_polls_count += 1
        logger.info(f"Autonomous worker: Starting poll cycle #{self.total_polls_count}...")

        ingested_count = 0
        processed_count = 0

        try:
            unread_messages = outlook_mail_client.fetch_unread_emails(limit=5)
        except Exception as e:
            logger.error(f"Autonomous worker: Error querying Outlook Mail: {e}")
            return {"ingested": 0, "processed": 0, "error": str(e)}

        with SessionLocal() as db:
            for msg in unread_messages:
                subject = msg.get("subject", "No Subject")
                sender = msg.get("sender", "")
                body = msg.get("body", "")
                recipient = msg.get("recipient", "user@nexus.ai")
                thread_id = msg.get("id")

                # Check if email is already ingested to prevent duplicates
                existing = db.query(EmailModel).filter(
                    EmailModel.subject == subject,
                    EmailModel.sender == sender,
                    EmailModel.body == body
                ).first()

                if existing:
                    continue

                # Ingest new email into MSSQL
                email_record = EmailModel(
                    subject=subject,
                    sender=sender,
                    recipient=recipient,
                    body=body,
                    thread_id=thread_id,
                    status="unread",
                    is_read=False
                )
                db.add(email_record)
                db.commit()
                db.refresh(email_record)

                ingested_count += 1
                self.total_emails_ingested += 1
                logger.info(f"Autonomous worker: Ingested new Email #{email_record.id} '{subject}' from {sender}")

                # Broadcast new email event via WebSocket
                await ws_manager.broadcast({
                    "event_type": "email_ingested",
                    "email_id": email_record.id,
                    "agent_name": "AutonomousWorker",
                    "step": "Ingest",
                    "details": {
                        "subject": subject,
                        "sender": sender,
                        "autonomy_level": settings.AUTONOMY_LEVEL
                    },
                    "timestamp": datetime.utcnow().isoformat()
                })

                # Autonomously process email if autonomy level > L0
                if settings.AUTONOMY_LEVEL != "L0":
                    try:
                        logger.info(f"Autonomous worker: Auto-triggering orchestrator for Email #{email_record.id}...")
                        await orchestrator.process_email(
                            email_id=email_record.id,
                            db=db,
                            tone="professional"
                        )
                        processed_count += 1
                        self.total_emails_processed += 1
                    except Exception as exc:
                        logger.error(f"Autonomous worker: Error auto-processing Email #{email_record.id}: {exc}")

        return {
            "poll_number": self.total_polls_count,
            "ingested": ingested_count,
            "processed": processed_count,
            "timestamp": self.last_poll_time.isoformat()
        }

    async def _worker_loop(self):
        """Infinite polling loop executed as a background task."""
        logger.info("Autonomous Worker Loop initialized.")
        while self.is_running:
            try:
                if settings.BACKGROUND_POLLING_ENABLED:
                    await self.poll_once()
            except asyncio.CancelledError:
                logger.info("Autonomous Worker Loop cancelled.")
                break
            except Exception as e:
                logger.error(f"Unexpected error in autonomous worker loop: {e}")

            await asyncio.sleep(settings.BACKGROUND_POLLING_INTERVAL_SECONDS)

    def start(self):
        """Starts the background worker loop."""
        if self.is_running:
            logger.warning("Autonomous worker is already running.")
            return

        self.is_running = True
        self._loop_task = asyncio.create_task(self._worker_loop())
        logger.info("Autonomous background worker started.")

    def stop(self):
        """Stops the background worker loop gracefully."""
        self.is_running = False
        if self._loop_task:
            self._loop_task.cancel()
            self._loop_task = None
        logger.info("Autonomous background worker stopped.")

autonomous_worker = AutonomousBackgroundWorker()
