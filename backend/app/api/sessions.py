"""
Session management API endpoints.
"""
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session as DBSession
from sqlalchemy import desc

from app.database import get_db
from app.models.session import Session
from app.schemas.session import SessionCreate, SessionResponse, SessionListResponse, SessionUpdate

router = APIRouter(prefix="/api/sessions", tags=["sessions"])


@router.post("", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(
    session_data: SessionCreate,
    db: DBSession = Depends(get_db)
):
    """
    Create a new chat session.

    - **title**: Session title (auto-generated as "New Chat" if not provided)
    - **llm_provider**: LLM provider (openai, anthropic, google)
    - **llm_model**: LLM model name
    """
    # Auto-generate title if not provided
    title = session_data.title if session_data.title else "New Chat"

    # Create new session
    new_session = Session(
        title=title,
        llm_provider=session_data.llm_provider,
        llm_model=session_data.llm_model
    )

    db.add(new_session)
    db.commit()
    db.refresh(new_session)

    return new_session


@router.get("", response_model=SessionListResponse)
async def list_sessions(
    db: DBSession = Depends(get_db)
):
    """
    List all sessions, sorted by most recently updated.
    """
    sessions = db.query(Session).order_by(desc(Session.updated_at)).all()

    return SessionListResponse(
        sessions=sessions,
        total=len(sessions)
    )


@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: UUID,
    db: DBSession = Depends(get_db)
):
    """
    Get a specific session by ID.
    """
    session = db.query(Session).filter(Session.id == session_id).first()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found"
        )

    return session


@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_session(
    session_id: UUID,
    db: DBSession = Depends(get_db)
):
    """
    Delete a session by ID.
    """
    session = db.query(Session).filter(Session.id == session_id).first()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found"
        )

    db.delete(session)
    db.commit()

    return None


@router.patch("/{session_id}", response_model=SessionResponse)
async def update_session(
    session_id: UUID,
    session_data: SessionUpdate,
    db: DBSession = Depends(get_db)
):
    """
    Update a session (currently only title).
    """
    session = db.query(Session).filter(Session.id == session_id).first()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found"
        )

    if session_data.title is not None:
        session.title = session_data.title

    db.commit()
    db.refresh(session)

    return session


@router.post("/{session_id}/clone", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
async def clone_session(
    session_id: UUID,
    db: DBSession = Depends(get_db)
):
    """
    Clone an existing session.
    Creates a new session with the same title (with " (Copy)" appended), provider, and model.
    """
    # Get original session
    original_session = db.query(Session).filter(Session.id == session_id).first()

    if not original_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found"
        )

    # Create cloned session
    cloned_session = Session(
        title=f"{original_session.title} (Copy)",
        llm_provider=original_session.llm_provider,
        llm_model=original_session.llm_model
    )

    db.add(cloned_session)
    db.commit()
    db.refresh(cloned_session)

    return cloned_session
