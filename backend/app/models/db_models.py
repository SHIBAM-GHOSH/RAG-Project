"""
=============================================================================
FILE: backend/app/models/db_models.py
PURPOSE: Defines SQLAlchemy ORM Database Table Schemas.
WHAT IT DOES:
  1. Defines 'projects' table for storing Project records.
  2. Defines 'documents' table for storing PDF metadata linked to a Project.
  3. Defines 'sessions' table for storing Chat Session records linked to a Project.
=============================================================================
"""

from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.core.database import Base

class ProjectModel(Base):
    """Database table model for Study Projects."""
    __tablename__ = "projects"

    id = Column(String(255), primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships with cascade delete (Deleting a project removes its docs and sessions)
    documents = relationship("DocumentModel", back_populates="project", cascade="all, delete-orphan")
    sessions = relationship("SessionModel", back_populates="project", cascade="all, delete-orphan")


class DocumentModel(Base):
    """Database table model for uploaded PDF Documents."""
    __tablename__ = "documents"

    id = Column(String(255), primary_key=True, index=True)
    project_id = Column(String(255), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    filename = Column(String(255), nullable=False)
    total_chunks = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship back to parent project
    project = relationship("ProjectModel", back_populates="documents")


class SessionModel(Base):
    """Database table model for Chat Sessions (e.g. s1, s2)."""
    __tablename__ = "sessions"

    id = Column(String(255), primary_key=True, index=True)
    project_id = Column(String(255), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship back to parent project
    project = relationship("ProjectModel", back_populates="sessions")
