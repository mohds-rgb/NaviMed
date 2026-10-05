from fastapi import Depends, Header
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import Actor, require_actor
from app.db.models import ClinicMembership, User
from app.db.session import get_db


def get_current_user(actor: Actor = Depends(require_actor), db: Session = Depends(get_db)) -> User:
    user = db.scalar(select(User).where(User.auth_subject == actor.auth_subject))
    if user:
        return user
    user = User(auth_subject=actor.auth_subject, email=actor.email, display_name=actor.email)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def require_capability(capability: str):
    def dependency(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> User:
        memberships = db.scalars(select(ClinicMembership).where(ClinicMembership.user_id == user.id, ClinicMembership.active.is_(True))).all()
        if any(capability in (m.capabilities or []) for m in memberships):
            return user
        if user.platform_role in {"owner", "platformAdmin"}:
            return user
        from app.core.errors import ForbiddenError
        raise ForbiddenError(f"Missing capability: {capability}")
    return dependency


def idempotency_header(idempotency_key: str = Header(..., alias="Idempotency-Key")) -> str:
    return idempotency_key


def request_id_header(request_id: str = Header(default="", alias="X-Request-Id")) -> str:
    return request_id or "generated"
