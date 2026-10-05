from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.db.base import Base
from app.db.models import Clinic, Provider, User


@pytest.fixture()
def db():
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(engine)


@pytest.fixture()
def demo_records(db: Session):
    patient = User(auth_subject="patient-auth", email="patient@example.invalid", display_name="Demo Patient")
    provider_user = User(auth_subject="provider-auth", email="provider@example.invalid", display_name="Demo Provider")
    db.add_all([patient, provider_user])
    db.flush()
    provider = Provider(user_id=provider_user.id, display_name="Demo Provider", verification_status="approved")
    db.add(provider)
    db.flush()
    clinic = Clinic(provider_id=provider.id, name="Demo Clinic", city="دمشق", booking_policy="provider_confirmation", policy_version=3, active=True)
    db.add(clinic)
    db.commit()
    return patient, provider, clinic
