from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import select

from app.core.errors import ConflictError
from app.db.models import Appointment, AppointmentSlot, AppointmentEvent
from app.services.appointments import AppointmentService


def make_slot(db, clinic, provider):
    slot = AppointmentSlot(
        clinic_id=clinic.id,
        provider_id=provider.id,
        start_at=datetime.now(timezone.utc) + timedelta(days=1),
        end_at=datetime.now(timezone.utc) + timedelta(days=1, minutes=30),
    )
    db.add(slot)
    db.commit()
    db.refresh(slot)
    return slot


def test_hold_then_create_appointment(db, demo_records):
    patient, provider, clinic = demo_records
    slot = make_slot(db, clinic, provider)
    service = AppointmentService(db)

    hold = service.hold_slot(slot_id=slot.id, patient_user_id=patient.id, idempotency_key="hold-1", request_id="req-1")
    appointment = service.create_appointment(hold_id=hold.id, patient_user_id=patient.id, idempotency_key="appt-1", request_id="req-2")
    db.commit()

    assert appointment.status == "pendingConfirmation"
    assert db.scalar(select(AppointmentEvent).where(AppointmentEvent.appointment_id == appointment.id)) is not None


def test_double_hold_same_slot_conflicts(db, demo_records):
    patient, provider, clinic = demo_records
    another = __import__('app.db.models', fromlist=['User']).User(auth_subject='patient-2', email='p2@example.invalid', display_name='Second')
    db.add(another); db.commit()
    slot = make_slot(db, clinic, provider)
    service = AppointmentService(db)
    service.hold_slot(slot_id=slot.id, patient_user_id=patient.id, idempotency_key="hold-1", request_id="req-1")
    db.commit()

    with pytest.raises(ConflictError) as exc:
        service.hold_slot(slot_id=slot.id, patient_user_id=another.id, idempotency_key="hold-2", request_id="req-2")
    assert exc.value.code == "APPOINTMENT_SLOT_UNAVAILABLE"


def test_same_idempotency_key_returns_same_hold(db, demo_records):
    patient, provider, clinic = demo_records
    slot = make_slot(db, clinic, provider)
    service = AppointmentService(db)
    first = service.hold_slot(slot_id=slot.id, patient_user_id=patient.id, idempotency_key="same-key", request_id="req-1")
    db.commit()
    second = service.hold_slot(slot_id=slot.id, patient_user_id=patient.id, idempotency_key="same-key", request_id="req-2")
    assert first.id == second.id


def test_transition_is_idempotent(db, demo_records):
    patient, provider, clinic = demo_records
    slot = make_slot(db, clinic, provider)
    service = AppointmentService(db)
    hold = service.hold_slot(slot_id=slot.id, patient_user_id=patient.id, idempotency_key="hold-transition", request_id="req-1")
    appointment = service.create_appointment(hold_id=hold.id, patient_user_id=patient.id, idempotency_key="appt-transition", request_id="req-2")
    db.commit()

    first = service.transition(
        appointment_id=appointment.id,
        target="confirmed",
        actor_id=patient.id,
        actor_role="patient",
        request_id="req-3",
        idempotency_key="transition-confirm-1",
    )
    db.commit()
    second = service.transition(
        appointment_id=appointment.id,
        target="confirmed",
        actor_id=patient.id,
        actor_role="patient",
        request_id="req-4",
        idempotency_key="transition-confirm-1",
    )

    events = db.scalars(select(AppointmentEvent).where(AppointmentEvent.appointment_id == appointment.id)).all()
    assert first.id == second.id == appointment.id
    assert second.status == "confirmed"
    assert [event.action for event in events].count("confirmed") == 1


def test_reschedule_is_idempotent_and_preserves_history(db, demo_records):
    patient, provider, clinic = demo_records
    clinic.booking_policy = "instant"
    first_slot = make_slot(db, clinic, provider)
    second_slot = make_slot(db, clinic, provider)
    service = AppointmentService(db)
    hold = service.hold_slot(slot_id=first_slot.id, patient_user_id=patient.id, idempotency_key="hold-reschedule", request_id="req-5")
    appointment = service.create_appointment(hold_id=hold.id, patient_user_id=patient.id, idempotency_key="appt-reschedule", request_id="req-6")
    db.commit()

    first = service.reschedule(
        appointment_id=appointment.id,
        new_slot_id=second_slot.id,
        actor_id=patient.id,
        actor_role="patient",
        request_id="req-7",
        idempotency_key="reschedule-1",
    )
    db.commit()
    second = service.reschedule(
        appointment_id=appointment.id,
        new_slot_id=second_slot.id,
        actor_id=patient.id,
        actor_role="patient",
        request_id="req-8",
        idempotency_key="reschedule-1",
    )

    db.refresh(appointment)
    db.refresh(second_slot)
    assert first.id == second.id
    assert appointment.status == "rescheduled"
    assert second_slot.status == "booked"
    assert db.scalar(select(Appointment).where(Appointment.id == first.id)) is not None
    assert db.scalar(select(Appointment).where(Appointment.reschedule_of_appointment_id == appointment.id)) is not None


def test_reschedule_rejects_cross_clinic_slot(db, demo_records):
    patient, provider, clinic = demo_records
    first_slot = make_slot(db, clinic, provider)
    other_user = __import__('app.db.models', fromlist=['User']).User(auth_subject='other-provider-auth', email='other@example.invalid', display_name='Other Provider')
    db.add(other_user); db.flush()
    other_provider = __import__('app.db.models', fromlist=['Provider']).Provider(user_id=other_user.id, display_name='Other Provider', verification_status='approved')
    db.add(other_provider); db.flush()
    other_clinic = __import__('app.db.models', fromlist=['Clinic']).Clinic(provider_id=other_provider.id, name='Other Clinic', city='حلب', booking_policy='instant', active=True)
    db.add(other_clinic); db.flush()
    other_slot = __import__('app.db.models', fromlist=['AppointmentSlot']).AppointmentSlot(
        clinic_id=other_clinic.id,
        provider_id=other_provider.id,
        start_at=datetime.now(timezone.utc) + timedelta(days=2),
        end_at=datetime.now(timezone.utc) + timedelta(days=2, minutes=30),
    )
    db.add(other_slot); db.commit()

    service = AppointmentService(db)
    hold = service.hold_slot(slot_id=first_slot.id, patient_user_id=patient.id, idempotency_key='cross-clinic-hold', request_id='req-cross-1')
    appointment = service.create_appointment(hold_id=hold.id, patient_user_id=patient.id, idempotency_key='cross-clinic-appt', request_id='req-cross-2')
    db.commit()

    with pytest.raises(ConflictError) as exc:
        service.reschedule(
            appointment_id=appointment.id,
            new_slot_id=other_slot.id,
            actor_id=patient.id,
            actor_role='patient',
            request_id='req-cross-3',
            idempotency_key='cross-clinic-reschedule',
        )
    assert exc.value.code == 'APPOINTMENT_SLOT_SCOPE_CONFLICT'
