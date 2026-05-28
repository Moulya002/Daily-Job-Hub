-- Run after Prisma migrations on PostgreSQL with pgvector enabled.
-- Tune ivfflat lists/probes according to dataset size and recall requirements.

CREATE INDEX IF NOT EXISTS idx_embedding_vector_ivfflat
ON "Embedding"
USING ivfflat ("vector" vector_cosine_ops)
WITH (lists = 200);

CREATE INDEX IF NOT EXISTS idx_job_search_tsv_gin
ON "Job"
USING GIN ("searchTsv");

CREATE INDEX IF NOT EXISTS idx_job_keywords_gin
ON "Job"
USING GIN ("keywords");

CREATE INDEX IF NOT EXISTS idx_job_techstack_gin
ON "Job"
USING GIN ("techStack");
