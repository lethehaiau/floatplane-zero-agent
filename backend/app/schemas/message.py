"""
Pydantic schemas for message endpoints.
"""
from datetime import datetime
from uuid import UUID
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

    class Config:
        from_attributes = True


class ChatRequest(BaseModel):
    """Schema for chat request."""
    session_id: UUID
    message: str = Field(..., min_length=1, description="User message")

    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "d7ad1d40-8583-4d40-bb27-6e120bac72ea",
                "message": "Explain how photosynthesis works"
            }
        }


class ChatResponse(BaseModel):
    """Schema for chat response (includes both user and assistant messages)."""
    user_message: MessageResponse
    assistant_message: MessageResponse
