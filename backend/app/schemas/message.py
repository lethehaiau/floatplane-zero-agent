"""
Pydantic schemas for message endpoints.
"""
from datetime import datetime
from uuid import UUID
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class MessageCreate(BaseModel):
    """Schema for creating a new message (user input)."""
    content: str = Field(..., min_length=1, description="Message content")

    class Config:
        json_schema_extra = {
            "example": {
                "content": "What is the weather like today?"
            }
        }


class MessageResponse(BaseModel):
    """Schema for message response."""
    id: UUID
    session_id: UUID
    role: str
    content: str
    created_at: datetime
    message_metadata: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


class FileMetadata(BaseModel):
    """Schema for file metadata attached to a message."""
    filename: str
    file_type: str


class ChatRequest(BaseModel):
    """Schema for chat request."""
    session_id: UUID
    message: str = Field(..., min_length=1, description="User message")
    files_metadata: Optional[List[FileMetadata]] = Field(None, description="File metadata to attach to this message")

    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "d7ad1d40-8583-4d40-bb27-6e120bac72ea",
                "message": "Explain how photosynthesis works",
                "files_metadata": [
                    {"filename": "document.pdf", "file_type": "pdf"}
                ]
            }
        }


class ChatResponse(BaseModel):
    """Schema for chat response (includes both user and assistant messages)."""
    user_message: MessageResponse
    assistant_message: MessageResponse
