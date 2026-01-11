"""
P1 Tests: Session CRUD operations.

Core functionality tests for session management.
"""
import pytest
from tests.conftest import create_test_session, create_test_message


class TestSessionCRUD:
    """Basic session operations."""

    def test_create_session(self, client, db):
        """Create a new session with minimal data."""
        response = client.post("/api/sessions", json={
            "llm_provider": "openai",
            "llm_model": "gpt-4o-mini"
        })

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "New Chat"  # Auto-generated
        assert data["llm_provider"] == "openai"
        assert data["llm_model"] == "gpt-4o-mini"
        assert "id" in data
        assert "created_at" in data

    def test_create_session_with_custom_title(self, client, db):
        """Create session with custom title."""
        response = client.post("/api/sessions", json={
            "title": "My Custom Chat",
            "llm_provider": "openai",
            "llm_model": "gpt-4o-mini"
        })

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "My Custom Chat"

    def test_list_sessions(self, client, db):
        """List all sessions ordered by updated_at."""
        # Create multiple sessions
        session1 = create_test_session(db, title="Session 1")
        session2 = create_test_session(db, title="Session 2")
        session3 = create_test_session(db, title="Session 3")

        response = client.get("/api/sessions")
        assert response.status_code == 200

        data = response.json()
        assert data["total"] == 3
        assert len(data["sessions"]) == 3

        # Should be ordered by updated_at (most recent first)
        # Since all created at same time, order may vary but all should be present
        titles = {s["title"] for s in data["sessions"]}
        assert titles == {"Session 1", "Session 2", "Session 3"}

    def test_get_session(self, client, db):
        """Get a specific session by ID."""
        session = create_test_session(db, title="Test Session")

        response = client.get(f"/api/sessions/{session.id}")
        assert response.status_code == 200

        data = response.json()
        assert data["id"] == str(session.id)
        assert data["title"] == "Test Session"

    def test_get_nonexistent_session(self, client, db):
        """Getting non-existent session returns 404."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = client.get(f"/api/sessions/{fake_id}")
        assert response.status_code == 404

    def test_update_session_title(self, client, db):
        """Update session title."""
        session = create_test_session(db, title="Old Title")

        response = client.patch(f"/api/sessions/{session.id}", json={
            "title": "New Title"
        })

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "New Title"

        # Verify persistence
        response = client.get(f"/api/sessions/{session.id}")
        assert response.json()["title"] == "New Title"

    def test_delete_session(self, client, db):
        """Delete a session."""
        session = create_test_session(db)

        response = client.delete(f"/api/sessions/{session.id}")
        assert response.status_code == 204

        # Verify deletion
        response = client.get(f"/api/sessions/{session.id}")
        assert response.status_code == 404

    def test_delete_nonexistent_session(self, client, db):
        """Deleting non-existent session returns 404."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = client.delete(f"/api/sessions/{fake_id}")
        assert response.status_code == 404


class TestSessionCloneBasic:
    """Basic clone functionality (P1 - non-critical paths)."""

    def test_clone_session_basic(self, client, db):
        """Clone creates new session with (Copy) suffix."""
        session = create_test_session(db, title="Original Session")

        response = client.post(f"/api/sessions/{session.id}/clone")
        assert response.status_code == 201

        data = response.json()
        assert data["title"] == "Original Session (Copy)"
        assert data["llm_provider"] == session.llm_provider
        assert data["llm_model"] == session.llm_model
        assert data["id"] != str(session.id)  # Different ID

    def test_clone_empty_session(self, client, db):
        """Clone session with no messages or files."""
        session = create_test_session(db)

        response = client.post(f"/api/sessions/{session.id}/clone")
        assert response.status_code == 201

        cloned = response.json()

        # Should have no messages or files
        response = client.get(f"/api/chat/sessions/{cloned['id']}/messages")
        assert len(response.json()) == 0

    def test_clone_nonexistent_session(self, client, db):
        """Cloning non-existent session returns 404."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = client.post(f"/api/sessions/{fake_id}/clone")
        assert response.status_code == 404


class TestMessages:
    """Basic message operations."""

    def test_get_session_messages(self, client, db):
        """Get all messages for a session."""
        session = create_test_session(db)
        create_test_message(db, session.id, role="user", content="Hello")
        create_test_message(db, session.id, role="assistant", content="Hi there")

        response = client.get(f"/api/chat/sessions/{session.id}/messages")
        assert response.status_code == 200

        messages = response.json()
        assert len(messages) == 2
        assert messages[0]["content"] == "Hello"
        assert messages[1]["content"] == "Hi there"

    def test_get_messages_empty_session(self, client, db):
        """Session with no messages returns empty array."""
        session = create_test_session(db)

        response = client.get(f"/api/chat/sessions/{session.id}/messages")
        assert response.status_code == 200
        assert response.json() == []

    def test_get_messages_nonexistent_session(self, client, db):
        """Getting messages for non-existent session returns 404."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = client.get(f"/api/chat/sessions/{fake_id}/messages")
        assert response.status_code == 404
