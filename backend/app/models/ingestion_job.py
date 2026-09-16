"""
Model: IngestionJob
Purpose: Tracks background repository ingestion status (PENDING, PROCESSING, COMPLETED, FAILED) 
         and error messages so HTTP requests return immediately (in ~50ms) and the frontend 
         can display live progress without gateway timeouts.
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class IngestionJob(Base):
    # Table name in PostgreSQL
    __tablename__ = "ingestion_jobs"

    # Primary key ID (Job ID returned to frontend)
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Foreign key linking job to its Target Repository
    repository_id: Mapped[int] = mapped_column(ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False)
    
    # Current Job Status: PENDING, PROCESSING, COMPLETED, FAILED
    status: Mapped[str] = mapped_column(String(50), default="PENDING", index=True)
    
    # If job fails, stores the error message and traceback for debugging
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Timestamp when job was queued
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    # Timestamp when job finished or failed
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationship back to target Repository
    repository: Mapped["Repository"] = relationship("Repository", back_populates="jobs")
