# Messaging Integration Boundary

## Current state

A real WhatsApp provider is intentionally not selected. The repository implements only the provider-neutral boundary and safe disabled/demo adapters.

## Interface

```text
MessagingProvider
├── sendTemplateMessage
├── queryDeliveryStatus
├── verifyWebhook
└── mapProviderError (conceptual mapping boundary)
```

## Required real-provider gate

```text
provider selection
official docs review
account ownership verification
server-side credential storage
webhook signature verification
template policy
consent policy
idempotency
retry limits
delivery state mapping
staging test
owner approval
production enablement
```

## Truth rule

API acceptance is not delivery. The demo adapter only returns `provider_accepted` and intentionally never claims `delivered` or `read`.

## Outage behavior

A messaging failure must not revert or corrupt an appointment. Appointment state remains authoritative.
