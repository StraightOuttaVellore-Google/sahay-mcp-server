"""
PostgreSQL Database Client for MCP Server

This module provides database connectivity for the MCP server to use the same
PostgreSQL database as the main backend application. This ensures data consistency
and eliminates the Firebase/PostgreSQL split.

Usage:
    from .db_client import get_db_client
    
    db = get_db_client()
    with db.get_session() as session:
        # Use session for queries
        pass
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
import os
from dotenv import load_dotenv
import logging

load_dotenv()

logger = logging.getLogger(__name__)


class DatabaseClient:
    """
    PostgreSQL database client for MCP server tools.
    Provides connection pooling and session management.
    """
    
    def __init__(self):
        """Initialize database connection using environment variables"""
        db_user = os.getenv('DB_USER')
        db_password = os.getenv('DB_PASSWORD')
        db_host = os.getenv('DB_HOST', 'localhost')
        db_port = os.getenv('DB_PORT', '5432')
        db_name = os.getenv('DB_NAME')
        
        if not all([db_user, db_password, db_name]):
            raise ValueError(
                "Missing required database environment variables: "
                "DB_USER, DB_PASSWORD, DB_NAME"
            )
        
        # Construct PostgreSQL connection URL
        self.db_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
        
        # Create engine with connection pooling
        self.engine = create_engine(
            self.db_url,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True,  # Verify connections before using
            echo=False  # Set to True for SQL debugging
        )
        
        # Create session factory
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )
        
        logger.info(f"PostgreSQL client initialized: {db_host}:{db_port}/{db_name}")
    
    @contextmanager
    def get_session(self) -> Session:
        """
        Get a database session with automatic cleanup.
        
        Usage:
            with db.get_session() as session:
                result = session.execute(...)
                session.commit()
        
        Yields:
            Session: SQLAlchemy database session
        """
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            session.close()
    
    def test_connection(self) -> bool:
        """
        Test database connectivity.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            with self.get_session() as session:
                session.execute(text("SELECT 1"))
            logger.info("Database connection test successful")
            return True
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False


# Global database client instance
_db_client = None


def get_db_client() -> DatabaseClient:
    """
    Get the global database client instance (singleton pattern).
    
    Returns:
        DatabaseClient: The database client instance
    """
    global _db_client
    if _db_client is None:
        _db_client = DatabaseClient()
    return _db_client


def close_db_client():
    """Close the database client and dispose of connections"""
    global _db_client
    if _db_client is not None:
        _db_client.engine.dispose()
        _db_client = None
        logger.info("Database client closed")

