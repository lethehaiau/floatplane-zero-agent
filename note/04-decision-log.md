# Design Decision Log

**Version**: 1.0
**Date**: January 8, 2026

---

## Purpose

This document records important design decisions made during development, including:
- **What** was decided
- **Why** we chose this approach
- **Alternatives** considered
- **Trade-offs** accepted

---

## Decision Template

When adding a new decision, use this format:

```markdown
### [Decision ID]: [Short Title]

**Date**: YYYY-MM-DD
**Phase**: [Phase number]
**Status**: Accepted / Revisited / Superseded

**Context**: [What problem are we solving? What constraints exist?]

**Decision**: [What did we decide to do?]

**Rationale**: [Why this approach?]
- [Reason 1]
- [Reason 2]
- [Reason 3]

**Alternatives Considered**:
1. **[Alternative A]**: [Why not chosen]
2. **[Alternative B]**: [Why not chosen]

**Consequences**:
- ✅ **Pros**: [Benefits of this decision]
- ⚠️ **Cons**: [Drawbacks or limitations]
- 🔮 **Future Impact**: [How this affects future work]

**Related Decisions**: [Links to other decisions]
```

---

## Decisions

### D001: Pure Monolithic Architecture

**Date**: 2026-01-08
**Phase**: Planning
**Status**: Accepted

**Context**:
Need to choose overall architecture for the chat agent application. Team has 1-2 developers, MVP timeline is 4 weeks, limited budget.

**Decision**:
Use pure monolithic architecture with FastAPI backend and React frontend, all deployed via Docker Compose.

**Rationale**:
- Fastest development time (3-4 weeks vs 6+ for other approaches)
- Simplest to understand and modify
- Lowest operational complexity (single deployment)
- Cost-effective for MVP (~$30-60/month)
- Can evolve to hybrid/microservices later if needed

**Alternatives Considered**:
1. **Hybrid Architecture**: More scalable but adds 2-4 weeks to development
2. **Microservices**: Too complex for MVP, requires 10-12 weeks and larger team
3. **Serverless**: Variable costs, cold start issues, different local dev experience

**Consequences**:
- ✅ **Pros**: Fast MVP, simple deployment, low cost, easy debugging
- ⚠️ **Cons**: Limited independent scaling, technology lock-in
- 🔮 **Future Impact**: May need to refactor to hybrid if scaling LLM processing becomes bottleneck

**Related Decisions**: D002 (Storage Abstraction)

---

### D002: Storage Abstraction Layer

**Date**: 2026-01-08
**Phase**: Planning
**Status**: Accepted

**Context**:
Need to decide between local file storage vs cloud storage (S3) for uploaded files. Want simplicity for MVP but clear path to cloud migration.

**Decision**:
Build storage abstraction layer from day 1, start with local file storage implementation, add S3 as enhancement.

**Rationale**:
- Local storage is simplest to implement (~30 min vs 2-3 hours for S3)
- Abstraction layer enables zero-code-change migration to S3 later
- No cloud costs during development
- Clean separation of concerns (API doesn't know about storage implementation)

**Alternatives Considered**:
1. **S3 from start**: More complexity, cloud costs from day 1, harder to develop locally
2. **Local storage only**: Would require significant refactoring to migrate to cloud later
3. **No abstraction layer**: Couples API code to storage implementation

**Consequences**:
- ✅ **Pros**: Fast MVP, future-proof design, clean architecture
- ⚠️ **Cons**: Slight upfront complexity for abstraction layer
- 🔮 **Future Impact**: S3 migration is configuration change, not code change

**Related Decisions**: D001 (Architecture)

---

### D003: No Authentication in MVP

**Date**: 2026-01-08
**Phase**: Planning
**Status**: Accepted

**Context**:
Building chat agent MVP. Authentication adds complexity and development time. Need to balance security with speed to market.

**Decision**:
Launch MVP without authentication (single-user mode), design database schema to easily add authentication later.

**Rationale**:
- Saves 3-5 days of development time
- Simplifies testing and development
- Good for demo/POC use cases
- Schema designed with `user_id` column ready for future auth

**Alternatives Considered**:
1. **Basic auth from start**: Adds 3-5 days, may not be needed for all users
2. **OAuth only**: Too complex for MVP
3. **API key only**: Still requires user management

**Consequences**:
- ✅ **Pros**: Faster MVP, simpler initial deployment
- ⚠️ **Cons**: Cannot support multiple users, not production-ready for public access
- 🔮 **Future Impact**: Auth can be added as enhancement without schema migration

**Related Decisions**: None

---

### D004: SSE for Streaming (Not WebSocket)

**Date**: 2026-01-08
**Phase**: Planning
**Status**: Accepted

**Context**:
Need real-time streaming of LLM responses to frontend. Two main options: Server-Sent Events (SSE) or WebSocket.

**Decision**:
Use Server-Sent Events (SSE) for streaming LLM responses.

**Rationale**:
- Simpler than WebSocket (one-way communication is sufficient)
- Native browser support via EventSource API
- Automatic reconnection handling
- Works with standard HTTP/HTTPS
- FastAPI has built-in SSE support (sse-starlette)
- No need for bidirectional communication

**Alternatives Considered**:
1. **WebSocket**: More complex, bidirectional (overkill for this use case)
2. **Polling**: Inefficient, high latency, poor user experience
3. **Long polling**: Better than polling but still inefficient

**Consequences**:
- ✅ **Pros**: Simple, reliable, automatic reconnection
- ⚠️ **Cons**: One-way only (not a problem for this use case)
- 🔮 **Future Impact**: If we need bidirectional communication later, can add WebSocket for specific features

**Related Decisions**: None

---

### D005: DuckDuckGo for Search (Free)

**Date**: 2026-01-08
**Phase**: Planning
**Status**: Accepted

**Context**:
Agent needs internet search capability. Options include Google Custom Search, Bing API, SerpAPI (paid), or DuckDuckGo (free).

**Decision**:
Use DuckDuckGo search via `duckduckgo-search` Python package.

**Rationale**:
- Completely free (no API key needed)
- No rate limits for reasonable usage
- Python package available and maintained
- Good enough quality for MVP
- Zero cost during development

**Alternatives Considered**:
1. **Google Custom Search**: Limited free tier (100 queries/day), then $5/1000 queries
2. **Bing Web Search API**: Requires Azure account, complex pricing
3. **SerpAPI**: $50+/month, overkill for MVP

**Consequences**:
- ✅ **Pros**: Free, simple, no API keys
- ⚠️ **Cons**: May have lower quality than Google, potential rate limiting at high volume
- 🔮 **Future Impact**: Can switch to paid search API if needed (implementation stays same, just swap tool)

**Related Decisions**: None

---

### D006: Local Text Extraction (Not Vector Store for MVP)

**Date**: 2026-01-08
**Phase**: Planning
**Status**: Accepted

**Context**:
Need to extract and search text from uploaded files (PDF, TXT, MD). Options: simple full-text search vs OpenAI vector store for semantic search.

**Decision**:
Start with local text extraction (PyMuPDF) and full-text search (SQL LIKE or pg_trgm), add vector store as enhancement.

**Rationale**:
- Simpler to implement (~2-3 hours vs 1-2 days for vector store)
- No additional costs (vector store has API costs)
- Good enough for small files and exact matches
- Clear upgrade path to vector store later

**Alternatives Considered**:
1. **OpenAI Vector Store from start**: Better search quality but adds complexity and costs
2. **Local vector embeddings (sentence-transformers)**: Requires GPU/CPU compute, slower
3. **No file search**: Incomplete feature

**Consequences**:
- ✅ **Pros**: Simple, fast to implement, no extra costs
- ⚠️ **Cons**: Limited to keyword matching, not semantic search
- 🔮 **Future Impact**: Vector store can be added as enhancement without breaking existing functionality

**Related Decisions**: None

---

### D007: Flexible LLM Provider Configuration

**Date**: 2026-01-09
**Phase**: Planning
**Status**: Accepted

**Context**:
Need to decide if all 3 LLM providers (OpenAI, Anthropic, Google) must be configured for app to run, or if developers can test with just one.

**Decision**:
App can run with only 1 provider configured. Model selector shows only configured providers.

**Rationale**:
- Easier for local development and testing
- Not all developers may have access to all 3 API keys
- Lower barrier to entry for trying the app
- Production can enable all providers while dev uses just one

**Alternatives Considered**:
1. **Require all 3 providers**: Forces complete setup, harder for dev/testing
2. **Mock providers if not configured**: Adds complexity, confusing behavior

**Consequences**:
- ✅ **Pros**: Flexible, easier development, lower barrier to entry
- ⚠️ **Cons**: Need to handle "no providers configured" edge case
- 🔮 **Future Impact**: UI must dynamically populate model selector based on configured providers

**Related Decisions**: None

---

### D008: Simple State Management First

**Date**: 2026-01-09
**Phase**: Planning
**Status**: Accepted

**Context**:
Need to choose frontend state management approach. Options: Redux, Context API, local state, or state management library (Zustand, Jotai).

**Decision**:
Start simple with React Context and local state. Only add Redux if complexity requires it.

**Rationale**:
- MVP state is relatively simple (sessions list, current session, messages)
- Context API + local state sufficient for most React apps
- Redux adds boilerplate and learning curve
- Can migrate to Redux later if state management becomes complex
- Avoid premature abstraction

**Alternatives Considered**:
1. **Redux from start**: More boilerplate, overkill for MVP
2. **Zustand/Jotai**: Lighter than Redux but still adds dependency
3. **Local state only**: Too fragmented, harder to share state

**Consequences**:
- ✅ **Pros**: Simpler code, faster development, less boilerplate
- ⚠️ **Cons**: May need refactor to Redux if state grows complex
- 🔮 **Future Impact**: If we add advanced features (real-time collaboration, undo/redo), may need Redux

**Related Decisions**: None

---

### D009: Session Title Auto-Generation Strategy

**Date**: 2026-01-09
**Phase**: Planning
**Status**: Accepted

**Context**:
Need to decide how to generate session titles. Options: default "New Chat", use first N words, ask LLM to generate title.

**Decision**:
Auto-generate from first user message:
- **MVP**: Use first 50 characters of user's first message
- **Enhancement**: Ask LLM to generate concise title (2-6 words)
- Always user-editable

**Rationale**:
- More descriptive than generic "New Chat" or "New Chat 1, 2, 3..."
- First N words is simple and free (no extra LLM call)
- LLM-generated titles as enhancement provides better quality
- User can edit if they don't like auto-generated title

**Alternatives Considered**:
1. **Default "New Chat"**: Less helpful, all sessions look same in list
2. **LLM generate in MVP**: Extra LLM call cost, slower session creation
3. **User must provide title**: Friction in UX, slows down creation

**Consequences**:
- ✅ **Pros**: Descriptive titles, no extra cost in MVP, better UX
- ⚠️ **Cons**: First 50 chars might be too long/truncated awkwardly
- 🔮 **Future Impact**: Enhancement can improve title quality with LLM summarization

**Related Decisions**: None

---

### D010: Empty State UI Design

**Date**: 2026-01-09
**Phase**: Planning
**Status**: Accepted

**Context**:
Need to design the UI for empty state (no messages yet) and new session creation.

**Decision**:
Centered landing page UI (similar to Grok but simpler):
- App logo at top
- Large text input card: "What do you want to know?"
- Model selector dropdown above/near input
- On first message submit → transition to chat UI layout
- Same UI shown when creating new session

**Rationale**:
- Clean, focused entry point
- Model selection upfront (locked to session after first message)
- Smooth transition to chat UI after first interaction
- Grok's design is proven and user-friendly
- Simpler implementation than dual layout (sidebar always visible)

**Alternatives Considered**:
1. **Always show sidebar**: More complex initial layout, less focused
2. **Empty chat UI with placeholder**: Less inviting, unclear what to do
3. **Onboarding wizard**: Too much friction for simple app

**Consequences**:
- ✅ **Pros**: Clean, inviting, clear call-to-action, model selection upfront
- ⚠️ **Cons**: Requires layout transition after first message (adds complexity)
- 🔮 **Future Impact**: May add quick action buttons (like Grok's DeepSearch) in enhancement

**Related Decisions**: D009 (session title uses first message)

---

## How to Add Decisions

**During Development**:
1. When you make an important design choice during implementation
2. Copy the decision template above
3. Fill in all sections
4. Assign next decision ID (D007, D008, etc.)
5. Add to this document

**What Qualifies as a Decision**:
- ✅ Architectural choices (patterns, frameworks, tools)
- ✅ Technology selections (libraries, databases, APIs)
- ✅ Design patterns (how to structure code)
- ✅ Trade-offs (performance vs simplicity, cost vs features)
- ❌ Implementation details (variable names, minor refactors)
- ❌ Obvious choices (using React hooks, FastAPI decorators)

**Keep It Useful**:
- Be concise but complete
- Focus on "why" not "what"
- Include alternatives considered
- Note trade-offs honestly
- Link related decisions

---

**Document Version**: 1.1
**Last Updated**: January 9, 2026
**Total Decisions**: 10
