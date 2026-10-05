import pytest
from fastapi import HTTPException

from app.core.security import verify_supabase_token


def test_unconfigured_supabase_verification_fails_closed(monkeypatch):
    monkeypatch.delenv("NAVIMED_SUPABASE_URL", raising=False)
    monkeypatch.delenv("NAVIMED_SUPABASE_ISSUER", raising=False)
    monkeypatch.delenv("NAVIMED_SUPABASE_JWKS_URL", raising=False)
    with pytest.raises(HTTPException) as exc:
        verify_supabase_token("not-a-real-token")
    assert exc.value.status_code == 503
