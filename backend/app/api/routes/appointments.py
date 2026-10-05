from fastapi import APIRouter, Depends, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, idempotency_header
from app.core.errors import ForbiddenError, NotFoundError
from app.db.models import Appointment, AppointmentSlot, Clinic, User
from app.db.enums import Capability
from app.db.session import get_db
from app.schemas.appointments import AppointmentCancel, AppointmentCreate, AppointmentOut, AppointmentReschedule, HoldCreate, HoldOut
from app.services.appointments import AppointmentService

router = APIRouter(prefix="/appointments", tags=["appointments"])


@router.post("/holds", response_model=HoldOut, status_code=201)
def create_hold(payload: HoldCreate, request: Request, idempotency_key: str = Depends(idempotency_header), db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    service = AppointmentService(db)
    try:
        item = service.hold_slot(slot_id=payload.slot_id, patient_user_id=user.id, idempotency_key=idempotency_key, request_id=request.state.request_id)
        db.commit()
        return item
    except Exception:
        db.rollback()
        raise


@router.post("", response_model=AppointmentOut, status_code=201)
def create_appointment(payload: AppointmentCreate, request: Request, idempotency_key: str = Depends(idempotency_header), db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    service = AppointmentService(db)
    try:
        item = service.create_appointment(hold_id=payload.hold_id, patient_user_id=user.id, idempotency_key=idempotency_key, request_id=request.state.request_id)
        db.commit()
        return item
    except Exception:
        db.rollback()
        raise


@router.get("", response_model=list[AppointmentOut])
def list_appointments(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.scalars(select(Appointment).where(Appointment.patient_user_id == user.id).order_by(Appointment.scheduled_start_at.desc())).all()


@router.get("/{appointment_id}", response_model=AppointmentOut)
def get_appointment(appointment_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    appointment = db.get(Appointment, appointment_id)
    if not appointment:
        raise NotFoundError("Appointment not found")
    if appointment.patient_user_id != user.id and user.platform_role not in {"owner", "platformAdmin", "supportAdmin"}:
        raise ForbiddenError("Appointment access denied")
    return appointment


def _staff_can_manage(db: Session, user: User, clinic_id: str, capability: str) -> bool:
    if user.platform_role in {"owner", "platformAdmin"}:
        return True
    from app.db.models import ClinicMembership
    memberships = db.scalars(select(ClinicMembership).where(ClinicMembership.user_id == user.id, ClinicMembership.clinic_id == clinic_id, ClinicMembership.active.is_(True))).all()
    return any(capability in (m.capabilities or []) for m in memberships)


def _effective_actor_role(db: Session, user: User, clinic_id: str) -> str:
    if user.platform_role:
        return user.platform_role
    from app.db.models import ClinicMembership
    membership = db.scalar(
        select(ClinicMembership)
        .where(
            ClinicMembership.user_id == user.id,
            ClinicMembership.clinic_id == clinic_id,
            ClinicMembership.active.is_(True),
        )
        .order_by(ClinicMembership.created_at.asc())
    )
    return membership.role if membership else "patient"


def _transition(appointment_id: str, target: str, request: Request, idempotency_key: str, db: Session, user: User, *, reason: str | None = None, required_capability: str | None = None):
    appointment = db.get(Appointment, appointment_id)
    if not appointment:
        raise NotFoundError("Appointment not found")
    is_owner = appointment.patient_user_id == user.id
    if target == "cancelledByPatient":
        if not is_owner and not _staff_can_manage(db, user, appointment.clinic_id, Capability.APPOINTMENT_CANCEL.value):
            raise ForbiddenError("Appointment access denied")
    else:
        capability = required_capability or Capability.APPOINTMENT_MANAGE.value
        if not _staff_can_manage(db, user, appointment.clinic_id, capability):
            raise ForbiddenError("Appointment management denied")
    service = AppointmentService(db)
    try:
        item = service.transition(appointment_id=appointment_id, target=target, actor_id=user.id, actor_role=_effective_actor_role(db, user, appointment.clinic_id), request_id=request.state.request_id, idempotency_key=idempotency_key, reason=reason)
        db.commit(); return item
    except Exception:
        db.rollback(); raise


@router.post("/{appointment_id}/confirm", response_model=AppointmentOut)
def confirm(appointment_id: str, request: Request, idempotency_key: str = Depends(idempotency_header), db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    appointment = db.get(Appointment, appointment_id)
    if not appointment or not _staff_can_manage(db, user, appointment.clinic_id, Capability.APPOINTMENT_CONFIRM.value):
        raise ForbiddenError("Appointment confirmation denied")
    return _transition(appointment_id, "confirmed", request, idempotency_key, db, user)


@router.post("/{appointment_id}/cancel", response_model=AppointmentOut)
def cancel(appointment_id: str, payload: AppointmentCancel, request: Request, idempotency_key: str = Depends(idempotency_header), db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    appointment = db.get(Appointment, appointment_id)
    if not appointment:
        raise NotFoundError("Appointment not found")
    target = "cancelledByPatient" if appointment.patient_user_id == user.id else "cancelledByProvider"
    return _transition(appointment_id, target, request, idempotency_key, db, user, reason=payload.reason)


@router.post("/{appointment_id}/reschedule", response_model=AppointmentOut)
def reschedule(appointment_id: str, payload: AppointmentReschedule, request: Request, idempotency_key: str = Depends(idempotency_header), db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    appointment = db.get(Appointment, appointment_id)
    if not appointment:
        raise NotFoundError("Appointment not found")
    if appointment.patient_user_id != user.id and not _staff_can_manage(db, user, appointment.clinic_id, Capability.APPOINTMENT_RESCHEDULE.value):
        raise ForbiddenError("Rescheduling denied")
    service = AppointmentService(db)
    try:
        item = service.reschedule(appointment_id=appointment_id, new_slot_id=payload.new_slot_id, actor_id=user.id, actor_role=_effective_actor_role(db, user, appointment.clinic_id), request_id=request.state.request_id, idempotency_key=idempotency_key)
        db.commit(); return item
    except Exception:
        db.rollback(); raise


@router.post("/{appointment_id}/check-in", response_model=AppointmentOut)
def check_in(appointment_id: str, request: Request, idempotency_key: str = Depends(idempotency_header), db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return _transition(appointment_id, "checkedIn", request, idempotency_key, db, user, required_capability=Capability.APPOINTMENT_CHECKIN.value)


@router.post("/{appointment_id}/start", response_model=AppointmentOut)
def start(appointment_id: str, request: Request, idempotency_key: str = Depends(idempotency_header), db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return _transition(appointment_id, "inProgress", request, idempotency_key, db, user, required_capability=Capability.APPOINTMENT_MANAGE.value)


@router.post("/{appointment_id}/complete", response_model=AppointmentOut)
def complete(appointment_id: str, request: Request, idempotency_key: str = Depends(idempotency_header), db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return _transition(appointment_id, "completed", request, idempotency_key, db, user, required_capability=Capability.APPOINTMENT_COMPLETE.value)


@router.post("/{appointment_id}/no-show", response_model=AppointmentOut)
def no_show(appointment_id: str, request: Request, idempotency_key: str = Depends(idempotency_header), db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return _transition(appointment_id, "noShow", request, idempotency_key, db, user, required_capability=Capability.APPOINTMENT_MANAGE.value)
