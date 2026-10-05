# Product / Engineering Risk Register

| ID | Risk | Likelihood | Impact | Mitigation | Status |
|---|---|---:|---:|---|---|
| R-01 | Double booking under concurrent requests | Medium | Critical | Row locking + unique active-slot index + idempotency + concurrency tests planned | Open until PostgreSQL concurrency verification |
| R-02 | Wrong pharmacy duty information | Medium | High | Admin verification + publication gate + freshness boundary + audit | Implemented in source |
| R-03 | Messaging provider outage | High | Medium | Appointment state is independent of message dispatch; disabled/demo adapter | Implemented |
| R-04 | Unauthorized cross-clinic access | Medium | Critical | Server-side membership/capability/object checks | Implemented in API boundary; full matrix pending |
| R-05 | Retention policy conflicts with law | Medium | Critical | Do not claim legal compliance; legal basis remains open | Open |
| R-06 | Client cache presented as current | Medium | High | UI/API contract treats backend as authority; freshness indicators documented | Implemented by design |
| R-07 | Malicious APK/update | Low/Medium | Critical | Signed/update manifest boundary + SHA-256 verification design | Designed; release verification not executed |
| R-08 | Owner hosting/billing decision unresolved | Medium | High | Keep infrastructure templates local-first; no paid resource provisioning | Open |
