from datetime import datetime
from zoneinfo import ZoneInfo

from app.core.config import get_settings

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import EmergencyContact, PublicPharmacyDutyListing
from app.db.session import get_db
from app.schemas.pharmacy import PublicDutyOut

router = APIRouter(prefix="/public", tags=["public"] )


@router.get("/cities", response_model=list[str])
def cities(db: Session = Depends(get_db)):
    rows = db.scalars(select(PublicPharmacyDutyListing.city).distinct().order_by(PublicPharmacyDutyListing.city)).all()
    return list(rows)


@router.get("/pharmacies/on-duty", response_model=list[PublicDutyOut])
def on_duty(city: str = Query(..., min_length=1, max_length=120), date: str | None = Query(default=None, alias="date"), db: Session = Depends(get_db)):
    duty_date = date or datetime.now(ZoneInfo(get_settings().app_timezone)).date().isoformat()
    rows = db.scalars(select(PublicPharmacyDutyListing).where(PublicPharmacyDutyListing.city == city, PublicPharmacyDutyListing.duty_date == duty_date, PublicPharmacyDutyListing.status == "published")).all()
    return rows


@router.get("/pharmacies/{pharmacy_id}", response_model=list[PublicDutyOut])
def pharmacy_public(pharmacy_id: str, db: Session = Depends(get_db)):
    today = datetime.now(ZoneInfo(get_settings().app_timezone)).date().isoformat()
    return db.scalars(select(PublicPharmacyDutyListing).where(
        PublicPharmacyDutyListing.pharmacy_id == pharmacy_id,
        PublicPharmacyDutyListing.duty_date == today,
        PublicPharmacyDutyListing.status == "published",
    )).all()


@router.get("/emergency-contacts", response_model=list[dict])
def emergency_contacts(db: Session = Depends(get_db)):
    rows = db.scalars(select(EmergencyContact).where(EmergencyContact.status == "active")).all()
    return [{"id": x.id, "label": x.label, "phone": x.phone, "publishedAt": x.published_at} for x in rows]
