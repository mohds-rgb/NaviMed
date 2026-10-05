from dataclasses import dataclass
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import DeviceRegistration, Notification


@dataclass(frozen=True, slots=True)
class PushSendResult:
    accepted: bool
    provider_message_id: str | None = None
    error_code: str | None = None
    evidence: str = "none"


class PushProvider:
    def send(self, *, push_token: str, title_key: str, body_key: str) -> PushSendResult:
        raise NotImplementedError


class DisabledPushProvider(PushProvider):
    def send(self, *, push_token: str, title_key: str, body_key: str) -> PushSendResult:
        return PushSendResult(False, error_code="PUSH_PROVIDER_UNAVAILABLE", evidence="disabled")


class NotificationService:
    def __init__(self, db: Session, push_provider: PushProvider | None = None):
        self.db = db
        self.push_provider = push_provider or DisabledPushProvider()

    def create_in_app(self, *, user_id: str, category: str, title_key: str, body_key: str) -> Notification:
        item = Notification(user_id=user_id, category=category, title_key=title_key, body_key=body_key)
        self.db.add(item)
        return item

    def send_push_for_user(self, *, user_id: str, title_key: str, body_key: str) -> list[PushSendResult]:
        devices = self.db.scalars(select(DeviceRegistration).where(DeviceRegistration.user_id == user_id, DeviceRegistration.active.is_(True))).all()
        results: list[PushSendResult] = []
        for device in devices:
            result = self.push_provider.send(push_token=device.push_token, title_key=title_key, body_key=body_key)
            results.append(result)
            device.last_seen_at = datetime.now(timezone.utc)
        return results
