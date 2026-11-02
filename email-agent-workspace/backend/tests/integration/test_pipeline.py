"""
End-to-End Pipeline Integration Tests.
Verifies all 5 use cases through FastAPI endpoints and MSSQL persistence.
"""
import pytest

def test_root_status(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "Nexus" in data["app_name"] or "Workspace" in data["app_name"]

def test_case1_meeting_scheduling_pipeline(client, sample_case1_email):
    # Ingest email
    res_ingest = client.post("/api/emails", json=sample_case1_email)
    assert res_ingest.status_code == 201
    email_id = res_ingest.json()["id"]

    # Trigger multi-agent pipeline
    res_proc = client.post("/api/process", json={"email_id": email_id, "tone": "professional"})
    assert res_proc.status_code == 200
    data = res_proc.json()
    assert data["intent"] in ["meeting", "mixed_intent"]
    assert data["status"] == "processed"
    assert data["meeting_proposal"] is not None
    assert len(data["meeting_proposal"]["proposed_slots"]) >= 1

    # Confirm proposal (Stage 1 -> Stage 2)
    proposal_id = data["meeting_proposal"]["id"]
    res_conf = client.post(f"/api/scheduled-meetings/{proposal_id}/confirm")
    assert res_conf.status_code == 200
    assert res_conf.json()["stage"] == 2

def test_case2_task_extraction_pipeline(client, sample_case2_email):
    # Ingest email
    res_ingest = client.post("/api/emails", json=sample_case2_email)
    assert res_ingest.status_code == 201
    email_id = res_ingest.json()["id"]

    # Trigger multi-agent pipeline
    res_proc = client.post("/api/process", json={"email_id": email_id, "tone": "professional"})
    assert res_proc.status_code == 200
    data = res_proc.json()
    assert data["intent"] in ["task", "mixed_intent"]
    assert len(data["tasks"]) >= 1

    # Verify tasks are persisted in MSSQL via /api/tasks
    res_tasks = client.get(f"/api/tasks?email_id={email_id}")
    assert res_tasks.status_code == 200
    tasks_list = res_tasks.json()["tasks"]
    assert len(tasks_list) >= 1
    assert "deck" in tasks_list[0]["title"].lower() or "budget" in tasks_list[0]["title"].lower()

def test_case3_mixed_intent_pipeline(client, sample_case3_email):
    # Ingest email
    res_ingest = client.post("/api/emails", json=sample_case3_email)
    assert res_ingest.status_code == 201
    email_id = res_ingest.json()["id"]

    # Trigger multi-agent pipeline
    res_proc = client.post("/api/process", json={"email_id": email_id, "tone": "professional"})
    assert res_proc.status_code == 200
    data = res_proc.json()
    assert data["intent"] in ["mixed_intent", "meeting", "task"]
    assert data["status"] == "processed"
    # Should have both meeting proposal and task data
    assert data["meeting_proposal"] is not None or len(data["tasks"]) >= 1

def test_case4_draft_approval_and_send(client):
    # Manually compose draft
    res_compose = client.post("/api/compose", json={
        "recipient": "client@nexus.ai",
        "subject": "Re: Follow up",
        "body": "Here are the suggested meeting slots.",
        "tone": "executive"
    })
    assert res_compose.status_code == 201
    draft_id = res_compose.json()["id"]

    # Approve draft
    res_approve = client.post(f"/api/drafts/{draft_id}/approve")
    assert res_approve.status_code == 200
    assert res_approve.json()["status"] == "approved"

    # Send draft
    res_send = client.post(f"/api/drafts/{draft_id}/send")
    assert res_send.status_code == 200
    assert res_send.json()["status"] == "sent"

def test_case5_clarification_workflow(client, sample_case5_email):
    # Ingest ambiguous email
    res_ingest = client.post("/api/emails", json=sample_case5_email)
    assert res_ingest.status_code == 201
    email_id = res_ingest.json()["id"]

    # Trigger multi-agent pipeline
    res_proc = client.post("/api/process", json={"email_id": email_id, "tone": "professional"})
    assert res_proc.status_code == 200
    data = res_proc.json()
    assert data["status"] == "clarification_needed"
    assert data["clarification"] is not None

    clarification_id = data["clarification"]["id"]

    # Answer clarification
    res_reply = client.post(f"/api/clarifications/{clarification_id}/reply", json={
        "answer": "Tomorrow afternoon between 2:00 PM and 3:00 PM EST"
    })
    assert res_reply.status_code == 200
    assert res_reply.json()["status"] == "resolved"
