from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.errors import DomainError, NotFoundError
from app.db.models import DeviceRegistration, Notification, User
from app.db.session import get_db

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("")
def list_notifications(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.scalars(select(Notification).where(Notification.user_id == user.id).order_by(Notification.created_at.desc()).limit(100)).all()


@router.post("/device")
def register_device(body: dict, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    platform = body.get("platform")
    push_token = body.get("pushToken")
    if platform not in {"android", "ios", "web"} or not isinstance(push_token, str) or not 10 <= len(push_token) <= 512:
        raise DomainError("INVALID_REQUEST", "Invalid push registration")
    existing = db.scalar(select(DeviceRegistration).where(DeviceRegistration.push_token == push_token))
    if existing:
        existing.user_id = user.id
        existing.platform = platform
        existing.active = True
        existing.last_seen_at = datetime.now(timezone.utc)
    else:
        db.add(DeviceRegistration(user_id=user.id, platform=platform, push_token=push_token))
    db.commit()
    return {"registered": True}


@router.post("/{notification_id}/read")
def mark_read(notification_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    item = db.get(Notification, notification_id)
    if not item or item.user_id != user.id:
        raise NotFoundError("Notification not found")
    item.read_at = datetime.now(timezone.utc)
    db.commit()
    return {"id": item.id, "read": True}
