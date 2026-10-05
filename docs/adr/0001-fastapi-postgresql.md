# ADR-0001: FastAPI + PostgreSQL for the application boundary

**Status:** Accepted

## Context

NaviMed requires transactional scheduling, relational integrity, tenant-aware authorization and auditable mutation history.

## Decision

Use FastAPI as the trusted backend boundary and PostgreSQL as the primary relational datastore. SQLAlchemy and Alembic provide persistence/migration layers.

## Consequences

The design can use row locks, unique constraints and transactional writes for appointment integrity. The trade-off is that production PostgreSQL operations, backup/restore and concurrency behavior must still be verified in a real PostgreSQL environment before production.
