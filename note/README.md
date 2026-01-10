# Simple AI Chat Agent - Project Documentation

**Status**: Phase 1 Development Started 🚀
**Date**: January 9, 2026

---

## Overview

This directory contains the complete specification and planning documentation for the **Simple AI Chat Agent** project - a clean, developer-friendly chat application that enables users to interact with multiple LLM providers through a web interface.

---

## Documents

### 📋 [01-technical-specification.md](./01-technical-specification.md)
**Technical Specification** (~30 pages - simplified)

**WHAT to build** - High-level specification covering:
- Project overview and goals
- System architecture and technology choices
- Feature specifications with behavior logic
- Agent decision-making and tool usage
- Error handling strategies
- API design principles (not detailed schemas)
- Database schema concepts (not exact SQL)
- Project structure overview
- Testing approach
- Deployment approach
- Dependency categories (not exact versions)

**Philosophy**: Provides architectural guidance and key decisions, leaving implementation details for conversational development.

**Status**: ✅ Complete and ready for development

---

### 🗓️ [02-implementation-plan.md](./02-implementation-plan.md)
**Implementation Plan** (v2.0)

**WHEN to build** - Phased development roadmap:
- **Phase 1**: Complete chat + sessions (5-7 days) - Full working chat app
- **Phase 2**: File upload feature (3-4 days) - Upload and use files
- **Phase 3**: Search tool (2-3 days) - Internet search capability
- **Phase 4**: Polish & deployment (3-5 days) - Production-ready
- **Total Core**: ~2-3 weeks
- Enhancement phases (post-MVP)
- Each phase delivers visible, testable functionality

**Philosophy**: Build biggest value first, all core before enhancements

**Status**: ✅ Complete (v2.0 - Option 3)

---

### 🎯 [03-current-focus.md](./03-current-focus.md)
**Current Focus** (Working Memory)

**Active work tracking** - Keep context during development:
- What we're currently working on
- Recent completions
- Working notes for active discussions
- Open questions and blockers

**Status**: ✅ Ready for use (updated during development)

---

### 📝 [04-decision-log.md](./04-decision-log.md)
**Design Decision Log**

**WHY we chose** - Record of important decisions:
- Architectural choices (10 decisions logged)
- Technology selections
- Design patterns
- Trade-offs and alternatives considered

**Recent Decisions**:
- D007: Flexible LLM Provider Configuration (can run with 1 provider)
- D008: Simple State Management First (Context/local, Redux only if needed)
- D009: Session Title Auto-Generation (first 50 chars MVP, LLM enhancement)
- D010: Empty State UI Design (centered Grok-style landing page)

**Status**: ✅ Active (10 decisions logged)

---

### ✅ [05-progress-tracker.md](./05-progress-tracker.md)
**Progress Tracker** (Checklist)

**Track completion** - Simple checklist for all tasks:
- Phase 1: 30+ backend tasks
- Phase 2: 20+ LLM & agent tasks
- Phase 3: 25+ frontend tasks
- Phase 4: 30+ testing & deployment tasks
- Enhancement tasks
- Success criteria checklist

**Status**: ✅ Ready for use (check off as you complete)

---

## Quick Reference

### Core Features (Phase 1 MVP)

| Feature | Description | Status |
|---------|-------------|--------|
| **Chat Interface** | Web UI with Markdown rendering | 📋 Specified |
| **Session Management** | Create, delete, clone sessions | 📋 Specified |
| **File Upload** | PDF, TXT, MD (3/session, 10MB each) | 📋 Specified |
| **Multi-LLM** | GPT-4, Claude Sonnet, Gemini Flash | 📋 Specified |
| **Internet Search** | DuckDuckGo (agent-initiated) | 📋 Specified |
| **Streaming** | Real-time SSE streaming | 📋 Specified |
| **No Auth** | Single-user mode for MVP | 📋 Specified |

### Enhancement Features

| Feature | Priority |
|---------|----------|
| Cloud Storage (S3/R2) | High |
| OpenAI Vector Store | High |
| DOCX Support | Medium |
| Per-Message LLM Switching | Low |
| Email/Password Auth | High |
| OAuth (Google) | Medium |
| Usage Tracking | Low |

---

## Technology Stack

### Frontend
- **Framework**: React 19 + TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **Routing**: React Router DOM
- **Markdown**: react-markdown + react-syntax-highlighter
- **Streaming**: EventSource API (SSE)

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL 15+ with SQLAlchemy
- **Migrations**: Alembic
- **Streaming**: SSE (sse-starlette)
- **File Processing**: PyMuPDF (PDF), built-in (TXT/MD)
- **Search**: DuckDuckGo (duckduckgo-search)

### LLM Providers
- OpenAI (GPT-4)
- Anthropic (Claude Sonnet)
- Google (Gemini Flash)

### Deployment
- Docker Compose (Backend + Frontend + PostgreSQL)
- Monorepo structure

---

## Architecture Overview

```
Frontend (React)
    ↓ HTTP/REST + SSE
Backend (FastAPI)
    ↓
PostgreSQL + Local File Storage
    ↓
OpenAI / Anthropic / Google APIs
DuckDuckGo Search
```

**Pattern**: Pure Monolithic
- Single codebase (monorepo)
- Backend API + Frontend SPA
- PostgreSQL database
- Local file storage
- No Redis (MVP)
- No Authentication (MVP)

---

## Key Design Decisions

### ✅ What We Chose

1. **Pure Monolithic Architecture**: Simplest to build and maintain
2. **Vite + React**: Fast dev experience, lighter than Next.js
3. **SSE Streaming**: Simpler than WebSocket for one-way streaming
4. **Storage Abstraction**: Local storage (Phase 1) with abstraction layer for easy S3 migration
5. **Local Text Extraction**: Start simple, enhance with vector store later
6. **Per-Session LLM**: Lock model choice to session (simpler)
7. **No Authentication**: MVP is single-user, designed for easy auth addition
8. **PostgreSQL**: Production-ready, ACID compliance
9. **Docker Compose**: Easy local dev and deployment

### 📋 What We're Deferring (Enhancements)

1. **Cloud Storage** - S3/Cloudflare R2 (abstraction ready)
2. **Vector Store** - OpenAI vector store for better file search
3. **DOCX Support** - Microsoft Word document processing
4. **Per-Message LLM Switching** - Change model within session
5. **Authentication** - Email/password and OAuth (Google)
6. **Redis Caching** - Response caching for performance
7. **Usage Tracking** - Token and cost monitoring
8. **Advanced Context Management** - Auto-summarization

---

## File Limits

| Limit | Value |
|-------|-------|
| Max file size | 10 MB |
| Files per session | 3 |
| Total files per user | 30 (when auth added) |
| Supported formats | PDF, TXT, MD |

---

## API Quick Reference

**Base URL**: `http://localhost:8000/api`

### Key Endpoints

```
POST   /api/sessions                    # Create session
GET    /api/sessions                    # List sessions
GET    /api/sessions/{id}               # Get session with messages
DELETE /api/sessions/{id}               # Delete session
POST   /api/sessions/{id}/clone         # Clone session

POST   /api/chat/stream                 # Send message (SSE stream)

POST   /api/sessions/{id}/files         # Upload file
DELETE /api/files/{id}                  # Delete file
GET    /api/files/{id}/download         # Download file
```

---

## Development Timeline

**Note**: Detailed phased timeline is in the Implementation Plan document.

**Estimated Timeline**:
- Core MVP: 4 weeks
- Enhancements: 3-4 weeks
- Total: 7-8 weeks for complete product

---

## Success Criteria

### Functional
- ✅ Create, delete, clone sessions
- ✅ Chat with 3 LLM providers
- ✅ Upload and use files
- ✅ Internet search capability
- ✅ Real-time streaming responses
- ✅ Markdown rendering

### Technical
- ✅ Test coverage 70%+
- ✅ API response < 200ms
- ✅ LLM first token < 2s
- ✅ Support 10 concurrent users
- ✅ Docker Compose setup

### Quality
- ✅ Linting passes
- ✅ Type checking passes
- ✅ Code follows standards
- ✅ Documentation complete

---

## Workflow Guide

### How to Use These Documents

**Planning Phase** (✅ Complete):
1. Read `01-technical-specification.md` to understand WHAT to build
2. Read `02-implementation-plan.md` to understand WHEN to build features
3. Review `04-decision-log.md` to understand WHY we chose this approach

**Development Phase** (🔜 Ready to Start):
1. **Before starting work**:
   - Update `03-current-focus.md` with what you're working on
   - Check `05-progress-tracker.md` for task list

2. **During development**:
   - Work conversationally with LLM (discuss options, make decisions)
   - Use `03-current-focus.md` for working notes
   - Log important decisions in `04-decision-log.md`

3. **After completing work**:
   - Check off tasks in `05-progress-tracker.md`
   - Update `03-current-focus.md` to reflect completion
   - Clear working notes from `03-current-focus.md`

**Conversational Workflow**:
- Discuss options before implementing
- Make decisions collaboratively
- Adapt to discoveries and learnings
- No rigid templates - stay flexible

---

## Next Steps

1. ✅ **Specification Complete**
2. ✅ **Implementation Plan Complete**
3. ✅ **Supporting Files Created**
4. ✅ **Pre-Development Validation Complete**
5. 🚀 **Phase 1 Development Started**

**Current Work**:
- Creating monorepo structure (backend/, frontend/, docker-compose.yml)
- Setting up backend FastAPI project
- Configuring Docker Compose for local development
- Track progress in `05-progress-tracker.md`
- Active notes in `03-current-focus.md`

---

## Document History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-01-08 | Initial specification complete |
| 1.1 | 2026-01-08 | Planning complete - all 5 files created |
| 1.2 | 2026-01-09 | Simplified spec - removed implementation details for conversational development |
| 1.3 | 2026-01-09 | Final clarifications - added all behavioral details (file processing, tool visibility, error handling) |
| 2.0 | 2026-01-09 | New implementation plan (Option 3) - each phase delivers visible, working functionality |

---

**Status**: 🚀 Phase 1 Development Started
**Next**: Complete monorepo setup and backend foundation
