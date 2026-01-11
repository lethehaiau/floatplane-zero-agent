"""
Local file storage utility.
"""
import os
from pathlib import Path
from uuid import UUID


class LocalStorage:
    """Handle local file storage operations."""

    def __init__(self, base_path: str = "./uploads"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def get_session_dir(self, session_id: UUID) -> Path:
        """Get directory for session files."""
        session_dir = self.base_path / str(session_id)
        session_dir.mkdir(parents=True, exist_ok=True)
        return session_dir

    def save_file(self, session_id: UUID, file_id: UUID, filename: str, content: bytes) -> str:
        """
        Save file to local storage.

        Returns: file_path relative to base_path
        """
        session_dir = self.get_session_dir(session_id)

        # Get file extension
        ext = Path(filename).suffix
        file_name = f"{file_id}{ext}"

        file_path = session_dir / file_name
        file_path.write_bytes(content)

        # Return relative path
        return str(file_path.relative_to(self.base_path))

    def read_file(self, relative_path: str) -> bytes:
        """Read file from storage."""
        file_path = self.base_path / relative_path
        return file_path.read_bytes()

    def delete_file(self, relative_path: str) -> None:
        """Delete file from storage."""
        file_path = self.base_path / relative_path
        if file_path.exists():
            file_path.unlink()

    def delete_session_files(self, session_id: UUID) -> None:
        """Delete all files for a session."""
        session_dir = self.get_session_dir(session_id)
        if session_dir.exists():
            for file_path in session_dir.iterdir():
                file_path.unlink()
            session_dir.rmdir()


# Global storage instance
storage = LocalStorage()
