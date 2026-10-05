# Security References Checked

Checked 2026-10-05 for version-sensitive architecture decisions.

- Supabase Auth overview: https://supabase.com/docs/guides/auth
- Supabase JWT guidance: https://supabase.com/docs/guides/auth/jwts
- Supabase JWT fields: https://supabase.com/docs/guides/auth/jwt-fields
- FastAPI security/JWT guidance: https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/
- PostgreSQL constraints: https://www.postgresql.org/docs/current/ddl-constraints.html
- PostgreSQL transaction processing: https://www.postgresql.org/docs/current/transactions.html
- AWS RDS regions: https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Concepts.RegionsAndAvailabilityZones.html

## Portfolio dependency snapshot

Flutter packages referenced in the mobile project were checked against pub.dev on 2026-10-05:

- `supabase_flutter` 2.18.0; min Dart SDK 3.9.
- `http` 1.6.0; min Dart SDK 3.4.
- `shared_preferences` 2.5.5; min Dart SDK 3.9 for the current stable release.
- `crypto` 3.0.7; min Dart SDK 3.4.

These versions are documented facts from the checked package pages, not a claim that this environment successfully resolved or built the mobile dependency graph.
