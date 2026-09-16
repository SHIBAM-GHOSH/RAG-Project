from datetime import datetime
from typing import List, Optional
from sqlalchemy import String, Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.GitHubProfile import GitHubProfile
    from app.models.repository_file import RepositoryFile
    from app.models.chunk import CodeChunk
    from app.models.ingestion_job import IngestionJob





class Repository(Base):
    # Table name in PostgreSQL
    __tablename__ = "repositories"

    # Primary key ID
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Foreign key linking this repo to its GitHubProfile owner
    profile_id: Mapped[int] = mapped_column(ForeignKey("github_profiles.id", ondelete="CASCADE"), nullable=False)
    
    # Short repo name (e.g., "flask")
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Full name (e.g., "pallets/flask"), indexed and unique
    full_name: Mapped[str] = mapped_column(String(512), unique=True, index=True, nullable=False)
    
    # Default git branch (e.g., "main" or "master")
    default_branch: Mapped[str] = mapped_column(String(100), default="main")
    
    # Primary programming language (e.g., "python")
    language: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Ingestion status: UNPROCESSED, INGESTING, READY, FAILED
    status: Mapped[str] = mapped_column(String(50), default="UNPROCESSED")
    
    # Timestamp when discovered
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships (Many-to-One back to profile, One-to-Many to files and chunks)
    profile: Mapped["GitHubProfile"] = relationship("GitHubProfile", back_populates="repositories")
    files: Mapped[List["RepositoryFile"]] = relationship("RepositoryFile", back_populates="repository", cascade="all, delete-orphan")
    chunks: Mapped[List["CodeChunk"]] = relationship("CodeChunk", back_populates="repository", cascade="all, delete-orphan")
    jobs: Mapped[List["IngestionJob"]] = relationship("IngestionJob", back_populates="repository", cascade="all, delete-orphan")
