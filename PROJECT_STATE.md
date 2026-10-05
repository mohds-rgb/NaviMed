# NaviMed Project State

**Mode:** MVP
**Product:** NaviMed | نافيميد — Dental & Health Network
**Portfolio status:** Active engineering implementation; not production deployed.

## Owner decisions

| ID | Decision | Status | Notes |
|---|---|---|---|
| OQ-01 | Launch cities | Decided | All cities in Syria; data model remains city-driven. |
| OQ-02 | Market | Decided | Syria. |
| OQ-03 | Execution mode | Decided | MVP. All P0 security/privacy/safety/migration invariants remain in scope. |
| OQ-04 | Identity | Decided | Supabase Auth. FastAPI verifies Supabase JWTs server-side. |
| OQ-05 | Backend/data | Decided | PostgreSQL + FastAPI. This is an owner decision overriding the Firestore-specific example in the source specification. |
| OQ-06 | WhatsApp provider | Open | Real integration later; provider not selected. |
| OQ-07 | Provider verification | Decided | Super Admin approval. |
| OQ-08 | Cancellation/reschedule | Decided | Free to cancel or modify, subject to lifecycle/state constraints. |
| OQ-09 | Booking policy | Decided | Each clinic selects its own booking policy in configuration. |
| OQ-10 | Pharmacy duty data authority | Decided | Manual admin entry. No public schedule becomes authoritative without admin verification/publication. |
| OQ-11 | Emergency contact ownership | Decided | App administration and recognized government authorities. Actual numbers remain owner-controlled data. |
| OQ-12 | Pharmacy freshness | Decided | Daily; freshness boundary is midnight in the configured Syria application timezone. |
| OQ-13 | Retention | Partially decided | 5 years for approved retained sensitive/clinical data; permanent basic records; booking records 2 years. Exact legal basis remains unverified and must not be presented as legal advice. |
| OQ-14 | Account deletion | Decided conceptually | Delete personal account data where allowed; de-identify/minimize retained records required for clinical/financial/audit integrity. Legal policy requires validation before production. |
| OQ-15 | Languages | Decided | Arabic + English, RTL/LTR. |
| OQ-16 | Update distribution | Decided | Internal direct APK links for clinics + GitHub Releases; update manifest/integrity verification designed for future distribution. |
| OQ-17 | Production hosting/region | Decided | AWS Frankfurt (`eu-central-1`) for the planned production deployment. No infrastructure is provisioned by this portfolio artifact. |
| OQ-18 | Billing limits | Open | No billing-enabled production resources should be created by this portfolio implementation; owner budget ceiling is not required for the portfolio artifact. |

## Owner product decisions added in this iteration

- Primary language: Arabic; English is supported.
- Currency context: SYP and USD; no online payment flow is included in MVP.
- Product UI theme: Modern Healthcare + Premium Medical, light mode only.
- Pharmacy is an independent account type. Clinic Staff is an independent account type.
- City Duty Coordinator is an approved operational role for future/admin workflows.
- Admin may enter pharmacy duty rosters weekly or monthly and may correct/replace published schedules through controlled re-verification.
- In-app + push + WhatsApp notification channels are part of the product boundary; actual push/WhatsApp providers remain gated integrations.
- Real provider/clinic/pharmacy data will be provisioned outside the public repository.
- Owner identity does not appear inside the mobile app.

## Current implementation status

- Backend domain and API foundation: IMPLEMENTED.
- PostgreSQL relational model: IMPLEMENTED/DESIGNED; production DB migration has not been run in this environment. Appointment notes and device registrations are included in the current schema migration.
- Supabase Auth verification boundary: IMPLEMENTED in source; real provider integration not executed here.
- Appointment hold/idempotency/state logic: IMPLEMENTED; verified by local unit tests using SQLite compatibility tests.
- Real PostgreSQL transaction/concurrency behavior: NOT VERIFIED in this environment.
- Pharmacy manual verification/public projection: IMPLEMENTED in source; not deployed.
- Messaging abstraction + disabled/demo adapters: IMPLEMENTED; no real WhatsApp provider.
- Flutter application source: IMPLEMENTED; branded icon assets and a widget smoke test are included. Flutter SDK is unavailable in this environment, so not locally executed.

## Environment evidence

Checked 2026-10-05 in the build environment:

- Python 3.13.5: available.
- Node.js 22.16.0: available.
- Git 2.47.3: available.
- FastAPI/SQLAlchemy/Pydantic/PyJWT/Pytest/Alembic: available.
- Flutter/Dart: not installed.
- Android SDK: not available.
- PostgreSQL CLI: not available.
- Docker: not available.
- Network package installation: unavailable from this environment.

## Truthfulness rule

No production deployment, real WhatsApp delivery, APK build, device smoke test, PostgreSQL migration execution, CI run, restore drill, or live metrics are claimed unless evidence is added here.
