"""
Files API endpoints.
"""
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File as FastAPIFile, status
from sqlalchemy.orm import Session as DBSession

from app.database import get_db
from app.models.session import Session
from app.models.file import File
from app.schemas.file import FileResponse
from app.utils.storage import storage
from app.utils.text_extraction import extract_text

router = APIRouter(prefix="/api/sessions", tags=["files"])


@router.get("/{session_id}/files", response_model=list[FileResponse])
async def get_session_files(
    session_id: UUID,
    db: DBSession = Depends(get_db)
):
    """
    Get all files for a session.

    Returns list of files with metadata (no extracted text).
    """
    # Verify session exists
    session = db.query(Session).filter(Session.id == session_id).first()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found"
        )

    # Get all files for this session
    files = db.query(File).filter(
        File.session_id == session_id
    ).order_by(File.created_at).all()

    return files


@router.post("/{session_id}/files", response_model=FileResponse, status_code=status.HTTP_201_CREATED)
async def upload_file(
    session_id: UUID,
    file: UploadFile = FastAPIFile(...),
    db: DBSession = Depends(get_db)
):
    """
    Upload a file to a session.

    Validates file type, size, and session file count.
    Extracts text content and stores both file and extracted text.
    """
    # Verify session exists
    session = db.query(Session).filter(Session.id == session_id).first()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found"
        )

    # Check session file count (max 3)
    file_count = db.query(File).filter(File.session_id == session_id).count()
    if file_count >= 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 3 files per session"
        )

    # Validate file type
    file_ext = file.filename.split('.')[-1].lower() if '.' in file.filename else ''
    if file_ext not in ['pdf', 'txt', 'md']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type: {file_ext}. Supported: pdf, txt, md"
        )

    # Read file content
    content = await file.read()
    file_size = len(content)

    # Validate file size (max 10MB)
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large: {file_size} bytes. Maximum: {MAX_FILE_SIZE} bytes (10MB)"
        )

    # Extract text
    try:
        extracted_text = extract_text(content, file_ext)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to extract text: {str(e)}"
        )

    # Create file record
    file_record = File(
        session_id=session_id,
        filename=file.filename,
        file_type=file_ext,
        file_size=file_size,
        extracted_text=extracted_text
    )

    # Save file to storage
    try:
        file_path = storage.save_file(
            session_id=session_id,
            file_id=file_record.id,
            filename=file.filename,
            content=content
        )
        file_record.file_path = file_path
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save file: {str(e)}"
        )

    # Save to database
    db.add(file_record)
    db.commit()
    db.refresh(file_record)

    return file_record


@router.delete("/{session_id}/files/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_file(
    session_id: UUID,
    file_id: UUID,
    db: DBSession = Depends(get_db)
):
    """
    Delete a file from a session.

    Removes both the database record and the physical file.
    """
    # Get file record
    file_record = db.query(File).filter(
        File.id == file_id,
        File.session_id == session_id
    ).first()

    if not file_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File {file_id} not found in session {session_id}"
        )

    # Delete from storage
    try:
        storage.delete_file(file_record.file_path)
    except Exception as e:
        # Log error but continue with database deletion
        print(f"Warning: Failed to delete file from storage: {str(e)}")

    # Delete from database
    db.delete(file_record)
    db.commit()

    return None
