"""
API Endpoints for Inbox Emails.
Supports fetching unread/all emails, ingesting incoming corporate messages,
and retrieving email threads with complete multi-agent metadata.
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.db.models import EmailModel
from app.schemas.email import EmailCreate, EmailResponse, EmailListResponse

router = APIRouter()

@router.get("", response_model=EmailListResponse)
def list_emails(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
    intent: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Retrieves list of emails with optional filtering by processing status or intent."""
    query = db.query(EmailModel)
    if status:
        query = query.filter(EmailModel.status == status)
    if intent:
        query = query.filter(EmailModel.intent == intent)

    total = query.count()
    emails = query.order_by(EmailModel.received_at.desc()).offset(skip).limit(limit).all()

    return EmailListResponse(total=total, emails=emails)


@router.post("", response_model=EmailResponse, status_code=201)
def ingest_email(email_in: EmailCreate, db: Session = Depends(get_db)):
    """Ingests a new incoming email into the Microsoft SQL Server database."""
    email_record = EmailModel(
        subject=email_in.subject,
        sender=email_in.sender,
        recipient=email_in.recipient,
        body=email_in.body,
        thread_id=email_in.thread_id,
        status="unread",
        is_read=False
    )
    db.add(email_record)
    db.commit()
    db.refresh(email_record)
    return email_record


@router.get("/{email_id}", response_model=EmailResponse)
def get_email(email_id: int, db: Session = Depends(get_db)):
    """Fetches a specific email by its primary key ID."""
    email = db.query(EmailModel).filter(EmailModel.id == email_id).first()
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")
    return email


@router.patch("/{email_id}/read", response_model=EmailResponse)
def mark_as_read(email_id: int, db: Session = Depends(get_db)):
    """Marks an email as read."""
    email = db.query(EmailModel).filter(EmailModel.id == email_id).first()
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")
    email.is_read = True
    db.commit()
    db.refresh(email)
    return email
