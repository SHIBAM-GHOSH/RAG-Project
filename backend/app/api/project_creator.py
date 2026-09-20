"""
=============================================================================
FILE: backend/app/api/project_creator.py
PURPOSE: Manages Persistent Study Projects & Pinecone Resource Clean-up.
WHAT IT DOES:
  1. Creates & persists new Study Projects in SQL Database.
  2. Lists all active Projects for the user interface.
  3. Deletes a Project from SQL DB & wipes its vector embeddings from Pinecone!
=============================================================================
"""

import uuid
from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.models.db_models import ProjectModel
from backend.app.models.schemas import ProjectCreate, ProjectResponse
from backend.app.services.vector_service import vector_service

router = APIRouter(prefix="/api/v1/projects", tags=["Projects"])

@router.post("/", response_model=ProjectResponse)
def create_project(payload: ProjectCreate, db: Session = Depends(get_db)):
    """Create & persist a new study project in SQL Database."""
    project_id = str(uuid.uuid4())
    
    project = ProjectModel(
        id=project_id,
        name=payload.name,
        created_at=datetime.utcnow()
    )
    
    db.add(project)
    db.commit()
    db.refresh(project)
    
    return ProjectResponse(
        id=project.id,
        name=project.name,
        created_at=project.created_at.isoformat()
    )

@router.get("/", response_model=List[ProjectResponse])
def list_projects(db: Session = Depends(get_db)):
    """List all persisted study projects."""
    projects = db.query(ProjectModel).all()
    return [
        ProjectResponse(
            id=p.id,
            name=p.name,
            created_at=p.created_at.isoformat()
        )
        for p in projects
    ]

@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project_id: str, db: Session = Depends(get_db)):
    """Delete a Project from SQL DB & wipe all its vector embeddings from Pinecone."""
    project = db.query(ProjectModel).filter(ProjectModel.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # 1. Clean up vectors in Pinecone Cloud Vector DB
    try:
        vector_service.index.delete(filter={"project_id": project_id})
    except Exception as e:
        print(f"[WARNING] Pinecone vector delete exception: {e}")

    # 2. Delete project from SQL Database (Cascade removes documents & sessions)
    db.delete(project)
    db.commit()
    return None
