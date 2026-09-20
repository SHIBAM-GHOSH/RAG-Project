"""
=============================================================================
FILE: backend/app/api/session_manager.py
PURPOSE: Manages Chat Sessions (e.g. s1, s2) inside a Study Project.
WHAT IT DOES:
  1. Allows users to create multiple chat sessions inside a Project.
  2. Lists all active chat sessions belonging to a specific Project.
  NOTE: Sessions are persisted in Supabase PostgreSQL (not in-memory).
=============================================================================
"""

import uuid
from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.models.db_models import ProjectModel, SessionModel
from backend.app.models.schemas import SessionCreate, SessionResponse

# Create APIRouter instance for chat session endpoints
router = APIRouter(prefix="/api/v1/projects", tags=["Sessions"])


@router.post("/{project_id}/sessions", response_model=SessionResponse)
def create_session(project_id: str, payload: SessionCreate, db: Session = Depends(get_db)):
    """Create a new chat session (e.g. s1) inside a project."""
    # 1. Verify project exists in DB
    project = db.query(ProjectModel).filter(ProjectModel.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # 2. Create session record in DB
    session_id = str(uuid.uuid4())
    session_record = SessionModel(
        id=session_id,
        project_id=project_id,
        name=payload.name,
        created_at=datetime.utcnow()
    )

    db.add(session_record)
    db.commit()
    db.refresh(session_record)

    return SessionResponse(
        id=session_record.id,
        project_id=session_record.project_id,
        name=session_record.name,
        created_at=session_record.created_at.isoformat()
    )


@router.get("/{project_id}/sessions", response_model=List[SessionResponse])
def list_sessions(project_id: str, db: Session = Depends(get_db)):
    """List all chat sessions inside a specific project."""
    # 1. Verify project exists in DB
    project = db.query(ProjectModel).filter(ProjectModel.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # 2. Fetch all sessions for this project from DB
    sessions = db.query(SessionModel).filter(SessionModel.project_id == project_id).all()

    return [
        SessionResponse(
            id=s.id,
            project_id=s.project_id,
            name=s.name,
            created_at=s.created_at.isoformat()
        )
        for s in sessions
    ]
