"""
Model: CodeChunk
Purpose: Stores AST-parsed code blocks (functions, classes, methods) with line numbers, 
         symbol names, raw code content, and dense vector embeddings (pgvector Vector(1536)) 
         for hybrid RAG search and citation generation.
"""

from typing import Optional
from sqlalchemy import String, Integer, Text, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pgvector.sqlalchemy import Vector

from app.core.database import Base

from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.repository import Repository
    from app.models.repository_file import RepositoryFile




class CodeChunk(Base):
    # Table name in PostgreSQL
    __tablename__ = "code_chunks"

    # Primary key ID
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Foreign Keys linking chunk to its parent Repository and File
    repository_id: Mapped[int] = mapped_column(ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False, index=True)
    file_id: Mapped[int] = mapped_column(ForeignKey("repository_files.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Extracted AST Symbol Name (e.g. "doFilterInternal" or "SecurityConfig")
    symbol_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    
    # Symbol Type (e.g. "function", "class", "method", "docstring")
    symbol_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # Start and End line numbers in the original source code file
    start_line: Mapped[int] = mapped_column(Integer, nullable=False)
    end_line: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # Raw source code text content of the chunk
    content: Mapped[str] = mapped_column(Text, nullable=False)
    
    # DENSE VECTOR EMBEDDING (pgvector Vector type with 1536 dimensions for OpenAI/compatible models)
    embedding = mapped_column(Vector(1536), nullable=True)

    # Relationships back to Repository and File
    repository: Mapped["Repository"] = relationship("Repository", back_populates="chunks")
    file: Mapped["RepositoryFile"] = relationship("RepositoryFile", back_populates="chunks")

    # Composite Index for fast repository-level and file-level filtered queries
    __table_args__ = (
        Index("idx_code_chunks_repo_file", "repository_id", "file_id"),
    )
