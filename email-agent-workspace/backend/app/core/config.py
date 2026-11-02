"""
Enterprise configuration module using Pydantic Settings.
Loads environment variables and sets defaults for MSSQL, Nexus AI Engine, and Graph APIs.
"""
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
import os
from urllib.parse import quote_plus

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Application settings
    APP_NAME: str = "Enterprise Email Agent Workspace"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    ENABLE_GUARDRAILS: bool = True
    CORS_ORIGINS: List[str] = [
        "http://localhost:4200",
        "http://127.0.0.1:4200",
        "http://localhost:3000",
        "http://127.0.0.1:8000",
        "*"
    ]

    # Microsoft SQL Server settings
    MSSQL_SERVER: str = "LIN-5CD6268KRS"
    MSSQL_DATABASE: str = "EmailAgentWorkSpaceDb"
    MSSQL_USER: str = "sa"
    MSSQL_PASSWORD: str = "Capgemini@12345"
    MSSQL_DRIVER: str = "ODBC Driver 18 for SQL Server"
    MSSQL_TRUST_CERT: str = "yes"
    MSSQL_CONNECTION_STRING: str = (
        "DRIVER={ODBC Driver 18 for SQL Server};"
        "SERVER=LIN-5CD6268KRS;"
        "DATABASE=EmailAgentWorkSpaceDb;"
        "UID=sa;"
        "PWD=Capgemini@12345;"
        "TrustServerCertificate=yes;"
    )

    @property
    def sqlalchemy_database_url(self) -> str:
        """Returns the SQLAlchemy connection URL with ODBC formatting."""
        params = (
            f"DRIVER={self.MSSQL_DRIVER};"
            f"SERVER={self.MSSQL_SERVER};"
            f"DATABASE={self.MSSQL_DATABASE};"
            f"UID={self.MSSQL_USER};"
            f"PWD={self.MSSQL_PASSWORD};"
            f"TrustServerCertificate={self.MSSQL_TRUST_CERT};"
        )
        return f"mssql+pyodbc:///?odbc_connect={quote_plus(params)}"

    # Nexus Generative Engine Platform
    CAPGEMINI_API_KEY: str = "sk-x3FOSdELzRNhQ1fpzloftA"
    CAPGEMINI_BASE_URL: str = "https://openai.generative.engine.capgemini.com/v1"
    CAPGEMINI_WS_URL: str = "wss://ws.generative.engine.capgemini.com/"
    NEXUS_API_KEY: str = "sk-x3FOSdELzRNhQ1fpzloftA"
    NEXUS_BASE_URL: str = "https://openai.generative.engine.capgemini.com/v1"
    NEXUS_WS_URL: str = "wss://ws.generative.engine.capgemini.com/"

    # Multi-Model Orchestration
    MODEL_ROUTER: str = "amazon.nova-micro-v1:0"
    MODEL_EXTRACTOR: str = "amazon.nova-micro-v1:0"
    MODEL_REASONING: str = "anthropic.claude-sonnet-5"
    MODEL_DRAFTING: str = "anthropic.claude-sonnet-5"
    MODEL_FALLBACK: str = "openai.gpt-4o"
    MODEL_EMBEDDING: str = "amazon.titan-embed-text-v2:0"

    # Microsoft Graph / Outlook credentials
    MS_GRAPH_CLIENT_ID: str = ""
    MS_GRAPH_CLIENT_SECRET: str = ""
    MS_GRAPH_TENANT_ID: str = ""
    USE_MOCK_OUTLOOK: bool = True

    # Autonomous & Autopilot Operations
    # L0 = Manual trigger only
    # L1 = Assisted (Auto-extract & stage draft)
    # L2 = Semi-Autonomous (Auto-approve & dispatch routine high-confidence emails)
    # L3 = Full Autopilot (End-to-end auto-schedule & auto-dispatch)
    AUTONOMY_LEVEL: str = "L1"
    AUTOPILOT_CONFIDENCE_THRESHOLD: float = 0.85
    BACKGROUND_POLLING_ENABLED: bool = False
    BACKGROUND_POLLING_INTERVAL_SECONDS: int = 30
    THREAD_CONTEXT_ENABLED: bool = True
    TASK_DEDUPLICATION_ENABLED: bool = True
    CRITIC_VERIFICATION_ENABLED: bool = True

    # User Persona & Corporate Scheduling Preferences
    USER_WORKING_HOURS_START: str = "09:00"
    USER_WORKING_HOURS_END: str = "17:00"
    USER_MEETING_BUFFER_MINUTES: int = 15
    USER_DEFAULT_TIMEZONE: str = "EST"

settings = Settings()

