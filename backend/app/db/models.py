from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, String, Text, UniqueConstraint, JSON, text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


def uid() -> str:
    return str(uuid.uuid4())


def now_utc() -> datetime:
    from datetime import timezone
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    auth_subject: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    email: Mapped[str | None] = mapped_column(String(320), nullable=True)
    display_name: Mapped[str | None] = mapped_column(String(160), nullable=True)
    phone_e164: Mapped[str | None] = mapped_column(String(32), nullable=True)
    preferred_language: Mapped[str] = mapped_column(String(8), default="ar")
    status: Mapped[str] = mapped_column(String(32), default="active")
    platform_role: Mapped[str | None] = mapped_column(String(40), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, onupdate=now_utc)


class Provider(Base):
    __tablename__ = "providers"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), unique=True, index=True)
    display_name: Mapped[str] = mapped_column(String(160))
    verification_status: Mapped[str] = mapped_column(String(32), default="pending")
    specialty: Mapped[str] = mapped_column(String(120), default="Dentistry")
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, onupdate=now_utc)


class Clinic(Base):
    __tablename__ = "clinics"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    provider_id: Mapped[str] = mapped_column(ForeignKey("providers.id"), index=True)
    name: Mapped[str] = mapped_column(String(180))
    city: Mapped[str] = mapped_column(String(120), index=True)
    area: Mapped[str | None] = mapped_column(String(120), nullable=True)
    address_summary: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone_public: Mapped[str | None] = mapped_column(String(32), nullable=True)
    booking_policy: Mapped[str] = mapped_column(String(32), default="provider_confirmation")
    policy_version: Mapped[int] = mapped_column(Integer, default=1)
    active: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, onupdate=now_utc)


class ClinicMembership(Base):
    __tablename__ = "clinic_memberships"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    clinic_id: Mapped[str] = mapped_column(ForeignKey("clinics.id"), index=True)
    role: Mapped[str] = mapped_column(String(40))
    capabilities: Mapped[list[str]] = mapped_column(JSON, default=list)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
    __table_args__ = (UniqueConstraint("user_id", "clinic_id", name="uq_membership_user_clinic"),)


class ProviderSchedule(Base):
    __tablename__ = "provider_schedules"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    clinic_id: Mapped[str] = mapped_column(ForeignKey("clinics.id"), index=True)
    provider_id: Mapped[str] = mapped_column(ForeignKey("providers.id"), index=True)
    weekday: Mapped[int] = mapped_column(Integer)
    start_minute: Mapped[int] = mapped_column(Integer)
    end_minute: Mapped[int] = mapped_column(Integer)
    appointment_duration_minutes: Mapped[int] = mapped_column(Integer, default=30)
    breaks: Mapped[list[dict[str, int]]] = mapped_column(JSON, default=list)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    __table_args__ = (Index("ix_schedule_provider_weekday", "provider_id", "weekday"),)


class ScheduleException(Base):
    __tablename__ = "schedule_exceptions"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    provider_id: Mapped[str] = mapped_column(ForeignKey("providers.id"), index=True)
    clinic_id: Mapped[str] = mapped_column(ForeignKey("clinics.id"), index=True)
    exception_date: Mapped[str] = mapped_column(String(10), index=True)
    reason: Mapped[str | None] = mapped_column(String(255), nullable=True)
    closed: Mapped[bool] = mapped_column(Boolean, default=True)


class AppointmentSlot(Base):
    __tablename__ = "appointment_slots"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    clinic_id: Mapped[str] = mapped_column(ForeignKey("clinics.id"), index=True)
    provider_id: Mapped[str] = mapped_column(ForeignKey("providers.id"), index=True)
    start_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    end_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(24), default="available")
    hold_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    version: Mapped[int] = mapped_column(Integer, default=1)
    __table_args__ = (UniqueConstraint("provider_id", "start_at", name="uq_slot_provider_start"),)


class AppointmentHold(Base):
    __tablename__ = "appointment_holds"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    slot_id: Mapped[str] = mapped_column(ForeignKey("appointment_slots.id"), index=True)
    patient_user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    status: Mapped[str] = mapped_column(String(24), default="active")
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    idempotency_key: Mapped[str] = mapped_column(String(160))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)


class Appointment(Base):
    __tablename__ = "appointments"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    clinic_id: Mapped[str] = mapped_column(ForeignKey("clinics.id"), index=True)
    provider_id: Mapped[str] = mapped_column(ForeignKey("providers.id"), index=True)
    patient_user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    slot_id: Mapped[str] = mapped_column(ForeignKey("appointment_slots.id"), index=True)
    status: Mapped[str] = mapped_column(String(40), index=True)
    request_status: Mapped[str] = mapped_column(String(24), default="submitted")
    appointment_policy_version: Mapped[int] = mapped_column(Integer, default=1)
    scheduled_start_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    scheduled_end_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
    confirmed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    cancel_reason: Mapped[str | None] = mapped_column(String(255), nullable=True)
    reschedule_of_appointment_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    version: Mapped[int] = mapped_column(Integer, default=1)
    __table_args__ = (
        Index(
            "uq_active_appointment_slot",
            "slot_id",
            unique=True,
            postgresql_where=text("status NOT IN ('cancelledByPatient','cancelledByProvider','rescheduled','noShow','expired')"),
            sqlite_where=text("status NOT IN ('cancelledByPatient','cancelledByProvider','rescheduled','noShow','expired')"),
        ),
    )


class AppointmentEvent(Base):
    __tablename__ = "appointment_events"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    appointment_id: Mapped[str] = mapped_column(ForeignKey("appointments.id"), index=True)
    actor_id: Mapped[str] = mapped_column(String(36), index=True)
    actor_role: Mapped[str] = mapped_column(String(40))
    action: Mapped[str] = mapped_column(String(64))
    from_state: Mapped[str | None] = mapped_column(String(40), nullable=True)
    to_state: Mapped[str | None] = mapped_column(String(40), nullable=True)
    reason: Mapped[str | None] = mapped_column(String(255), nullable=True)
    event_metadata: Mapped[dict[str, Any]] = mapped_column("metadata", JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
    correlation_id: Mapped[str] = mapped_column(String(80), index=True)


class IdempotencyRecord(Base):
    __tablename__ = "idempotency_records"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    scope_key: Mapped[str] = mapped_column(String(160))
    operation: Mapped[str] = mapped_column(String(80))
    idempotency_key: Mapped[str] = mapped_column(String(160))
    request_hash: Mapped[str] = mapped_column(String(128))
    actor_id: Mapped[str] = mapped_column(String(36))
    organization_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    result_ref: Mapped[str | None] = mapped_column(String(36), nullable=True)
    status: Mapped[str] = mapped_column(String(24), default="completed")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    __table_args__ = (UniqueConstraint("scope_key", "operation", "idempotency_key", name="uq_idem_scope_op_key"),)


class AppointmentNote(Base):
    __tablename__ = "appointment_notes"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    appointment_id: Mapped[str] = mapped_column(ForeignKey("appointments.id"), index=True)
    author_user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    note_body: Mapped[str] = mapped_column(Text)
    visibility: Mapped[str] = mapped_column(String(24), default="internal")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)


class MessageDispatch(Base):
    __tablename__ = "message_dispatches"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    tenant_id: Mapped[str | None] = mapped_column(String(36), nullable=True, index=True)
    appointment_id: Mapped[str | None] = mapped_column(String(36), nullable=True, index=True)
    recipient_user_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    template_key: Mapped[str] = mapped_column(String(120))
    status: Mapped[str] = mapped_column(String(32), default="queued")
    dispatch_key: Mapped[str] = mapped_column(String(180), unique=True)
    provider_message_id: Mapped[str | None] = mapped_column(String(180), nullable=True)
    last_error_code: Mapped[str | None] = mapped_column(String(120), nullable=True)
    attempt_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, onupdate=now_utc)


class MessageWebhookEvent(Base):
    __tablename__ = "message_webhook_events"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    provider_event_id: Mapped[str] = mapped_column(String(180), unique=True)
    dispatch_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
    valid_signature: Mapped[bool] = mapped_column(Boolean, default=False)
    status: Mapped[str] = mapped_column(String(32), default="received")


class Pharmacy(Base):
    __tablename__ = "pharmacies"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    display_name: Mapped[str] = mapped_column(String(180))
    city: Mapped[str] = mapped_column(String(120), index=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True)


class PharmacyBranch(Base):
    __tablename__ = "pharmacy_branches"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    pharmacy_id: Mapped[str] = mapped_column(ForeignKey("pharmacies.id"), index=True)
    display_name: Mapped[str] = mapped_column(String(180))
    address_summary: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone_public: Mapped[str | None] = mapped_column(String(32), nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True)


class PharmacyDutySchedule(Base):
    __tablename__ = "pharmacy_duty_schedules"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    pharmacy_id: Mapped[str] = mapped_column(ForeignKey("pharmacies.id"), index=True)
    branch_id: Mapped[str] = mapped_column(ForeignKey("pharmacy_branches.id"), index=True)
    city: Mapped[str] = mapped_column(String(120), index=True)
    duty_date: Mapped[str] = mapped_column(String(10), index=True)
    duty_start_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    duty_end_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    source: Mapped[str] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(24), default="draft")
    verification_status: Mapped[str] = mapped_column(String(24), default="unverified")
    verified_by: Mapped[str | None] = mapped_column(String(36), nullable=True)
    last_verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, onupdate=now_utc)
    __table_args__ = (Index("ix_duty_city_date_status", "city", "duty_date", "status"),)


class PublicPharmacyDutyListing(Base):
    __tablename__ = "public_pharmacy_duty_listings"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    city: Mapped[str] = mapped_column(String(120), index=True)
    pharmacy_id: Mapped[str] = mapped_column(String(36), index=True)
    pharmacy_display_name: Mapped[str] = mapped_column(String(180))
    branch_display_name: Mapped[str] = mapped_column(String(180))
    address_summary: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(32), nullable=True)
    duty_date: Mapped[str] = mapped_column(String(10), index=True)
    duty_start_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    duty_end_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(24), default="published")
    last_verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    source_schedule_id: Mapped[str] = mapped_column(String(36), unique=True)


class EmergencyContact(Base):
    __tablename__ = "emergency_contacts"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    label: Mapped[str] = mapped_column(String(180))
    phone: Mapped[str] = mapped_column(String(32))
    authority_source: Mapped[str] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(24), default="draft")
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    replaced_by_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)


class DeviceRegistration(Base):
    __tablename__ = "device_registrations"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    platform: Mapped[str] = mapped_column(String(24))
    push_token: Mapped[str] = mapped_column(String(512), unique=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
    last_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, onupdate=now_utc)


class Notification(Base):
    __tablename__ = "notifications"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    category: Mapped[str] = mapped_column(String(40))
    title_key: Mapped[str] = mapped_column(String(120))
    body_key: Mapped[str] = mapped_column(String(180))
    read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)


class AuditLog(Base):
    __tablename__ = "audit_logs"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    actor_id: Mapped[str] = mapped_column(String(36), index=True)
    actor_role: Mapped[str] = mapped_column(String(40))
    action: Mapped[str] = mapped_column(String(80), index=True)
    target_type: Mapped[str] = mapped_column(String(80))
    target_id: Mapped[str] = mapped_column(String(36))
    organization_id: Mapped[str | None] = mapped_column(String(36), nullable=True, index=True)
    before_snapshot: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    after_snapshot: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    audit_metadata: Mapped[dict[str, Any]] = mapped_column("metadata", JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
    correlation_id: Mapped[str] = mapped_column(String(80), index=True)
    request_id: Mapped[str] = mapped_column(String(80), index=True)


class FeatureFlag(Base):
    __tablename__ = "feature_flags"
    key: Mapped[str] = mapped_column(String(100), primary_key=True)
    state: Mapped[str] = mapped_column(String(24), default="disabled")
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, onupdate=now_utc)


class PlatformConfig(Base):
    __tablename__ = "platform_config"
    key: Mapped[str] = mapped_column(String(120), primary_key=True)
    value: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    sensitive: Mapped[bool] = mapped_column(Boolean, default=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, onupdate=now_utc)
