# Portfolio Engineering Review Guide

## Owner

**Mohammed Yaman ALdous** — Software Engineer | Full-Stack Developer  
GitHub: `@mohds-rgb`  
Email: `moydous@gmail.com`

The owner identity is repository metadata only and is intentionally absent from the mobile UI.

## What this repository demonstrates

NaviMed is deliberately structured to demonstrate engineering depth instead of product vanity metrics. A reviewer can inspect:

| Engineering area | Evidence |
|---|---|
| API architecture | `backend/app/api/routes/` + `docs/API_CONTRACT.md` |
| Domain modeling | `backend/app/domain/` |
| Scheduling integrity | `backend/app/services/appointments.py` |
| Transaction/idempotency design | `backend/app/services/idempotency.py` + appointment tests |
| Auth boundary | `backend/app/core/security.py` + `backend/app/api/deps.py` |
| Relational design | `backend/app/db/models.py` + Alembic migrations |
| Public/private data separation | pharmacy service + public routes |
| Mobile architecture | `mobile/lib/core/` + `mobile/lib/features/` |
| i18n / RTL | `mobile/lib/core/localization/` + app shell |
| Testing | `backend/tests/` + `mobile/test/` |
| Security governance | `SECURITY.md` + risk registers + GitHub templates |
| Architecture decisions | `docs/adr/` |
| Operations/readiness | `docs/OPERATIONS_RUNBOOK.md` + `docs/RELEASE_PLAN.md` |

## Data authenticity policy

This project intentionally does not use fabricated real-world provider, pharmacy, patient or emergency datasets to create the appearance of a live network. The schema, API contracts, imports and workflows are the evidence that the system is designed for real data.

## Evidence labels

- **VERIFIED:** executed in the documented assembly environment.
- **IMPLEMENTED:** source exists and is connected but may require an unavailable runtime/provider for execution.
- **DESIGNED:** architecture contract is present but not live-integrated.
- **PLANNED:** requires a future owner/provider/legal/hosting decision.

## Before public production claims

The remaining gates are real PostgreSQL deployment/concurrency verification, Supabase live Auth validation, real WhatsApp provider integration and webhook verification, push delivery, restore testing, signed APK/device smoke tests, legal retention validation, operational monitoring and production security review.
