"""
Session model for chat sessions.
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime
from app.database import Base, UUIDType


class Session(Base):
    """
    Chat session model.

    Represents a conversation session with a specific LLM provider.
    """
    __tablename__ = "sessions"

    id = Column(UUIDType(), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    llm_provider = Column(String(50), nullable=False)  # openai, anthropic, google
    llm_model = Column(String(100), nullable=False)    # gpt-4, claude-sonnet-4, gemini-flash-2.0
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Session(id={self.id}, title={self.title}, provider={self.llm_provider})>"
