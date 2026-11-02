"""
Enterprise Email Agent Workspace - FastAPI Main Entry Point.
Integrates MSSQL persistence, Nexus Generative Engine, multi-agent orchestration,
and real-time WebSocket event streaming.
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.database import init_db
from app.core.guardrails import GuardrailViolation
from app.api.router import api_router
from app.agents.orchestrator import ws_manager
from app.core.background_worker import autonomous_worker

# Configure structured logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("EmailAgentWorkspace")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle hook managing startup and shutdown routines."""
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}...")
    try:
        init_db()
        logger.info("Database connection and schema initialization successful.")
    except Exception as e:
        logger.error(f"Critical error during startup database initialization: {e}")

    # Start background polling worker if enabled
    if settings.BACKGROUND_POLLING_ENABLED:
        autonomous_worker.start()

    yield

    autonomous_worker.stop()
    logger.info("Shutting down Email Agent Workspace application.")

# Initialize FastAPI App
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Enterprise Multi-Agent Email Workspace with Nexus AI Engine & Microsoft SQL Server",
    lifespan=lifespan
)

# Configure CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Custom Exception Handlers
@app.exception_handler(GuardrailViolation)
async def guardrail_violation_handler(request: Request, exc: GuardrailViolation):
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc), "violation_type": exc.violation_type}
    )

# Mount API Routers
app.include_router(api_router)

# Health & System Status Endpoint
@app.get("/", tags=["System"])
def root_status():
    return {
        "status": "online",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "database": {
            "server": settings.MSSQL_SERVER,
            "database": settings.MSSQL_DATABASE,
            "engine": "Microsoft SQL Server"
        },
        "generative_engine": {
            "endpoint": settings.NEXUS_BASE_URL,
            "models": {
                "router": settings.MODEL_ROUTER,
                "extractor": settings.MODEL_EXTRACTOR,
                "reasoning": settings.MODEL_REASONING,
                "drafting": settings.MODEL_DRAFTING,
                "fallback": settings.MODEL_FALLBACK
            }
        },
        "autopilot": autonomous_worker.get_status(),
        "realtime_ws": "/ws/stream"
    }

# Real-time WebSocket Event Stream Endpoint
@app.websocket("/ws/stream")
async def websocket_event_stream(websocket: WebSocket):
    """
    Subscribes client to real-time multi-agent execution steps (Observe -> Think -> Act).
    Streams agent decisions, extraction steps, and state updates live.
    """
    await ws_manager.connect(websocket)
    try:
        await websocket.send_json({
            "event_type": "connection_established",
            "message": "Connected to Email Agent Workspace Real-time Stream",
            "app": settings.APP_NAME
        })
        while True:
            # Keep socket alive and receive client signals
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception as e:
        logger.warning(f"WebSocket client error: {e}")
        ws_manager.disconnect(websocket)
