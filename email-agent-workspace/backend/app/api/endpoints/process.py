"""
API Endpoint for Process Coordination.
Triggers the multi-agent orchestrator pipeline on an ingested email.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.agents.orchestrator import orchestrator
from app.schemas.response import ProcessRequest, ProcessResponse

router = APIRouter()

@router.post("", response_model=ProcessResponse)
async def process_email(
    request: ProcessRequest,
    db: Session = Depends(get_db)
):
    """
    Executes the multi-agent loop (Observe -> Think -> Act) on the specified email.
    Handles Case 1 (Calendar), Case 2 (Task), Case 3 (Mixed Intent), Case 4 (Draft), and Case 5 (Clarification).
    """
    try:
        result = await orchestrator.process_email(
            email_id=request.email_id,
            db=db,
            tone=request.tone or "professional"
        )
        return ProcessResponse(**result)
    except ValueError as val_err:
        raise HTTPException(status_code=404, detail=str(val_err))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Agent workflow error: {str(exc)}")
