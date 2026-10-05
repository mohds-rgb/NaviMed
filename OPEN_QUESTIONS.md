# Open Questions & Gates

These items are intentionally not invented. They are blocking only for the corresponding production-sensitive phase.

| ID | Priority | Question | Current state | Blocking phase |
|---|---|---|---|---|
| OQ-06 | P1 | Which real WhatsApp provider/account/template policy will be used? | Not selected | Messaging integration / production enablement |
| OQ-13 | P0 | What exact Syrian legal/regulatory basis and retention schedule applies to each data class? | Owner policy provided, legal basis not verified | Production retention/deletion |
| OQ-17 | P1 | Final hosting platform: AWS Frankfurt or alternative? | AWS Frankfurt (`eu-central-1`) confirmed by owner | Production deployment |
| OQ-18 | P1 | What is the owner-approved production budget/billing ceiling? | Not specified | Billing/provisioning |
| OQ-19 | P1 | Final professional owner name and public links for repository metadata | Resolved: Mohammed Yaman ALdous / @mohds-rgb / moydous@gmail.com | Public README/license |
| OQ-20 | P1 | Exact provider booking-policy options and wording visible to clinics | Resolved for MVP: `instant` and `provider_confirmation` | Provider settings UX |

## Non-blocking portfolio assumptions

- Application timezone defaults to `Asia/Damascus`; it is configurable through backend configuration and must be validated against authoritative operational requirements before production.
- Rescheduling is modeled as a new appointment linked to the historical appointment; old history remains append-only.
- Public pharmacy listings are projections, not direct access to private administration records.
