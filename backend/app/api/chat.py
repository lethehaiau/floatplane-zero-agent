"""
Chat API endpoints.
"""
import json
import os
from datetime import datetime
from typing import AsyncGenerator

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session as DBSession
import litellm

from app.database import get_db, SessionLocal
from app.models.session import Session
from app.models.message import Message
from app.schemas.message import ChatRequest, ChatResponse, MessageResponse
from app.config import settings

router = APIRouter(prefix="/api/chat", tags=["chat"])

# Configure LiteLLM - set environment variables for each provider
# LiteLLM automatically reads these when making API calls
if settings.OPENAI_API_KEY:
    os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY
if settings.ANTHROPIC_API_KEY:
    os.environ["ANTHROPIC_API_KEY"] = settings.ANTHROPIC_API_KEY
if settings.GOOGLE_API_KEY:
    os.environ["GEMINI_API_KEY"] = settings.GOOGLE_API_KEY


@router.post("", response_model=ChatResponse)
async def send_message(
    chat_request: ChatRequest,
    db: DBSession = Depends(get_db)
):
    """
    Send a message and get a response from GPT-4 (non-streaming).

    - **session_id**: ID of the session to add message to
    - **message**: User message content
    """
    # Verify session exists
    session = db.query(Session).filter(Session.id == chat_request.session_id).first()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {chat_request.session_id} not found"
        )

    # Create user message
    user_message = Message(
        session_id=chat_request.session_id,
        role="user",
        content=chat_request.message
    )
    db.add(user_message)
    db.commit()
    db.refresh(user_message)

    # Get all previous messages in this session for context
    previous_messages = db.query(Message).filter(
        Message.session_id == chat_request.session_id
    ).order_by(Message.created_at).all()

    # Build conversation history for OpenAI
    messages = [
        {"role": msg.role, "content": msg.content}
        for msg in previous_messages
    ]

    try:
        # Call OpenAI API (non-streaming)
        response = openai_client.chat.completions.create(
            model=session.llm_model,
            messages=messages,
            temperature=0.7,
            max_tokens=1000
        )

        # Extract assistant response
        assistant_content = response.choices[0].message.content

        # Create assistant message
        assistant_message = Message(
            session_id=chat_request.session_id,
            role="assistant",
            content=assistant_content
        )
        db.add(assistant_message)

        # Update session updated_at timestamp
        session.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(assistant_message)

        return ChatResponse(
            user_message=user_message,
            assistant_message=assistant_message
        )

    except Exception as e:
        # Rollback if LLM call fails
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get response from OpenAI: {str(e)}"
        )


@router.get("/sessions/{session_id}/messages", response_model=list[MessageResponse])
async def get_session_messages(
    session_id: str,
    db: DBSession = Depends(get_db)
):
    """
    Get all messages for a session.
    """
    # Verify session exists
    session = db.query(Session).filter(Session.id == session_id).first()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found"
        )

    # Get all messages
    messages = db.query(Message).filter(
        Message.session_id == session_id
    ).order_by(Message.created_at).all()

    return messages


@router.post("/stream")
async def stream_chat(
    chat_request: ChatRequest,
    db: DBSession = Depends(get_db)
):
    """
    Send a message and stream the response via SSE.

    SSE Event Types:
    - content_delta: {"chunk": "text"} - Streamed text chunk
    - user_message: {"message": {...}} - User message saved
    - done: {"message_id": "uuid"} - Response complete
    - error: {"detail": "error message"} - Error occurred
    """
    # Verify session exists and get model info
    session = db.query(Session).filter(Session.id == chat_request.session_id).first()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {chat_request.session_id} not found"
        )

    # Store session info we need (before db session closes)
    session_id = session.id
    llm_model = session.llm_model

    # Create user message
    user_message = Message(
        session_id=session_id,
        role="user",
        content=chat_request.message
    )
    db.add(user_message)
    db.commit()
    db.refresh(user_message)

    # Store user message info for the generator
    user_msg_data = {
        "id": str(user_message.id),
        "session_id": str(user_message.session_id),
        "role": user_message.role,
        "content": user_message.content,
        "created_at": user_message.created_at.isoformat()
    }

    # Get all previous messages for context (before db session closes)
    previous_messages = db.query(Message).filter(
        Message.session_id == session_id
    ).order_by(Message.created_at).all()

    # Build conversation history for LLM
    llm_messages = [
        {"role": msg.role, "content": msg.content}
        for msg in previous_messages
    ]

    async def generate() -> AsyncGenerator[str, None]:
        """Generate SSE events for streaming response."""
        # Send user message confirmation
        yield f"event: user_message\ndata: {json.dumps(user_msg_data)}\n\n"

        try:
            # Stream response using LiteLLM
            response = await litellm.acompletion(
                model=llm_model,
                messages=llm_messages,
                temperature=0.7,
                max_tokens=4096,
                stream=True
            )

            # Collect full response for saving
            full_content = ""

            async for chunk in response:
                try:
                    if chunk.choices and len(chunk.choices) > 0:
                        delta = chunk.choices[0].delta
                        # Get content - handle different response formats
                        content = getattr(delta, 'content', None)
                        if content:
                            full_content += content
                            yield f"event: content_delta\ndata: {json.dumps({'chunk': content})}\n\n"
                except (AttributeError, IndexError) as e:
                    # Log but continue processing
                    print(f"Warning: Error processing chunk: {e}")
                    continue

            # Save assistant message using a fresh db session
            with SessionLocal() as save_db:
                assistant_message = Message(
                    session_id=session_id,
                    role="assistant",
                    content=full_content
                )
                save_db.add(assistant_message)

                # Update session timestamp
                db_session = save_db.query(Session).filter(Session.id == session_id).first()
                if db_session:
                    db_session.updated_at = datetime.utcnow()

                save_db.commit()
                save_db.refresh(assistant_message)

                # Send done event
                done_data = {
                    "message_id": str(assistant_message.id),
                    "message": {
                        "id": str(assistant_message.id),
                        "session_id": str(assistant_message.session_id),
                        "role": assistant_message.role,
                        "content": assistant_message.content,
                        "created_at": assistant_message.created_at.isoformat()
                    }
                }
                yield f"event: done\ndata: {json.dumps(done_data)}\n\n"

        except Exception as e:
            # Send error event
            yield f"event: error\ndata: {json.dumps({'detail': str(e)})}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )
