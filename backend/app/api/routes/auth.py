from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.errors import DomainError
from app.db.models import User
from app.db.session import get_db

router = APIRouter(tags=["identity"])


@router.get("/me")
def me(user: User = Depends(get_current_user)):
    return {
        "id": user.id,
        "email": user.email,
        "displayName": user.display_name,
        "phone": user.phone_e164,
        "preferredLanguage": user.preferred_language,
        "platformRole": user.platform_role,
    }


@router.put("/me")
def update_me(body: dict, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    allowed = {"displayName", "phone", "preferredLanguage"}
    if set(body) - allowed:
        raise DomainError("INVALID_REQUEST", "Unsupported profile fields")
    if "displayName" in body:
        value = body["displayName"]
        if not isinstance(value, str) or not 0 < len(value.strip()) <= 160:
            raise DomainError("INVALID_REQUEST", "Invalid display name")
        user.display_name = value.strip()
    if "phone" in body:
        value = body["phone"]
        if value is not None and (not isinstance(value, str) or len(value) > 32):
            raise DomainError("INVALID_REQUEST", "Invalid phone")
        user.phone_e164 = value
    if "preferredLanguage" in body:
        if body["preferredLanguage"] not in {"ar", "en"}:
            raise DomainError("INVALID_REQUEST", "Unsupported language")
        user.preferred_language = body["preferredLanguage"]
    db.commit(); db.refresh(user)
    return me(user)
