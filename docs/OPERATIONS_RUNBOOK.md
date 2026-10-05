# Operations Runbook

## Development

Use local PostgreSQL and development-only Supabase resources. Never point development builds at production.

## Incident categories

- privacy breach
- credential compromise
- wrong pharmacy schedule
- emergency-contact error
- appointment double booking
- message-provider compromise/outage
- data corruption
- migration failure
- service outage

## First response

1. Preserve evidence.
2. Record request/correlation identifiers where available.
3. Contain the affected capability through authorization/feature flag controls if safe.
4. Avoid destructive cleanup.
5. Document owner approval for irreversible production action.

## Observability

Structured logs include request/correlation/operation/result/latency/error code fields and redact sensitive keys. Product health signals include appointment conflict rate, confirmation latency, message failures, pharmacy publication failures, authentication failures and cost anomalies.
