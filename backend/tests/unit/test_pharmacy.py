from datetime import datetime, timezone, timedelta

import pytest

from app.core.errors import ConflictError
from app.db.models import Pharmacy, PharmacyBranch
from app.services.pharmacy import PharmacyService


def test_invalid_duty_range_rejected(db):
    pharmacy = Pharmacy(display_name="Demo Pharmacy", city="دمشق")
    db.add(pharmacy); db.flush()
    branch = PharmacyBranch(pharmacy_id=pharmacy.id, display_name="Main")
    db.add(branch); db.commit()
    service = PharmacyService(db)
    with pytest.raises(Exception) as exc:
        service.create_duty_schedule(pharmacy_id=pharmacy.id, branch_id=branch.id, city="دمشق", duty_date="2099-01-01", start_at=datetime(2099,1,1,22,tzinfo=timezone.utc), end_at=datetime(2099,1,1,21,tzinfo=timezone.utc), source="Demo", actor_id="admin", request_id="req", idempotency_key="invalid-duty-1")
    assert getattr(exc.value, "code", None) == "DUTY_SCHEDULE_INVALID"



def test_duty_creation_is_idempotent(db):
    pharmacy = Pharmacy(display_name="Demo Pharmacy", city="دمشق")
    db.add(pharmacy); db.flush()
    branch = PharmacyBranch(pharmacy_id=pharmacy.id, display_name="Main")
    db.add(branch); db.commit()
    service = PharmacyService(db)
    kwargs = dict(
        pharmacy_id=pharmacy.id,
        branch_id=branch.id,
        city="دمشق",
        duty_date="2099-01-02",
        start_at=datetime(2099, 1, 2, 8, tzinfo=timezone.utc),
        end_at=datetime(2099, 1, 2, 20, tzinfo=timezone.utc),
        source="Demo",
        actor_id="admin",
        request_id="req",
        idempotency_key="duty-create-1",
    )
    first = service.create_duty_schedule(**kwargs)
    db.commit()
    second = service.create_duty_schedule(**kwargs)
    assert first.id == second.id



def test_public_visibility_requires_verified_current_publication():
    from app.domain.pharmacy import is_publicly_visible

    assert is_publicly_visible(status="published", verification_status="verified", duty_date="2026-10-05", current_date="2026-10-05")
    assert not is_publicly_visible(status="draft", verification_status="verified", duty_date="2026-10-05", current_date="2026-10-05")
    assert not is_publicly_visible(status="published", verification_status="unverified", duty_date="2026-10-05", current_date="2026-10-05")
    assert not is_publicly_visible(status="published", verification_status="verified", duty_date="2026-10-04", current_date="2026-10-05")


def test_duty_correction_withdraws_previous_public_listing(db):
    from app.db.models import PublicPharmacyDutyListing

    pharmacy = Pharmacy(display_name="Synthetic Pharmacy", city="دمشق")
    db.add(pharmacy); db.flush()
    branch = PharmacyBranch(pharmacy_id=pharmacy.id, display_name="Main")
    db.add(branch); db.commit()
    service = PharmacyService(db)
    schedule = service.create_duty_schedule(
        pharmacy_id=pharmacy.id,
        branch_id=branch.id,
        city="دمشق",
        duty_date="2099-02-01",
        start_at=datetime(2099, 2, 1, 8, tzinfo=timezone.utc),
        end_at=datetime(2099, 2, 1, 20, tzinfo=timezone.utc),
        source="synthetic",
        actor_id="admin",
        request_id="req-create",
        idempotency_key="duty-correction-create",
    )
    schedule.verification_status = "verified"
    schedule.status = "verified"
    schedule.last_verified_at = datetime.now(timezone.utc)
    db.commit()
    listing = service.publish(
        schedule_id=schedule.id,
        actor_id="admin",
        request_id="req-publish",
        idempotency_key="duty-correction-publish",
    )
    db.commit()

    updated = service.update_duty_schedule(
        pharmacy_id=pharmacy.id,
        schedule_id=schedule.id,
        branch_id=branch.id,
        city="دمشق",
        duty_date="2099-02-01",
        start_at=datetime(2099, 2, 1, 9, tzinfo=timezone.utc),
        end_at=datetime(2099, 2, 1, 21, tzinfo=timezone.utc),
        source="corrected",
        actor_id="admin",
        request_id="req-update",
        idempotency_key="duty-correction-update",
    )
    db.commit()
    db.refresh(listing)
    assert updated.status == "draft"
    assert updated.verification_status == "unverified"
    assert listing.status == "withdrawn"


def test_duty_batch_supports_multiple_dates(db):
    pharmacy = Pharmacy(display_name="Synthetic Pharmacy", city="حلب")
    db.add(pharmacy); db.flush()
    branch = PharmacyBranch(pharmacy_id=pharmacy.id, display_name="Main")
    db.add(branch); db.commit()
    service = PharmacyService(db)
    entries = []
    for index in range(3):
        duty_day = 10 + index
        entries.append({
            "branch_id": branch.id,
            "city": "حلب",
            "duty_date": f"2099-03-{duty_day:02d}",
            "start_at": datetime(2099, 3, duty_day, 8, tzinfo=timezone.utc),
            "end_at": datetime(2099, 3, duty_day, 20, tzinfo=timezone.utc),
            "source": "synthetic-batch",
        })
    created = service.create_batch(
        pharmacy_id=pharmacy.id,
        entries=entries,
        actor_id="admin",
        request_id="req-batch",
        idempotency_key="duty-batch-1",
    )
    db.commit()
    assert len(created) == 3
    assert {item.duty_date for item in created} == {"2099-03-10", "2099-03-11", "2099-03-12"}
