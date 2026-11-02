"""
API Endpoints for Calendar Meetings and Proposals.
Tracks staged meeting proposals and auto-coordination stages.
"""
import json
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.db.models import MeetingProposalModel
from app.schemas.meeting import MeetingProposalResponse, MeetingProposalListResponse
from app.adapters.outlook_calendar import outlook_calendar_client

router = APIRouter()

@router.get("", response_model=MeetingProposalListResponse)
def list_meetings(
    status: Optional[str] = Query(None),
    stage: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    """Retrieves all meeting proposals."""
    query = db.query(MeetingProposalModel)
    if status:
        query = query.filter(MeetingProposalModel.status == status)
    if stage is not None:
        query = query.filter(MeetingProposalModel.stage == stage)

    total = query.count()
    proposals = query.order_by(MeetingProposalModel.created_at.desc()).all()
    return MeetingProposalListResponse(total=total, proposals=proposals)


@router.post("/{proposal_id}/confirm", response_model=MeetingProposalResponse)
def confirm_meeting(
    proposal_id: int,
    db: Session = Depends(get_db)
):
    """
    Advances Stage 1 (user draft review) to Stage 2 (auto-coordinated and confirmed on calendar).
    Picks the confirmed non-overlapping slot and commits booking to calendar and database.
    """
    proposal = db.query(MeetingProposalModel).filter(MeetingProposalModel.id == proposal_id).first()
    if not proposal:
        raise HTTPException(status_code=404, detail="Meeting proposal not found")

    slots = []
    if proposal.proposed_slots_json:
        try:
            slots = json.loads(proposal.proposed_slots_json)
        except Exception:
            slots = []

    # Query already confirmed slots from other proposals in DB
    other_confirmed = db.query(MeetingProposalModel).filter(
        MeetingProposalModel.id != proposal_id,
        (MeetingProposalModel.stage == 2) | (MeetingProposalModel.status == "confirmed")
    ).all()
    already_booked = set()
    for other in other_confirmed:
        if other.proposed_slots_json:
            try:
                for s in json.loads(other.proposed_slots_json):
                    if isinstance(s, dict) and "start_time" in s:
                        already_booked.add(s["start_time"])
            except Exception:
                pass

    # Pick the first slot that does not collide with existing bookings
    chosen_slot = None
    for s in slots:
        if isinstance(s, dict) and s.get("start_time") not in already_booked:
            chosen_slot = s
            break
    if not chosen_slot and slots:
        chosen_slot = slots[0]

    if chosen_slot:
        chosen_slot["confirmed"] = True
        proposal.proposed_slots_json = json.dumps([chosen_slot])
        if "display" in chosen_slot:
            proposal.requested_dates = chosen_slot["display"]

    proposal.status = "confirmed"
    proposal.stage = 2
    db.commit()
    db.refresh(proposal)

    # Schedule event on Outlook calendar
    participants = [p.strip() for p in (proposal.participants or "").split(",") if p.strip()]
    outlook_calendar_client.schedule_event(
        subject="Confirmed Meeting from Email Proposal",
        start_time=chosen_slot["start_time"] if chosen_slot else (proposal.requested_dates or "Tomorrow 2:00 PM"),
        end_time=chosen_slot.get("end_time", "02:30 PM") if chosen_slot else "Tomorrow 2:30 PM",
        attendees=participants
    )

    return proposal
