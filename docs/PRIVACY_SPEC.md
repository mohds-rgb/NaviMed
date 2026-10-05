# Privacy Specification

NaviMed V1 follows data minimization. The current V1 domain does not introduce medical histories, diagnoses, radiographs, prescriptions or treatment records. Appointment coordination data may still be sensitive because it can reveal healthcare interactions.

## Rules

- Do not expose patient information in public pharmacy listings.
- Do not place sensitive health details in push previews, WhatsApp text, logs, analytics, URLs or QR payloads.
- Do not infer communication consent from a phone number.
- Record consent state, timestamp and source when the approved communication workflow requires it.
- Support controlled deletion/anonymization without breaking appointment/audit integrity.
- Support masked/time-limited support access in future admin tooling.

## Retention owner policy

The owner provided: five years for approved retained sensitive/clinical data; permanent basic records; booking records two years. This is treated as a product policy input, not as a legal conclusion. Exact legal mapping must be verified against authoritative Syrian requirements before production.

## Analytics

Allowed metrics are aggregate counts/rates. Patient names, phone numbers, message bodies and raw notes are excluded.


## Public repository boundary

The public Git repository contains architecture, source, tests, schemas and non-sensitive fixtures only. Real patient/provider/pharmacy operational datasets are provisioned outside Git. The mobile client obtains operational data from the configured backend rather than embedding named real-world records in source code.

## Appointment notes

MVP notes are limited internal coordination notes. They are not intended to serve as a complete medical record and are not included in public discovery responses.
