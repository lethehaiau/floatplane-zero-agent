"""
P0 Tests: Chat and Message functionality.

Critical tests to prevent regression bugs:
- File metadata stored correctly per message
- LLM receives session files content
"""
import pytest
from unittest.mock import patch, MagicMock
from tests.conftest import create_test_session, create_test_file


class TestFileMetadataPerMessage:
    """
    P0 - Regression test for file metadata bug.

    Bug: Backend queried ALL session files for every message,
    causing every message to show all uploaded files.

    Fix: Frontend sends files_metadata in request.
    """

    def test_message_with_specific_files_metadata(self, client, db, temp_storage):
        """Each message should only have the files metadata sent with it."""
        # Create session
        session = create_test_session(db)

        # Upload file1 and send message with it
        create_test_file(db, session.id, "file1.txt", "Content 1")

        response = client.post("/api/chat", json={
            "session_id": str(session.id),
            "message": "First message",
            "files_metadata": [{"filename": "file1.txt", "file_type": "txt"}]
        })
        # Accept both 200 (LLM success) and 500 (LLM failure)
        assert response.status_code in [200, 500]

        # Upload file2 and send message with it
        create_test_file(db, session.id, "file2.md", "Content 2")

        response = client.post("/api/chat", json={
            "session_id": str(session.id),
            "message": "Second message",
            "files_metadata": [{"filename": "file2.md", "file_type": "md"}]
        })
        assert response.status_code in [200, 500]

        # Get messages
        response = client.get(f"/api/chat/sessions/{session.id}/messages")
        assert response.status_code == 200
        messages = response.json()

        user_messages = [m for m in messages if m["role"] == "user"]
        assert len(user_messages) == 2

        # Message 1 should have only file1.txt
        msg1_files = user_messages[0]["message_metadata"]["files"]
        assert len(msg1_files) == 1
        assert msg1_files[0]["filename"] == "file1.txt"

        # Message 2 should have only file2.md
        msg2_files = user_messages[1]["message_metadata"]["files"]
        assert len(msg2_files) == 1
        assert msg2_files[0]["filename"] == "file2.md"

    def test_message_without_files_metadata(self, client, db, temp_storage):
        """Message sent without files_metadata should have None metadata."""
        session = create_test_session(db)

        response = client.post("/api/chat", json={
            "session_id": str(session.id),
            "message": "Message with no files"
        })
        assert response.status_code in [200, 500]

        # Get messages
        response = client.get(f"/api/chat/sessions/{session.id}/messages")
        messages = response.json()

        user_message = [m for m in messages if m["role"] == "user"][0]
        assert user_message["message_metadata"] is None

    def test_message_with_empty_files_metadata(self, client, db, temp_storage):
        """Message with empty files_metadata array should have None metadata."""
        session = create_test_session(db)

        response = client.post("/api/chat", json={
            "session_id": str(session.id),
            "message": "Message with empty files array",
            "files_metadata": []
        })
        assert response.status_code in [200, 500]

        # Get messages
        response = client.get(f"/api/chat/sessions/{session.id}/messages")
        messages = response.json()

        user_message = [m for m in messages if m["role"] == "user"][0]
        assert user_message["message_metadata"] is None


class TestLLMReceivesFileContent:
    """
    P0 - Regression test for LLM file content.

    Bug: Accidentally removing session_files query means LLM doesn't
    receive uploaded file content in context.

    Critical: Files uploaded but LLM can't see them!
    """

    @patch('app.api.chat.litellm.acompletion')
    async def test_llm_receives_session_files_content(self, mock_llm, client, db, temp_storage):
        """LLM should receive all session files in system message."""
        # Create session and upload file with known content
        session = create_test_session(db)
        create_test_file(db, session.id, "answer.txt", "The answer is 42", "txt")

        # Mock LLM response
        mock_response = MagicMock()
        mock_response.__aiter__ = lambda self: iter([
            MagicMock(choices=[MagicMock(delta=MagicMock(content="Test response"))])
        ])
        mock_llm.return_value = mock_response

        # Send message via streaming endpoint
        response = client.post("/api/chat/stream", json={
            "session_id": str(session.id),
            "message": "What is the answer?",
            "files_metadata": [{"filename": "answer.txt", "file_type": "txt"}]
        })

        # Verify LLM was called
        assert mock_llm.called

        # Get the messages passed to LLM
        call_args = mock_llm.call_args
        llm_messages = call_args[1]["messages"]

        # Should have system message with file content
        assert len(llm_messages) >= 2  # System message + user message
        system_msg = llm_messages[0]
        assert system_msg["role"] == "system"
        assert "The answer is 42" in system_msg["content"]
        assert "answer.txt" in system_msg["content"]

    @patch('app.api.chat.litellm.acompletion')
    async def test_llm_receives_multiple_files(self, mock_llm, client, db, temp_storage):
        """LLM should receive all session files, not just those in current message metadata."""
        session = create_test_session(db)

        # Upload two files
        create_test_file(db, session.id, "file1.txt", "Content from file 1")
        create_test_file(db, session.id, "file2.txt", "Content from file 2")

        # Mock LLM
        mock_response = MagicMock()
        mock_response.__aiter__ = lambda self: iter([
            MagicMock(choices=[MagicMock(delta=MagicMock(content="OK"))])
        ])
        mock_llm.return_value = mock_response

        # Send message with only file1 in metadata
        response = client.post("/api/chat/stream", json={
            "session_id": str(session.id),
            "message": "Test",
            "files_metadata": [{"filename": "file1.txt", "file_type": "txt"}]
        })

        # LLM should still receive BOTH files
        call_args = mock_llm.call_args
        llm_messages = call_args[1]["messages"]
        system_msg = llm_messages[0]

        assert "Content from file 1" in system_msg["content"]
        assert "Content from file 2" in system_msg["content"]

    @patch('app.api.chat.litellm.acompletion')
    async def test_llm_without_files(self, mock_llm, client, db, temp_storage):
        """LLM should not receive system message when no files uploaded."""
        session = create_test_session(db)

        # Mock LLM
        mock_response = MagicMock()
        mock_response.__aiter__ = lambda self: iter([
            MagicMock(choices=[MagicMock(delta=MagicMock(content="OK"))])
        ])
        mock_llm.return_value = mock_response

        # Send message with no files
        response = client.post("/api/chat/stream", json={
            "session_id": str(session.id),
            "message": "Test"
        })

        # LLM messages should only have user message, no system message
        call_args = mock_llm.call_args
        llm_messages = call_args[1]["messages"]

        # Should not have system message
        assert len(llm_messages) == 1
        assert llm_messages[0]["role"] == "user"
