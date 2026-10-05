# API Contract

Base path: `/v1`
Transport: HTTPS REST.

## Envelope

Success:

```json
{"ok":true,"data":{},"requestId":"req_..."}
```

Failure:

```json
{"ok":false,"error":{"code":"APPOINTMENT_SLOT_UNAVAILABLE","message":"The selected appointment slot is no longer available.","retryable":false},"requestId":"req_..."}
```

Stack traces, filesystem paths, database internals, credentials and sensitive patient fields are not exposed.

## Endpoint contract matrix

| Method | Path | Auth | Capability / rule | Idempotency | Purpose |
|---|---|---|---|---|---|
| GET | `/me` | required | own identity | no | Current profile |
| PUT | `/me` | required | own profile | no | Update allowed profile fields |
| GET | `/providers` | public | approved active providers only | no | Provider discovery |
| GET | `/providers/{id}` | public | approved provider only | no | Provider detail |
| GET | `/providers/{id}/clinics` | public | active clinics | no | Clinic list |
| GET | `/providers/{id}/availability` | public | published availability only | no | Slot discovery |
| POST | `/providers/me/onboarding` | required | creates pending provider profile | no | Provider onboarding request |
| POST | `/providers/{id}/clinics` | required | provider ownership or platform admin | no | Create clinic |
| POST | `/providers/{id}/schedule` | required | provider owner/admin | no | Create weekly schedule |
| POST | `/providers/{id}/schedule/generate-slots` | required | provider owner/admin | no | Materialize slots for a date |
| POST | `/appointments/holds` | required | authenticated patient | required | Hold a slot |
| POST | `/appointments` | required | authenticated patient | required | Convert hold to appointment |
| GET | `/appointments` | required | own appointments | no | Patient history |
| GET | `/appointments/{id}` | required | own appointment or authorized admin | no | Appointment detail |
| POST | `/appointments/{id}/confirm` | required | `appointment.confirm` | required | Provider confirmation |
| POST | `/appointments/{id}/cancel` | required | patient or authorized staff | required | Free cancellation |
| POST | `/appointments/{id}/reschedule` | required | patient or authorized staff | required | Reschedule |
| POST | `/appointments/{id}/check-in` | required | staff capability | required | Arrival transition |
| POST | `/appointments/{id}/start` | required | staff capability | required | Start visit |
| POST | `/appointments/{id}/complete` | required | staff capability | required | Complete visit |
| POST | `/appointments/{id}/no-show` | required | staff capability | required | Mark no-show |
| GET | `/public/cities` | public | public projection | no | Public city discovery |
| GET | `/public/pharmacies/on-duty` | public | published projection + date | no | On-duty pharmacy search |
| GET | `/public/pharmacies/{id}` | public | public projection | no | Public pharmacy view |
| GET | `/public/emergency-contacts` | public | active contacts only | no | Published emergency contacts |
| GET | `/pharmacies/{id}/duty-schedules` | admin | platform admin | no | List pharmacy duty records |
| POST | `/pharmacies/{id}/duty-schedules` | admin | platform admin | required | Manual duty input |
| POST | `/pharmacies/{id}/duty-schedules/batch` | admin | platform admin | required | Weekly/monthly duty entry (max 31 dates) |
| PUT | `/pharmacies/{id}/duty-schedules/{sid}` | admin | platform admin | required | Correct a duty schedule; previous public projection is withdrawn and must be re-verified |
| POST | `/pharmacies/{id}/duty-schedules/{sid}/submit` | admin | platform admin | required | Submit schedule |
| GET | `/messages` | required | message.read | no | Messaging status |
| POST | `/messages/webhooks/provider` | provider | verified webhook only | event id | Provider callback boundary |
| GET | `/owner/providers` | platform | owner/admin | no | Provider oversight |
| POST | `/owner/providers/{id}/approve` | platform | admin.manage | required | Approve provider |
| POST | `/owner/providers/{id}/suspend` | platform | admin.manage | required | Suspend provider |
| POST | `/owner/duty-schedules/{id}/verify` | platform | dutySchedule.publish | required | Verify duty schedule |
| POST | `/owner/duty-schedules/{id}/publish` | platform | dutySchedule.publish | required | Publish public schedule |
| GET | `/owner/audit` | platform | audit.read | no | Audit visibility |
| POST | `/owner/emergency-contacts` | platform | emergencyContact.manage | required | Create controlled contact |
| POST | `/owner/emergency-contacts/{id}/publish` | platform | emergencyContact.manage | required | Publish/revise contact |

## Stable error codes

See `backend` domain/API code for machine-readable values including `APPOINTMENT_SLOT_UNAVAILABLE`, `APPOINTMENT_STATE_CONFLICT`, `MESSAGE_PROVIDER_UNAVAILABLE`, `DUTY_SCHEDULE_NOT_VERIFIED`, `IDEMPOTENCY_KEY_REUSED_WITH_DIFFERENT_PAYLOAD`, and `SERVICE_UNAVAILABLE`.

## Idempotency

Sensitive and publication-affecting mutation endpoints require an `Idempotency-Key` header. The backend records a request hash and rejects reuse of the same key with a different payload.

## Pagination

List APIs use bounded `limit` semantics; maximum is 100. Public/search endpoints must remain bounded and may evolve to cursor pagination without changing the business authority model.

## Notifications

| POST | `/notifications/device` | required | registers a push-token boundary for the signed-in user | no | token stored server-side; real push provider remains gated |
| GET | `/notifications` | required | lists the signed-in user's in-app notifications | no | private to the user |
| POST | `/notifications/{notification_id}/read` | required | marks a notification read | yes | owner-only object check |

## Limited appointment coordination notes

| GET | `/appointments/{appointment_id}/notes` | required | lists internal coordination notes for staff/provider access | no | patients receive no note body in MVP |
| POST | `/appointments/{appointment_id}/notes` | required | creates a bounded internal coordination note | yes | 1000-character limit; not a medical-record system |
