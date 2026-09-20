# AGENTS.md

# Project‑Scoped Rules for RAG‑Project2

- **Scope**: These rules apply only to the current workspace (`RAG-Project2`).
- **Purpose**: Guide any custom agents, sub‑agents, or automation scripts used during development and deployment.

## General Guidelines
1. **Do not modify frontend files** unless explicitly requested. All work should focus on the backend (`backend/` directory).
2. **Maintain API stability** – keep existing endpoint signatures (`/api/v1/projects/{project_id}/documents`, etc.) unchanged unless a migration plan is approved.
3. **Error handling** – raise `HTTPException` with appropriate status codes and clear messages for validation failures.
4. **Security** – never log raw file bytes or secret keys; use environment variables for secrets.
5. **Testing** – write unit tests under a `tests/` package that only import backend modules.

## Agent‑Specific Rules
- **PDF Upload Agent** (`doc_uploader`):
  - Verify the project exists before processing the file.
  - Accept only `.pdf` extensions.
  - Extract text, chunk, and upsert to Pinecone scoped by `project_id`.
- **RAG Service Agent** (`rag_service`):
  - Retrieve top‑k chunks using similarity search limited to the project.
  - Pass retrieved chunks to the Groq LLM via the official SDK.
  - Return a response model containing `answer`, `source_chunks`, and metadata.

## Development Workflow
- Run `pytest` locally; push to Git only when CI/CD pipelines are ready.
- Use `uvicorn backend/app/main.py --reload` for local testing.
- Keep `.env` out of version control.

---

*This file is intentionally minimal; extend it as new agents or rules are added.*
