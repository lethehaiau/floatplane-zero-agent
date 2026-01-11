"""
Test fixtures and configuration.
"""
import os
import tempfile
import shutil
from typing import Generator
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models.session import Session
from app.models.message import Message
from app.models.file import File
from app.utils.storage import storage


# Use in-memory SQLite for tests
TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    """Create a fresh database for each test."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    """Create a test client with test database."""
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def temp_storage():
    """Create temporary storage directory for file tests."""
    from pathlib import Path

    temp_dir = tempfile.mkdtemp()
    original_base_path = storage.base_path
    storage.base_path = Path(temp_dir)

    yield temp_dir

    # Cleanup
    storage.base_path = original_base_path
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)


# Helper functions for creating test data

def create_test_session(db, title="Test Session", llm_model="gpt-4o-mini"):
    """Create a test session."""
    session = Session(
        title=title,
        llm_provider="openai",
        llm_model=llm_model
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def create_test_message(db, session_id, role="user", content="Test message", metadata=None):
    """Create a test message."""
    message = Message(
        session_id=session_id,
        role=role,
        content=content,
        message_metadata=metadata
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    return message


def create_test_file(db, session_id, filename="test.txt", content="Test content", file_type="txt"):
    """Create a test file record and physical file."""
    from uuid import uuid4

    file_id = uuid4()
    file_path = storage.save_file(session_id, file_id, filename, content.encode())

    file_record = File(
        id=file_id,
        session_id=session_id,
        filename=filename,
        file_path=file_path,
        file_type=file_type,
        file_size=len(content),
        extracted_text=content
    )
    db.add(file_record)
    db.commit()
    db.refresh(file_record)
    return file_record
