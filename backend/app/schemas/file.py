"""
Pydantic schemas for file endpoints.
"""
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel


class FileResponse(BaseModel):
    """Schema for file response."""
    id: UUID
    session_id: UUID
    filename: str
    file_size: int
    file_type: str
    created_at: datetime

    class Config:
        from_attributes = True
