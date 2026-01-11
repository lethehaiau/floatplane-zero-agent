"""
Main FastAPI application entry point.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api import sessions, chat, files

# Create FastAPI app
app = FastAPI(
    title="Floatplane Zero Agent API",
    description="AI Chat Agent with multi-LLM support",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(sessions.router)
app.include_router(chat.router)
app.include_router(files.router)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "floatplane-zero-agent",
        "version": "1.0.0"
    }


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Floatplane Zero Agent API",
        "docs": "/docs"
    }


@app.get("/api/models")
async def list_models():
    """
    List available LLM providers and models.
    Only returns providers that have API keys configured.
    """
    models = []

    # OpenAI
    if settings.OPENAI_API_KEY:
        models.append({
            "provider": "openai",
            "model": "gpt-4",
            "display_name": "OpenAI / GPT-4"
        })

    # Anthropic
    if settings.ANTHROPIC_API_KEY:
        models.append({
            "provider": "anthropic",
            "model": "claude-sonnet-4-20250514",
            "display_name": "Anthropic / Claude Sonnet 4"
        })

    # Google
    if settings.GOOGLE_API_KEY:
        models.append({
            "provider": "google",
            "model": "gemini/gemini-2.5-flash",
            "display_name": "Google / Gemini 2.5 Flash"
        })

    return {"models": models}
