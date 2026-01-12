"""
Chat API endpoints.
"""
import json
import logging
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
from app.models.file import File
from app.schemas.message import ChatRequest, ChatResponse, MessageResponse
from app.config import settings
from app.tools.search import search_internet
from app.tools.definitions import AVAILABLE_TOOLS

router = APIRouter(prefix="/api/chat", tags=["chat"])
logger = logging.getLogger(__name__)

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

    # Build file metadata for user message from request
    file_metadata = None
    if chat_request.files_metadata:
        file_metadata = {
            "files": [
                {
                    "filename": f.filename,
                    "file_type": f.file_type
                }
                for f in chat_request.files_metadata
            ]
        }

    # Create user message with file metadata
    user_message = Message(
        session_id=chat_request.session_id,
        role="user",
        content=chat_request.message,
        message_metadata=file_metadata
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
        # Call LLM API (non-streaming)
        response = litellm.completion(
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

    # Build file metadata for user message from request
    file_metadata = None
    if chat_request.files_metadata:
        file_metadata = {
            "files": [
                {
                    "filename": f.filename,
                    "file_type": f.file_type
                }
                for f in chat_request.files_metadata
            ]
        }

    # Create user message with file metadata
    user_message = Message(
        session_id=session_id,
        role="user",
        content=chat_request.message,
        message_metadata=file_metadata
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
        "created_at": user_message.created_at.isoformat(),
        "message_metadata": user_message.message_metadata
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

    session_files = db.query(File).filter(
        File.session_id == session_id
    ).order_by(File.created_at).all()

    # If there are files, prepend them as a system message
    if session_files:
        files_content = []
        for file in session_files:
            file_text = f"[File: {file.filename}]\n{file.extracted_text}\n[End of file]"
            files_content.append(file_text)

        system_message = {
            "role": "system",
            "content": "The following files have been uploaded by the user. Use their content to answer questions:\n\n" + "\n\n".join(files_content)
        }
        llm_messages.insert(0, system_message)

    async def generate() -> AsyncGenerator[str, None]:
        """Generate SSE events for streaming response."""
        # Send user message confirmation
        yield f"event: user_message\ndata: {json.dumps(user_msg_data)}\n\n"

        try:
            # Stream response using LiteLLM with tools
            response = await litellm.acompletion(
                model=llm_model,
                messages=llm_messages,
                tools=AVAILABLE_TOOLS,
                temperature=0.7,
                max_tokens=4096,
                stream=True
            )

            # Collect full response for saving
            full_content = ""
            tool_calls_accumulator = []

            async for chunk in response:
                try:
                    if chunk.choices and len(chunk.choices) > 0:
                        delta = chunk.choices[0].delta

                        # Handle tool calls
                        if hasattr(delta, 'tool_calls') and delta.tool_calls:
                            for tool_call in delta.tool_calls:
                                # Accumulate tool call data
                                if len(tool_calls_accumulator) <= tool_call.index:
                                    tool_calls_accumulator.append({
                                        "id": tool_call.id,
                                        "type": "function",
                                        "function": {
                                            "name": tool_call.function.name if tool_call.function.name else "",
                                            "arguments": tool_call.function.arguments if tool_call.function.arguments else ""
                                        }
                                    })
                                else:
                                    # Append to existing tool call arguments
                                    if tool_call.function.arguments:
                                        tool_calls_accumulator[tool_call.index]["function"]["arguments"] += tool_call.function.arguments

                        # Handle regular content
                        content = getattr(delta, 'content', None)
                        if content:
                            full_content += content
                            yield f"event: content_delta\ndata: {json.dumps({'chunk': content})}\n\n"

                except (AttributeError, IndexError) as e:
                    # Log error and send error event to frontend
                    logger.error(f"Error processing chunk: {e}", exc_info=True)
                    yield f"event: error\ndata: {json.dumps({'detail': 'Stream interrupted - chunk processing failed'})}\n\n"
                    return  # Stop streaming on error

            # If LLM made tool calls, execute them and get final response
            if tool_calls_accumulator:
                logger.info(f"LLM requested {len(tool_calls_accumulator)} tool call(s)", extra={"tool_calls": tool_calls_accumulator})
                for tool_call in tool_calls_accumulator:
                    if tool_call["function"]["name"] == "search_internet":
                        try:
                            # Parse arguments
                            args = json.loads(tool_call["function"]["arguments"])
                            query = args.get("query", "")

                            # Execute search
                            search_results = search_internet(query)
                            logger.info(f"Search completed for query: '{query}'", extra={"query": query, "result_count": len(search_results)})

                            # Add assistant message with tool call to conversation
                            llm_messages.append({
                                "role": "assistant",
                                "content": None,
                                "tool_calls": [{
                                    "id": tool_call["id"],
                                    "type": "function",
                                    "function": {
                                        "name": "search_internet",
                                        "arguments": tool_call["function"]["arguments"]
                                    }
                                }]
                            })

                            # Add tool response to conversation
                            llm_messages.append({
                                "role": "tool",
                                "tool_call_id": tool_call["id"],
                                "content": json.dumps(search_results)
                            })

                        except Exception as e:
                            logger.error(f"Error executing search tool: {e}", exc_info=True, extra={"query": query})
                            # Add empty result on error
                            llm_messages.append({
                                "role": "tool",
                                "tool_call_id": tool_call["id"],
                                "content": "[]"
                            })

                # Call LLM again with tool results to get final response
                logger.debug(f"Calling LLM with {len(llm_messages)} messages including tool results")
                response = await litellm.acompletion(
                    model=llm_model,
                    messages=llm_messages,
                    temperature=0.7,
                    max_tokens=4096,
                    stream=True
                )

                # Stream final response
                full_content = ""
                async for chunk in response:
                    try:
                        if chunk.choices and len(chunk.choices) > 0:
                            delta = chunk.choices[0].delta
                            content = getattr(delta, 'content', None)
                            if content:
                                full_content += content
                                yield f"event: content_delta\ndata: {json.dumps({'chunk': content})}\n\n"
                    except (AttributeError, IndexError) as e:
                        logger.error(f"Error processing final response chunk: {e}", exc_info=True)
                        yield f"event: error\ndata: {json.dumps({'detail': 'Stream interrupted - chunk processing failed'})}\n\n"
                        return  # Stop streaming on error

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
