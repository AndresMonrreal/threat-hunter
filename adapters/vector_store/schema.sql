-- Esquema de la tabla que respalda VectorStorePort para pgvector.
-- Si mañana migras a OpenSearch, este archivo no aplica: cada
-- adaptador define su propio esquema/mapeo, no hay uno "universal".

CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS chunks (
    id          TEXT PRIMARY KEY,
    content     TEXT NOT NULL,
    metadata    JSONB NOT NULL DEFAULT '{}',
    embedding   VECTOR(768) NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_chunks_embedding
    ON chunks USING hnsw (embedding vector_cosine_ops);

CREATE INDEX IF NOT EXISTS idx_chunks_metadata
    ON chunks USING gin (metadata);
