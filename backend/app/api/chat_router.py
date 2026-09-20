"""
=============================================================================
FILE: backend/app/api/chat_router.py
PURPOSE: Handles RAG Q&A Chat queries for a specific Chat Session.
WHAT IT DOES:
  1. Applies IP-based rate limiting (5 questions / minute).
  2. Verifies session_id exists in SQL DB and extracts parent project_id.
  3. Queries Pinecone vector database for relevant context snippets.
  4. Calls Groq LLM API to generate grounded answer with citations.
=============================================================================
"""

# 1. FastAPI core imports (Request required for SlowAPI rate limiter)
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

# 2. SlowAPI Rate Limiter imports
from slowapi import Limiter
from slowapi.util import get_remote_address

# 3. Application database, models, and RAG service imports
from backend.app.core.database import get_db
from backend.app.models.db_models import SessionModel
from backend.app.models.schemas import ChatQueryRequest, ChatQueryResponse
from backend.app.services.rag_service import rag_service

# 4. Initialize rate limiter instance (tracks client IP)
limiter = Limiter(key_func=get_remote_address)

# 5. Create APIRouter instance for chat Q&A endpoints
router = APIRouter(prefix="/api/v1/sessions", tags=["Chat"])


# 6. Chat Endpoint with Rate Limiter (Max 5 calls per minute per IP)
@router.post("/{session_id}/chat", response_model=ChatQueryResponse)
@limiter.limit("5/minute")
def ask_question_in_session(
    request: Request,                     # Required parameter for SlowAPI rate limiter
    session_id: str,                      # Chat session ID from URL path
    payload: ChatQueryRequest,            # JSON request body containing user question
    db: Session = Depends(get_db)         # SQLAlchemy DB session dependency
):
    """Ask a study question in a session and get a grounded RAG response from project PDFs."""
    
    # Step A: Verify that chat session exists in SQL DB
    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")

    # Step B: Get parent project_id linked to this session
    project_id = session.project_id

    # Step C: Execute RAG pipeline (Pinecone vector search + Groq LLM inference)
    result = rag_service.answer_question(
        query=payload.question,
        project_id=project_id,
        top_k=3
    )

    # Step D: Return generated answer and page citations
    return result
