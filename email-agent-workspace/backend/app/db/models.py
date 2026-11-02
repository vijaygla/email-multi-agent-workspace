"""
SQLAlchemy database models for Microsoft SQL Server persistence.
Provides schemas for Emails, Tasks, Meeting Proposals, Drafts, Agent Logs, and Clarification Requests.
"""
from datetime import datetime
from typing import List, Optional
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class EmailModel(Base):
    __tablename__ = "Emails"

    id = Column(Integer, primary_key=True, autoincrement=True)
    thread_id = Column(String(100), nullable=True)
    subject = Column(String(255), nullable=False)
    sender = Column(String(255), nullable=False)
    recipient = Column(String(255), nullable=False)
    body = Column(Text, nullable=False)
    received_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    status = Column(String(50), default="unread", nullable=False)  # unread, processing, processed, clarification_needed, failed
    intent = Column(String(50), nullable=True)  # meeting, task, mixed_intent, general_inquiry, unknown
    confidence = Column(Float, default=0.0, nullable=True)
    is_read = Column(Boolean, default=False, nullable=False)

    # Relationships
    tasks = relationship("TaskModel", back_populates="email", cascade="all, delete-orphan")
    meeting_proposals = relationship("MeetingProposalModel", back_populates="email", cascade="all, delete-orphan")
    drafts = relationship("DraftModel", back_populates="email", cascade="all, delete-orphan")
    agent_logs = relationship("AgentLogModel", back_populates="email", cascade="all, delete-orphan")
    clarifications = relationship("ClarificationRequestModel", back_populates="email", cascade="all, delete-orphan")


class TaskModel(Base):
    __tablename__ = "Tasks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email_id = Column(Integer, ForeignKey("Emails.id", ondelete="CASCADE"), nullable=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    owner = Column(String(255), default="Me", nullable=False)
    due_date = Column(String(100), nullable=True)
    urgency = Column(String(50), default="medium", nullable=False)  # low, medium, high, urgent
    status = Column(String(50), default="pending", nullable=False)  # pending, in_progress, completed
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationship
    email = relationship("EmailModel", back_populates="tasks")


class MeetingProposalModel(Base):
    __tablename__ = "MeetingProposals"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email_id = Column(Integer, ForeignKey("Emails.id", ondelete="CASCADE"), nullable=True)
    requested_dates = Column(String(500), nullable=True)
    participants = Column(String(1000), nullable=True)
    proposed_slots_json = Column(Text, nullable=False)  # JSON formatted slots array
    status = Column(String(50), default="staged", nullable=False)  # staged, confirmed, declined
    stage = Column(Integer, default=1, nullable=False)  # 1 = Review Draft, 2 = Auto Coordinated
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationship
    email = relationship("EmailModel", back_populates="meeting_proposals")


class DraftModel(Base):
    __tablename__ = "Drafts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email_id = Column(Integer, ForeignKey("Emails.id", ondelete="CASCADE"), nullable=True)
    recipient = Column(String(255), nullable=False)
    subject = Column(String(255), nullable=False)
    body = Column(Text, nullable=False)
    tone = Column(String(50), default="professional", nullable=False)  # professional, friendly, concise, executive
    status = Column(String(50), default="staged", nullable=False)  # staged, approved, sent
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    approved_at = Column(DateTime, nullable=True)
    sent_at = Column(DateTime, nullable=True)

    # Relationship
    email = relationship("EmailModel", back_populates="drafts")


class AgentLogModel(Base):
    __tablename__ = "AgentLogs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email_id = Column(Integer, ForeignKey("Emails.id", ondelete="CASCADE"), nullable=True)
    agent_name = Column(String(100), nullable=False)
    step = Column(String(100), nullable=False)  # Observe, Think, Act, Error
    action = Column(String(255), nullable=False)
    thought = Column(Text, nullable=True)
    input_data = Column(Text, nullable=True)
    output_data = Column(Text, nullable=True)
    model_used = Column(String(100), nullable=True)
    latency_ms = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationship
    email = relationship("EmailModel", back_populates="agent_logs")


class ClarificationRequestModel(Base):
    __tablename__ = "ClarificationRequests"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email_id = Column(Integer, ForeignKey("Emails.id", ondelete="CASCADE"), nullable=True)
    missing_fields = Column(String(500), nullable=False)  # e.g. "time_zone, due_date"
    question = Column(Text, nullable=False)
    options_json = Column(Text, nullable=False)  # JSON array of selectable choices
    status = Column(String(50), default="pending", nullable=False)  # pending, resolved
    resolution = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationship
    email = relationship("EmailModel", back_populates="clarifications")
