from collections import defaultdict, deque
from time import monotonic

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse


class InMemoryRateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, per_minute: int = 60, protected_prefixes: tuple[str, ...] = ("/v1/public", "/v1/appointments", "/v1/messages")):
        super().__init__(app)
        self.per_minute = per_minute
        self.protected_prefixes = protected_prefixes
        self._events: dict[tuple[str, str], deque[float]] = defaultdict(deque)

    async def dispatch(self, request, call_next):
        path = request.url.path
        if not any(path.startswith(prefix) for prefix in self.protected_prefixes):
            return await call_next(request)

        client = request.client.host if request.client else "unknown"
        key = (client, path.split("/", 3)[2] if path.startswith("/v1/") else path)
        now = monotonic()
        bucket = self._events[key]
        while bucket and now - bucket[0] >= 60:
            bucket.popleft()
        if len(bucket) >= self.per_minute:
            return JSONResponse(status_code=429, content={"ok":False,"error":{"code":"RATE_LIMITED","message":"Too many requests.","retryable":True},"requestId":"rate_limited"})
        bucket.append(now)
        return await call_next(request)
