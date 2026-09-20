# 📚 Study Session RAG API & Dashboard

A production-grade Retrieval-Augmented Generation (RAG) system built with **FastAPI**, **Streamlit**, **Supabase PostgreSQL**, **Pinecone Vector Database**, and **Groq LLM**. Designed for multi-project study organization, instant PDF document chunking & vector search, page-level citation tracking, and persistent chat sessions.

---

## 🏗️ System Architecture

```
                                  +-----------------------+
                                  |   Streamlit Frontend  |
                                  |   (ChatGPT-Style UI)  |
                                  +-----------+-----------+
                                              |
                                              | HTTP REST API
                                              v
                                  +-----------------------+
                                  |    FastAPI Backend    |
                                  +-----+-----------+-----+
                                        |           |
            +---------------------------+           +---------------------------+
            | Metadata & Sessions                   | Vector Search & LLM       |
            v                                       v
+-----------------------+               +-----------------------+
|  Supabase PostgreSQL  |               |  HuggingFace Embed    |
|   (SQLAlchemy ORM)    |               | (all-MiniLM-L6-v2)    |
|                       |               +-----------+-----------+
| - Projects            |                           |
| - Documents Metadata  |                           v
| - Chat Sessions       |               +-----------------------+
+-----------------------+               |    Pinecone Vector    |
                                        |    Database (384d)    |
                                        +-----------+-----------+
                                                    | Context Chunks
                                                    v
                                        +-----------------------+
                                        |   Groq LLM Engine     |
                                        |    (groq/compound)    |
                                        +-----------------------+
```

---

## 💾 Database Schemas

### Relational Database (Supabase PostgreSQL)

| Table | Primary Key | Foreign Keys | Key Attributes |
|---|---|---|---|
| `projects` | `id` (VARCHAR 255) | None | `name` (VARCHAR), `created_at` (DATETIME) |
| `documents` | `id` (VARCHAR 255) | `project_id` -> `projects.id` (CASCADE) | `filename` (VARCHAR), `total_chunks` (INT), `created_at` (DATETIME) |
| `sessions` | `id` (VARCHAR 255) | `project_id` -> `projects.id` (CASCADE) | `name` (VARCHAR), `created_at` (DATETIME) |

### Vector Database (Pinecone)

- **Index Name:** `study-rag-index`
- **Dimension:** 384 (`all-MiniLM-L6-v2`)
- **Metric:** Cosine Similarity
- **Metadata Filters:** `project_id` (guarantees strict project-level data isolation), `filename`, `page`, `text`

---

## 🛠️ Technology Stack

- **Backend:** Python 3.11, FastAPI, Pydantic V2, Uvicorn
- **Database & ORM:** Supabase PostgreSQL, SQLAlchemy, Psycopg2
- **Vector DB & Embeddings:** Pinecone Serverless SDK, `sentence-transformers` (`all-MiniLM-L6-v2`)
- **LLM Provider:** Groq API (`groq/compound` model via official `groq` SDK)
- **Frontend:** Streamlit (Custom Dark Theme with Chat-Style UI & Citation previews)
- **Testing & CI/CD:** `pytest`, `fastapi.testclient.TestClient`, GitHub Actions (`.github/workflows/ci.yml`)

---

## 📡 API Endpoints

### Projects
- `POST /api/v1/projects/` - Create a new study project
- `GET /api/v1/projects/` - List all active projects

### Documents
- `POST /api/v1/projects/{project_id}/documents` - Upload PDF, auto-chunk, generate 384-dim embeddings, & upsert to Pinecone

### Sessions & Chat
- `POST /api/v1/projects/{project_id}/sessions` - Create a chat session (e.g. `s1`, `Exam Prep`)
- `GET /api/v1/projects/{project_id}/sessions` - List chat sessions for a project
- `POST /api/v1/sessions/{session_id}/chat` - Query grounded RAG pipeline; returns answer with page-level citations

---

## 🧪 Testing & CI/CD Pipeline

The project includes an automated testing suite using `pytest` and `TestClient`:

```bash
# Run pytest locally
pytest tests/ -v
```

### GitHub Actions CI Workflow (`.github/workflows/ci.yml`)
- Triggers automatically on every `push` or `pull_request`.
- Spins up a clean Ubuntu container with Python 3.11.
- Installs dependencies from `requirements.txt`.
- Injects environment secrets (`DATABASE_URL`, `GROQ_API_KEY`, `PINECONE_API_KEY`, etc.).
- Executes `pytest tests/ -v` to ensure zero regressions before merging.

---

## 🚀 Local Development Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/SHIBAM-GHOSH/RAG-Project.git
   cd RAG-Project
   ```

2. **Configure Environment Variables (`.env`):**
   Create a `.env` file in the project root:
   ```env
   DATABASE_URL=postgresql+psycopg2://user:password@host:5432/postgres
   GROQ_API_KEY=gsk_your_groq_api_key
   PINECONE_API_KEY=your_pinecone_api_key
   PINECONE_INDEX_NAME=study-rag-index
   EMBEDDING_MODEL_NAME=all-MiniLM-L6-v2
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run FastAPI Backend:**
   ```bash
   uvicorn backend.app.main:app --reload
   ```

5. **Run Streamlit Frontend:**
   ```bash
   streamlit run frontend/app.py
   ```