from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings

settings = get_settings()

try:
    if not settings.database_url:
        raise RuntimeError("NAVIMED_DATABASE_URL is not configured")
    engine = create_engine(settings.database_url, pool_pre_ping=True, future=True)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)
except ModuleNotFoundError as exc:
    if exc.name != "psycopg":
        raise
    # The repository can still be imported for domain/unit tests in environments
    # where the PostgreSQL driver is unavailable. Runtime DB access fails closed.
    engine = None
    SessionLocal = None
except RuntimeError as exc:
    if str(exc) != "NAVIMED_DATABASE_URL is not configured":
        raise
    engine = None
    SessionLocal = None


def get_db():
    if SessionLocal is None:
        raise RuntimeError("PostgreSQL driver is not installed; install project dependencies first")
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
