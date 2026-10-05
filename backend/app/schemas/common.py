from typing import Any
from pydantic import BaseModel, Field


class ErrorBody(BaseModel):
    code: str
    message: str
    retryable: bool = False
    details: dict[str, Any] | None = None


class ErrorEnvelope(BaseModel):
    ok: bool = False
    error: ErrorBody
    requestId: str


class SuccessEnvelope(BaseModel):
    ok: bool = True
    data: Any
    requestId: str


class PageParams(BaseModel):
    page: int = Field(default=1, ge=1)
    limit: int = Field(default=20, ge=1, le=100)
