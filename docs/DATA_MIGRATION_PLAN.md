# Data Migration Plan

## Principles

Every persisted schema change requires a versioned migration with preconditions, postconditions, interruption behavior and compatibility notes.

### Backend

- Alembic is the migration boundary.
- No destructive auto-DDL.
- Prefer additive changes first.
- Preserve old columns during compatibility windows when needed.
- Backfills must be paginated, resumable, idempotent and rate-limited.

### Mobile

- Local schema version is stored separately from business cache content.
- Migration must not require uninstall/clear-data recovery.
- Authoritative appointment/provider/pharmacy state is cloud-owned.

## Migration evidence checklist

```text
pre-migration snapshot/evidence
migration execution evidence
post-migration validation
invariant validation
old-client compatibility
interrupted-migration recovery
rollback/recovery notes
```

The current portfolio environment has not executed a PostgreSQL migration or Android update preservation test.
