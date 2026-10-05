# ADR-0004: Public pharmacy duty projection

**Status:** Accepted

## Context

Pharmacy administration records may contain operational and contact data that should not be exposed wholesale to anonymous users.

## Decision

Publish only a controlled read model (`public_pharmacy_duty_listings`) after administrator verification. The public model contains only fields approved for service discovery.

## Consequences

Public consumers do not require direct access to private administration tables. Corrections can withdraw an existing listing and force re-verification before republication.
