from dataclasses import dataclass
from functools import lru_cache

import jwt
from fastapi import HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import PyJWKClient

from app.core.config import get_settings


bearer = HTTPBearer(auto_error=False)


@dataclass(frozen=True, slots=True)
class Actor:
    auth_subject: str
    email: str | None
    role: str | None
    session_id: str | None


@lru_cache
def _jwks_client(url: str) -> PyJWKClient:
    return PyJWKClient(url, cache_jwk_set=True, lifespan=300, timeout=5)


def verify_supabase_token(token: str) -> Actor:
    settings = get_settings()
    issuer = settings.resolved_supabase_issuer
    jwks_url = settings.resolved_supabase_jwks_url
    if not issuer or not jwks_url:
        raise HTTPException(status_code=503, detail="Authentication provider is not configured")

    try:
        signing_key = _jwks_client(jwks_url).get_signing_key_from_jwt(token).key
        claims = jwt.decode(
            token,
            signing_key,
            algorithms=["RS256", "ES256", "ES384", "ES512"],
            audience=settings.supabase_jwt_audience,
            issuer=issuer,
            options={"require": ["exp", "sub", "iss", "aud"]},
        )
    except (jwt.PyJWTError, ValueError) as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication token") from exc

    subject = claims.get("sub")
    if not isinstance(subject, str) or not subject:
        raise HTTPException(status_code=401, detail="Invalid authentication subject")

    return Actor(
        auth_subject=subject,
        email=claims.get("email") if isinstance(claims.get("email"), str) else None,
        role=claims.get("role") if isinstance(claims.get("role"), str) else None,
        session_id=claims.get("session_id") if isinstance(claims.get("session_id"), str) else None,
    )


def require_actor(credentials: HTTPAuthorizationCredentials | None = Security(bearer)) -> Actor:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Authentication required")
    return verify_supabase_token(credentials.credentials)
