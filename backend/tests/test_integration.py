"""
P0 Tests: Integration tests for cross-feature functionality.

Critical tests to prevent regression bugs:
- Session clone preserves message metadata and files
- Session deletion cascades correctly (no orphaned data)
"""
import os
import pytest
from tests.conftest import create_test_session, create_test_message, create_test_file


class TestSessionClone:
    """
    P0 - Regression test for session cloning.

    Bug: Cloned messages didn't include message_metadata,
    causing files to disappear in cloned sessions.
    """

    def test_clone_preserves_message_metadata(self, client, db, temp_storage):
        """Cloned messages should have the same message_metadata as original."""
        # Create session with message that has file metadata
        session = create_test_session(db, title="Original Session")
        create_test_message(
            db,
            session.id,
            content="Message with files",
            metadata={"files": [{"filename": "test.txt", "file_type": "txt"}]}
        )

        # Clone session
        response = client.post(f"/api/sessions/{session.id}/clone")
        assert response.status_code == 201
        cloned = response.json()

        # Get messages from cloned session
        response = client.get(f"/api/chat/sessions/{cloned['id']}/messages")
        messages = response.json()

        # Should have same message with same metadata
        assert len(messages) == 1
        assert messages[0]["content"] == "Message with files"
        assert messages[0]["message_metadata"] == {
            "files": [{"filename": "test.txt", "file_type": "txt"}]
        }

    def test_clone_preserves_files(self, client, db, temp_storage):
        """Cloned session should have copies of all files."""
        # Create session with files
        session = create_test_session(db)
        file1 = create_test_file(db, session.id, "file1.txt", "Content 1")
        file2 = create_test_file(db, session.id, "file2.md", "Content 2")

        # Clone session
        response = client.post(f"/api/sessions/{session.id}/clone")
        assert response.status_code == 201
        cloned = response.json()

        # Get files from cloned session
        response = client.get(f"/api/sessions/{cloned['id']}/files")
        assert response.status_code == 200
        cloned_files = response.json()

        # Should have same number of files
        assert len(cloned_files) == 2

        # Files should have same names and types (but different IDs)
        filenames = {f["filename"] for f in cloned_files}
        assert filenames == {"file1.txt", "file2.md"}

        # Verify cloned files exist in database (physical file check not needed in API test)
        assert all(f["id"] != str(file1.id) for f in cloned_files)  # Different IDs
        assert all(f["id"] != str(file2.id) for f in cloned_files)

    def test_clone_independence(self, client, db, temp_storage):
        """Deleting original session should not affect clone."""
        # Create and clone session
        session = create_test_session(db)
        create_test_message(db, session.id, content="Test message")
        create_test_file(db, session.id, "test.txt", "Test content")

        response = client.post(f"/api/sessions/{session.id}/clone")
        cloned = response.json()

        # Delete original
        response = client.delete(f"/api/sessions/{session.id}")
        assert response.status_code == 204

        # Clone should still exist with all data
        response = client.get(f"/api/sessions/{cloned['id']}")
        assert response.status_code == 200

        response = client.get(f"/api/chat/sessions/{cloned['id']}/messages")
        assert len(response.json()) == 1

        response = client.get(f"/api/sessions/{cloned['id']}/files")
        assert len(response.json()) == 1


class TestCascadeDelete:
    """
    P0 - Regression test for cascade deletion.

    Bug: File relationship had no cascade config, causing
    IntegrityError when deleting session with files.
    """

    def test_delete_session_removes_messages(self, client, db):
        """Deleting session should cascade delete all messages."""
        session = create_test_session(db)
        session_id = str(session.id)
        create_test_message(db, session.id, content="Message 1")
        create_test_message(db, session.id, content="Message 2")

        # Delete session
        response = client.delete(f"/api/sessions/{session_id}")
        assert response.status_code == 204

        # Messages should be gone
        response = client.get(f"/api/chat/sessions/{session_id}/messages")
        assert response.status_code == 404

    def test_delete_session_removes_files(self, client, db, temp_storage):
        """Deleting session should cascade delete file records and physical files."""
        from pathlib import Path
        session = create_test_session(db)
        file1 = create_test_file(db, session.id, "file1.txt", "Content 1")
        file2 = create_test_file(db, session.id, "file2.txt", "Content 2")

        # Store full file paths
        file1_path = Path(temp_storage) / file1.file_path
        file2_path = Path(temp_storage) / file2.file_path

        # Verify files exist
        assert file1_path.exists()
        assert file2_path.exists()

        # Delete session
        response = client.delete(f"/api/sessions/{session.id}")
        assert response.status_code == 204

        # File records should be gone
        response = client.get(f"/api/sessions/{session.id}/files")
        assert response.status_code == 404

        # Physical files should be deleted
        assert not file1_path.exists()
        assert not file2_path.exists()

    def test_delete_session_with_everything(self, client, db, temp_storage):
        """Delete session with messages and files - complete cleanup."""
        from pathlib import Path
        session = create_test_session(db)

        # Add messages with metadata
        create_test_message(
            db,
            session.id,
            content="Message 1",
            metadata={"files": [{"filename": "test.txt", "file_type": "txt"}]}
        )
        create_test_message(db, session.id, content="Message 2")

        # Add files
        file1 = create_test_file(db, session.id, "file1.txt", "Content 1")
        file2 = create_test_file(db, session.id, "file2.txt", "Content 2")

        file_paths = [
            Path(temp_storage) / file1.file_path,
            Path(temp_storage) / file2.file_path
        ]

        # Delete session
        response = client.delete(f"/api/sessions/{session.id}")
        assert response.status_code == 204

        # Everything should be gone
        response = client.get(f"/api/sessions/{session.id}")
        assert response.status_code == 404

        response = client.get(f"/api/chat/sessions/{session.id}/messages")
        assert response.status_code == 404

        response = client.get(f"/api/sessions/{session.id}/files")
        assert response.status_code == 404

        for path in file_paths:
            assert not path.exists()


class TestFileMetadataVsSessionFiles:
    """
    P0 - Test that two file systems work together correctly.

    1. message_metadata: What files to display with each message (frontend)
    2. session_files: What file content to send to LLM (backend)
    """

    def test_message_metadata_for_display_session_files_for_llm(self, client, db, temp_storage):
        """
        Message metadata controls display, but LLM gets all session files.

        Scenario:
        - Upload file1, send message 1 with file1 metadata
        - Upload file2, send message 2 with NO metadata
        - Message 1 displays file1, message 2 displays nothing
        - BUT LLM for message 2 should have access to BOTH files
        """
        session = create_test_session(db)

        # Upload file1 and send message with it
        create_test_file(db, session.id, "file1.txt", "Content 1")

        response = client.post("/api/chat", json={
            "session_id": str(session.id),
            "message": "Message 1",
            "files_metadata": [{"filename": "file1.txt", "file_type": "txt"}]
        })

        # Upload file2 but DON'T include in message metadata
        create_test_file(db, session.id, "file2.txt", "Content 2")

        response = client.post("/api/chat", json={
            "session_id": str(session.id),
            "message": "Message 2"
            # No files_metadata
        })

        # Get messages
        response = client.get(f"/api/chat/sessions/{session.id}/messages")
        user_messages = [m for m in response.json() if m["role"] == "user"]

        # Message 1 should display file1
        assert user_messages[0]["message_metadata"] == {
            "files": [{"filename": "file1.txt", "file_type": "txt"}]
        }

        # Message 2 should display nothing
        assert user_messages[1]["message_metadata"] is None

        # Note: Testing LLM receives both files requires mocking,
        # covered in test_chat.py::test_llm_receives_multiple_files
