# Demo Scenario

This document describes an optional local fixture scenario only; these records are synthetic and are never presented as production data.

## Patient
`Demo Patient` discovers an approved `Demo Dental Provider` and views published availability.

## Booking flow
1. Provider schedule is generated for a date.
2. Patient requests a short server-authoritative hold.
3. The hold is converted to an appointment using an idempotency key.
4. The clinic's configured booking policy decides whether the appointment is immediately confirmed or waits for provider confirmation.
5. The appointment can be cancelled/rescheduled without a fee in the current owner policy.

## Pharmacy flow
1. Admin enters a synthetic duty schedule.
2. Admin submits and verifies it.
3. Admin publishes it.
4. The public client queries the public projection for the selected city/date.

## Messaging flow
The demo adapter represents provider acceptance only. No WhatsApp delivery is claimed.
