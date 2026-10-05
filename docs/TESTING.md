# Testing Strategy

## Layers

- Unit/domain: state machines and policy rules.
- Service: appointment holds, idempotency, pharmacy workflows.
- API: request/response and authorization matrices.
- Database: PostgreSQL constraints/rules.
- Concurrency: real PostgreSQL race tests before production.
- Messaging: adapter, retry, webhook, duplicate and consent behavior.
- Migration: backend and mobile interruption/recovery.
- UI/accessibility/localization: Flutter widget/integration/device tests.

## Evidence policy

A requirement cannot be `VERIFIED` without actual evidence.

### Executed in current environment

`python -m pytest` executed successfully: **16 passed**.

These tests use SQLite for portability in this environment and therefore do not constitute proof of PostgreSQL production concurrency behavior.

Additional executed checks:
- `python -m compileall` for backend source/tests.
- Python import sweep for all backend modules.
- FastAPI OpenAPI generation (45 total paths in the current assembly artifact).
- Alembic upgrade and downgrade against SQLite.

The repository does not claim a successful GitHub Actions run because CI was not executed from this environment.

### Not executed

- Flutter analyzer/tests
- Android build/APK
- real PostgreSQL server tests
- real Supabase Auth session flow
- staging concurrency
- real WhatsApp provider/webhook tests
- restore drill
- update installation test
- CI workflow


## Portfolio-hardening tests

Pharmacy duty correction and batch entry behavior are covered at the service layer. Mobile CI includes a widget smoke test for the branded Arabic-first application shell.
