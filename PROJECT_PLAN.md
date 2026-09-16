# GitHub Code Intelligence Platform - Project Plan & Roadmap

## Overview
A production-grade Code RAG (Retrieval-Augmented Generation) platform designed to ingest public GitHub repositories, perform AST/code-aware chunking, index code using PostgreSQL + `pgvector` and BM25 lexical search, and deliver grounded Q&A with precise citation verification and multi-layered security guardrails.

---

## Technical Stack

- **Backend**: Python 3.12+, FastAPI, Pydantic v2, SQLAlchemy 2.0, Alembic, `asyncio`, `pytest`, `httpx`
- **Frontend**: React, TypeScript, Vite, Tailwind CSS, Vitest, React Testing Library, Playwright
- **Database**: PostgreSQL 16 + `pgvector`
- **Retrieval & RAG**: Dense vector search (pgvector), BM25 lexical search, Reciprocal Rank Fusion (RRF), AST/Tree-sitter chunking, Configurable LLM & Embedding providers
- **DevOps & Infrastructure**: Docker, Docker Compose, GitHub Actions CI/CD, Nginx, AWS Deployment

---

## 18-Phase Implementation Roadmap

- [x] **PHASE 0**: Architecture & Repository Setup (Workspace inspection, directory structure, ADR-001, implementation plan)
- [ ] **PHASE 1**: FastAPI Skeleton + PostgreSQL + Alembic Setup
- [ ] **PHASE 2**: GitHub REST API Integration & Repository Discovery
- [ ] **PHASE 3**: React + TypeScript + Tailwind UI Repository Dashboard
- [ ] **PHASE 4**: Asynchronous Repository Ingestion Pipeline
- [ ] **PHASE 5**: AST / Code-Aware Parsing & Chunking Engine (Tree-sitter)
- [ ] **PHASE 6**: Embedding Generation & `pgvector` Indexing
- [ ] **PHASE 7**: BM25 Lexical Retrieval Engine
- [ ] **PHASE 8**: Reciprocal Rank Fusion (RRF) Hybrid Retrieval Engine
- [ ] **PHASE 9**: RAG Context Assembly, Generation & Citation Engine
- [ ] **PHASE 10**: Security Guardrails (Prompt Injection, Secret & PII Scanner)
- [ ] **PHASE 11**: Citation Verification Engine
- [ ] **PHASE 12**: Automated RAG Evaluation Framework (Recall@K, Precision@K, Correctness)
- [ ] **PHASE 13**: Comprehensive Testing (Unit, Integration, E2E with Playwright)
- [ ] **PHASE 14**: Containerization (Docker & Docker Compose)
- [ ] **PHASE 15**: CI/CD Pipelines (GitHub Actions with RAG Eval & Security checks)
- [ ] **PHASE 16**: Observability & Metrics (Structured Logging, Latency & Token Tracking)
- [ ] **PHASE 17**: AWS Cloud Deployment
- [ ] **PHASE 18**: Performance Optimization, Final Load Testing & Documentation
