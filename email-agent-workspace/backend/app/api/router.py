"""
Main API Router. Aggregates all endpoint modules.
"""
from fastapi import APIRouter
from app.api.endpoints import emails, process, tasks, meetings, actions, autopilot

api_router = APIRouter(prefix="/api")

api_router.include_router(emails.router, prefix="/emails", tags=["Emails"])
api_router.include_router(process.router, prefix="/process", tags=["Multi-Agent Process"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["Tasks"])
api_router.include_router(meetings.router, prefix="/scheduled-meetings", tags=["Meetings"])
api_router.include_router(actions.router, tags=["Actions"])
api_router.include_router(autopilot.router, prefix="/autopilot", tags=["Autopilot"])

