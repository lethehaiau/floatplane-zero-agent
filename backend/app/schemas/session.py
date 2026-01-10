"""
Pydantic schemas for session endpoints.
"""
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field


class SessionCreate(BaseModel):
    """Schema for creating a new session."""
    title: Optional[str] = Field(None, max_length=255, description="Session title (auto-generated if not provided)")
    llm_provider: str = Field(..., description="LLM provider (openai, anthropic, google)")
    llm_model: str = Field(..., description="LLM model (gpt-4, claude-sonnet-4, gemini-flash-2.5)")

    class Config:
        json_schema_extra = {
            "example": {
                "title": "New Chat",
                "llm_provider": "openai",
                "llm_model": "gpt-4"
            }
        }


class SessionResponse(BaseModel):
    """Schema for session response."""
    id: UUID
    title: str
    llm_provider: str
    llm_model: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SessionListResponse(BaseModel):
    """Schema for listing sessions."""
    sessions: list[SessionResponse]
    total: int


class SessionUpdate(BaseModel):
    """Schema for updating a session."""
    title: Optional[str] = Field(None, max_length=255, description="Session title")
