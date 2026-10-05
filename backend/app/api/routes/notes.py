from fastapi import APIRouter, Depends, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, idempotency_header
from app.core.errors import ForbiddenError, NotFoundError
from app.db.enums import Capability
from app.db.models import Appointment, AppointmentNote, ClinicMembership, User
from app.db.session import get_db
from app.schemas.notes import AppointmentNoteCreate, AppointmentNoteOut
from app.services.audit import record_audit
from app.services.idempotency import create_record, find_existing

router = APIRouter(prefix="/appointments", tags=["appointment-notes"])


def _staff_allowed(db: Session, user: User, clinic_id: str) -> bool:
    if user.platform_role in {"owner", "platformAdmin"}:
        return True
    memberships = db.scalars(select(ClinicMembership).where(
        ClinicMembership.user_id == user.id, ClinicMembership.clinic_id == clinic_id, ClinicMembership.active.is_(True)
    )).all()
    return any(Capability.PATIENT_READ.value in (m.capabilities or []) or Capability.APPOINTMENT_MANAGE.value in (m.capabilities or []) for m in memberships)


@router.get("/{appointment_id}/notes", response_model=list[AppointmentNoteOut])
def list_notes(appointment_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    appointment = db.get(Appointment, appointment_id)
    if not appointment:
        raise NotFoundError("Appointment not found")
    if appointment.patient_user_id != user.id and not _staff_allowed(db, user, appointment.clinic_id):
        raise ForbiddenError("Appointment notes access denied")
    # Notes are internal coordination data in MVP; patients receive only the appointment record.
    if appointment.patient_user_id == user.id:
        return []
    return db.scalars(select(AppointmentNote).where(AppointmentNote.appointment_id == appointment_id).order_by(AppointmentNote.created_at.asc())).all()


@router.post("/{appointment_id}/notes", response_model=AppointmentNoteOut, status_code=201)
def add_note(appointment_id: str, payload: AppointmentNoteCreate, request: Request, idempotency_key: str = Depends(idempotency_header), db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    appointment = db.get(Appointment, appointment_id)
    if not appointment:
        raise NotFoundError("Appointment not found")
    if not _staff_allowed(db, user, appointment.clinic_id):
        raise ForbiddenError("Appointment notes access denied")
    idem_payload = {"appointment_id": appointment_id, **payload.model_dump()}
    operation = "appointment_note_create"
    existing = find_existing(db, scope_key=user.id, operation=operation, key=idempotency_key, payload=idem_payload)
    if existing and existing.result_ref:
        return db.get(AppointmentNote, existing.result_ref)
    note = AppointmentNote(appointment_id=appointment.id, author_user_id=user.id, note_body=payload.note_body.strip(), visibility="internal")
    db.add(note); db.flush()
    record_audit(db, actor_id=user.id, actor_role="staff", action="appointment_note_created", target_type="AppointmentNote", target_id=note.id, request_id=request.state.request_id, correlation_id=request.state.correlation_id, organization_id=appointment.clinic_id, after={"appointmentId": appointment.id, "visibility": "internal"})
    create_record(db, scope_key=user.id, operation=operation, key=idempotency_key, payload=idem_payload, actor_id=user.id, organization_id=appointment.clinic_id, result_ref=note.id)
    db.commit(); db.refresh(note)
    return note
