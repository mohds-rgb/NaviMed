import hashlib
import json
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import ConflictError
from app.db.models import IdempotencyRecord


def request_hash(payload: dict) -> str:
    normalized = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode()
    return hashlib.sha256(normalized).hexdigest()


def _utc(value):
    return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value


def find_existing(db: Session, *, scope_key: str, operation: str, key: str, payload: dict) -> IdempotencyRecord | None:
    record = db.scalar(select(IdempotencyRecord).where(
        IdempotencyRecord.scope_key == scope_key,
        IdempotencyRecord.operation == operation,
        IdempotencyRecord.idempotency_key == key,
    ))
    if record and _utc(record.expires_at) <= datetime.now(timezone.utc):
        db.delete(record)
        db.flush()
        return None
    if record and record.request_hash != request_hash(payload):
        raise ConflictError("IDEMPOTENCY_KEY_REUSED_WITH_DIFFERENT_PAYLOAD", "Idempotency key was reused with a different payload")
    return record


def create_record(db: Session, *, scope_key: str, operation: str, key: str, payload: dict, actor_id: str, organization_id: str | None = None, result_ref: str | None = None, ttl_hours: int = 24) -> IdempotencyRecord:
    record = IdempotencyRecord(
        scope_key=scope_key, operation=operation, idempotency_key=key, request_hash=request_hash(payload),
        actor_id=actor_id, organization_id=organization_id, result_ref=result_ref,
        expires_at=datetime.now(timezone.utc) + timedelta(hours=ttl_hours),
    )
    db.add(record)
    db.flush()
    return record
