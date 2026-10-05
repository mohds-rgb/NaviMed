# Delivery Manifest

## Current portfolio artifact

- Project: NaviMed | نافيميد
- Release: 0.1.0
- Version code: 1
- Owner: Mohammed Yaman ALdous
- Professional title: Software Engineer | Full-Stack Developer
- GitHub: `mohds-rgb`
- Public contact: `moydous@gmail.com`
- Git commit: not created; the owner will create history from the owner's GitHub account.
- Build timestamp: repository assembly timestamp, not a release-build timestamp.
- Planned production hosting region: AWS Frankfurt (`eu-central-1`); no infrastructure provisioned by this artifact.
- Supabase: Auth only.
- Database: PostgreSQL.
- API: FastAPI `/v1`.
- Latest Alembic head: `6e2a44f12c7b`.
- Mobile branding: supplied NaviMed icon integrated into the mobile shell and Android launcher resources.
- Public real-world data: intentionally excluded; controlled provisioning is documented in `docs/DATA_INGESTION.md`.

## Verification evidence

- `python -m compileall backend/app backend/scripts backend/tests` — PASS.
- `python -m pytest backend/tests` — PASS (18 tests).
- Python backend import/OpenAPI generation — PASS (45 total OpenAPI paths (44 under `/v1` plus `/health`)).
- Alembic upgrade/downgrade on SQLite — PASS (portability smoke test through the latest migration head).
- Repository secret heuristic scan — PASS (no production credentials/signing keys found).
- Flutter analyzer/tests/build — NOT EXECUTED; Flutter SDK unavailable in this assembly environment.
- PostgreSQL migration/concurrency — NOT EXECUTED; PostgreSQL/Docker unavailable in this assembly environment.
- Supabase live Auth — NOT EXECUTED; no project credentials.
- WhatsApp delivery/webhooks — NOT EXECUTED; real provider not selected.
- Push delivery — NOT EXECUTED; provider remains a designed boundary.
- Real Android device smoke test — NOT EXECUTED; Android SDK/device unavailable.
- GitHub Actions — workflow files included; remote CI execution is not claimed here.
- Legal retention/deletion compliance — NOT VERIFIED; the project records an owner policy but does not present it as legal advice.

## Portfolio-hardening additions

- Owner/GitHub metadata and MIT copyright line.
- GitHub issue templates, PR template, CODEOWNERS and Dependabot.
- ADR set documenting backend/database, identity, hosting, public pharmacy projection and repository data minimization.
- Public OpenAPI JSON artifact under `docs/api/openapi.json`.
- Limited internal appointment coordination notes with strict scope.
- Device-registration and in-app notification boundaries for future push delivery.
- Weekly/monthly pharmacy duty batch creation and controlled post-publication correction workflow.
- Dedicated public provider response schema that omits internal verification state.
- Future-only appointment availability/hold checks and same-provider/same-clinic reschedule protection.

## Integrity

The final ZIP SHA-256 is supplied as a sidecar file next to the archive. The manifest itself does not embed the final archive hash because that would make the archive hash self-referential.
