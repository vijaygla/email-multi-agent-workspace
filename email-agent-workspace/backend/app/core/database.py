"""
Database engine configuration, connection pooling, and session management for Microsoft SQL Server.
Supports automatic table creation and query execution.
"""
import logging
from typing import Generator
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import settings
from app.db.models import Base

logger = logging.getLogger(__name__)

# Configure SQLAlchemy engine with pyodbc
engine = create_engine(
    settings.sqlalchemy_database_url,
    pool_size=10,
    max_overflow=20,
    pool_recycle=1800,
    pool_pre_ping=True,
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Generator[Session, None, None]:
    """FastAPI Dependency for database session management."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db() -> None:
    """
    Initializes the MSSQL database: creates tables if they do not exist
    and verifies connection stability.
    """
    try:
        logger.info("Initializing Microsoft SQL Server database connection...")
        with engine.connect() as connection:
            result = connection.execute(text("SELECT DB_NAME() AS CurrentDB, @@VERSION AS Version"))
            row = result.fetchone()
            logger.info(f"Connected to MSSQL Database: {row[0]}")
            logger.info(f"MSSQL Engine Version: {row[1][:60]}...")

        # Create all tables defined in Base metadata
        Base.metadata.create_all(bind=engine)
        logger.info("MSSQL tables verified / created successfully.")
    except Exception as exc:
        logger.error(f"Failed to initialize database: {exc}", exc_info=True)
        raise exc
