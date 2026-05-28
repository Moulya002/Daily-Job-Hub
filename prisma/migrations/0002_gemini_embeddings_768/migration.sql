-- Switch embeddings to Google Gemini text-embedding-004 (768 dimensions).
-- The Embedding table is recreated empty for new dimensions; any existing
-- vectors (incompatible 1536-dim) are cleared.

DROP INDEX IF EXISTS "Embedding_vector_ivfflat_idx";

DELETE FROM "Embedding";

ALTER TABLE "Embedding" ALTER COLUMN "vector" TYPE vector(768);
ALTER TABLE "Embedding" ALTER COLUMN "dimensions" SET DEFAULT 768;

CREATE INDEX "Embedding_vector_ivfflat_idx"
ON "Embedding" USING ivfflat ("vector" vector_cosine_ops) WITH (lists = 200);
