# Simple AI Chat Agent - Implementation Plan

**Version**: 2.0
**Date**: January 9, 2026
**Status**: Ready for Development

---

## Overview

This document defines **WHEN** to build features through a phased implementation approach. See `01-technical-specification.md` for **WHAT** to build.

**Phasing Philosophy**: Each phase delivers a **visible, testable, complete feature** that works in the browser.

---

## Development Approach

**Workflow**: Conversational pair-programming with LLM
- Discuss options and trade-offs before implementing
- Make decisions collaboratively during development
- Adapt to discoveries and learning
- Document decisions in `04-decision-log.md`

**Phase Structure**: Build complete chat experience first, then add tools
- **Phase 1**: Complete chat + sessions (biggest value first) - Full working chat app
- **Phase 2**: File upload feature (complete end-to-end)
- **Phase 3**: Search tool feature (complete end-to-end)
- **Phase 4**: Polish, testing, and deployment (production-ready)
- **Phase 5+**: Enhancements (vector store, auth, etc.)

**Core Principle**: All core features (Phase 1-4) complete before any enhancements

---

## Phase 1: Complete Chat Experience (No Tools Yet)

**Goal**: Full working chat app with sessions and 3 LLM providers

**Duration**: 5-7 days

**What You Can Do After This Phase**:
✅ Open browser → Create new session → Select model (GPT-4/Claude/Gemini) → Type message → See streaming response
✅ Create multiple sessions, switch between them, delete/clone sessions
✅ Each session preserves conversation history
✅ Responses render with Markdown and code highlighting

---

### Backend Tasks

**Project Setup**:
- Monorepo structure (backend/, frontend/, docker-compose.yml)
- Docker Compose (FastAPI + PostgreSQL + Frontend)
- Environment variables setup (.env files)
- Git repository initialization

**Database**:
- PostgreSQL database schema (sessions, messages tables)
- SQLAlchemy models (Session, Message)
- Alembic migrations setup
- Initial migration

**API Endpoints**:
- `POST /api/sessions` - Create new session with model selection
- `GET /api/sessions` - List all sessions (sorted by updated_at)
- `GET /api/sessions/{id}` - Get session with all messages
- `DELETE /api/sessions/{id}` - Delete session (cascade messages)
- `POST /api/sessions/{id}/clone` - Clone session with messages
- `POST /api/chat/stream` - Send message and stream response (SSE)

**LLM Integration**:
- LLM provider abstraction (base class with common interface)
- OpenAI provider implementation (gpt-4)
- Anthropic provider implementation (claude-sonnet-4)
- Google provider implementation (gemini-flash-2.0)
- Provider factory (select by name from session config)
- SSE streaming for all providers
- Error handling with retry logic (3 attempts, exponential backoff)
- Context window management (detect overflow, return error)

**Core Logic**:
- Message storage (user and assistant messages)
- Session title auto-generation (first 50 chars of first message)
- Load all messages for session (no pagination yet)
- CORS configuration for frontend

---

### Frontend Tasks

**Project Setup**:
- React 19 + Vite + TypeScript
- Tailwind CSS configuration
- React Router setup (optional for Phase 1, can be single page)
- Project structure (components/, hooks/, services/, types/)

**Empty State UI** (Grok-style):
- Centered layout with app logo/title
- Large text input card: "What do you want to know?"
- Model selector dropdown (GPT-4, Claude Sonnet, Gemini Flash)
- Send button
- On first message → transition to chat UI

**Chat UI**:
- App layout (session sidebar + main chat area)
- Session sidebar:
  - "New Session" button
  - Session list (sorted by updated_at)
  - Session item (title, delete button, clone button)
  - Active session highlighting
- Chat area:
  - Session title header (editable)
  - Current model display
  - Message list (scrollable)
  - Message component (user/assistant)
  - Markdown rendering (react-markdown)
  - Code syntax highlighting (react-syntax-highlighter)
  - Message input (textarea + send button)
  - Typing indicator ("Agent is typing...")
  - Disable input during response

**API Integration**:
- API client service (axios or fetch)
- Session CRUD operations
- SSE client hook (useSSE or custom EventSource handling)
- Handle streaming chunks (content_delta events)
- Handle done/error events
- Error display in chat UI
- State management (React Context or local state)

**Basic Styling**:
- Responsive layout (works on desktop)
- Basic loading states
- Error message display
- Scroll to bottom on new message

---

### Testing (Minimal)

**Backend**:
- Session CRUD endpoint tests
- Message storage tests
- SSE streaming test (basic)
- LLM provider switching test

**Frontend**:
- Critical component tests (MessageList, ChatInput)
- SSE hook test

---

### Deliverables

✅ **Working chat app accessible at http://localhost:3000**
✅ **Can create/manage sessions with UI**
✅ **Can chat with all 3 LLM providers**
✅ **Streaming responses work smoothly**
✅ **Markdown and code blocks render correctly**
✅ **Session history persists and loads correctly**

---

## Phase 2: File Upload Feature

**Goal**: Complete file upload and agent usage capability

**Duration**: 3-4 days

**What You Can Do After This Phase**:
✅ Upload PDF/TXT/MD files (drag-drop or button)
✅ See files displayed alongside your message
✅ Ask agent about file content → Agent searches file and responds with relevant information

---

### Backend Tasks

**Database**:
- Add `files` table to schema
- SQLAlchemy File model
- Alembic migration for files table
- Foreign key to sessions (cascade delete)

**Storage**:
- Storage abstraction interface (base class)
- Local storage implementation (./uploads/{session_id}/{file_id}.ext)
- Storage factory (select backend from config)

**File Processing**:
- File upload endpoint: `POST /api/sessions/{id}/files`
- File validation (size <= 10MB, type in [PDF, TXT, MD])
- Session file limit check (max 3 files per session)
- Save file to storage (synchronous)
- Text extraction (synchronous - wait before returning):
  - PDF: PyMuPDF (extract text only)
  - TXT/MD: UTF-8 read with encoding fallback
  - Limit to first 100,000 characters
- Store file metadata + extracted text in database
- File download endpoint: `GET /api/files/{id}/download`
- File delete endpoint: `DELETE /api/files/{id}`

**Agent Tool Integration**:
- File search tool implementation
- Full-text search on extracted text (SQL LIKE or pg_trgm)
- Return relevant excerpts with context
- Agent tool calling logic (LLM decides when to use files)
- Incorporate file content into LLM context

---

### Frontend Tasks

**File Upload UI**:
- File upload button or drag-drop zone in message input area
- File preview component (shows selected files before upload)
- Upload progress indicator
- File display alongside user message (above message text)
- File list in session (show uploaded files)
- Delete file button

**File Management**:
- Upload file API call
- Handle upload progress
- Handle extraction completion
- Display file metadata (name, size, type)
- Error handling (size limit, type validation, extraction failure)

---

### Testing (Minimal)

**Backend**:
- File upload endpoint test
- Text extraction tests (PDF, TXT, MD)
- File search tool test
- Agent tool calling test

**Frontend**:
- File upload component test

---

### Deliverables

✅ **Can upload files via UI (drag-drop or button)**
✅ **Files display alongside user messages**
✅ **Agent can search and reference file content in responses**
✅ **File management works (view, delete)**

---

## Phase 3: Search Tool Feature

**Goal**: Agent can search the internet when needed

**Duration**: 2-3 days

**What You Can Do After This Phase**:
✅ Ask "What's the weather today?" → Agent searches DuckDuckGo → Responds with current info
✅ See simple indicator when agent is searching ("Searching...")
✅ Agent decides autonomously when to search vs use knowledge

---

### Backend Tasks

**Search Integration**:
- DuckDuckGo search implementation (duckduckgo-search library)
- Search tool interface (query → results)
- Search parameters (max 5 results, safe search moderate)
- Error handling (silent failure - continue without results)
- Search result formatting for LLM

**Agent Tool Integration**:
- Add search tool to agent's available tools
- Agent decision logic (LLM function calling for search)
- Tool execution in response flow
- Handle search failures gracefully (agent notifies user: "I'm not able to search the internet right now, but...")

---

### Frontend Tasks

**Search Visibility**:
- Simple tool indicator component ("Searching..." message)
- Display indicator during search execution
- Handle tool_call SSE events from backend
- Clear indicator when search completes

---

### Testing (Minimal)

**Backend**:
- DuckDuckGo search integration test
- Search tool execution test
- Search failure handling test

---

### Deliverables

✅ **Agent can search internet when user asks about current events**
✅ **Search results incorporated into responses**
✅ **Simple "Searching..." indicator shows during search**
✅ **Search failures handled gracefully**

---

## Phase 4: Polish & Comprehensive Testing

**Goal**: Production-ready application

**Duration**: 3-5 days

**What You Can Do After This Phase**:
✅ Fully tested, polished MVP deployed to production
✅ Comprehensive documentation
✅ Ready for real users

---

### Backend Tasks

**Testing**:
- Increase test coverage to >70%
- Integration tests for all endpoints
- SSE streaming edge cases
- Error scenario tests
- Context window overflow tests
- Concurrent request handling tests
- Load testing (10 concurrent users)

**Code Quality**:
- Ruff linting (pass with no errors)
- Black formatting
- mypy type checking (pass)
- Clean up TODO comments
- Code review and refactoring

**Error Handling Polish**:
- Comprehensive error messages
- Logging improvements (structured logging)
- Error tracking setup (optional: Sentry)

**Performance**:
- API response time optimization (<200ms target)
- Database query optimization
- Connection pooling tuning

---

### Frontend Tasks

**Testing**:
- Increase test coverage to >60%
- Component tests (all major components)
- Hook tests (useSSE, custom hooks)
- Integration tests (user flows)
- End-to-end critical paths

**Code Quality**:
- ESLint linting (pass)
- Prettier formatting
- TypeScript strict mode (pass)
- Remove unused code/components

**UI Polish**:
- Loading states everywhere
- Error message styling
- Empty state refinements
- Responsive design (mobile + desktop)
- Animations and transitions
- Accessibility improvements (keyboard navigation, ARIA labels)
- Visual feedback for all actions

---

### Documentation

- README.md (setup instructions, features, architecture)
- API documentation (Swagger/OpenAPI)
- Environment variables documentation
- Deployment guide
- Development workflow guide

---

### Deployment

**Docker Production Setup**:
- Production Dockerfiles (multi-stage builds)
- Production docker-compose.yml
- Environment variable management
- Secrets handling

**Deployment**:
- Choose platform (VPS, AWS, GCP, etc.)
- Setup managed PostgreSQL
- Deploy backend + frontend
- Configure domain and SSL/HTTPS
- Health check endpoints
- Verify deployment

**Monitoring** (Optional):
- Basic logging setup
- Health check monitoring
- Error tracking (Sentry)

---

### Deliverables

✅ **Test coverage targets met (>70% backend, >60% frontend)**
✅ **All linting and type checking passes**
✅ **Production deployment successful**
✅ **Documentation complete**
✅ **Application ready for real users**

---

## Enhancement Phases (Post-MVP)

**Important**: Only start enhancements AFTER Phase 1-4 (all core features) are complete.

---

### Enhancement 1: Advanced File Processing

**Duration**: 1-2 weeks

**Features**:
- OpenAI vector store integration for semantic search
- DOCX file support (Microsoft Word documents)
- Cloud storage migration (S3 or Cloudflare R2)
- Better file search with embeddings
- File preview in UI (PDF viewer)

**Value**: Better file search quality, cloud scalability, more file formats

---

### Enhancement 2: Authentication & User Management

**Duration**: 1 week

**Features**:
- User registration and login (email/password)
- JWT-based session management
- Password hashing with bcrypt
- User-scoped sessions and files
- User profile management
- Protected API routes

**Value**: Multi-user support, privacy, production-ready

---

### Enhancement 3: OAuth & Advanced Auth

**Duration**: 1 week

**Features**:
- Google OAuth integration
- Account linking (email + OAuth)
- User settings page
- API key management per user
- Session sharing controls

**Value**: Easier login, better user experience

---

### Enhancement 4: Advanced Chat Features

**Duration**: 2-4 weeks (depends on scope)

**Features**:
- Per-message LLM switching (change model mid-conversation)
- Message editing (regenerate responses)
- Message deletion
- Conversation branching (explore alternatives)
- Export conversations (JSON, Markdown, PDF)
- Message pagination for long sessions
- Auto-summarization for context window management

**Value**: Power user features, better UX for long conversations

---

### Enhancement 5: Analytics & Monitoring

**Duration**: 1-2 weeks

**Features**:
- Usage analytics dashboard
- Token usage tracking and display
- Cost monitoring per user/session
- Performance metrics dashboard
- Error tracking and alerting (Sentry)
- User activity logs

**Value**: Cost control, performance insights, debugging

---

## Development Timeline

**Core MVP Development**: ~2-3 weeks (Phase 1-4)
**With All Enhancements**: ~6-10 weeks total

### Timeline Breakdown

| Timeframe | Phase | What Works | Visible Result |
|-----------|-------|------------|----------------|
| **Days 1-7** | Phase 1 | Complete chat + sessions | ✅ Working chat app in browser |
| **Days 8-11** | Phase 2 | File upload | ✅ Can upload and use files |
| **Days 12-14** | Phase 3 | Search tool | ✅ Agent can search internet |
| **Days 15-19** | Phase 4 | Polish & deploy | ✅ Production-ready MVP |
| **Week 4-5** | Enhancement 1 | Advanced files | Vector store, cloud storage |
| **Week 6** | Enhancement 2 | Authentication | User accounts |
| **Week 7** | Enhancement 3 | OAuth | Google login |
| **Week 8-10** | Enhancement 4-5 | Advanced features | Full product |

**Note**: Timeline is approximate. Conversational development may adjust based on discoveries.

---

## Risk Management

### Potential Blockers & Mitigation

**Phase 1 Risks**:
1. **LLM API Rate Limits**
   - **Mitigation**: Retry with exponential backoff (3 attempts)
   - **Monitoring**: Log all API errors

2. **SSE Streaming Complexity**
   - **Mitigation**: Use proven libraries (sse-starlette), test early
   - **Fallback**: Start with simple streaming, enhance error handling later

3. **Three LLM Providers at Once**
   - **Mitigation**: Build abstraction first, implement one provider, then add others
   - **Note**: Abstraction makes adding providers straightforward

**Phase 2 Risks**:
1. **File Text Extraction Failures**
   - **Mitigation**: Strict validation, limit to 10MB, handle encoding issues
   - **Fallback**: Return clear error to user if extraction fails

2. **Synchronous Processing Blocking**
   - **Mitigation**: Set reasonable timeout, show progress indicator
   - **Note**: 10MB limit keeps processing fast (<5s for most files)

**Phase 3 Risks**:
1. **DuckDuckGo Rate Limiting**
   - **Mitigation**: Use free tier responsibly, implement caching if needed
   - **Fallback**: Agent notifies user if search fails

**General Risks**:
1. **Context Window Overflow**
   - **Mitigation**: Detect token count, disable input when limit reached
   - **Enhancement**: Auto-summarization later

2. **Deployment Complexity**
   - **Mitigation**: Use Docker Compose, document thoroughly
   - **Start Simple**: Deploy to VPS before attempting cloud platforms

---

## Success Metrics

### Phase 1 Success (Complete Chat)
- ✅ Can open browser and chat with all 3 LLM providers
- ✅ Sessions work (create, switch, delete, clone)
- ✅ Streaming responses work smoothly
- ✅ Markdown and code rendering correct
- ✅ Basic tests passing

### Phase 2 Success (File Upload)
- ✅ Can upload PDF/TXT/MD files
- ✅ Agent can search and use file content
- ✅ File display works in UI
- ✅ Synchronous processing works (<5s for 10MB)

### Phase 3 Success (Search Tool)
- ✅ Agent searches when appropriate
- ✅ Search results incorporated into responses
- ✅ Search indicator displays
- ✅ Search failures handled gracefully

### Phase 4 Success (Production-Ready MVP)
- ✅ All core features working end-to-end
- ✅ Test coverage: Backend >70%, Frontend >60%
- ✅ Linting and type checking pass (Ruff, ESLint, mypy, TypeScript)
- ✅ API response time <200ms (excluding LLM calls)
- ✅ LLM first token <2s
- ✅ Documentation complete (README, deployment guide)
- ✅ Deployed and accessible via domain/IP
- ✅ No critical bugs
- ✅ Ready for real users

---

## Flexibility and Adaptation

**Important**: This plan is a guide, not a rigid contract.

**Conversational Development Means**:
- Discuss options before implementing
- Make decisions collaboratively based on discoveries
- Adapt to better approaches found during development
- Adjust scope if needed (within core vs enhancement boundary)

**Expected Changes**:
- Find simpler implementations than originally planned
- Discover edge cases requiring additional handling
- Identify better library choices during setup
- Adjust UI/UX based on what feels right

**How to Handle Changes**:
1. **Discuss**: Talk through the discovery or blocker
2. **Evaluate**: Consider options and trade-offs
3. **Decide**: Make decision collaboratively
4. **Document**: Log important decisions in `04-decision-log.md`
5. **Update**: Update `05-progress-tracker.md` if tasks change
6. **Continue**: Keep building

**Guiding Principles**:
- ✅ Each phase delivers visible, working functionality
- ✅ All core features before any enhancements
- ✅ Test as you go (minimal but important tests)
- ✅ Ship working software, adapt based on reality

---

## Next Steps

### Ready to Start Phase 1?

**Before starting**:
1. ✅ Specification complete (`01-technical-specification.md` v1.2)
2. ✅ Implementation plan complete (`02-implementation-plan.md` v2.0)
3. ✅ Supporting files ready (decision-log, progress-tracker, current-focus)

**When starting Phase 1**:
1. Update `03-current-focus.md` with Phase 1 work
2. Set up development environment (Docker, Git)
3. Start with backend project setup
4. Log decisions as you make them
5. Check off tasks in `05-progress-tracker.md`

**Expected Output**:
After 5-7 days → **Full working chat app in your browser!**

---

**Document Version**: 2.0
**Last Updated**: January 9, 2026
**Status**: ✅ Ready to Start Phase 1

---

## Quick Phase Reference

| Phase | Duration | What You Get |
|-------|----------|--------------|
| **Phase 1** | 5-7 days | 🎯 Complete chat app (sessions + 3 LLMs + streaming) |
| **Phase 2** | 3-4 days | 📎 File upload and usage |
| **Phase 3** | 2-3 days | 🔍 Internet search capability |
| **Phase 4** | 3-5 days | 🚀 Production deployment |
| **Total Core** | **~2-3 weeks** | ✅ **Full MVP ready for users** |
