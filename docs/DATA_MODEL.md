# Relational Data Model

The owner-selected backend is PostgreSQL. The conceptual aggregates from the master specification are represented with relational tables rather than Firestore collections.

```text
users
providers
clinics
clinic_memberships
provider_schedules
schedule_exceptions
appointment_slots
appointment_holds
appointments
appointment_events
idempotency_records
message_dispatches
message_webhook_events
pharmacies
pharmacy_branches
pharmacy_duty_schedules
public_pharmacy_duty_listings
emergency_contacts
notifications
audit_logs
feature_flags
platform_config
```

## Appointment integrity

`appointment_slots` has a unique `(provider_id, start_at)` key. `appointments` has a partial unique index over `slot_id` for active states, providing a database-level invariant against multiple active appointments on a slot.

## Audit history

`appointment_events` is append-only by design. It records actor, role, action, previous state, target state, reason and correlation identifier.

## Public projection

`public_pharmacy_duty_listings` excludes operational verification notes, private account information, internal IDs not needed by the public interface and security metadata.

## Data classification

- PUBLIC: published pharmacy duty listings, public clinic profile, approved provider display name.
- INTERNAL: operational metrics/configuration.
- CONFIDENTIAL: staff data and appointment operational details.
- SENSITIVE: patient contact information, appointment history, messaging history, provider identity documents if ever collected.
- CRITICAL: secrets, credentials, cryptographic material, release-signing keys and provider tokens.


## Portfolio-hardening entities

- `appointment_notes`: bounded internal coordination notes attached to an appointment. The MVP deliberately does not model a full electronic medical record.
- `device_registrations`: active push-token registrations for future push delivery.
- `notifications`: in-app notification records owned by the target user.
- `public_pharmacy_duty_listings`: public projection that can be withdrawn and recreated after a schedule correction.
