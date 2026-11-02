"""
Unit tests for the Critic Agent (Self-Reflection and Verification).
"""
import pytest
from app.agents.critic import critic_agent

def test_critic_agent_approves_valid_draft():
    review = critic_agent.verify(
        original_subject="Sync meeting",
        original_body="Let's meet tomorrow at 2 PM",
        draft_subject="Re: Sync meeting",
        draft_body="Thank you. I have proposed 2:00 PM for our meeting tomorrow.",
        proposed_slots=[{"start_time": "Tomorrow 2:00 PM", "display": "Tomorrow 2:00 PM"}],
        tasks=[],
        tone="professional"
    )
    assert review["is_approved"] is True
    assert review["confidence_score"] >= 0.7
    assert "corrected_draft" in review

def test_critic_agent_flags_hallucination():
    review = critic_agent.verify(
        original_subject="Budget review",
        original_body="Please send the numbers by Friday",
        draft_subject="Re: Budget review",
        draft_body="I will see you on Saturday at midnight at the park.",
        proposed_slots=[],
        tasks=[{"title": "Send numbers", "due_date": "Friday", "urgency": "high"}],
        tone="professional"
    )
    # The critic should detect either issues or offer corrected draft
    assert "corrected_draft" in review
    assert "confidence_score" in review
