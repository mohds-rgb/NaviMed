from fastapi import APIRouter, Depends, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, idempotency_header
from app.core.errors import ForbiddenError, NotFoundError
from app.services.audit import record_audit
from app.services.idempotency import create_record, find_existing
from app.db.models import Pharmacy, PharmacyBranch, PharmacyDutySchedule, User
from app.db.session import get_db
from app.schemas.pharmacy import DutyBatchCreate, DutyCreate, DutyOut, DutyUpdate
from app.services.pharmacy import PharmacyService

router = APIRouter(prefix="/pharmacies", tags=["pharmacy"])


def _is_admin(user: User) -> bool:
    return user.platform_role in {"owner", "platformAdmin"}


@router.get("/{pharmacy_id}/duty-schedules", response_model=list[DutyOut])
def list_duty(pharmacy_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if not _is_admin(user):
        raise ForbiddenError("Pharmacy duty access denied")
    return db.scalars(select(PharmacyDutySchedule).where(PharmacyDutySchedule.pharmacy_id == pharmacy_id).order_by(PharmacyDutySchedule.duty_date.desc())).all()


@router.post("/{pharmacy_id}/duty-schedules", response_model=DutyOut, status_code=201)
def create_duty(pharmacy_id: str, payload: DutyCreate, request: Request, idempotency_key: str = Depends(idempotency_header), db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if not _is_admin(user):
        raise ForbiddenError("Only administrators may enter duty schedules")
    service = PharmacyService(db)
    try:
        item = service.create_duty_schedule(pharmacy_id=pharmacy_id, branch_id=payload.branch_id, city=payload.city, duty_date=payload.duty_date, start_at=payload.start_at, end_at=payload.end_at, source=payload.source, actor_id=user.id, request_id=request.state.request_id, idempotency_key=idempotency_key)
        db.commit(); return item
    except Exception:
        db.rollback(); raise


@router.post("/{pharmacy_id}/duty-schedules/batch", response_model=list[DutyOut], status_code=201)
def create_duty_batch(pharmacy_id: str, payload: DutyBatchCreate, request: Request, idempotency_key: str = Depends(idempotency_header), db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if not _is_admin(user):
        raise ForbiddenError("Only administrators may enter duty schedules")
    service = PharmacyService(db)
    try:
        entries = [item.model_dump() for item in payload.entries]
        created = service.create_batch(pharmacy_id=pharmacy_id, entries=entries, actor_id=user.id, request_id=request.state.request_id, idempotency_key=idempotency_key)
        db.commit()
        return created
    except Exception:
        db.rollback(); raise


@router.put("/{pharmacy_id}/duty-schedules/{schedule_id}", response_model=DutyOut)
def update_duty(pharmacy_id: str, schedule_id: str, payload: DutyUpdate, request: Request, idempotency_key: str = Depends(idempotency_header), db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if not _is_admin(user):
        raise ForbiddenError("Only administrators may update duty schedules")
    service = PharmacyService(db)
    try:
        item = service.update_duty_schedule(pharmacy_id=pharmacy_id, schedule_id=schedule_id, branch_id=payload.branch_id, city=payload.city, duty_date=payload.duty_date, start_at=payload.start_at, end_at=payload.end_at, source=payload.source, actor_id=user.id, request_id=request.state.request_id, idempotency_key=idempotency_key)
        db.commit(); return item
    except Exception:
        db.rollback(); raise


@router.post("/{pharmacy_id}/duty-schedules/{schedule_id}/submit", response_model=DutyOut)
def submit_duty(pharmacy_id: str, schedule_id: str, request: Request, db: Session = Depends(get_db), user: User = Depends(get_current_user), idempotency_key: str = Depends(idempotency_header)):
    if not _is_admin(user):
        raise ForbiddenError("Only administrators may submit schedules")
    payload = {"pharmacy_id": pharmacy_id, "schedule_id": schedule_id, "action": "submit"}
    operation = "pharmacy_duty_submit"
    existing = find_existing(db, scope_key=user.id, operation=operation, key=idempotency_key, payload=payload)
    if existing and existing.result_ref:
        return db.get(PharmacyDutySchedule, existing.result_ref)
    schedule = db.get(PharmacyDutySchedule, schedule_id)
    if not schedule or schedule.pharmacy_id != pharmacy_id:
        raise NotFoundError("Duty schedule not found")
    if schedule.status not in {"draft", "submitted"}:
        raise ForbiddenError("Only draft schedules may be submitted")
    schedule.status = "submitted"
    record_audit(db, actor_id=user.id, actor_role=user.platform_role or "platformAdmin", action="duty_schedule_submitted", target_type="PharmacyDutySchedule", target_id=schedule.id, request_id=request.state.request_id, correlation_id=request.state.correlation_id, organization_id=schedule.pharmacy_id, after={"status": "submitted"})
    create_record(db, scope_key=user.id, operation=operation, key=idempotency_key, payload=payload, actor_id=user.id, organization_id=schedule.pharmacy_id, result_ref=schedule.id)
    db.commit(); db.refresh(schedule); return schedule
