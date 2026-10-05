from app.core.errors import DomainError


ALLOWED_STATUSES = {
    "not_requested", "queued", "processing", "provider_accepted", "sent", "delivered", "read", "failed",
}


def validate_status_transition(current: str, target: str) -> None:
    if current == target:
        return
    allowed = {
        "queued": {"processing", "cancelled", "expired"},
        "processing": {"provider_accepted", "failed", "rateLimited", "providerUnavailable"},
        "provider_accepted": {"sent", "failed"},
        "sent": {"delivered", "failed"},
        "delivered": {"read"},
    }
    if target not in allowed.get(current, set()):
        raise DomainError("MESSAGE_STATE_CONFLICT", f"Illegal message transition: {current} -> {target}")
