"""
Database connection and session management.
"""
import uuid
from sqlalchemy import create_engine, TypeDecorator, CHAR
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings


class UUIDType(TypeDecorator):
    """
    UUID type that works with both PostgreSQL (UUID) and SQLite (CHAR(36)).

    Uses native UUID for PostgreSQL, falls back to CHAR(36) for SQLite.
    """
    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(PostgreSQLUUID(as_uuid=True))
        else:
            return dialect.type_descriptor(CHAR(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return value
        else:
            if isinstance(value, uuid.UUID):
                return str(value)
            return value

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return value
        else:
            if isinstance(value, str):
                return uuid.UUID(value)
            return value

# Create database engine with connection pooling
engine = create_engine(
    settings.DATABASE_URL,
    # Connection Pool Settings
    pool_size=5,              # Base pool: 5 persistent connections
    max_overflow=10,           # Burst capacity: +10 connections
    pool_timeout=30,           # Wait up to 30s for available connection
    pool_recycle=3600,         # Recycle connections after 1 hour (prevents stale connections)
    pool_pre_ping=True,        # Verify connection health before using (adds slight overhead)
    # Query Performance
    echo=False,                # Set to True for SQL query logging (debug only)
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()


def get_db():
    """
    Dependency for getting database session.
    Yields database session and ensures it's closed after use.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
