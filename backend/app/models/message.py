"""
Message model for chat messages.
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, backref
from app.database import Base


class Message(Base):
    """
    Chat message model.

    Represents a single message in a conversation (user or assistant).
    """
    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False)
    role = Column(String(20), nullable=False)  # "user" or "assistant"
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationship to session
    session = relationship(
        "Session",
        backref=backref("messages", cascade="all, delete-orphan", passive_deletes=True)
    )

    def __repr__(self):
        return f"<Message(id={self.id}, role={self.role}, session_id={self.session_id})>"
