"""
=============================================================================
FILE: backend/app/api/doc_uploader.py
PURPOSE: Handles PDF Document Uploads & Persistent DB Metadata.
WHAT IT DOES:
  1. Accepts PDF file uploads via HTTP POST.
  2. Verifies Project existence in SQL Database.
  3. Extracts text, chunks PDF, and upserts embeddings into Pinecone.
  4. Saves persistent document record in SQL Database.
=============================================================================
"""

import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.models.db_models import ProjectModel, DocumentModel
from backend.app.models.schemas import DocumentResponse
from backend.app.services.pdf_service import pdf_processor
from backend.app.services.vector_service import vector_service

router = APIRouter(prefix="/api/v1/projects", tags=["Documents"])

@router.post("/{project_id}/documents", response_model=DocumentResponse)
async def upload_document(
    project_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload a PDF study document to a specific project context."""
    # 1. Verify project exists in SQL Database
    project = db.query(ProjectModel).filter(ProjectModel.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # 2. Validate PDF file extension
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    # 3. Read raw binary file contents
    file_bytes = await file.read()

    # 4. Extract text & split into chunks tagged with metadata
    chunks = pdf_processor.chunk_pdf(
        file_bytes=file_bytes,
        filename=file.filename,
        project_id=project_id
    )

    if not chunks:
        raise HTTPException(status_code=400, detail="Failed to extract text from PDF or PDF is empty")

    # 5. Upsert embeddings into Pinecone Cloud Vector DB
    total_chunks = vector_service.upsert_chunks(chunks)

    # 6. Save persistent document record in SQL Database
    doc_id = str(uuid.uuid4())
    doc_record = DocumentModel(
        id=doc_id,
        project_id=project_id,
        filename=file.filename,
        total_chunks=total_chunks,
        created_at=datetime.now(timezone.utc)
    )

    
    db.add(doc_record)
    db.commit()
    db.refresh(doc_record)

    return DocumentResponse(
        id=doc_record.id,
        project_id=doc_record.project_id,
        filename=doc_record.filename,
        total_chunks=doc_record.total_chunks
    )
