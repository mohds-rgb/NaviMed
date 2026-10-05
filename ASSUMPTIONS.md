# Engineering Assumptions

These are implementation assumptions, not personal or legal facts. They are visible so they can be challenged without silently becoming policy.

| ID | Assumption | Reason | Risk |
|---|---|---|---|
| A-01 | `Asia/Damascus` is the application default timezone. | One national launch market uses a single civil-time context. | Medium; verify operational timezone rules before production. |
| A-02 | Clinic booking policies are limited initially to instant confirmation and provider confirmation. | Matches the minimum appointment workflow and keeps the state machine explicit. | Low/medium; extend through ADR if more policies are approved. |
| A-03 | Appointment rescheduling creates a new authoritative appointment linked to the old record. | Preserves historical truth and avoids silent overwrites. | Low. |
| A-04 | Public pharmacy data is a dedicated read projection. | Prevents leakage from private administration records. | Low. |
| A-05 | Messaging is provider-neutral and disabled by default. | Real provider is intentionally not selected. | Low. |
| A-06 | SharedPreferences-like client storage contains only bounded safe-read/cache data and settings, never authoritative appointment state. | Matches the source specification's offline policy. | Low. |


## Portfolio data boundary

The public repository is intentionally data-minimal. Real provider, clinic, pharmacy and emergency-contact datasets are supplied through controlled non-repository workflows. This keeps the portfolio artifact reviewable without exposing third-party personal or operational data.

## Limited appointment notes

MVP notes are coordination notes attached to an appointment. They are not a replacement for an electronic medical-record system and are not exposed through public discovery endpoints.
