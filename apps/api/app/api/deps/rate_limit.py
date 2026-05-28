from collections import defaultdict
from time import time

from fastapi import HTTPException, Request, status

from app.core.config import settings

_rate_bucket: dict[str, list[float]] = defaultdict(list)


def check_rate_limit(request: Request) -> None:
    identifier = request.client.host if request.client else "anonymous"
    window_start = time() - 60
    recent = [ts for ts in _rate_bucket[identifier] if ts > window_start]
    if len(recent) >= settings.rate_limit_per_minute:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded.",
        )
    recent.append(time())
    _rate_bucket[identifier] = recent
