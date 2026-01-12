# Floatplane Zero Agent

A simple AI chat agent that allows users to interact with multiple LLM providers (OpenAI, Anthropic, Google) through a web-based chat interface.



https://github.com/user-attachments/assets/dd7d68cf-e141-4e88-8082-59ff2c1813f9



## Tech Stack

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL 15
- **LLM Integration**: LiteLLM (OpenAI, Anthropic, Google)
- **Streaming**: Server-Sent Events (SSE)

### Frontend
- **Framework**: React 19 + TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **State Management**: React Context + Local State

### Infrastructure
- **Containerization**: Docker + Docker Compose
- **Database Migrations**: Alembic

## Getting Started

### Prerequisites
- Docker and Docker Compose installed
- LLM API keys (at least one):
  - OpenAI API key
  - Anthropic API key
  - Google API key

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd floatplane-zero-agent
   ```

2. **Configure environment variables**

   Backend:
   ```bash
   cd backend
   cp .env.example .env
   # Edit .env and add your API keys
   ```

   Frontend:
   ```bash
   cd ../frontend
   cp .env.example .env
   # (Optional) Modify VITE_API_BASE_URL if needed
   ```

3. **Start the application**
   ```bash
   # From the project root
   docker-compose up --build
   ```

4. **Access the application**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

### Development

**Stop the application**:
```bash
docker-compose down
```

**View logs**:
```bash
docker-compose logs -f backend
docker-compose logs -f frontend
```

**Rebuild after changes**:
```bash
docker-compose up --build
```

## Project Structure

```
floatplane-zero-agent/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── main.py         # FastAPI app entry point
│   │   └── config.py       # Configuration
│   ├── tests/              # Backend tests
│   ├── uploads/            # File uploads (gitignored)
│   ├── Dockerfile
│   ├── requirements.txt
│   └── .env
├── frontend/               # React frontend
│   ├── src/
│   │   ├── App.tsx         # Main app component
│   │   ├── main.tsx        # Entry point
│   │   └── index.css       # Tailwind styles
│   ├── Dockerfile
│   ├── package.json
│   └── .env
├── note/                   # Project documentation
├── docker-compose.yml
└── README.md
```

## Documentation

See the `note/` directory for detailed project documentation:
- `01-technical-specification.md` - Technical specification
- `02-implementation-plan.md` - Implementation plan
- `03-current-focus.md` - Current development focus
- `04-decision-log.md` - Design decisions
- `05-progress-tracker.md` - Progress tracking

## License

[Add your license here]
