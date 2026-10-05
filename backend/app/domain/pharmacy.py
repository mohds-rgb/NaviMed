from datetime import datetime

from app.core.errors import DomainError


def validate_duty_range(start_at: datetime, end_at: datetime) -> None:
    if end_at <= start_at:
        raise DomainError("DUTY_SCHEDULE_INVALID", "Duty start must be earlier than duty end")


def is_publicly_visible(*, status: str, verification_status: str, duty_date: str, current_date: str) -> bool:
    return status in {"published", "active"} and verification_status == "verified" and duty_date == current_date
