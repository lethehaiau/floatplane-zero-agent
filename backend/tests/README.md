# Backend Tests

Clean, maintainable tests for Floatplane Zero Agent backend.

## Test Organization

### P0 Tests (Critical - Prevent Regression Bugs)
- **test_chat.py** - File metadata per message, LLM receives files
- **test_integration.py** - Session clone, cascade delete, file systems integration

### P1 Tests (Important - Core Functionality)
- **test_sessions.py** - Session CRUD operations
- **test_files.py** - File upload, delete, validation

## Running Tests

### Install test dependencies
```bash
cd backend
pip install pytest pytest-asyncio httpx
```

### Run all tests
```bash
pytest tests/
```

### Run specific test file
```bash
pytest tests/test_chat.py
```

### Run specific test
```bash
pytest tests/test_chat.py::TestFileMetadataPerMessage::test_message_with_specific_files_metadata
```

### Run with verbose output
```bash
pytest tests/ -v
```

### Run only P0 tests
```bash
pytest tests/test_chat.py tests/test_integration.py
```

## Test Design Principles

1. **Simple and maintainable** - Tests focus on behavior, not implementation
2. **Independent** - Each test can run alone, fresh database per test
3. **Fast** - Use in-memory SQLite, mock external APIs (LiteLLM)
4. **Focused** - P0 tests prevent critical bugs, P1 tests cover core flows
5. **Flexible** - Not overly strict, allows for codebase evolution

## Key Regression Tests

### File Metadata Bug (test_chat.py)
Prevents: Each message showing ALL session files instead of only its own files.

### LLM Context Bug (test_chat.py)
Prevents: Accidentally removing session_files query, causing LLM to not receive file content.

### Clone Metadata Bug (test_integration.py)
Prevents: Cloned messages losing file metadata, making files disappear.

### Cascade Delete Bug (test_integration.py)
Prevents: IntegrityError when deleting sessions with files due to missing cascade config.

## Writing New Tests

```python
def test_your_feature(client, db, temp_storage):
    """Clear description of what this tests."""
    # Arrange - setup test data
    session = create_test_session(db)

    # Act - perform action
    response = client.post("/api/endpoint", json={...})

    # Assert - verify behavior
    assert response.status_code == 200
    assert response.json()["field"] == "expected_value"
```

## Fixtures Available

- `client` - FastAPI TestClient with test database
- `db` - SQLAlchemy database session (in-memory SQLite)
- `temp_storage` - Temporary directory for file uploads
- `create_test_session(db, title, llm_model)` - Helper to create sessions
- `create_test_message(db, session_id, role, content, metadata)` - Helper for messages
- `create_test_file(db, session_id, filename, content, file_type)` - Helper for files

## Mocking LLM Calls

```python
from unittest.mock import patch, MagicMock

@patch('app.api.chat.litellm.acompletion')
async def test_llm_feature(mock_llm, client, db):
    # Setup mock response
    mock_response = MagicMock()
    mock_response.__aiter__ = lambda self: iter([
        MagicMock(choices=[MagicMock(delta=MagicMock(content="Response"))])
    ])
    mock_llm.return_value = mock_response

    # Make request
    response = client.post("/api/chat/stream", json={...})

    # Verify LLM was called correctly
    assert mock_llm.called
    call_args = mock_llm.call_args
    assert call_args[1]["model"] == "gpt-4o-mini"
```
