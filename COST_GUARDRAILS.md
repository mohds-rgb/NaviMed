# Cost Guardrails

## Portfolio objective

Development is emulator/local-first. This repository does not promise zero-cost production. Billing-sensitive infrastructure requires explicit owner approval.

## Current dependencies

- Local PostgreSQL via Docker Compose for development (Docker not available in the current verification environment).
- FastAPI application runtime.
- Supabase Auth as an external identity service.
- Optional future WhatsApp provider.
- Planned production host: AWS Frankfurt (`eu-central-1`), subject to production approval and current AWS pricing review.

## Cost controls implemented/designed

- bounded API page sizes (max 100);
- bounded appointment hold duration;
- explicit idempotency records;
- no unbounded background jobs;
- provider-neutral messaging boundary;
- public pharmacy projection;
- safe-read cache instead of authoritative client writes;
- no secrets in source.

## Not estimated yet

No real traffic profile or production cost forecast is claimed. Pricing-sensitive values will be refreshed from official provider sources before production planning.
