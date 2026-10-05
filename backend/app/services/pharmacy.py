from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from app.core.config import get_settings

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import ConflictError, NotFoundError
from app.db.models import Pharmacy, PharmacyBranch, PharmacyDutySchedule, PublicPharmacyDutyListing
from app.domain.pharmacy import is_publicly_visible, validate_duty_range
from app.services.audit import record_audit
from app.services.idempotency import create_record, find_existing


class PharmacyService:
    def __init__(self, db: Session):
        self.db = db

    def create_duty_schedule(self, *, pharmacy_id: str, branch_id: str, city: str, duty_date: str, start_at, end_at, source: str, actor_id: str, request_id: str, idempotency_key: str) -> PharmacyDutySchedule:
        payload = {
            "pharmacy_id": pharmacy_id,
            "branch_id": branch_id,
            "city": city,
            "duty_date": duty_date,
            "start_at": start_at,
            "end_at": end_at,
            "source": source,
        }
        operation = "pharmacy_duty_create"
        existing = find_existing(self.db, scope_key=actor_id, operation=operation, key=idempotency_key, payload=payload)
        if existing and existing.result_ref:
            return self.db.get(PharmacyDutySchedule, existing.result_ref)

        pharmacy = self.db.get(Pharmacy, pharmacy_id)
        branch = self.db.get(PharmacyBranch, branch_id)
        if not pharmacy or not branch or branch.pharmacy_id != pharmacy_id:
            raise NotFoundError("Pharmacy branch not found")
        validate_duty_range(start_at, end_at)
        conflict = self.db.scalar(select(PharmacyDutySchedule).where(
            PharmacyDutySchedule.branch_id == branch_id,
            PharmacyDutySchedule.duty_date == duty_date,
            PharmacyDutySchedule.status.in_(["submitted", "verified", "published", "active"]),
        ))
        if conflict:
            raise ConflictError("DUTY_SCHEDULE_CONFLICT", "A duty schedule already exists for this branch/date")
        schedule = PharmacyDutySchedule(
            pharmacy_id=pharmacy_id, branch_id=branch_id, city=city, duty_date=duty_date,
            duty_start_at=start_at, duty_end_at=end_at, source=source, status="draft", verification_status="unverified",
        )
        self.db.add(schedule)
        self.db.flush()
        record_audit(self.db, actor_id=actor_id, actor_role="admin", action="duty_schedule_created", target_type="PharmacyDutySchedule", target_id=schedule.id, request_id=request_id, correlation_id=request_id, organization_id=pharmacy_id, after={"status":"draft"})
        create_record(self.db, scope_key=actor_id, operation=operation, key=idempotency_key, payload=payload, actor_id=actor_id, organization_id=pharmacy_id, result_ref=schedule.id)
        return schedule

    def update_duty_schedule(self, *, pharmacy_id: str, schedule_id: str, branch_id: str, city: str, duty_date: str, start_at, end_at, source: str, actor_id: str, request_id: str, idempotency_key: str) -> PharmacyDutySchedule:
        payload = {
            "pharmacy_id": pharmacy_id, "schedule_id": schedule_id, "branch_id": branch_id,
            "city": city, "duty_date": duty_date, "start_at": start_at, "end_at": end_at, "source": source,
        }
        operation = "pharmacy_duty_update"
        existing = find_existing(self.db, scope_key=actor_id, operation=operation, key=idempotency_key, payload=payload)
        if existing and existing.result_ref:
            return self.db.get(PharmacyDutySchedule, existing.result_ref)

        schedule = self.db.scalar(select(PharmacyDutySchedule).where(
            PharmacyDutySchedule.id == schedule_id, PharmacyDutySchedule.pharmacy_id == pharmacy_id
        ).with_for_update())
        if not schedule:
            raise NotFoundError("Duty schedule not found")
        pharmacy = self.db.get(Pharmacy, pharmacy_id)
        branch = self.db.get(PharmacyBranch, branch_id)
        if not pharmacy or not branch or branch.pharmacy_id != pharmacy_id:
            raise NotFoundError("Pharmacy branch not found")
        validate_duty_range(start_at, end_at)

        old_listing = self.db.scalar(select(PublicPharmacyDutyListing).where(
            PublicPharmacyDutyListing.source_schedule_id == schedule.id
        ))
        if old_listing:
            old_listing.status = "withdrawn"

        schedule.branch_id = branch_id
        schedule.city = city
        schedule.duty_date = duty_date
        schedule.duty_start_at = start_at
        schedule.duty_end_at = end_at
        schedule.source = source
        schedule.status = "draft"
        schedule.verification_status = "unverified"
        schedule.verified_by = None
        schedule.last_verified_at = None
        schedule.updated_at = datetime.now(timezone.utc)

        record_audit(self.db, actor_id=actor_id, actor_role="admin", action="duty_schedule_updated",
                     target_type="PharmacyDutySchedule", target_id=schedule.id, request_id=request_id,
                     correlation_id=request_id, organization_id=pharmacy_id,
                     after={"status": "draft", "dutyDate": duty_date})
        create_record(self.db, scope_key=actor_id, operation=operation, key=idempotency_key,
                      payload=payload, actor_id=actor_id, organization_id=pharmacy_id, result_ref=schedule.id)
        self.db.flush()
        return schedule

    def create_batch(self, *, pharmacy_id: str, entries: list[dict], actor_id: str, request_id: str, idempotency_key: str) -> list[PharmacyDutySchedule]:
        payload = {"pharmacy_id": pharmacy_id, "entries": entries}
        operation = "pharmacy_duty_batch_create"
        existing = find_existing(self.db, scope_key=actor_id, operation=operation, key=idempotency_key, payload=payload)
        if existing and existing.result_ref:
            ids = str(existing.result_ref).split(",")
            return [self.db.get(PharmacyDutySchedule, item) for item in ids if self.db.get(PharmacyDutySchedule, item)]

        created: list[PharmacyDutySchedule] = []
        for entry in entries:
            item = self.create_duty_schedule(
                pharmacy_id=pharmacy_id, actor_id=actor_id, request_id=request_id,
                idempotency_key=f"{idempotency_key}:{len(created)}", **entry
            )
            created.append(item)
        return created

    def publish(self, *, schedule_id: str, actor_id: str, request_id: str, idempotency_key: str) -> PublicPharmacyDutyListing:
        payload = {"schedule_id": schedule_id}
        operation = "pharmacy_duty_publish"
        existing = find_existing(self.db, scope_key=actor_id, operation=operation, key=idempotency_key, payload=payload)
        if existing and existing.result_ref:
            return self.db.get(PublicPharmacyDutyListing, existing.result_ref)

        schedule = self.db.scalar(select(PharmacyDutySchedule).where(PharmacyDutySchedule.id == schedule_id).with_for_update())
        if not schedule:
            raise NotFoundError("Duty schedule not found")
        if schedule.verification_status != "verified" or schedule.status not in {"verified", "published", "active"}:
            raise ConflictError("DUTY_SCHEDULE_NOT_VERIFIED", "Duty schedule must be verified before publication")
        pharmacy = self.db.get(Pharmacy, schedule.pharmacy_id)
        branch = self.db.get(PharmacyBranch, schedule.branch_id)
        if not pharmacy or not branch:
            raise NotFoundError("Pharmacy branch not found")
        existing_listing = self.db.scalar(select(PublicPharmacyDutyListing).where(PublicPharmacyDutyListing.source_schedule_id == schedule.id))
        if existing_listing:
            create_record(self.db, scope_key=actor_id, operation=operation, key=idempotency_key, payload=payload, actor_id=actor_id, organization_id=schedule.pharmacy_id, result_ref=existing_listing.id)
            return existing_listing
        schedule.status = "published"
        schedule.updated_at = datetime.now(timezone.utc)
        listing = PublicPharmacyDutyListing(
            city=schedule.city, pharmacy_id=pharmacy.id, pharmacy_display_name=pharmacy.display_name, branch_display_name=branch.display_name,
            address_summary=branch.address_summary, phone=branch.phone_public, duty_date=schedule.duty_date,
            duty_start_at=schedule.duty_start_at, duty_end_at=schedule.duty_end_at, status="published", last_verified_at=schedule.last_verified_at,
            source_schedule_id=schedule.id,
        )
        self.db.add(listing)
        self.db.flush()
        record_audit(self.db, actor_id=actor_id, actor_role="admin", action="duty_schedule_published", target_type="PharmacyDutySchedule", target_id=schedule.id, request_id=request_id, correlation_id=request_id, organization_id=schedule.pharmacy_id, after={"status":"published"})
        create_record(self.db, scope_key=actor_id, operation=operation, key=idempotency_key, payload=payload, actor_id=actor_id, organization_id=schedule.pharmacy_id, result_ref=listing.id)
        return listing

    def public_listings(self, *, city: str, duty_date: str) -> list[PublicPharmacyDutyListing]:
        rows = self.db.scalars(select(PublicPharmacyDutyListing).where(PublicPharmacyDutyListing.city == city, PublicPharmacyDutyListing.duty_date == duty_date, PublicPharmacyDutyListing.status == "published")).all()
        today = datetime.now(ZoneInfo(get_settings().app_timezone)).date().isoformat()
        return [r for r in rows if is_publicly_visible(status=r.status, verification_status="verified", duty_date=r.duty_date, current_date=today)]
