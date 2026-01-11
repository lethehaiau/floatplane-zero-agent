"""
File model for uploaded files.
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship, backref
from app.database import Base, UUIDType


class File(Base):
    """
    File model.

    Represents an uploaded file (PDF, TXT, MD) with extracted text.
    """
    __tablename__ = "files"

    id = Column(UUIDType(), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUIDType(), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(512), nullable=False)  # Path to file on disk
    file_size = Column(Integer, nullable=False)  # Size in bytes
    file_type = Column(String(50), nullable=False)  # pdf, txt, md
    extracted_text = Column(Text, nullable=True)  # Extracted text content (max 100K chars)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationship to session
    session = relationship(
        "Session",
        backref=backref("files", cascade="all, delete-orphan", passive_deletes=True)
    )

    def __repr__(self):
        return f"<File(id={self.id}, filename={self.filename}, session_id={self.session_id})>"
