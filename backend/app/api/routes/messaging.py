from fastapi import APIRouter, Depends, Header, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, idempotency_header
from app.core.errors import ForbiddenError, NotFoundError
from app.db.models import MessageDispatch, User
from app.db.session import get_db
from app.services.idempotency import create_record, find_existing

router = APIRouter(prefix="/messages", tags=["messaging"])


@router.get("")
def list_messages(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    rows = db.scalars(select(MessageDispatch).where(MessageDispatch.recipient_user_id == user.id).order_by(MessageDispatch.created_at.desc()).limit(100)).all()
    return rows


@router.get("/{message_id}")
def get_message(message_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    row = db.get(MessageDispatch, message_id)
    if not row:
        raise NotFoundError("Message not found")
    if row.recipient_user_id != user.id and user.platform_role not in {"owner", "platformAdmin", "supportAdmin"}:
        raise ForbiddenError("Message access denied")
    return row


@router.post("/{message_id}/retry")
def retry_message(message_id: str, request: Request, idempotency_key: str = Depends(idempotency_header), db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    row = db.get(MessageDispatch, message_id)
    if not row:
        raise NotFoundError("Message not found")
    if row.recipient_user_id != user.id and user.platform_role not in {"owner", "platformAdmin"}:
        raise ForbiddenError("Message retry denied")
    payload = {"message_id": message_id, "action": "retry"}
    operation = "message_retry"
    existing = find_existing(db, scope_key=user.id, operation=operation, key=idempotency_key, payload=payload)
    if existing and existing.result_ref:
        return db.get(MessageDispatch, existing.result_ref)
    if row.status not in {"failed", "providerUnavailable", "rateLimited"}:
        create_record(db, scope_key=user.id, operation=operation, key=idempotency_key, payload=payload, actor_id=user.id, result_ref=row.id)
        db.commit()
        return row
    row.status = "queued"
    row.attempt_count += 1
    row.last_error_code = None
    create_record(db, scope_key=user.id, operation=operation, key=idempotency_key, payload=payload, actor_id=user.id, organization_id=row.tenant_id, result_ref=row.id)
    db.commit(); db.refresh(row)
    return row


@router.post("/webhooks/provider")
async def provider_webhook(request: Request, x_provider_signature: str | None = Header(default=None), x_provider_event_id: str | None = Header(default=None)):
    # The real provider is intentionally not selected yet. Reject unverified callbacks rather than trusting them.
    return {"accepted": False, "code": "MESSAGE_PROVIDER_UNAVAILABLE", "eventId": x_provider_event_id, "signaturePresent": bool(x_provider_signature)}
