from pydantic import BaseModel, Field
from typing import List, Optional

# ==========================================
# 1. Project Schemas (ChatGPT Projects)
# ==========================================
class ProjectCreate(BaseModel):
    """Payload required to create a new study project"""
    name: str = Field(..., description="Name of the project", json_schema_extra={"example": "Physics-101"})

class ProjectResponse(BaseModel):
    """API response model for a project"""
    id: str
    name: str
    created_at: str


# ==========================================
# 2. Document Schemas (PDF Metadata)
# ==========================================
class DocumentResponse(BaseModel):
    """API response model for an uploaded study PDF"""
    id: str
    project_id: str
    filename: str
    total_chunks: int


# ==========================================
# 3. Session Schemas (Chat Sessions: s1, s2)
# ==========================================
class SessionCreate(BaseModel):
    """Payload required to create a chat session (e.g. s1) inside a project"""
    name: str = Field(..., description="Name of the session", json_schema_extra={"example": "s1"})

class SessionResponse(BaseModel):
    """API response model for a chat session"""
    id: str
    project_id: str
    name: str
    created_at: str


# ==========================================
# 4. RAG Chat Question & Response Schemas
# ==========================================
class ChatQueryRequest(BaseModel):
    """Payload sent by user when asking a question in a session"""
    question: str = Field(..., description="User question", json_schema_extra={"example": "What is Newton's second law?"})

class SourceCitation(BaseModel):
    """Citation snippet showing which page the answer came from"""
    filename: str
    page: int
    text_snippet: str

class ChatQueryResponse(BaseModel):
    """API response containing the LLM generated answer and source citations"""
    answer: str
    sources: List[SourceCitation]
