"""
=============================================================================
FILE: backend/app/api/chat_router.py
PURPOSE: Handles RAG Q&A Chat queries for a specific Chat Session.
WHAT IT DOES:
  1. Verifies the session_id exists in Supabase PostgreSQL DB.
  2. Extracts its parent project_id from the DB record.
  3. Calls rag_service to perform vector search in Pinecone and Groq LLM inference.
  4. Returns the generated answer alongside page-level PDF source citations.
=============================================================================
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.models.db_models import SessionModel
from backend.app.models.schemas import ChatQueryRequest, ChatQueryResponse
from backend.app.services.rag_service import rag_service

# Create APIRouter instance for chat Q&A endpoints
router = APIRouter(prefix="/api/v1/sessions", tags=["Chat"])


@router.post("/{session_id}/chat", response_model=ChatQueryResponse)
def ask_question_in_session(session_id: str, payload: ChatQueryRequest, db: Session = Depends(get_db)):
    """Ask a study question in a session and get a grounded RAG response from project PDFs."""
    # 1. Verify that session exists in DB
    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")

    # 2. Get parent project_id for this session from DB record
    project_id = session.project_id

    # 3. Call RAG service to query Pinecone & Groq LLM
    result = rag_service.answer_question(
        query=payload.question,
        project_id=project_id,
        top_k=3
    )

    return result
