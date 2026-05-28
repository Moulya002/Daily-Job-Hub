from collections.abc import Generator

from psycopg import Connection
from psycopg.rows import dict_row

from app.core.config import settings


def open_db_connection() -> Connection:
    return Connection.connect(settings.database_url, row_factory=dict_row)


def get_db_connection() -> Generator[Connection, None, None]:
    connection = open_db_connection()
    try:
        yield connection
    finally:
        connection.close()
