# UX Specification

## Mobile

Primary user modes:

1. Public/patient: discover provider → inspect availability → hold slot → request/book → view authoritative appointment state.
2. Provider/staff: manage clinic/schedule → review requests → confirm/reschedule/cancel → operate daily schedule.
3. Public pharmacy: choose city/date → view verified published duty records → view freshness → use phone action for published contact.
4. Platform admin: verify providers → verify/publish pharmacy duty schedules → manage emergency contacts → inspect audit.

## Language

Arabic and English are supported. Arabic uses RTL, English uses LTR. User-facing strings are centralized in the localization module rather than copied across widgets.

## Offline

Safe reads and settings may be cached. Mutations such as holds, booking, confirmation, rescheduling, cancellation, schedule changes and pharmacy publication require network authority. Cached data must show freshness where applicable.
