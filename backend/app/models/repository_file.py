"""
Model: RepositoryFile
Purpose: Stores the file tree metadata of ingested GitHub repositories 
         (e.g., file path, language, file size in bytes) so RAG retrieval 
         can cite exact source file names in AI responses.
"""

from typing import List, Optional
from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.repository import Repository
    from app.models.chunk import CodeChunk




class RepositoryFile(Base):
    # Name of table in PostgreSQL database
    __tablename__ = "repository_files"

    # Auto-incrementing Primary Key
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Foreign key link: Deleting a repository deletes all its files automatically
    repository_id: Mapped[int] = mapped_column(ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False)
    
    # File path relative to repo root (e.g. "src/auth/jwt_filter.py")
    file_path: Mapped[str] = mapped_column(String(1024), nullable=False, index=True)
    
    # Programming language detected by AST parser (e.g. "python", "java")
    language: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    
    # Size of the file in bytes
    size_bytes: Mapped[int] = mapped_column(Integer, default=0)

    # Relationship back to parent Repository
    repository: Mapped["Repository"] = relationship("Repository", back_populates="files")
    
    # Relationship down to parsed CodeChunks inside this file
    chunks: Mapped[List["CodeChunk"]] = relationship("CodeChunk", back_populates="file", cascade="all, delete-orphan")
