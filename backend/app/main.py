"""
=============================================================================
FILE: backend/app/main.py
PURPOSE: Main entry point for the FastAPI Study Session RAG Application.
WHAT IT DOES:
  1. Initializes the FastAPI app instance with CORS middleware.
  2. Registers all API routers (projects, documents, sessions, chat).
  3. Provides root & health check endpoints for server monitoring.
=============================================================================
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

#rate limiter
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded


# Import all API routers
from backend.app.api.project_creator import router as projects_router
from backend.app.api.doc_uploader import router as documents_router
from backend.app.api.session_manager import router as sessions_router
from backend.app.api.chat_router import router as chat_router

from backend.app.core.database import Base, engine
import backend.app.models.db_models  # Load ORM models for table creation


# Initialize FastAPI app
app = FastAPI(
    title="Study Session RAG API",
    description="Production-Grade RAG API for Study Sessions using Groq LLM & Pinecone",
    version="1.0.0"
)

# Initialize IP-based Rate Limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)



# Auto-create tables in database if they do not exist
Base.metadata.create_all(bind=engine)


# Configure CORS (Cross-Origin Resource Sharing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows requests from any frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(projects_router)
app.include_router(documents_router)
app.include_router(sessions_router)
app.include_router(chat_router)

@app.get("/")
def root():
    """Root route returning API welcome message."""
    return {"message": "Welcome to the Study Session RAG API!"}

@app.get("/health")
def health_check():
    """Health check endpoint for cloud monitoring."""
    return {"status": "healthy"}
