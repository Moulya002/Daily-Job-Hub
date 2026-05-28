from psycopg import Connection

from app.repositories.recommendations_repository import recommendations_for_user
from app.schemas.jobs import JobOut


def get_recommendations_for_user(connection: Connection, user_id: str) -> list[JobOut]:
    return recommendations_for_user(connection, user_id=user_id)
