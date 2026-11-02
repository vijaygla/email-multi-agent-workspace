"""
Pydantic contracts for Calendar slot extraction, proposals, and scheduling.
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

class MeetingSlot(BaseModel):
    start_time: str = Field(..., description="ISO 8601 formatted start time or human-readable format")
    end_time: str = Field(..., description="ISO 8601 formatted end time or human-readable format")
    title: str = Field(default="Proposed Meeting", description="Meeting topic")
    confidence: float = Field(default=1.0, description="Slot suitability score")

class MeetingProposalCreate(BaseModel):
    email_id: Optional[int] = None
    requested_dates: Optional[str] = None
    participants: Optional[str] = None
    proposed_slots: List[MeetingSlot]
    stage: int = 1

class MeetingProposalResponse(BaseModel):
    id: int
    email_id: Optional[int] = None
    requested_dates: Optional[str] = None
    participants: Optional[str] = None
    proposed_slots_json: str
    status: str
    stage: int
    created_at: datetime

    model_config = {"from_attributes": True}

class MeetingProposalListResponse(BaseModel):
    total: int
    proposals: List[MeetingProposalResponse]
