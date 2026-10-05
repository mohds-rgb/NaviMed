# NaviMed Backend

FastAPI application implementing the trusted application boundary for NaviMed. See the root README and `docs/ARCHITECTURE.md`.

The database layer targets PostgreSQL. `NAVIMED_DATABASE_URL` is required at runtime; the repository does not embed a database password. The current environment could not install additional packages or start PostgreSQL, so database runtime access is intentionally not claimed here.


## Production boundary

Supabase Auth is the only Supabase service used by the application architecture. PostgreSQL is the application database and AWS Frankfurt (`eu-central-1`) is the planned production hosting target. No live infrastructure or production credentials are included in this repository.
