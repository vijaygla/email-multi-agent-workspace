"""
Enterprise Telemetry and Audit Logging.
Tracks agent spans, model latency, token counts, and persists execution traces to MSSQL AgentLogs.
"""
import time
import json
import logging
from typing import Optional, Any
from sqlalchemy.orm import Session
from app.db.models import AgentLogModel

logger = logging.getLogger(__name__)

class AgentSpan:
    """Context manager for tracing agent execution time and outcomes."""
    def __init__(
        self,
        db: Session,
        email_id: Optional[int],
        agent_name: str,
        step: str,
        action: str,
        model_used: Optional[str] = None
    ):
        self.db = db
        self.email_id = email_id
        self.agent_name = agent_name
        self.step = step
        self.action = action
        self.model_used = model_used
        self.start_time = 0.0
        self.latency_ms = 0.0
        self.thought = ""
        self.input_data = ""
        self.output_data = ""

    def __enter__(self):
        self.start_time = time.perf_counter()
        return self

    def record_io(self, input_val: Any = None, output_val: Any = None, thought: str = ""):
        if input_val is not None:
            self.input_data = json.dumps(input_val, default=str) if not isinstance(input_val, str) else input_val
        if output_val is not None:
            self.output_data = json.dumps(output_val, default=str) if not isinstance(output_val, str) else output_val
        if thought:
            self.thought = thought

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.latency_ms = (time.perf_counter() - self.start_time) * 1000.0
        if exc_val is not None:
            self.step = "Error"
            self.output_data = f"Exception: {str(exc_val)}"

        try:
            log_record = AgentLogModel(
                email_id=self.email_id,
                agent_name=self.agent_name,
                step=self.step,
                action=self.action,
                thought=self.thought or None,
                input_data=self.input_data[:2000] if self.input_data else None,
                output_data=self.output_data[:2000] if self.output_data else None,
                model_used=self.model_used,
                latency_ms=round(self.latency_ms, 2)
            )
            self.db.add(log_record)
            self.db.commit()
            logger.info(
                f"[{self.agent_name}] {self.step} - {self.action} finished in {self.latency_ms:.2f}ms (Model: {self.model_used})"
            )
        except Exception as e:
            logger.warning(f"Telemetry logging to MSSQL failed: {e}")
            self.db.rollback()
