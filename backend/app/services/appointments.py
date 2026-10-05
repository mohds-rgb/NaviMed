from datetime import datetime, timedelta, timezone

from sqlalchemy import select

from app.core.config import get_settings
from sqlalchemy.orm import Session

from app.core.errors import ConflictError, DomainError, ForbiddenError, NotFoundError
from app.db.enums import AppointmentStatus, BookingPolicy
from app.db.models import Appointment, AppointmentEvent, AppointmentHold, AppointmentSlot, Clinic
from app.domain.appointments import assert_transition, can_cancel, can_reschedule, initial_status
from app.services.audit import record_audit
from app.services.idempotency import create_record, find_existing


class AppointmentService:
    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def _server_now() -> datetime:
        return datetime.now(timezone.utc)

    @staticmethod
    def _utc(value: datetime | None) -> datetime | None:
        if value is None:
            return None
        return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value

    def hold_slot(self, *, slot_id: str, patient_user_id: str, idempotency_key: str, request_id: str) -> AppointmentHold:
        payload = {"slot_id": slot_id}
        existing = find_existing(self.db, scope_key=patient_user_id, operation="hold_slot", key=idempotency_key, payload=payload)
        if existing and existing.result_ref:
            return self.db.get(AppointmentHold, existing.result_ref)

        slot = self.db.scalar(select(AppointmentSlot).where(AppointmentSlot.id == slot_id).with_for_update())
        if not slot:
            raise NotFoundError("Appointment slot not found")
        now = self._server_now()
        if slot.status == "reserved" and self._utc(slot.hold_expires_at) and self._utc(slot.hold_expires_at) > now:
            raise ConflictError("APPOINTMENT_SLOT_UNAVAILABLE", "The selected appointment slot is reserved")
        if slot.status == "booked" or self._utc(slot.start_at) <= now:
            raise ConflictError("APPOINTMENT_SLOT_UNAVAILABLE", "The selected appointment slot is no longer available")

        existing_hold = self.db.scalar(select(AppointmentHold).where(AppointmentHold.slot_id == slot_id, AppointmentHold.status == "active", AppointmentHold.expires_at > now).with_for_update())
        if existing_hold:
            raise ConflictError("APPOINTMENT_SLOT_UNAVAILABLE", "The selected appointment slot is reserved")

        hold = AppointmentHold(
            slot_id=slot.id, patient_user_id=patient_user_id, idempotency_key=idempotency_key,
            expires_at=now + timedelta(minutes=get_settings().default_hold_minutes), status="active",
        )
        self.db.add(hold)
        slot.status = "reserved"
        slot.hold_expires_at = hold.expires_at
        slot.version += 1
        self.db.flush()
        create_record(self.db, scope_key=patient_user_id, operation="hold_slot", key=idempotency_key, payload=payload, actor_id=patient_user_id, result_ref=hold.id)
        return hold

    def create_appointment(self, *, hold_id: str, patient_user_id: str, idempotency_key: str, request_id: str) -> Appointment:
        payload = {"hold_id": hold_id}
        existing = find_existing(self.db, scope_key=patient_user_id, operation="create_appointment", key=idempotency_key, payload=payload)
        if existing and existing.result_ref:
            return self.db.get(Appointment, existing.result_ref)

        hold = self.db.scalar(select(AppointmentHold).where(AppointmentHold.id == hold_id).with_for_update())
        if not hold or hold.patient_user_id != patient_user_id:
            raise NotFoundError("Appointment hold not found")
        slot = self.db.scalar(select(AppointmentSlot).where(AppointmentSlot.id == hold.slot_id).with_for_update())
        clinic = self.db.get(Clinic, slot.clinic_id) if slot else None
        if not slot or not clinic:
            raise NotFoundError("Appointment slot not found")

        now = self._server_now()
        if hold.status != "active" or self._utc(hold.expires_at) <= now:
            hold.status = "expired"
            if slot.status == "reserved":
                slot.status = "available"
                slot.hold_expires_at = None
            raise ConflictError("APPOINTMENT_SLOT_UNAVAILABLE", "The appointment hold has expired")
        if slot.status != "reserved" or self._utc(slot.hold_expires_at) is None or self._utc(slot.hold_expires_at) <= now:
            raise ConflictError("APPOINTMENT_SLOT_UNAVAILABLE", "The appointment slot is no longer reserved")
        if self._utc(slot.start_at) <= now:
            raise ConflictError("APPOINTMENT_SLOT_UNAVAILABLE", "The appointment slot is in the past")

        status = initial_status(clinic.booking_policy)
        appointment = Appointment(
            clinic_id=clinic.id, provider_id=slot.provider_id, patient_user_id=patient_user_id, slot_id=slot.id,
            status=status.value, request_status="accepted" if status == AppointmentStatus.CONFIRMED else "submitted",
            appointment_policy_version=clinic.policy_version, scheduled_start_at=slot.start_at, scheduled_end_at=slot.end_at,
        )
        self.db.add(appointment)
        hold.status = "converted"
        slot.status = "booked"
        slot.hold_expires_at = None
        slot.version += 1
        self.db.flush()

        self.db.add(AppointmentEvent(
            appointment_id=appointment.id, actor_id=patient_user_id, actor_role="patient", action="appointment_created",
            from_state=None, to_state=status.value, reason=None, event_metadata={}, created_at=now, correlation_id=request_id,
        ))
        record_audit(self.db, actor_id=patient_user_id, actor_role="patient", action="appointment_created", target_type="Appointment", target_id=appointment.id, request_id=request_id, correlation_id=request_id, organization_id=clinic.id, after={"status": status.value, "slot_id": slot.id})
        create_record(self.db, scope_key=patient_user_id, operation="create_appointment", key=idempotency_key, payload=payload, actor_id=patient_user_id, organization_id=clinic.id, result_ref=appointment.id)
        return appointment

    def transition(self, *, appointment_id: str, target: str, actor_id: str, actor_role: str, request_id: str, idempotency_key: str, reason: str | None = None) -> Appointment:
        payload = {"appointment_id": appointment_id, "target": target, "reason": reason}
        operation = f"appointment_transition:{target}"
        existing = find_existing(self.db, scope_key=actor_id, operation=operation, key=idempotency_key, payload=payload)
        if existing and existing.result_ref:
            return self.db.get(Appointment, existing.result_ref)
        appointment = self.db.scalar(select(Appointment).where(Appointment.id == appointment_id).with_for_update())
        if not appointment:
            raise NotFoundError("Appointment not found")

        if target in {AppointmentStatus.CANCELLED_BY_PATIENT.value, AppointmentStatus.CANCELLED_BY_PROVIDER.value} and not can_cancel(appointment.status):
            raise ConflictError("APPOINTMENT_STATE_CONFLICT", "Appointment cannot be cancelled in its current state")
        if target == AppointmentStatus.RESCHEDULED.value and not can_reschedule(appointment.status):
            raise ConflictError("APPOINTMENT_NOT_RESCHEDULABLE", "Appointment cannot be rescheduled in its current state")

        assert_transition(appointment.status, target)
        before = appointment.status
        appointment.status = target
        appointment.version += 1
        if target == AppointmentStatus.CONFIRMED.value:
            appointment.confirmed_at = self._server_now()
            appointment.request_status = "accepted"
        if target.startswith("cancelled"):
            appointment.cancelled_at = self._server_now()
            appointment.cancel_reason = reason
        if target == AppointmentStatus.COMPLETED.value:
            appointment.completed_at = self._server_now()

        self.db.add(AppointmentEvent(
            appointment_id=appointment.id, actor_id=actor_id, actor_role=actor_role, action=target,
            from_state=before, to_state=target, reason=reason, event_metadata={}, created_at=self._server_now(), correlation_id=request_id,
        ))
        record_audit(self.db, actor_id=actor_id, actor_role=actor_role, action=target, target_type="Appointment", target_id=appointment.id, request_id=request_id, correlation_id=request_id, organization_id=appointment.clinic_id, before={"status": before}, after={"status": target})
        create_record(self.db, scope_key=actor_id, operation=operation, key=idempotency_key, payload=payload, actor_id=actor_id, organization_id=appointment.clinic_id, result_ref=appointment.id)
        return appointment

    def reschedule(self, *, appointment_id: str, new_slot_id: str, actor_id: str, actor_role: str, request_id: str, idempotency_key: str) -> Appointment:
        payload = {"appointment_id": appointment_id, "new_slot_id": new_slot_id}
        operation = "appointment_reschedule"
        existing = find_existing(self.db, scope_key=actor_id, operation=operation, key=idempotency_key, payload=payload)
        if existing and existing.result_ref:
            return self.db.get(Appointment, existing.result_ref)

        appointment = self.db.scalar(select(Appointment).where(Appointment.id == appointment_id).with_for_update())
        if not appointment:
            raise NotFoundError("Appointment not found")
        if appointment.patient_user_id != actor_id and actor_role not in {"provider", "receptionist", "clinicManager", "providerAdmin", "owner", "platformAdmin"}:
            raise ForbiddenError("You are not allowed to reschedule this appointment")
        if not can_reschedule(appointment.status):
            raise ConflictError("APPOINTMENT_NOT_RESCHEDULABLE", "Appointment cannot be rescheduled in its current state")

        old_slot = self.db.scalar(select(AppointmentSlot).where(AppointmentSlot.id == appointment.slot_id).with_for_update())
        new_slot = self.db.scalar(select(AppointmentSlot).where(AppointmentSlot.id == new_slot_id).with_for_update())
        if not new_slot:
            raise NotFoundError("New appointment slot not found")
        if new_slot.provider_id != appointment.provider_id or new_slot.clinic_id != appointment.clinic_id:
            raise ConflictError("APPOINTMENT_SLOT_SCOPE_CONFLICT", "The new appointment slot belongs to a different provider or clinic")
        now = self._server_now()
        if new_slot.status == "reserved" and self._utc(new_slot.hold_expires_at) and self._utc(new_slot.hold_expires_at) > now:
            raise ConflictError("APPOINTMENT_SLOT_UNAVAILABLE", "The new appointment slot is unavailable")
        if new_slot.status == "booked" or self._utc(new_slot.start_at) <= now:
            raise ConflictError("APPOINTMENT_SLOT_UNAVAILABLE", "The new appointment slot is unavailable")

        assert_transition(appointment.status, AppointmentStatus.RESCHEDULED.value)
        old_status = appointment.status
        appointment.status = AppointmentStatus.RESCHEDULED.value
        appointment.version += 1
        if old_slot and old_slot.status == "booked":
            old_slot.status = "available"
            old_slot.version += 1
        new_appointment = Appointment(
            clinic_id=new_slot.clinic_id, provider_id=new_slot.provider_id, patient_user_id=appointment.patient_user_id, slot_id=new_slot.id,
            status=AppointmentStatus.CONFIRMED.value if old_status == AppointmentStatus.CONFIRMED.value else AppointmentStatus.PENDING_CONFIRMATION.value,
            request_status="accepted" if old_status == AppointmentStatus.CONFIRMED.value else "submitted",
            appointment_policy_version=appointment.appointment_policy_version, scheduled_start_at=new_slot.start_at, scheduled_end_at=new_slot.end_at,
            reschedule_of_appointment_id=appointment.id,
        )
        self.db.add(new_appointment)
        new_slot.status = "booked"
        new_slot.version += 1
        self.db.flush()
        self.db.add(AppointmentEvent(
            appointment_id=appointment.id, actor_id=actor_id, actor_role=actor_role, action="rescheduled",
            from_state=old_status, to_state=AppointmentStatus.RESCHEDULED.value, reason=None, event_metadata={"newAppointmentId": new_appointment.id},
            created_at=now, correlation_id=request_id,
        ))
        self.db.add(AppointmentEvent(
            appointment_id=new_appointment.id, actor_id=actor_id, actor_role=actor_role, action="appointment_created",
            from_state=None, to_state=new_appointment.status, reason="reschedule", event_metadata={"sourceAppointmentId": appointment.id},
            created_at=now, correlation_id=request_id,
        ))
        record_audit(self.db, actor_id=actor_id, actor_role=actor_role, action="appointment_rescheduled", target_type="Appointment", target_id=new_appointment.id, request_id=request_id, correlation_id=request_id, organization_id=new_appointment.clinic_id, metadata={"sourceAppointmentId": appointment.id})
        create_record(self.db, scope_key=actor_id, operation=operation, key=idempotency_key, payload=payload, actor_id=actor_id, organization_id=new_appointment.clinic_id, result_ref=new_appointment.id)
        return new_appointment
