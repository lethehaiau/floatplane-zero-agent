# Simple AI Chat Agent - Technical Specification

**Version**: 1.0
**Date**: January 8, 2026
**Status**: Ready for Development

---

## 1. Overview

### 1.1 Project Goal

Build a simple AI chat agent that allows users to interact with multiple LLM providers through a web-based chat interface. The agent can search the internet, process user-uploaded files as knowledge sources, and respond with well-formatted answers.

### 1.2 Key Principles

- **Simplicity**: Clean, readable code over clever abstractions
- **Developer-friendly**: Easy to understand, modify, and extend
- **Maintainability**: Well-tested, documented, and organized
- **Scalability considerations**: Design for future growth without premature optimization

### 1.3 Core Features [Phase 1 MVP]

1. **Chat Interface**: Web-based UI with message history and Markdown rendering
2. **Session Management**: Create, delete, and clone chat sessions
3. **File Upload**: Support PDF, TXT, and MD files as knowledge sources (local text extraction)
4. **Multi-LLM Support**: Switch between GPT-4, Claude Sonnet, and Gemini Flash
5. **Internet Search**: DuckDuckGo integration (agent-initiated)
6. **Streaming Responses**: Real-time response streaming via SSE
7. **No Authentication**: Single-user mode for MVP

### 1.4 Enhancement Features [Future Phases]

- **Vector Store**: OpenAI vector store integration for better file search
- **DOCX Support**: Microsoft Word document processing
- **Per-Message LLM Switching**: Change model within a session
- **Input Validation**: Message length limits and rate limiting
- **Usage Tracking**: Token and cost monitoring
- **Authentication**: Email/password and OAuth (Google)

---

## 2. Architecture

### 2.1 System Architecture

```
┌─────────────────────────────────────────────────────┐
│                    Frontend                          │
│         (React + Vite + TypeScript)                  │
│  - Chat UI with Markdown rendering                  │
│  - Session management                                │
│  - File upload                                       │
│  - SSE client for streaming                          │
└──────────────┬──────────────────────────────────────┘
               │ HTTP/REST + SSE
               │
┌──────────────▼──────────────────────────────────────┐
│                   Backend API                        │
│              (FastAPI + Python)                      │
│  ┌────────────────────────────────────────────┐    │
│  │  REST API Endpoints                        │    │
│  │  - Sessions CRUD                           │    │
│  │  - Messages CRUD                           │    │
│  │  - Files upload/download                   │    │
│  └────────────────────────────────────────────┘    │
│  ┌────────────────────────────────────────────┐    │
│  │  SSE Streaming Endpoint                    │    │
│  │  - /api/chat/stream                        │    │
│  └────────────────────────────────────────────┘    │
│  ┌────────────────────────────────────────────┐    │
│  │  Agent Logic                               │    │
│  │  - LLM provider abstraction                │    │
│  │  - Tool orchestration (search, files)      │    │
│  │  - Response generation                     │    │
│  └────────────────────────────────────────────┘    │
└──────────────┬──────────────────────────────────────┘
               │
    ┌──────────┴──────────┐
    │                     │
    ▼                     ▼
┌─────────┐         ┌──────────────┐
│PostgreSQL│         │ File Storage │
│         │         │   (Local)    │
│Sessions │         │              │
│Messages │         │ ./uploads/   │
│Files    │         │              │
└─────────┘         └──────────────┘
               │
    ┌──────────┴──────────┐
    │                     │
    ▼                     ▼
┌──────────┐        ┌──────────────┐
│  OpenAI  │        │  DuckDuckGo  │
│Anthropic │        │    Search    │
│  Google  │        │              │
└──────────┘        └──────────────┘
```

### 2.2 Technology Stack

**Frontend**:
- React 19 with TypeScript
- Modern build tool (Vite recommended)
- CSS framework for styling
- Client-side routing
- Markdown rendering with code highlighting
- SSE client for streaming

**Backend**:
- Python 3.11+
- FastAPI web framework
- PostgreSQL with ORM
- Database migrations tool
- Request/response validation
- LLM provider SDKs (OpenAI, Anthropic, Google)
- PDF text extraction library
- DuckDuckGo search integration

**Deployment**:
- Docker Compose
- Monorepo structure

**Note**: Specific library choices to be discussed and selected during implementation based on current best practices and compatibility.

### 2.3 Component Organization

**Frontend**: Chat UI components, session management, file handling, model selection, API client

**Backend**: API routes, business logic services, database models, LLM provider abstraction, storage abstraction, agent tools

**Note**: Exact component names and file organization to be determined during implementation.

---

## 3. Feature Specifications

### 3.1 Chat Interface [Core]

**Description**: Web-based chat UI for interacting with the agent.

**Features**:
- Display message history (user messages + agent responses)
- Load all messages in session (pagination as enhancement)
- Real-time streaming of agent responses
- Markdown rendering (headers, lists, bold, italic, links, code blocks)
- Code syntax highlighting
- Typing indicator while agent is responding
- Error messages displayed inline
- Retry failed messages
- Uploaded files displayed alongside user message, above the message text

**Empty State / New Session UI**:
- Centered layout with app logo
- Large text input card: "What do you want to know?" (or similar)
- Model selector (dropdown) - select LLM provider/model before first message
- Clean, minimal design similar to Grok but simpler
- On first message submit → transitions to chat UI

**Chat UI (After First Message)**:
```
┌─────────────────────────────────────────┐
│  Session Title          [Model: GPT-4]  │
├─────────────────────────────────────────┤
│                                         │
│  User: How does photosynthesis work?   │
│                                         │
│  Agent: Photosynthesis is...           │
│  [Markdown formatted response]          │
│  - Uses light energy                    │
│  - Produces glucose                     │
│                                         │
│  [Agent is typing...]                   │
│                                         │
├─────────────────────────────────────────┤
│  [📎] Type a message...      [Send]     │
└─────────────────────────────────────────┘
```

**Technical Details**:
- Markdown rendering with code syntax highlighting
- SSE connection for streaming
- Single message at a time (no concurrent sending)
- State management: Start simple (Context/local state), add Redux only if complexity requires it

---

### 3.2 Session Management [Core]

**Description**: Users can organize conversations into sessions.

**Features**:
- **Create Session**: Start new conversation with selected LLM
- **Delete Session**: Remove session and all associated messages/files
- **Clone Session**: Duplicate session with full message history and uploaded files
- **View Sessions**: List all sessions sorted by last updated
- **Switch Sessions**: Navigate between different conversations

**Session Properties**:
- `id` (UUID)
- `title` (auto-generated from first message, editable)
- `llm_provider` (openai, anthropic, google)
- `llm_model` (gpt-4, claude-sonnet-4, gemini-flash-2.0)
- `created_at`
- `updated_at`
- `message_count`
- `file_count`

**Behavior**:
- **Title**: Auto-generated from first user message
  - Core MVP: Use first N words (e.g., first 50 characters)
  - Enhancement: Ask LLM to generate concise title
  - Always editable by user
- **Delete**: Hard delete with CASCADE to messages and files
- **Clone**: Creates new session with duplicated messages and files
  - File handling: Copy file bytes (or whichever is easier - TBD during implementation)
  - Messages duplicated to new session
- **LLM Selection**: Locked to session (cannot change mid-conversation)
- **Message Loading**: Load all messages for session (add pagination as enhancement)

**Limitations**:
- No limit on number of sessions (for MVP)
- No limit on messages per session (for MVP)

**Enhancement**:
- Per-message LLM switching
- Session folders/organization
- Session search
- Auto-generate title from first message content

---

### 3.3 Agent Behavior & Tool Usage [Core]

**Description**: Agent autonomously decides when to use tools (search, files) based on user queries.

**Decision-Making Logic**:
- Agent analyzes user query to determine if tools are needed
- Uses LLM function/tool calling to request tool execution
- Backend executes tools and returns results to agent
- Agent incorporates results into final response

**Available Tools**:
1. **Web Search** (DuckDuckGo)
2. **File Search** (uploaded files)

**Search Triggering** (Agent decides):
- **When to search**: User asks about current events, recent news, latest information
- **When NOT to search**: Factual knowledge, code explanations, general questions
- **Examples**:
  - "What's the weather today?" → Search
  - "Explain photosynthesis" → No search
  - "Latest news on AI" → Search

**File Usage** (Agent decides):
- **When to use**: Query relates to uploaded file content
- **How**: Full-text search on extracted text, return relevant excerpts
- **Agent sees**: Filename and relevant text snippets
- **Examples**:
  - "Summarize the document" → Use files
  - "What is photosynthesis?" → No files (unless file contains it)

**Tool Execution Flow**:
1. User sends message
2. LLM decides if tools needed (returns tool calls)
3. Backend executes each tool sequentially
4. Results sent back to LLM
5. LLM generates final response with tool information incorporated

**Tool Usage Visibility**:
- **MVP**: Simple indicator when agent is using tools (e.g., "Searching..." or "Reading files...")
- **Enhancement**: Detailed tool execution visibility with results preview

**Source Attribution**:
- Agent naturally incorporates sources in response text
- No explicit citation UI in Core MVP
- Enhancement: Add structured source references

---

### 3.4 Error Handling & Recovery [Core]

**Description**: Graceful error handling with user-friendly messages and recovery options.

**LLM API Failures**:
- **Retry Strategy**: 3 attempts with exponential backoff (1s, 2s, 4s)
- **Final Failure**: Display error in chat with "Retry" button
- **Error Message**: "Failed to get response from [provider]. Please try again."
- **Logging**: Log full error details server-side

**Search Failures**:
- **Behavior**: Continue without search results (don't block response)
- **User Experience**: Agent notifies user about search failure (e.g., "I'm not able to search the internet right now, but based on my knowledge...")
- **Agent Response**: Responds with available knowledge after notifying about search limitation
- **Logging**: Log search failures server-side

**File Processing Failures**:
- **Upload Success, Extraction Fails**: File saved, no extracted text
- **User Notification**: "File uploaded but couldn't extract text"
- **Agent Behavior**: Can see filename, cannot search content
- **Retry**: No automatic retry

**SSE Connection Drops**:
- **Frontend**: Automatic reconnection attempt (1 retry)
- **Reconnection Fails**: Show "Connection lost. Please refresh." message
- **Backend**: Mark incomplete messages in database
- **User Action**: Refresh page to restart

**Concurrent Messages**:
- **Behavior**: Block UI during response generation
- **User Experience**: Cannot send new message until current response complete
- **Visual Feedback**: Typing indicator, disabled input field

**Context Window Overflow**:
- **Detection**: Check token count before sending to LLM
- **Behavior**: Disable new message input when limit reached
- **User Message**: "Context limit reached. Please start a new session to continue."
- **UI State**: Input field disabled, clear visual indicator of limit reached
- **Enhancement**: Auto-summarize old messages to extend context window

**Incomplete Responses**:
- **Handling**: TBD during implementation
- **Considerations**: SSE connection drops mid-response, partial message storage, retry behavior

---

### 3.5 File Upload & Processing

#### 3.5.1 File Upload [Core]

**Description**: Users can upload files to provide context for the agent.

**Supported Formats**:
- PDF (`.pdf`)
- Plain text (`.txt`)
- Markdown (`.md`)

**Limitations**:
- Max file size: 10 MB per file
- Max files per session: 3 files
- Max files per user: 30 files
- Files are session-scoped (deleted when session is deleted)

**Upload Flow**:
```
1. User drags/selects file
2. Frontend validates: size, format, session limit
3. Upload to backend: POST /api/sessions/{id}/files
4. Backend validates and saves via storage abstraction
5. Extract text content synchronously (wait for completion)
6. Store file metadata and extracted text in database
7. Return file info to frontend
8. File immediately available for agent to use
```

**File Processing Behavior**:
- **Synchronous Processing**: Text extraction completes before returning to frontend
- **Processing Time**: User waits for extraction to complete (show progress indicator)
- **Upload Success**: File saved and text extracted before LLM can be called
- **Extraction Failure**: Return error to user, file not saved
- **Large Files**: Extract first 100,000 characters only
- **Encoding**: Try UTF-8 first, fallback to common encodings, fail gracefully
- **Agent Usage**: Files must be fully processed before agent can reference them

**Text Extraction**:
- **PDF**: Extract all text content, ignore images and formatting
- **TXT/MD**: Read as UTF-8 text
- **Library**: PyMuPDF for PDFs, built-in Python for text files

**File Search** (Simple Full-Text):
- Agent request triggers search across extracted text (SQL `LIKE` or full-text search)
- Return relevant excerpts (context window around matches)
- Agent incorporates excerpts into response

**Storage**:
- **Core**: Local filesystem at `./uploads/{session_id}/{file_id}.{ext}`
- **Design**: Storage abstraction layer (see 3.5.2)
- **Metadata**: PostgreSQL `files` table

#### 3.5.2 Storage Abstraction [Core Architecture]

**Description**: Abstract storage layer that supports multiple backends without code changes.

**Purpose**:
- Start with local filesystem storage (Core)
- Enable cloud storage migration without refactoring (Enhancement)
- Single configuration switch between backends

**Design Principles**:
- API layer does not know about storage implementation
- All file operations go through abstraction interface
- Storage backend determined by configuration

**Interface Requirements**:
- Save uploaded file to storage
- Retrieve file for text extraction (local path or temporary download)
- Delete file from storage
- Generate download URL (file path or presigned URL)

**Implementations**:
- **LocalStorage** [Core]: Save to filesystem at `./uploads/{session_id}/{file_id}.ext`
- **S3Storage** [Enhancement]: Save to S3/Cloudflare R2 bucket

**Configuration Switch**:
- Environment variable: `STORAGE_BACKEND=local` or `STORAGE_BACKEND=s3`
- Factory pattern selects appropriate implementation at runtime

**Key Benefit**: Zero code changes in API when migrating from local to cloud storage

#### 3.5.3 Cloud Storage Migration [Enhancement]

**Description**: Migrate from local filesystem to cloud storage (S3 or Cloudflare R2).

**When to Migrate**:
- Deploying to production with multiple backend servers
- File storage exceeds 10-20GB
- Need CDN for fast global file access
- Require built-in redundancy and backups

**Implementation Approach**:
- Create S3Storage class implementing StorageBackend interface
- Use boto3 SDK for AWS S3 operations
- Download files temporarily for text extraction
- Generate presigned URLs for file downloads
- Support Cloudflare R2 via custom endpoint configuration

**Migration Process**:
- Change `STORAGE_BACKEND` environment variable from `local` to `s3`
- Add S3 credentials to configuration
- Optionally migrate existing local files to S3
- No code changes required

**Cost Comparison**:
- **AWS S3**: ~$0.023/GB/month storage, $0.09/GB download
- **Cloudflare R2**: ~$0.015/GB/month storage, free egress (downloads)
- **Recommendation**: R2 for high-download applications, S3 for AWS ecosystem

#### 3.5.4 Vector Store Integration [Enhancement]

**Description**: Use OpenAI vector store for better semantic search across files.

**High-Level Approach**:
- Upload files to OpenAI vector store
- Use OpenAI's file search tool
- Works with any LLM (not just OpenAI) - vector store is separate from generation
- Better retrieval quality for large/complex files

**Note**: Detailed design to be created when implementing this enhancement

---

### 3.6 LLM Integration

#### 3.6.1 Multi-Provider Support [Core]

**Supported Providers**:

| Provider | Model | Context Window | Max Output |
|----------|-------|----------------|------------|
| OpenAI | gpt-4 | 128k tokens | 4k tokens |
| Anthropic | claude-sonnet-4 | 200k tokens | 4k tokens |
| Google | gemini-flash-2.0 | 1M tokens | 4k tokens |

**Provider Abstraction**:
- Abstract base class for all LLM providers
- Common interface for streaming responses
- Each provider implements: OpenAI, Anthropic, Google

**API Key Management**:
- System-provided keys in environment variables
- Single set of keys for all users (MVP, no auth)
- **Flexible Configuration**: App can run with only 1 provider configured
  - Only show configured providers in model selector
  - Allow developers to test with single API key
  - Production can enable all 3 providers

**Model Selection**:
- User selects provider + model when creating session
- Selection persists for entire session
- Default: First available provider (prefer GPT-4 if configured)

#### 3.6.2 Response Streaming [Core]

**Streaming Method**: Server-Sent Events (SSE)

**Flow**:
```
1. User sends message
2. Backend starts LLM generation
3. As tokens arrive, send SSE events:
   - event: content_delta
     data: {"chunk": "word"}
4. When complete, send:
   - event: done
     data: {"message_id": "uuid"}
5. Frontend displays chunks in real-time
```

**SSE Event Types**:
- `content_delta` - Text chunk
- `tool_call` - Agent is using a tool (search or file retrieval)
- `error` - Error occurred
- `done` - Response complete

**Error Handling**:
- Show error in chat UI
- Provide retry button
- Log error details server-side

#### 3.6.3 Tool Calling [Core]

**Agent Tools**:
1. **Web Search** (DuckDuckGo)
2. **File Search** (local text search)

**Tool Execution Flow**:
```
1. LLM decides to use tool (returns tool call)
2. Backend executes tool
3. Tool results sent back to LLM
4. LLM generates final response with tool info
```

**Source Attribution**:
- Agent naturally incorporates sources in response
- No explicit citation UI (MVP)
- Enhancement: Add source references section

#### 3.6.4 Context Window Management [Enhancement]

**MVP Approach**: Fail/warn when context exceeds limit

**Future Enhancement**:
- Auto-summarize old messages
- Keep recent N messages only

---

### 3.7 Internet Search [Core]

**Description**: Agent can search the internet for information.

**Search Provider**: DuckDuckGo (free, no API key needed)

**Triggering**:
- Agent autonomously decides when to search
- LLM uses tool calling to request search
- Not triggered on every query

**Search Parameters**:
- Query: Generated by agent based on user question
- Max results: 5
- Safe search: Moderate

**Search Flow**:
```
1. Agent determines search is needed
2. Agent generates search query
3. Backend calls DuckDuckGo API
4. Returns top 5 results (title, snippet, URL)
5. Agent incorporates info into response
6. Results NOT shown directly to user (agent uses them internally)
```

**Library**: `duckduckgo-search` Python package

**Rate Limiting**: None for MVP (DuckDuckGo is free)

---

### 3.8 Authentication [Enhancement]

**Email/Password Authentication**:
- User registration and login
- JWT-based sessions
- Password hashing (bcrypt)
- Session isolation per user

**OAuth (Google)**:
- Google Sign-In integration
- OAuth 2.0 flow
- Link accounts

**MVP**: No authentication, design schema to easily add later

---

## 4. API Design

### 4.1 REST Endpoints

**Base URL**: `http://localhost:8000/api`

**Session Management**:
- `POST /api/sessions` - Create new session
- `GET /api/sessions` - List all sessions
- `GET /api/sessions/{id}` - Get session with messages and files
- `DELETE /api/sessions/{id}` - Delete session
- `POST /api/sessions/{id}/clone` - Clone session with history

**Chat**:
- `POST /api/chat/stream` - Send message and stream response (SSE)

**File Management**:
- `POST /api/sessions/{id}/files` - Upload file to session
- `GET /api/files/{id}/download` - Download file
- `DELETE /api/files/{id}` - Delete file

### 4.2 Design Principles

**RESTful Conventions**:
- JSON for structured data
- Standard HTTP methods (GET, POST, DELETE)
- Standard status codes (200, 201, 204, 400, 404, 500)
- Resource-based URLs

**Streaming**:
- Server-Sent Events (SSE) for chat responses
- Event types: `content_delta`, `tool_call`, `error`, `done`

**Data Format**:
- ISO 8601 timestamps
- UUIDs for resource IDs
- Consistent error response structure

**Decisions During Implementation**:
- Exact request/response schemas (nested vs flat)
- Pagination approach for lists
- Include related resources or separate endpoints?
- Error response details structure

---

## 5. Database Schema

### 5.1 Core Tables

#### sessions
**Purpose**: Store conversation sessions

**Key Fields**:
- Unique ID (UUID)
- Title (editable by user)
- LLM provider and model selection
- Created and updated timestamps

**Indexes**: Index on `updated_at` for sorting recent sessions

#### messages
**Purpose**: Store conversation messages

**Key Fields**:
- Unique ID (UUID)
- Foreign key to session (cascade delete)
- Role: user or assistant
- Content (text)
- Created timestamp

**Indexes**: Index on `session_id` for retrieval, index on `created_at` for ordering

#### files
**Purpose**: Store file metadata

**Key Fields**:
- Unique ID (UUID)
- Foreign key to session (cascade delete)
- Filename, storage key (backend-agnostic path)
- Content type (PDF, TXT, MD)
- Size in bytes
- Extracted text for search
- Created timestamp

**Storage Key Design**: Format that works for both local and cloud storage
- Local: `{session_id}/{file_id}.ext` → `./uploads/session-uuid/file-uuid.pdf`
- S3: `{session_id}/{file_id}.ext` → `s3://bucket/session-uuid/file-uuid.pdf`

**Indexes**: Index on `session_id` for retrieval

### 5.2 Enhancement Tables

#### users [Enhancement - Authentication]
**Purpose**: Store user accounts (future)

**Key Fields**:
- Unique ID, email (unique), password hash
- Name, created timestamp
- Relationship: Add `user_id` to sessions table

### 5.3 Constraints

**Application-Level Enforcement**:
- Max 3 files per session
- Max 30 files per user (when auth added)
- Max 10MB per file
- No message limits in MVP

**Database Constraints**:
- Foreign key relationships with CASCADE delete
- NOT NULL constraints on required fields

**Decisions During Implementation**:
- Exact column types (VARCHAR lengths)
- Which additional indexes to create (add as needed based on query patterns)
- Whether to store computed fields (message_count) or calculate on-demand

---

## 6. Project Structure

### 6.1 Monorepo Layout

```
simple-agent/
├── backend/              # FastAPI application
│   ├── app/              # Main application code
│   │   ├── api/          # REST endpoint routes
│   │   ├── models/       # Database models (SQLAlchemy)
│   │   ├── schemas/      # Request/response schemas (Pydantic)
│   │   ├── services/     # Business logic (chat, files, search)
│   │   ├── llm/          # LLM provider abstraction
│   │   │   ├── base.py   # Abstract provider interface
│   │   │   └── ...       # OpenAI, Anthropic, Google implementations
│   │   ├── storage/      # File storage abstraction
│   │   │   ├── base.py   # Abstract storage interface
│   │   │   ├── local.py  # Local filesystem [Core]
│   │   │   └── s3.py     # Cloud storage [Enhancement]
│   │   ├── tools/        # Agent tools (search, file retrieval)
│   │   └── utils/        # Helpers (text extraction, SSE)
│   ├── alembic/          # Database migrations
│   ├── tests/            # Test suite
│   └── uploads/          # Local file storage (gitignored)
│
├── frontend/             # React application
│   └── src/
│       ├── components/   # UI components
│       ├── hooks/        # Custom React hooks
│       ├── services/     # API client
│       ├── types/        # TypeScript types
│       └── styles/       # CSS/styling
│
└── docker-compose.yml    # Dev environment setup
```

**Note**: Exact file names and module organization to be determined during implementation based on code structure needs.

---

## 7. Testing Strategy

### 7.1 Backend Testing (pytest)

**Unit Tests**:
- LLM provider abstraction
- Storage backend abstraction (local and S3)
- Text extraction utilities
- File validation logic
- Search service

**Integration Tests**:
- API endpoints (sessions, chat, files)
- Database operations
- SSE streaming

**Test Coverage Target**: 70%+

### 7.2 Frontend Testing (Vitest)

**Unit Tests**:
- Components (MessageList, FileUpload)
- Custom hooks (useSSE, useSessions)
- Utility functions

**Test Coverage Target**: 60%+

### 7.3 Testing Tools

**Backend**:
- pytest (test runner)
- pytest-asyncio (async tests)
- httpx (test client)
- pytest-cov (coverage)

**Frontend**:
- Vitest (test runner)
- @testing-library/react (component testing)
- @testing-library/user-event (user interactions)

---

## 8. Deployment

### 8.1 Docker Compose Setup

**Services**:
1. Backend (FastAPI)
2. Frontend (Vite dev server)
3. PostgreSQL

**Docker Compose Configuration**:
- **Backend service**: FastAPI on port 8000, connected to PostgreSQL
- **Frontend service**: Vite dev server on port 3000
- **PostgreSQL service**: Database on port 5432
- **Volumes**: Persistent storage for database and uploads
- **Environment variables**: LLM API keys, database URL, storage backend

### 8.2 Environment Variables

**Backend Configuration**:
- Database connection URL
- Storage backend selection (local or S3)
- LLM provider API keys (OpenAI, Anthropic, Google)
- File upload limits and constraints
- App configuration (max tokens, etc.)

**Frontend Configuration**:
- Backend API base URL

### 8.3 Development Workflow

**Initial Setup**:
1. Clone repository
2. Copy `.env.example` to `.env` for backend and frontend
3. Start services with `docker-compose up`
4. Run database migrations
5. Access frontend at http://localhost:3000
6. Access backend API at http://localhost:8000

**Common Commands**:
- View logs, run tests, restart services
- Database migrations with Alembic
- Frontend hot reload with Vite
- Backend hot reload with Uvicorn

### 8.4 Production Deployment

**Target Platforms**:
- VPS (DigitalOcean, Hetzner, Linode)
- Cloud (AWS, GCP, Azure)

**Production Considerations**:
- Managed PostgreSQL database
- Production-optimized builds (minified frontend, optimized backend)
- Environment-specific configurations
- Monitoring and logging infrastructure
- Secrets management (environment variables, secret stores)
- HTTPS/SSL certificates
- Reverse proxy (nginx or cloud load balancer)
- Auto-restart policies
- Health checks and readiness probes

---

## 9. Code Quality & Standards

### 9.1 Backend Standards

**Linting & Formatting**:
- Ruff (linting)
- Black (formatting)
- mypy (type checking)

**Type Hints**:
- All functions must have type hints
- Use Pydantic for data validation

**Code Style**:
- Follow PEP 8
- Maximum line length: 100 characters
- Docstrings for all public functions

### 9.2 Frontend Standards

**Linting & Formatting**:
- ESLint (linting)
- Prettier (formatting)
- TypeScript strict mode

**Code Style**:
- Functional components with hooks
- Use TypeScript interfaces for all props
- Meaningful component and variable names

### 9.3 Git Workflow

**Branch Strategy**:
- `main` - production-ready code
- `develop` - integration branch
- Feature branches: `feature/session-management`
- Bug fixes: `fix/file-upload-validation`

**Commit Messages**:
```
feat: add session cloning functionality
fix: resolve PDF extraction encoding issue
docs: update API documentation
test: add tests for chat streaming
```

---

## 10. Performance & Scalability

### 10.1 Performance Targets

**Response Times**:
- API endpoints: < 200ms
- LLM streaming: First token < 2s, complete response < 5s
- File upload: < 1s for 10MB file

**Concurrent Users**: 10 users (MVP)

**Database Queries**:
- All queries < 100ms
- Use indexes for frequent queries

### 10.2 Optimization Strategies

**Backend**:
- Async/await for all I/O operations
- Database connection pooling
- Efficient file handling (streaming)

**Frontend**:
- Code splitting (lazy load routes)
- Optimize bundle size
- Debounce user inputs

**Future Enhancements**:
- Response caching (Redis)
- CDN for static assets
- Database read replicas

---

## 11. Security Considerations

### 11.1 MVP Security

**Input Validation**:
- Validate all user inputs (Pydantic)
- Sanitize file uploads (check mime types, size)
- Prevent SQL injection (use ORM)

**File Upload Security**:
- Validate file types (whitelist: PDF, TXT, MD)
- Enforce size limits (10MB)
- Store files outside web root
- Generate random file IDs (UUID)

**API Security**:
- CORS configuration
- Rate limiting (future)

### 11.2 Future Security (with Auth)

**Authentication**:
- JWT tokens with short expiration
- Password hashing (bcrypt)
- Secure session management

**Authorization**:
- Users can only access their own sessions
- Role-based access control (future)

---

## 12. Monitoring & Observability

### 12.1 Logging

**MVP Approach**: Simple stdout logging

**Log Levels**:
- INFO: Request/response, tool usage
- WARNING: Validation errors, retries
- ERROR: LLM errors, system errors

**Log Format**:
```
[2026-01-08 12:00:00] INFO: User message received - session_id=uuid
[2026-01-08 12:00:01] INFO: LLM request started - provider=openai model=gpt-4
[2026-01-08 12:00:02] ERROR: Search failed - error=ConnectionTimeout
```

### 12.2 Error Tracking (Future)

**Enhancement**: Integrate Sentry
- Automatic error capture
- Stack traces and context
- Error grouping and alerts

### 12.3 Metrics (Future)

**Enhancement**: Add Prometheus + Grafana
- Request rates
- Response times
- Error rates
- Token usage

---

## 13. Dependencies

### 13.1 Backend Dependencies

**Core Framework**:
- FastAPI (web framework)
- Uvicorn (ASGI server)
- Python-multipart (file uploads)

**Database**:
- SQLAlchemy (ORM)
- Alembic (migrations)
- psycopg2-binary (PostgreSQL driver)

**Validation**:
- Pydantic (data validation)
- Pydantic-settings (configuration)

**LLM Integration**:
- openai (OpenAI SDK)
- anthropic (Anthropic SDK)
- google-generativeai (Gemini SDK)

**File Processing**:
- PDF text extraction library (e.g., PyMuPDF)

**Agent Tools**:
- DuckDuckGo search library
- HTTP client for API calls

**Utilities**:
- python-dotenv (environment variables)
- SSE library for streaming

**Cloud Storage** [Enhancement]:
- boto3 (AWS S3 / Cloudflare R2)

**Testing**:
- pytest (test runner)
- pytest-asyncio (async test support)
- pytest-cov (coverage reporting)

### 13.2 Frontend Dependencies

**Core**:
- React 19
- React DOM
- TypeScript

**Build & Dev Tools**:
- Vite (build tool)
- Build tool plugins

**Styling**:
- Tailwind CSS
- PostCSS and Autoprefixer

**Routing & State**:
- React Router DOM

**Markdown & Code**:
- Markdown rendering library
- Syntax highlighting library

**HTTP Client**:
- Axios or similar

**Testing**:
- Vitest (test runner)
- React Testing Library
- User event simulation

**Code Quality**:
- ESLint (linting)
- Prettier (formatting)

**Note**: Exact versions to be determined during setup based on latest stable releases and compatibility requirements.

---

## 14. Risks & Mitigation

### 14.1 Technical Risks

| Risk | Impact | Mitigation |
|------|--------|-----------|
| LLM API rate limits | High | Implement retry with backoff |
| Large file processing slow | Medium | Set strict file size limits (10MB) |
| Context window overflow | Medium | Fail/warn, future: auto-summarize |
| SSE connection drops | Medium | Client reconnection logic |

### 14.2 Operational Risks

| Risk | Impact | Mitigation |
|------|--------|-----------|
| LLM API costs | High | Monitor usage, set budgets |
| Storage growth | Low | File limits, cleanup policy (future) |
| Database performance | Medium | Proper indexing, connection pooling |

---

## 15. Future Roadmap

### File Enhancement
- OpenAI vector store integration
- DOCX file support
- Better semantic search

### Authentication
- Email/password registration and login
- JWT-based sessions
- User-scoped sessions and files

### OAuth Integration
- Google OAuth integration
- Account linking

### UI/UX Polish
- Interface improvements
- Performance optimization
- Enhanced error handling

### Advanced Features
- Per-message LLM switching
- Message editing/deletion
- Conversation branching
- Export conversations
- Usage analytics dashboard
- Multi-user collaboration

---

## 16. Success Criteria

### MVP Success Metrics

**Functional**:
- ✅ Users can create and manage sessions
- ✅ Users can chat with 3 different LLM providers
- ✅ Agent can search the internet
- ✅ Agent can use uploaded files
- ✅ Responses stream in real-time
- ✅ Markdown renders correctly

**Technical**:
- ✅ All tests passing (70%+ coverage)
- ✅ API response times < 200ms
- ✅ LLM first token < 2s
- ✅ Supports 10 concurrent users
- ✅ Docker Compose runs cleanly

**Quality**:
- ✅ Code follows style guidelines
- ✅ Linting passes with no errors
- ✅ Type checking passes
- ✅ Documentation is complete

---

## Appendix A: Glossary

- **Session**: A conversation context with message history
- **Agent**: The AI assistant powered by LLM
- **Tool**: Capability the agent can use (search, file retrieval)
- **SSE**: Server-Sent Events, one-way streaming protocol
- **LLM**: Large Language Model (GPT, Claude, Gemini)
- **Provider**: LLM service provider (OpenAI, Anthropic, Google)
- **Token**: Unit of text for LLM processing
- **Context Window**: Maximum tokens LLM can process

---

## Appendix B: References

- FastAPI Documentation: https://fastapi.tiangolo.com/
- React Documentation: https://react.dev/
- OpenAI API: https://platform.openai.com/docs
- Anthropic API: https://docs.anthropic.com/
- Google Generative AI: https://ai.google.dev/docs
- DuckDuckGo Search: https://pypi.org/project/duckduckgo-search/
- PyMuPDF: https://pymupdf.readthedocs.io/

---

**Document Version**: 1.2
**Last Updated**: January 9, 2026
**Status**: ✅ Ready for Development (All behavioral details finalized)
