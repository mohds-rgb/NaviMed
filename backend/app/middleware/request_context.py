import time
import uuid

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-Id") or f"req_{uuid.uuid4().hex[:16]}"
        correlation_id = request.headers.get("X-Correlation-Id") or request_id
        request.state.request_id = request_id
        request.state.correlation_id = correlation_id
        started = time.perf_counter()
        response = await call_next(request)
        response.headers["X-Request-Id"] = request_id
        response.headers["X-Correlation-Id"] = correlation_id
        response.headers["X-Response-Time-Ms"] = str(round((time.perf_counter() - started) * 1000, 2))
        return response
