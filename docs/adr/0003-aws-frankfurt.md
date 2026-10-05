# ADR-0003: Planned AWS Frankfurt hosting region

**Status:** Accepted for production planning; not deployed

## Context

The owner selected AWS Frankfurt as the target production region.

## Decision

Plan the production backend/data deployment for AWS Frankfurt (`eu-central-1`). No production resources or billing-enabled infrastructure are provisioned by this portfolio repository.

## Consequences

Infrastructure can later be designed with an explicit region boundary, data residency review, network controls, secrets management, backups and restore drills. Current status remains pre-deployment.
