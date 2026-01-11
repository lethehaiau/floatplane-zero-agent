# Current Focus

**Last Updated**: January 11, 2026

---

## What We're Working On

**Phase**: Phase 2 - File Upload Feature ✅ COMPLETE + Code Cleanup ✅
**Status**: Ready to commit and move to Phase 3 (Internet Search Tool)

### Phase 1 Feature Breakdown (5 Features)

**Approach**: Build testable features that combine FE+BE (not separate backend/frontend work)

**Feature 1: Project Setup + Health Check** ✅ COMPLETE
- Monorepo structure (backend/, frontend/, docker-compose.yml)
- Docker Compose (FastAPI + PostgreSQL + Frontend)
- Backend: Basic FastAPI with health endpoint
- Frontend: Basic React app that calls health endpoint
- **Test**: `docker-compose up` → browser shows React app + health check works ✅

**Feature 2: Session Management (CRUD)** ⏳ IN PROGRESS
- Backend: Database schema (sessions table), sessions CRUD API, Alembic migrations
- Frontend: Session sidebar (create new, list all, delete, clone)
- **Test**: Create sessions → see in sidebar → delete/clone → persists after refresh

**Feature 3: Basic Chat (Single LLM, No Streaming)** ✅ COMPLETE
- Backend: Messages table, chat endpoint (non-streaming), OpenAI only, store messages
- Frontend: Chat UI (message list, input field, send button, display messages)
- **Test**: Send message → get GPT-4 response → see both in chat → persists in session ✅

**Feature 4: Streaming Responses + SSE** ✅ COMPLETE
- Backend: SSE streaming endpoint (`/api/chat/stream`), LiteLLM async streaming
- Frontend: SSE client with fetch + ReadableStream, real-time streaming display
- **Test**: Send message → see response stream word-by-word in real-time ✅
- **Bugs Fixed**: SQLAlchemy detached session issue in async generator

**Feature 5: Multi-LLM + Empty State UI** ✅ COMPLETE
- Backend: `/api/models` endpoint lists available providers (based on configured API keys)
- Backend: PATCH `/api/sessions/{id}` for title updates
- Frontend: Empty state UI with model selector dropdown
- Frontend: Inline session title editing (click to edit)
- **Test**: Select model → type message → creates session with that model → title editable ✅

### Phase 2 Feature Breakdown (2 Features)

**Feature 6: File Storage + Text Extraction (Backend)** ✅ COMPLETE
- Backend: Files table, Alembic migration, local storage (`./uploads/`)
- Backend: Text extraction (PyMuPDF for PDF, plain read for TXT/MD)
- Backend: POST `/api/sessions/{id}/files` (upload), GET `/api/sessions/{id}/files` (list), DELETE endpoints
- **Test**: Upload PDF/TXT/MD → extract text → verify in DB → delete file ✅

**Feature 7: File Upload UI + LLM Integration (Full Flow)** ✅ COMPLETE
- Frontend: Paperclip button, file picker, display above input
- Frontend: Send files + message together
- Backend: Include file content in LLM context
- Frontend: Display uploaded files in session (read-only after send)
- Frontend: Per-session draft with localStorage (message + files persist)
- **Test**: Upload PDF → send message → LLM uses file content → files shown ✅
- **Bugs Fixed**: File metadata per message, draft state persistence

### Phase 3 Feature Breakdown (2 Features)

**Approach**: Backend tool integration first, then frontend indicator polish

**Feature 8: Search Tool Backend + LLM Integration** ✅ COMPLETE
- Backend: DuckDuckGo search implementation (ddgs library)
- Backend: Search tool interface (query → results formatting)
- Backend: Add search as LLM function calling tool
- Backend: Tool execution in chat stream flow
- Backend: Error handling (graceful fallback if search fails)
- **Test**: Ask "What's the weather?" → Agent searches → Response has current info ✅
- **Quality Test**: 5/5 queries successful (weather, tutorials, facts, news, technical) ✅

**Feature 9: Search Tool UI Indicator**
- Frontend: Tool indicator component ("Searching..." message)
- Frontend: Handle tool_call SSE events from backend
- Frontend: Display indicator during tool execution
- **Test**: Full end-to-end → see "Searching..." when agent uses tool ✅

---

## Active Context

### Recently Completed (Ready to Commit)

**✅ Phase 1 Complete (Features 1-5)**
- Project setup, session management, chat, streaming, multi-LLM
- All core chat functionality working with 3 providers

**✅ Phase 2 Complete (Features 6-7)**
- Feature 6: File Storage + Text Extraction (Backend)
  - Files table + migration, local storage, text extraction (PDF/TXT/MD)
  - POST/GET/DELETE endpoints, validation (3 files, 10MB, types)

- Feature 7: File Upload UI + LLM Integration (Full Flow)
  - Paperclip button, file picker, upload to session
  - Display uploaded files above input with delete button
  - Send files + message, LLM receives file content in context
  - Files displayed read-only with messages after send
  - Badge-style file icons (gray square with file type text)

**✅ Bug Fixes**
- File metadata per message (was showing all session files on every message)
  - Solution: Frontend sends `files_metadata` in chat request
  - Each message now shows only its own files

- Draft state persistence across sessions
  - Solution: Per-session draft with localStorage
  - Message text + file IDs saved per session
  - Draft loads when switching back to session
  - Draft clears after successful send

**✅ Test Suite (43 passing, 1 skipped)**
- P0 Tests (Critical Regression Prevention):
  - File metadata per message (3 tests)
  - LLM receives file content (3 tests)
  - Session clone preserves metadata/files (3 tests)
  - Cascade delete (files + messages) (3 tests)

- P1 Tests (Core Functionality):
  - Session CRUD (14 tests)
  - File management (12 tests)
  - Search tool (4 tests)

- Infrastructure:
  - Database compatibility layer (UUIDType, JSONType)
  - SQLite for tests, PostgreSQL for production
  - Test fixtures with helpers
  - Mocking for external services (DuckDuckGo)

**Success Criteria - All Met**:
- ✅ Paperclip button opens file picker (PDF/TXT/MD only)
- ✅ Selected files shown above input with delete button
- ✅ Can upload files to session
- ✅ Can delete files before sending message
- ✅ Send message includes file content in LLM context
- ✅ LLM can reference file content in response
- ✅ After send, files displayed read-only (no delete)
- ✅ Files show only with their original message
- ✅ Draft persists across session switches

---

## Working Notes

*This section is for quick notes during active work. Clear it when switching tasks.*

**Current Status**: 🚀 Phase 3 - Feature 8 Complete, Ready to Commit

**Phase 3 Feature 8 - Ready to Commit**:
1. Search tool implementation (`app/tools/search.py`)
2. Tool schema definition (`app/tools/definitions.py`)
3. LLM function calling integration (`app/api/chat.py`)
4. Tool execution loop in streaming chat
5. Dependency management (ddgs, httpx compatibility)
6. Unit tests (4 passing tests in `tests/test_search.py`)
7. Quality verification script (`test_search_quality.py` - 5/5 success rate)

**Feature 8 Implementation Details**:
- **Search Tool**: DuckDuckGo integration via `ddgs` package (v9.10.0)
  - Function: `search_internet(query, max_results=5)` returns formatted results
  - Graceful error handling (returns empty list on failure)
  - Results format: `{title, snippet, link}`

- **LLM Integration**: OpenAI function calling format
  - Tool schema with clear description and parameters
  - Passed to LiteLLM via `tools=AVAILABLE_TOOLS`
  - Tool execution loop in streaming endpoint

- **Chat Flow**:
  1. LLM requests search → backend executes → results returned to LLM
  2. LLM uses results to generate informed response
  3. Final response streamed to user

- **Package Management**:
  - Upgraded from `duckduckgo-search` to `ddgs>=1.0.0` (resolved rate limits)
  - Fixed dependency conflict: `httpx==0.27.2` (satisfies litellm < 0.28.0)
  - All searches working with 100% success rate

**Recent Bug Fixes**:
- ✅ Rate limit errors with old `duckduckgo-search` package → Upgraded to `ddgs`
- ✅ Package deprecation warning → Switched to maintained package
- ✅ httpx dependency conflict → Used compatible version (0.27.2)

**Code Refactoring Completed**:
- ✅ Consolidated `sendPendingMessage` into `handleSend` (removed 35 lines of duplication)
- ✅ Extracted file validation constants (ALLOWED_FILE_TYPES, MAX_FILE_SIZE, etc.)
- ✅ Extracted `getFilesMetadata()` helper function (DRY principle)
- ✅ Memoized `handleFileDelete` callback (performance)
- ✅ Fixed missing useEffect dependencies
- ✅ Fixed TypeScript error with onClick handler

**Files Changed (Phase 3 Feature 8)**:
- Backend:
  - `app/tools/__init__.py` - NEW: Tools module initialization
  - `app/tools/search.py` - NEW: DuckDuckGo search implementation
  - `app/tools/definitions.py` - NEW: Tool schemas for LLM function calling
  - `app/api/chat.py` - MODIFIED: Added tool execution loop in streaming endpoint
  - `requirements.txt` - MODIFIED: Added `ddgs>=1.0.0` for search
  - `requirements-test.txt` - MODIFIED: Set `httpx==0.27.2` for compatibility
  - `tests/test_search.py` - NEW: Unit tests for search functionality (4 tests)
  - `test_search_quality.py` - NEW: Quality verification script (5 test queries)

**Files Changed (Phase 2)**:
- Backend:
  - `app/schemas/message.py` - Added `FileMetadata` and `files_metadata` field
  - `app/api/chat.py` - Use request `files_metadata` instead of querying DB
  - `app/database.py` - Added `UUIDType` for SQLite compatibility
  - `app/models/message.py` - Added `JSONType` for SQLite compatibility
  - `app/models/session.py`, `app/models/file.py` - Use `UUIDType`
  - `tests/` - Full test suite (conftest, test_chat, test_integration, test_sessions, test_files)

- Frontend:
  - `src/components/ChatArea.tsx` - Badge-style icons, files_metadata in request, draft persistence (save on exit), refactored and cleaned
  - `src/utils/draftStorage.ts` - localStorage utility for per-session drafts
  - `package.json` - Added markdown dependencies

**Impact Summary**:
- Lines of code: -35 lines (-7.5%)
- Code duplication: Eliminated (2 → 1 function)
- Magic numbers: Centralized (6 locations → 0)
- React warnings: Fixed (missing deps)
- Better UX: Initial message restored on error

**Feature 8 Implementation Plan**:

**Step 1: Search Implementation (Backend)**
1. Install `duckduckgo-search` library
2. Create `app/tools/search.py` with search function
3. Format results for LLM consumption

**Step 2: LLM Tool Definition**
1. Define search tool schema (JSON schema for function calling)
2. Add to available tools list for LLM

**Step 3: Tool Execution in Chat Flow**
1. Update chat endpoint to handle tool calls
2. When LLM requests search → execute → return results to LLM
3. LLM uses results to generate final response
4. Stream final response to user

**Step 4: Error Handling**
1. Graceful fallback if search fails
2. LLM continues without search results

**Step 5: Testing**
1. Manual test: "What's the weather in SF?"
2. Verify response has current/recent data
3. Check network tab for tool execution

**Next Steps**:
1. Commit Phase 2 (when ready)
2. Implement Feature 8 (Search Tool Backend)
3. Implement Feature 9 (Search Tool UI Indicator)

**Future Tasks (Noted, Not Blocking)**:
- Add cronjob to cleanup orphaned files (uploaded but never sent)

**Open Questions**: None

**Blockers**: None

---

## How to Use This File

**Purpose**: Keep track of what you're actively working on during a session.

**When to Update**:
- ✅ Starting new work (update "What We're Working On")
- ✅ Mid-task discussions (add to "Working Notes")
- ✅ Completing work (move to "Recently Completed")
- ✅ Encountering blockers (add to "Blockers")

**Keep It Light**: This is working memory, not permanent record.
- Quick notes, not full explanations
- Clear old notes when task is done
- Use decision-log for important decisions
- Use progress-tracker for overall status

---

**Template for Starting New Task**:

```markdown
## What We're Working On

**Phase**: [Phase number and name]
**Current Task**: [Specific feature or component]

### What We're Building
- [Brief description]
- [Key files/components]

### Current Approach
- [High-level approach decided]
- [Open questions to discuss]
```

**Template for Working Notes**:

```markdown
## Working Notes

**Current Discussion**: [Topic being discussed]

**Options Considered**:
1. [Option A - pros/cons]
2. [Option B - pros/cons]

**Decision**: [What we decided and why]
→ Log this in decision-log.md when finalized

**Next Steps**:
- [ ] [Immediate next action]
- [ ] [Following action]
```
