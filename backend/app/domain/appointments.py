from app.core.errors import ConflictError, DomainError
from app.db.enums import AppointmentStatus, BookingPolicy


_ALLOWED: dict[AppointmentStatus, set[AppointmentStatus]] = {
    AppointmentStatus.REQUESTED: {AppointmentStatus.PENDING_CONFIRMATION, AppointmentStatus.CANCELLED_BY_PATIENT, AppointmentStatus.CANCELLED_BY_PROVIDER, AppointmentStatus.EXPIRED},
    AppointmentStatus.PENDING_CONFIRMATION: {AppointmentStatus.CONFIRMED, AppointmentStatus.CANCELLED_BY_PATIENT, AppointmentStatus.CANCELLED_BY_PROVIDER, AppointmentStatus.RESCHEDULED, AppointmentStatus.EXPIRED},
    AppointmentStatus.CONFIRMED: {AppointmentStatus.CHECKED_IN, AppointmentStatus.CANCELLED_BY_PATIENT, AppointmentStatus.CANCELLED_BY_PROVIDER, AppointmentStatus.RESCHEDULED, AppointmentStatus.NO_SHOW},
    AppointmentStatus.CHECKED_IN: {AppointmentStatus.IN_PROGRESS, AppointmentStatus.CANCELLED_BY_PROVIDER},
    AppointmentStatus.IN_PROGRESS: {AppointmentStatus.COMPLETED, AppointmentStatus.CANCELLED_BY_PROVIDER},
    AppointmentStatus.COMPLETED: set(),
    AppointmentStatus.CANCELLED_BY_PATIENT: set(),
    AppointmentStatus.CANCELLED_BY_PROVIDER: set(),
    AppointmentStatus.RESCHEDULED: set(),
    AppointmentStatus.NO_SHOW: set(),
    AppointmentStatus.EXPIRED: set(),
}


def assert_transition(current: str, target: str) -> None:
    try:
        current_state = AppointmentStatus(current)
        target_state = AppointmentStatus(target)
    except ValueError as exc:
        raise DomainError("APPOINTMENT_STATE_CONFLICT", "Unknown appointment state") from exc
    if target_state not in _ALLOWED[current_state]:
        raise ConflictError("APPOINTMENT_STATE_CONFLICT", f"Illegal appointment transition: {current} -> {target}")


def initial_status(policy: str) -> AppointmentStatus:
    if policy == BookingPolicy.INSTANT:
        return AppointmentStatus.CONFIRMED
    if policy == BookingPolicy.PROVIDER_CONFIRMATION:
        return AppointmentStatus.PENDING_CONFIRMATION
    raise DomainError("APPOINTMENT_POLICY_REJECTED", "Unsupported booking policy")


def can_cancel(status: str) -> bool:
    return status in {AppointmentStatus.REQUESTED.value, AppointmentStatus.PENDING_CONFIRMATION.value, AppointmentStatus.CONFIRMED.value}


def can_reschedule(status: str) -> bool:
    return status in {AppointmentStatus.REQUESTED.value, AppointmentStatus.PENDING_CONFIRMATION.value, AppointmentStatus.CONFIRMED.value}
