from datetime import date, datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.config import get_settings
from app.core.errors import ConflictError, DomainError, ForbiddenError, NotFoundError
from app.db.enums import Capability
from app.db.models import Appointment, AppointmentSlot, Clinic, Provider, ProviderSchedule, ScheduleException, User
from app.schemas.providers import ClinicCreate, ClinicOut, ProviderOut, PublicProviderOut, SlotOut
from app.db.session import get_db

router = APIRouter(prefix="/providers", tags=["providers"])


def _can_manage_provider(user: User, provider: Provider) -> bool:
    return provider.user_id == user.id or user.platform_role in {"owner", "platformAdmin"}


@router.get("", response_model=list[PublicProviderOut])
def list_providers(city: str | None = Query(default=None, max_length=120), specialty: str | None = Query(default=None, max_length=120), db: Session = Depends(get_db)):
    q = select(Provider).join(Clinic, Clinic.provider_id == Provider.id).where(Provider.verification_status == "approved", Clinic.active.is_(True))
    if city:
        q = q.where(Clinic.city == city)
    if specialty:
        q = q.where(Provider.specialty == specialty)
    return db.scalars(q.distinct()).all()


@router.get("/{provider_id}", response_model=PublicProviderOut)
def get_provider(provider_id: str, db: Session = Depends(get_db)):
    provider = db.get(Provider, provider_id)
    if not provider or provider.verification_status != "approved":
        raise NotFoundError("Provider not found")
    return provider


@router.get("/{provider_id}/clinics", response_model=list[ClinicOut])
def get_provider_clinics(provider_id: str, db: Session = Depends(get_db)):
    provider = db.get(Provider, provider_id)
    if not provider or provider.verification_status != "approved":
        raise NotFoundError("Provider not found")
    return db.scalars(select(Clinic).where(Clinic.provider_id == provider_id, Clinic.active.is_(True))).all()


@router.post("/{provider_id}/clinics", response_model=ClinicOut, status_code=201)
def create_clinic(provider_id: str, payload: ClinicCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    provider = db.get(Provider, provider_id)
    if not provider:
        raise NotFoundError("Provider not found")
    if not _can_manage_provider(user, provider):
        raise ForbiddenError("Not allowed to manage this provider")
    clinic = Clinic(provider_id=provider.id, name=payload.name.strip(), city=payload.city.strip(), area=payload.area, address_summary=payload.address_summary, phone_public=payload.phone_public, booking_policy=payload.booking_policy, active=False)
    db.add(clinic)
    db.commit(); db.refresh(clinic)
    return clinic


@router.get("/{provider_id}/availability", response_model=list[SlotOut])
def availability(provider_id: str, from_at: str | None = Query(default=None), limit: int = Query(default=50, ge=1, le=100), db: Session = Depends(get_db)):
    provider = db.get(Provider, provider_id)
    if not provider or provider.verification_status != "approved":
        raise NotFoundError("Provider not found")
    query = (
        select(AppointmentSlot)
        .join(Clinic, Clinic.id == AppointmentSlot.clinic_id)
        .where(
            AppointmentSlot.provider_id == provider_id,
            AppointmentSlot.status == "available",
            Clinic.active.is_(True),
            AppointmentSlot.start_at > datetime.now(timezone.utc),
        )
        .order_by(AppointmentSlot.start_at)
        .limit(limit)
    )
    if from_at:
        try:
            parsed = datetime.fromisoformat(from_at.replace("Z", "+00:00"))
        except ValueError as exc:
            raise HTTPException(status_code=400, detail={"code":"INVALID_REQUEST","message":"Invalid from_at"}) from exc
        query = query.where(AppointmentSlot.start_at >= parsed)
    return db.scalars(query).all()


@router.post("/me/onboarding", response_model=ProviderOut, status_code=201)
def provider_onboarding(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    existing = db.scalar(select(Provider).where(Provider.user_id == user.id))
    if existing:
        return existing
    provider = Provider(user_id=user.id, display_name=user.display_name or "Pending Provider")
    db.add(provider)
    db.commit(); db.refresh(provider)
    return provider


@router.post("/{provider_id}/schedule", response_model=dict, status_code=201)
def add_schedule(provider_id: str, weekday: int, start_minute: int, end_minute: int, appointment_duration_minutes: int = 30, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    provider = db.get(Provider, provider_id)
    if not provider:
        raise NotFoundError("Provider not found")
    if not _can_manage_provider(user, provider):
        raise ForbiddenError("Not allowed to manage this provider schedule")
    clinic = db.scalar(select(Clinic).where(Clinic.provider_id == provider_id).limit(1))
    if not clinic:
        raise NotFoundError("Clinic not found")
    if not (0 <= weekday <= 6 and 0 <= start_minute < end_minute <= 1440 and 5 <= appointment_duration_minutes <= 240):
        raise DomainError("INVALID_REQUEST", "Invalid schedule range")
    item = ProviderSchedule(clinic_id=clinic.id, provider_id=provider_id, weekday=weekday, start_minute=start_minute, end_minute=end_minute, appointment_duration_minutes=appointment_duration_minutes)
    db.add(item); db.commit(); db.refresh(item)
    return {"id": item.id, "weekday": item.weekday, "startMinute": item.start_minute, "endMinute": item.end_minute, "durationMinutes": item.appointment_duration_minutes}


@router.post("/{provider_id}/schedule/generate-slots", response_model=dict)
def generate_slots(provider_id: str, target_date: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    provider = db.get(Provider, provider_id)
    if not provider:
        raise NotFoundError("Provider not found")
    if not _can_manage_provider(user, provider):
        raise ForbiddenError("Not allowed to generate provider slots")
    try:
        requested_date = date.fromisoformat(target_date)
    except ValueError as exc:
        raise DomainError("INVALID_REQUEST", "Invalid target_date") from exc
    weekday = requested_date.weekday()
    exception = db.scalar(select(ScheduleException).where(ScheduleException.provider_id == provider_id, ScheduleException.exception_date == requested_date.isoformat()))
    if exception and exception.closed:
        return {"created": 0, "reason": "schedule_exception_closed"}
    schedules = db.scalars(select(ProviderSchedule).where(ProviderSchedule.provider_id == provider_id, ProviderSchedule.weekday == weekday, ProviderSchedule.active.is_(True))).all()
    created = 0
    tz = ZoneInfo(get_settings().app_timezone)
    for schedule in schedules:
        clinic = db.get(Clinic, schedule.clinic_id)
        if not clinic:
            continue
        minute = schedule.start_minute
        while minute + schedule.appointment_duration_minutes <= schedule.end_minute:
            hour, mins = divmod(minute, 60)
            local_start = datetime.combine(requested_date, time(hour, mins), tzinfo=tz)
            local_end = local_start + timedelta(minutes=schedule.appointment_duration_minutes)
            overlaps_break = any(max(minute, b.get("start", -1)) < min(minute + schedule.appointment_duration_minutes, b.get("end", -1)) for b in (schedule.breaks or []))
            if overlaps_break:
                minute += schedule.appointment_duration_minutes
                continue
            existing = db.scalar(select(AppointmentSlot).where(AppointmentSlot.provider_id == provider_id, AppointmentSlot.start_at == local_start))
            if not existing:
                db.add(AppointmentSlot(clinic_id=clinic.id, provider_id=provider_id, start_at=local_start.astimezone(timezone.utc), end_at=local_end.astimezone(timezone.utc)))
                created += 1
            minute += schedule.appointment_duration_minutes
    db.commit()
    return {"created": created, "date": requested_date.isoformat(), "timezone": get_settings().app_timezone}


@router.get("/{provider_id}/appointments")
def provider_appointments(provider_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    from app.db.models import Appointment, ClinicMembership
    provider = db.get(Provider, provider_id)
    if not provider:
        raise NotFoundError("Provider not found")
    clinics = db.scalars(select(Clinic).where(Clinic.provider_id == provider_id)).all()
    allowed_clinics = {c.id for c in clinics if _can_manage_provider(user, provider) or any(
        Capability.APPOINTMENT_READ.value in (m.capabilities or [])
        for m in db.scalars(select(ClinicMembership).where(ClinicMembership.user_id == user.id, ClinicMembership.clinic_id == c.id, ClinicMembership.active.is_(True))).all()
    )}
    if not allowed_clinics:
        raise ForbiddenError("Appointment access denied")
    return db.scalars(select(Appointment).where(Appointment.clinic_id.in_(allowed_clinics)).order_by(Appointment.scheduled_start_at.desc()).limit(100)).all()
