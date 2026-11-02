"""
Pydantic contracts for Drafts, Clarification Requests, Pipeline Execution Responses, and WebSocket Events.
"""
from datetime import datetime
from typing import Optional, List, Any, Dict
from pydantic import BaseModel, Field

class DraftCreate(BaseModel):
    email_id: Optional[int] = None
    recipient: str
    subject: str
    body: str
    tone: str = "professional"

class DraftResponse(BaseModel):
    id: int
    email_id: Optional[int] = None
    recipient: str
    subject: str
    body: str
    tone: str
    status: str
    created_at: datetime
    approved_at: Optional[datetime] = None
    sent_at: Optional[datetime] = None

    model_config = {"from_attributes": True}

class ClarificationCreate(BaseModel):
    email_id: Optional[int] = None
    missing_fields: str
    question: str
    options: List[str]

class ClarificationReply(BaseModel):
    answer: str = Field(..., description="Selected answer or clarification text provided by user")

class ClarificationResponse(BaseModel):
    id: int
    email_id: Optional[int] = None
    missing_fields: str
    question: str
    options_json: str
    status: str
    resolution: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}

class ProcessRequest(BaseModel):
    email_id: int = Field(..., description="Database ID of the email to process")
    tone: Optional[str] = Field(default="professional", description="Desired tone: professional, friendly, concise, executive")

class ProcessResponse(BaseModel):
    email_id: int
    intent: str
    confidence: float
    status: str  # processed, clarification_needed, failed
    meeting_proposal: Optional[Dict[str, Any]] = None
    tasks: Optional[List[Dict[str, Any]]] = None
    draft: Optional[Dict[str, Any]] = None
    clarification: Optional[Dict[str, Any]] = None
    autopilot: Optional[Dict[str, Any]] = None
    execution_time_ms: float

class WebSocketEvent(BaseModel):
    event_type: str  # agent_start, agent_observe, agent_think, agent_act, agent_finish, error
    email_id: Optional[int] = None
    agent_name: str
    step: str
    details: Dict[str, Any]
    timestamp: str
