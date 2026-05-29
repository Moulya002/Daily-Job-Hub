"""PostgreSQL access via a managed connection pool.

A single pool is created at application startup (see app lifespan) and shared
across requests. Each request borrows a connection and returns it on completion.
Workers/scripts running outside the API can use ``open_db_connection`` for a
short-lived standalone connection.
"""

import logging
from collections.abc import Generator

from psycopg import Connection
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

from app.core.config import settings
from app.core.retry import with_retry

logger = logging.getLogger(__name__)

_pool: ConnectionPool | None = None


def init_pool() -> None:
    """Create and open the global connection pool. Idempotent."""
    global _pool
    if _pool is not None:
        return
    _pool = ConnectionPool(
        conninfo=settings.database_url,
        min_size=settings.db_pool_min_size,
        max_size=settings.db_pool_max_size,
        timeout=settings.db_pool_timeout,
        kwargs={"row_factory": dict_row},
        open=False,
        name="djh-pool",
    )
    _pool.open()
    logger.info(
        "DB pool opened (min=%s max=%s)",
        settings.db_pool_min_size,
        settings.db_pool_max_size,
    )


def close_pool() -> None:
    global _pool
    if _pool is not None:
        _pool.close()
        _pool = None
        logger.info("DB pool closed")


@with_retry(attempts=3, base_delay=0.5, exceptions=(Exception,))
def open_db_connection() -> Connection:
    """Open a standalone connection (for workers/scripts), with retry."""
    return Connection.connect(settings.database_url, row_factory=dict_row)


def get_db_connection() -> Generator[Connection, None, None]:
    """FastAPI dependency yielding a pooled connection (falls back to direct)."""
    if _pool is None:
        connection = open_db_connection()
        try:
            yield connection
        finally:
            connection.close()
        return

    with _pool.connection() as connection:
        yield connection


def check_db() -> bool:
    """Readiness probe: confirm the database answers a trivial query."""
    try:
        if _pool is not None:
            with _pool.connection() as connection, connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
        else:
            connection = open_db_connection()
            try:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    cursor.fetchone()
            finally:
                connection.close()
        return True
    except Exception as exc:  # noqa: BLE001 - readiness must never raise
        logger.warning("DB readiness check failed: %s", exc)
        return False
