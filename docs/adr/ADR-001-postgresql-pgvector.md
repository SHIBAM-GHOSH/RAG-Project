# ADR-001: PostgreSQL + pgvector for Relational Data and Vector Search

- **Status**: Approved
- **Date**: 2026-09-16
- **Context**: The GitHub Code Intelligence Platform requires storing relational metadata (users, profiles, repositories, ingestion jobs, files, symbols, line numbers) alongside high-dimensional dense vector embeddings generated from code chunks.

---

## 1. Decision & Engineering Rationale

We have selected **PostgreSQL 16 with the `pgvector` extension** as our primary database engine for both relational metadata and vector embeddings.

### Why PostgreSQL + pgvector instead of a dedicated Vector DB (e.g., Chroma, Pinecone, Qdrant)?

1. **Transactional Consistency (ACID)**: Code indexing involves creating repository records, storing parsed file trees, saving chunk metadata, and writing vector embeddings. Using PostgreSQL guarantees single-transaction consistency (`BEGIN...COMMIT`). Vector DBs separated from metadata databases lead to dual-write problems, data drift, and complex cleanup logic if indexing fails halfway.
2. **Hybrid & Relational Filtering**: Queries often require filtering by metadata first (e.g., `WHERE repository_id = X AND language = 'python'`). PostgreSQL executes filtered vector search natively within SQL using standard indexing and query planner optimization.
3. **Operational Simplicity**: Running a single database engine drastically reduces operational overhead, container orchestration complexity, backup management, and memory footprint in early and production stages.
4. **Maturity & Ecosystem**: PostgreSQL is rock-solid, supporting Alembic schema migrations, connection pooling (`pgbouncer` or SQLAlchemy async pools), and standard backup tools (`pg_dump`).

---

## 2. Technical Details & Indexing Strategy

- **Vector Dimension**: 1536 (for OpenAI `text-embedding-3-small` / standard embedding models) or 768 / 384 depending on model configuration.
- **Distance Metrics**: Cosine Distance (`<=>`), Inner Product (`<#>`), or Euclidean Distance (`<->`). For normalized embeddings, Cosine distance is used.
- **Indexing Options**:
  - `HNSW` (Hierarchical Navigable Small World): High recall, fast query speeds, slightly slower build time and higher RAM usage. Ideal for production code search.
  - `IVFFlat` (Inverted File Flat): Faster index build times, smaller memory footprint, but lower recall unless `probes` are tuned.

---

## 3. Interview Trade-Off Analysis

| Criteria | PostgreSQL + pgvector | Dedicated Vector Database (e.g., Pinecone/Qdrant) |
| :--- | :--- | :--- |
| **Data Integrity** | Full ACID transactions | Eventual consistency across multi-store architectures |
| **Join Efficiency** | Native relational joins (Chunks ⟷ Files ⟷ Repos) | High network latency via API stitching across services |
| **Scale Limit** | Scale to ~10M vectors comfortably per node | Scales horizontally to billions of vectors out-of-box |
| **Operational Overhead** | Low (Single standard DB container / RDS instance) | Medium-High (Managing separate cluster & sync pipelines) |

### Production Failure Modes & Mitigation Strategies
- **Problem**: As embeddings grow to millions of rows, sequential vector scans freeze query execution.
- **Mitigation**: Pre-create `HNSW` vector index (`CREATE INDEX ON code_chunks USING hnsw (embedding vector_cosine_ops)`), tune `m` (connections per node) and `ef_construction`, and enforce strict SQL timeouts.
