import json

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response


class ApiEnvelopeMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        if not request.url.path.startswith("/v1") or "application/json" not in response.headers.get("content-type", ""):
            return response

        body = b""
        async for chunk in response.body_iterator:
            body += chunk
        if not body:
            return response
        try:
            payload = json.loads(body)
        except json.JSONDecodeError:
            return Response(content=body, status_code=response.status_code, headers=dict(response.headers), media_type=response.media_type)
        if isinstance(payload, dict) and "ok" in payload:
            return Response(content=json.dumps(payload, ensure_ascii=False), status_code=response.status_code, headers={k:v for k,v in response.headers.items() if k.lower() != "content-length"}, media_type="application/json")

        request_id = getattr(request.state, "request_id", "req_unknown")
        wrapped = {"ok": response.status_code < 400, "data": payload if response.status_code < 400 else None, "requestId": request_id}
        return Response(content=json.dumps(wrapped, ensure_ascii=False), status_code=response.status_code, headers={k:v for k,v in response.headers.items() if k.lower() != "content-length"}, media_type="application/json")
