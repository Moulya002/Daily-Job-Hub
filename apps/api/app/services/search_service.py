from psycopg import Connection

from app.repositories.jobs_repository import semantic_search_jobs as semantic_search_jobs_query
from app.schemas.jobs import SemanticSearchResult
from app.services.ai_service import get_embedding


def semantic_search_jobs(connection: Connection, query: str) -> list[SemanticSearchResult]:
    query_embedding = get_embedding(query, task_type="retrieval_query")
    return semantic_search_jobs_query(connection, query_embedding=query_embedding)
