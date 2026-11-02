"""
Unit tests for individual agents in isolation.
Tests Reader, Router, Entity Extractor, Task Extractor, Supervisor, and Reply Generator.
"""
import pytest
from app.agents.reader import reader_agent
from app.agents.router import router_agent
from app.agents.entity_extractor import entity_extractor_agent
from app.agents.task_extractor import task_extractor_agent
from app.agents.supervisor import supervisor_agent
from app.agents.reply_generator import reply_generator_agent

def test_reader_agent_cleans_disclaimers():
    raw_body = (
        "Hi John, let's meet tomorrow at 3 PM.\n\n"
        "-- \nThis message contains confidential information intended only for the recipient."
    )
    result = reader_agent.clean_email_body(raw_body)
    assert "confidential information" not in result
    assert "let's meet tomorrow at 3 PM" in result

def test_router_agent_meeting_intent():
    res = router_agent.route("Discussion", "Can we meet tomorrow afternoon for 30 minutes?")
    assert res["intent"] in ["meeting", "mixed_intent"]
    assert res["confidence"] > 0.5

def test_router_agent_task_intent():
    res = router_agent.route("Action required", "Please send the revised budget deck by Friday 5 PM.")
    assert res["intent"] in ["task", "mixed_intent"]
    assert res["has_task_intent"] is True

def test_router_agent_mixed_intent():
    res = router_agent.route("Budget & Sync", "Please send the budget deck by Friday. Also let's meet tomorrow afternoon.")
    assert res["intent"] == "mixed_intent" or (res["has_meeting_intent"] and res["has_task_intent"])

def test_entity_extractor_slots():
    res = entity_extractor_agent.extract_and_find_slots(
        "Sync", "Let's meet tomorrow afternoon", "sarah@nexus.ai"
    )
    assert "proposed_slots" in res
    assert len(res["proposed_slots"]) >= 1
    assert "sarah@nexus.ai" in res["participants"]

def test_task_extractor_action_items():
    tasks = task_extractor_agent.extract_tasks(
        "Budget Deck", "Send the budget deck by Friday. This is urgent.", "sarah@nexus.ai"
    )
    assert len(tasks) >= 1
    first_task = tasks[0]
    assert "title" in first_task
    assert "due_date" in first_task
    assert first_task["urgency"] in ["low", "medium", "high", "urgent"]

def test_supervisor_detects_ambiguity():
    audit = supervisor_agent.audit(
        subject="Quick catchup",
        body="Hey, let's connect sometime whenever you are free to discuss that thing.",
        intent="meeting"
    )
    assert audit["needs_clarification"] is True
    assert len(audit.get("options", [])) > 0

def test_reply_generator_tones():
    draft = reply_generator_agent.draft_reply(
        subject="Sync",
        body="Let's meet tomorrow",
        sender="sarah@nexus.ai",
        recipient="user@nexus.ai",
        intent="meeting",
        meeting_slots=[{"display": "Tomorrow 2:00 PM - 2:30 PM"}],
        tone="professional"
    )
    assert "Re: Sync" in draft["subject"]
    assert "2:00 PM" in draft["body"]
    assert draft["tone"] == "professional"
