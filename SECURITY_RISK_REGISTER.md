# Security Risk Register

| Threat | Asset | Control | Test/Evidence | Residual risk |
|---|---|---|---|---|
| Account takeover | User session | Supabase Auth + server JWT verification | Token boundary unit test; real Auth not executed | Provider configuration dependent |
| Privilege escalation | Clinic/provider admin operations | Server-derived role/capability + object authorization | Authorization tests planned | Full endpoint matrix pending |
| Tenant breakout | Clinic/provider data | Membership + ownership + capability checks | Service/API tests pending | Medium until full matrix |
| Double booking | Appointment slot | Transactional lock + unique active-slot index + idempotency | Domain tests executed; real DB race not verified | Medium |
| Replay/duplicate commands | State-changing operations | Idempotency records + request hash | Idempotency tests executed | Medium until production DB verified |
| Public directory poisoning | Pharmacy listing | Admin verify/publish gate + projection | Source tests planned | Low/medium |
| Emergency contact tampering | Emergency contact | Admin-only publish + audit + replacement trail | Source review; full API test pending | Medium |
| Webhook spoofing | Messaging | Signature/event/state checks required by interface | Real provider unavailable | High until provider integrated |
| Secret leakage | Credentials/tokens | `.env.example`, server-side secrets only, no real values | Repository scan pending | Low |
| Sensitive logging | Patient/contact data | JSON logger redaction rules | Static review; runtime log audit pending | Medium |


| Public provider status leakage | Public discovery may expose internal verification state | Dedicated public DTO omits verification status; only approved providers are queryable | Source review | Low
| Push-token misuse | Device tokens are sensitive identifiers | Server-owned registration table; no token in public APIs | Source review; provider delivery not live | Medium
| Published duty correction race | Stale public pharmacy projection after an edit | Correction withdraws old listing and resets verification before republish | Unit test | Low
