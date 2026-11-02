"""
Integration tests for Autopilot operations, runtime configuration, and autonomous workflows.
"""
import pytest
from app.core.config import settings

def test_autopilot_status_endpoint(client):
    res = client.get("/api/autopilot/status")
    assert res.status_code == 200
    data = res.json()
    assert "autonomy_level" in data
    assert "is_running" in data
    assert "confidence_threshold" in data

def test_autopilot_configure_endpoint(client):
    res = client.post("/api/autopilot/configure", json={
        "autonomy_level": "L2",
        "confidence_threshold": 0.80,
        "background_polling_enabled": False
    })
    assert res.status_code == 200
    data = res.json()["current_config"]
    assert data["autonomy_level"] == "L2"
    assert data["confidence_threshold"] == 0.80

    # Reset back to L1
    client.post("/api/autopilot/configure", json={"autonomy_level": "L1"})

def test_autopilot_execution_l2_auto_approves(client, sample_case1_email):
    # Set to L2 Semi-Autonomous mode
    client.post("/api/autopilot/configure", json={
        "autonomy_level": "L2",
        "confidence_threshold": 0.60
    })

    # Ingest email
    res_ingest = client.post("/api/emails", json=sample_case1_email)
    assert res_ingest.status_code == 201
    email_id = res_ingest.json()["id"]

    # Process email
    res_proc = client.post("/api/process", json={"email_id": email_id, "tone": "professional"})
    assert res_proc.status_code == 200
    data = res_proc.json()

    # Draft should be auto-approved in L2 mode
    assert data["draft"]["status"] in ["approved", "sent"]
    assert data["autopilot"]["executed"] is True
    assert len(data["autopilot"]["actions"]) >= 1

    # Reset back to L1
    client.post("/api/autopilot/configure", json={"autonomy_level": "L1"})

def test_autopilot_poll_now_endpoint(client):
    res = client.post("/api/autopilot/poll-now")
    assert res.status_code == 200
    assert "Immediate poll completed" in res.json()["message"]
