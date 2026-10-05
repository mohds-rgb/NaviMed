import logging
import uuid

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import admin, appointments, auth, messaging, notes, notifications, pharmacy, providers, public
from app.core.config import get_settings
from app.core.errors import DomainError
from app.core.logging import configure_logging
from app.middleware.request_context import RequestContextMiddleware
from app.middleware.api_envelope import ApiEnvelopeMiddleware
from app.middleware.rate_limit import InMemoryRateLimitMiddleware

settings = get_settings()
configure_logging()
logger = logging.getLogger("navimed.api")

app = FastAPI(title="NaviMed API", version="0.1.0", docs_url="/docs", redoc_url="/redoc")
app.add_middleware(RequestContextMiddleware)
app.add_middleware(InMemoryRateLimitMiddleware, per_minute=settings.rate_limit_per_minute)
app.add_middleware(ApiEnvelopeMiddleware)
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origin_list or ["*"], allow_credentials=False, allow_methods=["GET","POST","PUT","PATCH","DELETE","OPTIONS"], allow_headers=["*"])


@app.exception_handler(DomainError)
async def domain_error_handler(request: Request, exc: DomainError):
    request_id = getattr(request.state, "request_id", f"req_{uuid.uuid4().hex[:12]}")
    return JSONResponse(status_code=exc.status_code, content={"ok":False,"error":{"code":exc.code,"message":exc.message,"retryable":exc.retryable,"details":exc.details},"requestId":request_id})


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    request_id = getattr(request.state, "request_id", f"req_{uuid.uuid4().hex[:12]}")
    return JSONResponse(status_code=400, content={"ok":False,"error":{"code":"INVALID_REQUEST","message":"Request validation failed","retryable":False},"requestId":request_id})


@app.exception_handler(Exception)
async def unhandled_error_handler(request: Request, exc: Exception):
    request_id = getattr(request.state, "request_id", f"req_{uuid.uuid4().hex[:12]}")
    logger.exception("unhandled_request_error", extra={"requestId":request_id, "operation":request.url.path, "result":"error"})
    return JSONResponse(status_code=500, content={"ok":False,"error":{"code":"SERVICE_UNAVAILABLE","message":"An internal error occurred.","retryable":True},"requestId":request_id})


@app.get("/health")
def health():
    return {"status":"ok","service":"navimed-api","environment":settings.environment}


app.include_router(auth.router, prefix=settings.api_prefix)
app.include_router(providers.router, prefix=settings.api_prefix)
app.include_router(appointments.router, prefix=settings.api_prefix)
app.include_router(public.router, prefix=settings.api_prefix)
app.include_router(pharmacy.router, prefix=settings.api_prefix)
app.include_router(messaging.router, prefix=settings.api_prefix)
app.include_router(admin.router, prefix=settings.api_prefix)
app.include_router(notes.router, prefix=settings.api_prefix)
app.include_router(notifications.router, prefix=settings.api_prefix)
