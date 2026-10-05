# ADR-0002: Supabase Auth only for identity

**Status:** Accepted

## Context

The product needs a mature identity/session provider while keeping application authorization under the backend.

## Decision

Use Supabase Auth for authentication and session lifecycle only. Do not use Supabase as the application database in MVP. FastAPI verifies Supabase JWTs and derives roles/capabilities from its own server-side records.

## Consequences

Identity operations are delegated to a dedicated provider, while healthcare coordination state remains inside PostgreSQL. A live Supabase project is required for end-to-end authentication validation.
