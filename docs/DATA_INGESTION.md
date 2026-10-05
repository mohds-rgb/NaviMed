# Real Data Ingestion and Provisioning

## Principle

NaviMed is designed to consume real operational data without committing that data to public Git history.

## Provider / clinic data

Provision provider and clinic records through the authenticated administrative workflow or a controlled import job. Records should be reviewed by the Super Admin before public discovery.

Required review points include identity verification status, clinic activation, public contact fields, booking policy and working schedule.

## Pharmacy data

Pharmacy accounts and branches are stored privately. Duty schedules can be entered as individual dates or as a weekly/monthly batch. A schedule is not public until it passes the verification/publication gate.

Published corrections withdraw the previous public projection and require re-verification before republication.

## Emergency contacts

Emergency contact records are owner/admin-controlled and require an authority source before publication. The public endpoint exposes only active published records.

## What must never be imported into Git

Patient records, medical notes, government/third-party private datasets, credentials, provider tokens, Supabase secrets, WhatsApp credentials, production exports and private phone lists.

## Recommended handoff format

For a future authorized dataset handoff, provide CSV or JSON outside Git with stable identifiers and the following logical groups:

```text
providers
clinics
clinic_memberships
pharmacies
pharmacy_branches
duty_schedules
emergency_contacts
```

The receiving environment should validate schema, required fields, duplicates, referential integrity and authorization status before activation.
