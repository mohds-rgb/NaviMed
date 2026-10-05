from fastapi import APIRouter, Depends, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, idempotency_header
from app.core.errors import ConflictError, ForbiddenError, NotFoundError
from app.db.models import AuditLog, Clinic, EmergencyContact, PharmacyDutySchedule, Provider, User
from app.db.session import get_db
from app.schemas.admin import EmergencyContactCreate, ProviderApproval
from app.services.audit import record_audit
from app.services.pharmacy import PharmacyService
from app.services.idempotency import create_record, find_existing

router = APIRouter(prefix="/owner", tags=["owner"] )


def require_owner(user: User) -> None:
    if user.platform_role not in {"owner", "platformAdmin"}:
        raise ForbiddenError("Owner authorization required")


@router.get("/providers")
def providers(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    require_owner(user)
    return db.scalars(select(Provider).order_by(Provider.created_at.desc())).all()


@router.post("/providers/{provider_id}/approve")
def approve_provider(provider_id: str, payload: ProviderApproval, request: Request, idempotency_key: str = Depends(idempotency_header), db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    require_owner(user)
    idem_payload = {"provider_id": provider_id, "action": "approve", "reason": payload.reason}
    idem_operation = "provider_approval"
    existing = find_existing(db, scope_key=user.id, operation=idem_operation, key=idempotency_key, payload=idem_payload)
    if existing and existing.result_ref:
        provider = db.get(Provider, existing.result_ref)
        return {"id": provider.id, "status": provider.verification_status}
    provider = db.get(Provider, provider_id)
    if not provider:
        raise NotFoundError("Provider not found")
    before = {"verification_status": provider.verification_status}
    provider.verification_status = "approved"
    record_audit(db, actor_id=user.id, actor_role=user.platform_role or "platformAdmin", action="provider_approved", target_type="Provider", target_id=provider.id, request_id=request.state.request_id, correlation_id=request.state.correlation_id, after={"verification_status": provider.verification_status}, before=before, metadata={"reason":payload.reason} if payload.reason else {})
    create_record(db, scope_key=user.id, operation=idem_operation, key=idempotency_key, payload=idem_payload, actor_id=user.id, result_ref=provider.id)
    db.commit(); return {"id": provider.id, "status": provider.verification_status}


@router.post("/providers/{provider_id}/suspend")
def suspend_provider(provider_id: str, payload: ProviderApproval, request: Request, idempotency_key: str = Depends(idempotency_header), db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    require_owner(user)
    idem_payload = {"provider_id": provider_id, "action": "suspend", "reason": payload.reason}
    idem_operation = "provider_approval"
    existing = find_existing(db, scope_key=user.id, operation=idem_operation, key=idempotency_key, payload=idem_payload)
    if existing and existing.result_ref:
        provider = db.get(Provider, existing.result_ref)
        return {"id": provider.id, "status": provider.verification_status}
    provider = db.get(Provider, provider_id)
    if not provider:
        raise NotFoundError("Provider not found")
    before = {"verification_status": provider.verification_status}
    provider.verification_status = "suspended"
    record_audit(db, actor_id=user.id, actor_role=user.platform_role or "platformAdmin", action="provider_suspended", target_type="Provider", target_id=provider.id, request_id=request.state.request_id, correlation_id=request.state.correlation_id, before=before, after={"verification_status": provider.verification_status}, metadata={"reason":payload.reason} if payload.reason else {})
    create_record(db, scope_key=user.id, operation=idem_operation, key=idempotency_key, payload=idem_payload, actor_id=user.id, result_ref=provider.id)
    db.commit(); return {"id": provider.id, "status": provider.verification_status}


@router.post("/duty-schedules/{schedule_id}/verify")
def verify_duty(schedule_id: str, request: Request, idempotency_key: str = Depends(idempotency_header), db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    require_owner(user)
    idem_payload = {"schedule_id": schedule_id, "action": "verify"}
    idem_operation = "duty_schedule_verify"
    existing = find_existing(db, scope_key=user.id, operation=idem_operation, key=idempotency_key, payload=idem_payload)
    if existing and existing.result_ref:
        schedule = db.get(PharmacyDutySchedule, existing.result_ref)
        return {"id": schedule.id, "status": schedule.status, "verificationStatus": schedule.verification_status}
    schedule = db.get(PharmacyDutySchedule, schedule_id)
    if not schedule:
        raise NotFoundError("Duty schedule not found")
    schedule.verification_status = "verified"
    schedule.status = "verified"
    from datetime import datetime, timezone
    schedule.verified_by = user.id
    schedule.last_verified_at = datetime.now(timezone.utc)
    record_audit(db, actor_id=user.id, actor_role=user.platform_role or "platformAdmin", action="duty_schedule_verified", target_type="PharmacyDutySchedule", target_id=schedule.id, request_id=request.state.request_id, correlation_id=request.state.correlation_id, organization_id=schedule.pharmacy_id, after={"status":"verified"})
    create_record(db, scope_key=user.id, operation=idem_operation, key=idempotency_key, payload=idem_payload, actor_id=user.id, organization_id=schedule.pharmacy_id, result_ref=schedule.id)
    db.commit(); return {"id": schedule.id, "status": schedule.status, "verificationStatus": schedule.verification_status}


@router.post("/duty-schedules/{schedule_id}/publish")
def publish_duty(schedule_id: str, request: Request, idempotency_key: str = Depends(idempotency_header), db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    require_owner(user)
    service = PharmacyService(db)
    try:
        listing = service.publish(schedule_id=schedule_id, actor_id=user.id, request_id=request.state.request_id, idempotency_key=idempotency_key)
        db.commit(); return listing
    except Exception:
        db.rollback(); raise


@router.get("/audit")
def audit(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    require_owner(user)
    return db.scalars(select(AuditLog).order_by(AuditLog.created_at.desc()).limit(200)).all()


@router.post("/emergency-contacts")
def create_emergency(payload: EmergencyContactCreate, request: Request, idempotency_key: str = Depends(idempotency_header), db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    require_owner(user)
    idem_payload = {"label": payload.label, "phone": payload.phone, "authority_source": payload.authority_source}
    idem_operation = "emergency_contact_create"
    existing = find_existing(db, scope_key=user.id, operation=idem_operation, key=idempotency_key, payload=idem_payload)
    if existing and existing.result_ref:
        contact = db.get(EmergencyContact, existing.result_ref)
        return {"id": contact.id, "status": contact.status}
    contact = EmergencyContact(label=payload.label, phone=payload.phone, authority_source=payload.authority_source, status="draft")
    db.add(contact); db.flush()
    record_audit(db, actor_id=user.id, actor_role=user.platform_role or "platformAdmin", action="emergency_contact_changed", target_type="EmergencyContact", target_id=contact.id, request_id=request.state.request_id, correlation_id=request.state.correlation_id, after={"status":"draft","label":contact.label})
    create_record(db, scope_key=user.id, operation=idem_operation, key=idempotency_key, payload=idem_payload, actor_id=user.id, result_ref=contact.id)
    db.commit(); db.refresh(contact); return {"id":contact.id,"status":contact.status}


@router.post("/emergency-contacts/{contact_id}/publish")
def publish_emergency(contact_id: str, request: Request, idempotency_key: str = Depends(idempotency_header), db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    require_owner(user)
    idem_payload = {"contact_id": contact_id, "action": "publish"}
    idem_operation = "emergency_contact_publish"
    existing = find_existing(db, scope_key=user.id, operation=idem_operation, key=idempotency_key, payload=idem_payload)
    if existing and existing.result_ref:
        contact = db.get(EmergencyContact, existing.result_ref)
        return {"id": contact.id, "status": contact.status}
    contact = db.get(EmergencyContact, contact_id)
    if not contact:
        raise NotFoundError("Emergency contact not found")
    # Controlled replacement: a new published contact retires other active contacts only after audit.
    from datetime import datetime, timezone
    for current in db.scalars(select(EmergencyContact).where(EmergencyContact.status == "active")).all():
        current.status = "replaced"
        current.replaced_by_id = contact.id
        record_audit(db, actor_id=user.id, actor_role=user.platform_role or "platformAdmin", action="emergency_contact_changed", target_type="EmergencyContact", target_id=current.id, request_id=request.state.request_id, correlation_id=request.state.correlation_id, after={"status":"replaced","replacedById":contact.id})
    contact.status = "active"
    contact.published_at = datetime.now(timezone.utc)
    record_audit(db, actor_id=user.id, actor_role=user.platform_role or "platformAdmin", action="emergency_contact_changed", target_type="EmergencyContact", target_id=contact.id, request_id=request.state.request_id, correlation_id=request.state.correlation_id, after={"status":"active"})
    create_record(db, scope_key=user.id, operation=idem_operation, key=idempotency_key, payload=idem_payload, actor_id=user.id, result_ref=contact.id)
    db.commit()
    return {"id":contact.id,"status":contact.status}


@router.post("/clinics/{clinic_id}/activate")
def activate_clinic(clinic_id: str, request: Request, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    require_owner(user)
    clinic = db.get(Clinic, clinic_id)
    if not clinic:
        raise NotFoundError("Clinic not found")
    clinic.active = True
    record_audit(db, actor_id=user.id, actor_role=user.platform_role or "platformAdmin", action="clinic_activated", target_type="Clinic", target_id=clinic.id, request_id=request.state.request_id, correlation_id=request.state.correlation_id, organization_id=clinic.id, after={"active":True})
    db.commit()
    return {"id": clinic.id, "active": clinic.active}
