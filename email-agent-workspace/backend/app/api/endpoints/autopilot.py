"""
API Endpoints for Autonomous Operations & Autopilot Governance.
Provides real-time inspection and runtime configuration for:
- Autonomy Level (L0 Manual, L1 Assisted, L2 Semi-Autonomous, L3 Full Autopilot)
- Background Polling Daemon state and manual trigger
- Confidence thresholds and scheduling policies
"""
from typing import Optional
from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException
from app.core.config import settings
from app.core.background_worker import autonomous_worker

router = APIRouter()

class AutopilotConfigUpdate(BaseModel):
    autonomy_level: Optional[str] = Field(None, description="L0, L1, L2, L3")
    background_polling_enabled: Optional[bool] = None
    confidence_threshold: Optional[float] = Field(None, ge=0.0, le=1.0)
    poll_interval_seconds: Optional[int] = Field(None, ge=5, le=3600)
    task_deduplication_enabled: Optional[bool] = None
    critic_verification_enabled: Optional[bool] = None

@router.get("/status")
def get_autopilot_status():
    """Returns the live status of the autonomous engine and background poller."""
    return autonomous_worker.get_status()

@router.post("/configure")
def configure_autopilot(config: AutopilotConfigUpdate):
    """Updates runtime autonomy configurations without restarting the server."""
    if config.autonomy_level is not None:
        valid_levels = ["L0", "L1", "L2", "L3"]
        if config.autonomy_level.upper() not in valid_levels:
            raise HTTPException(status_code=400, detail=f"Invalid autonomy level. Must be one of: {valid_levels}")
        settings.AUTONOMY_LEVEL = config.autonomy_level.upper()

    if config.background_polling_enabled is not None:
        settings.BACKGROUND_POLLING_ENABLED = config.background_polling_enabled

    if config.confidence_threshold is not None:
        settings.AUTOPILOT_CONFIDENCE_THRESHOLD = config.confidence_threshold

    if config.poll_interval_seconds is not None:
        settings.BACKGROUND_POLLING_INTERVAL_SECONDS = config.poll_interval_seconds

    if config.task_deduplication_enabled is not None:
        settings.TASK_DEDUPLICATION_ENABLED = config.task_deduplication_enabled

    if config.critic_verification_enabled is not None:
        settings.CRITIC_VERIFICATION_ENABLED = config.critic_verification_enabled

    return {
        "message": "Autopilot settings updated successfully",
        "current_config": autonomous_worker.get_status()
    }

@router.post("/poll-now")
async def trigger_poll_now():
    """Manually triggers an immediate autonomous polling and ingestion cycle."""
    result = await autonomous_worker.poll_once()
    return {
        "message": "Immediate poll completed",
        "result": result
    }

@router.post("/worker/start")
def start_background_worker():
    """Starts the background worker polling daemon."""
    autonomous_worker.start()
    return {"message": "Background worker started", "status": autonomous_worker.get_status()}

@router.post("/worker/stop")
def stop_background_worker():
    """Stops the background worker polling daemon."""
    autonomous_worker.stop()
    return {"message": "Background worker stopped", "status": autonomous_worker.get_status()}
