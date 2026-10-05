from datetime import datetime, timedelta, timezone

from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.db.models import Clinic, Pharmacy, PharmacyBranch, Provider, User


def seed() -> None:
    Base.metadata.create_all(engine)
    db = SessionLocal()
    try:
        owner = User(auth_subject="demo-owner-auth", email="owner@example.invalid", display_name="Demo Platform Owner", platform_role="owner")
        patient = User(auth_subject="demo-patient-auth", email="patient@example.invalid", display_name="Demo Patient", platform_role=None)
        provider_user = User(auth_subject="demo-provider-auth", email="provider@example.invalid", display_name="Dr. Demo Provider")
        db.add_all([owner, patient, provider_user]); db.flush()
        provider = Provider(user_id=provider_user.id, display_name="Demo Dental Provider", verification_status="approved", specialty="General Dentistry")
        db.add(provider); db.flush()
        clinic = Clinic(provider_id=provider.id, name="Demo Dental Clinic", city="دمشق", area="Demo Area", booking_policy="provider_confirmation", active=True)
        db.add(clinic)
        pharmacy = Pharmacy(display_name="Demo Pharmacy", city="دمشق")
        db.add(pharmacy); db.flush()
        branch = PharmacyBranch(pharmacy_id=pharmacy.id, display_name="Demo Branch", address_summary="Demo address", phone_public=None)
        db.add(branch)
        db.commit()
        print("Seeded demo records; all data is synthetic.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
