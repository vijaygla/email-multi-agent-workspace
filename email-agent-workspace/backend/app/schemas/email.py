"""
Pydantic contracts for incoming emails, filters, and list views.
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

class EmailCreate(BaseModel):
    subject: str = Field(..., description="Subject line of the email")
    sender: str = Field(..., description="Sender's email address")
    recipient: str = Field(default="user@nexus.ai", description="Recipient's email address")
    body: str = Field(..., description="Raw text or HTML body of the email")
    thread_id: Optional[str] = Field(default=None, description="Thread conversation identifier")

class EmailResponse(BaseModel):
    id: int
    thread_id: Optional[str] = None
    subject: str
    sender: str
    recipient: str
    body: str
    received_at: datetime
    status: str
    intent: Optional[str] = None
    confidence: Optional[float] = 0.0
    is_read: bool

    model_config = {"from_attributes": True}

class EmailListResponse(BaseModel):
    total: int
    emails: List[EmailResponse]
