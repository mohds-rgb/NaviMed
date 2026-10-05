# Architecture & Product Decisions

## ADR-001 — Execution mode
**Status:** Accepted

MVP is the delivery mode. All P0 invariants remain in scope; P2/P3 work may be deferred with explicit tracking.

## ADR-002 — Identity provider
**Status:** Accepted

Use Supabase Auth for user identity/session lifecycle. FastAPI remains the trusted application backend and verifies Supabase JWTs server-side. Supabase Auth uses JWTs and exposes issuer/JWKS material suitable for server verification.

## ADR-003 — Backend and database
**Status:** Accepted by owner

Use FastAPI + PostgreSQL. The source specification includes a Firestore-specific data section conditional on a Firebase-based V1; this owner decision selects a relational implementation instead. Domain semantics, authorization boundaries, state machines and public/private data separation are preserved.

## ADR-004 — Appointment concurrency
**Status:** Accepted

Use PostgreSQL row-level transaction locking around slot mutation, idempotency records, server-authoritative time, and a unique partial index preventing more than one active appointment for the same slot. Real PostgreSQL race verification remains pending because PostgreSQL is unavailable in the current environment.

## ADR-005 — Booking policy
**Status:** Accepted by owner

Each clinic owns its booking policy. MVP models `instant` and `provider_confirmation`; new policy types require an ADR and state-machine review.

## ADR-006 — Rescheduling
**Status:** Accepted as portfolio design

A reschedule preserves the old appointment as historical truth and creates a new appointment linked by `reschedule_of_appointment_id`. This avoids destructive overwrites.

## ADR-007 — Pharmacy public projection
**Status:** Accepted

Public clients read a dedicated projection containing only approved public data. Private pharmacy administration records are never exposed directly.

## ADR-008 — Messaging provider abstraction
**Status:** Accepted

The appointment domain depends on a provider-neutral `MessagingProvider` boundary. The real provider is intentionally unselected; the repository includes disabled and demo-safe adapters only.

## ADR-009 — Update mechanism
**Status:** Designed

Use an owner-controlled update manifest containing application identity, version, minimum supported version, artifact URL, SHA-256, release notes, migration version and API compatibility. Installation must be delegated to Android's supported package installer after integrity checks.

## ADR-010 — Production hosting
**Status:** Open

AWS Frankfurt (`eu-central-1`) is the recommended production candidate because the chosen application backend is FastAPI + PostgreSQL. No production account, billing, or resource has been created by this repository.

## ADR-011 — Retention and deletion
**Status:** Partially accepted / legal validation required

Owner policy: five years for approved retained sensitive/clinical data, permanent basic records, two years for booking records. V1 does not introduce clinical notes as a new data collection domain. Exact legal basis and record-by-record retention mapping require authoritative legal validation before production.
