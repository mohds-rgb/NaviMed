# Requirements & Traceability

Status vocabulary follows the source specification: `DISCOVERED → SPECIFIED → DESIGNED → IMPLEMENTED → TESTED → VERIFIED → RELEASED → MONITORED`. `RELEASED` and `MONITORED` are not claimed for this portfolio baseline.

| ID | P | Requirement | Implementation | Tests | Evidence status |
|---|---|---|---|---|---|
| PROD-001 | P1 | Android-first healthcare coordination app | `mobile/` | Flutter execution unavailable | IMPLEMENTED / NOT VERIFIED |
| PROD-002 | P1 | Provider search and profiles | `backend/app/api/routes/providers.py`, mobile provider feature | Python tests + future API/UI tests | IMPLEMENTED / NOT VERIFIED |
| APT-001 | P0 | Server-authoritative appointment state | `domain/appointments.py`, appointment service | state tests | TESTED |
| APT-002 | P0 | Slot holds with expiry | `services/appointments.py` | hold tests | TESTED |
| APT-003 | P0 | Duplicate command protection | `services/idempotency.py` | idempotency test | TESTED |
| APT-004 | P0 | No active double booking | DB partial unique index + transaction path | sequential/domain coverage; real PG race pending | IMPLEMENTED / NOT VERIFIED |
| IAM-001 | P0 | Supabase JWT authentication boundary | `core/security.py` | fail-closed configuration test | IMPLEMENTED / PARTIAL TEST |
| IAM-002 | P0 | Server-side authorization | route capability/ownership checks | full matrix pending | IMPLEMENTED / NOT VERIFIED |
| PRIV-001 | P0 | Data minimization | models + privacy docs | static review | IMPLEMENTED |
| SAFE-001 | P0 | No diagnosis/prescription/emergency guarantee claims | UX + safety docs | static review | IMPLEMENTED |
| PHR-001 | P1 | Admin-controlled pharmacy duty input | `services/pharmacy.py`, admin routes | unit coverage partial | IMPLEMENTED / NOT VERIFIED |
| PHR-002 | P0 | Only verified/published schedules are public | public projection model + publication gate | service/domain tests; API matrix pending | IMPLEMENTED / NOT VERIFIED |
| EMG-001 | P0 | Emergency contact owner-controlled publication | admin route + audit | API tests pending | IMPLEMENTED / NOT VERIFIED |
| MSG-001 | P0 | Provider-neutral messaging boundary | `services/messaging.py` | demo/disabled tests | TESTED |
| MSG-002 | P0 | No false delivery state | demo adapter returns provider_accepted only | messaging test | TESTED |
| MIG-001 | P0 | Non-destructive client migration | `LocalCache` + migration docs | Flutter execution unavailable | DESIGNED / NOT VERIFIED |
| REL-001 | P0 | Update manifest integrity | `mobile/lib/core/config/update_manifest.dart` + release docs | Flutter execution unavailable | IMPLEMENTED / NOT VERIFIED |
| SEC-001 | P0 | Secrets excluded from source | `.gitignore`, `.env.example`, CI secret-scan workflow | static repository scan; Gitleaks CI not executed | IMPLEMENTED / NOT VERIFIED |
| OBS-001 | P2 | Structured redacted logs | `core/logging.py`, request middleware | static review only | IMPLEMENTED / NOT VERIFIED |
| UX-001 | P1 | Arabic/English + RTL/LTR | locale-aware app shell | Flutter execution unavailable | IMPLEMENTED / NOT VERIFIED |
