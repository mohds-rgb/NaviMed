from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "NaviMed API"
    environment: str = "development"
    api_prefix: str = "/v1"
    app_timezone: str = "Asia/Damascus"
    database_url: str = ""

    supabase_url: str = ""
    supabase_issuer: str = ""
    supabase_jwt_audience: str = "authenticated"
    supabase_jwks_url: str = ""

    messaging_enabled: bool = False
    default_hold_minutes: int = Field(default=5, ge=1, le=30)
    default_page_size: int = Field(default=20, ge=1, le=100)
    max_page_size: int = Field(default=100, ge=1, le=100)
    rate_limit_per_minute: int = Field(default=60, ge=1, le=10_000)

    cors_origins: str = "*"

    model_config = SettingsConfigDict(env_file=".env", env_prefix="NAVIMED_", extra="ignore")

    @property
    def cors_origin_list(self) -> list[str]:
        return [x.strip() for x in self.cors_origins.split(",") if x.strip()]

    @property
    def resolved_supabase_issuer(self) -> str:
        if self.supabase_issuer:
            return self.supabase_issuer.rstrip("/")
        return f"{self.supabase_url.rstrip('/')}/auth/v1" if self.supabase_url else ""

    @property
    def resolved_supabase_jwks_url(self) -> str:
        if self.supabase_jwks_url:
            return self.supabase_jwks_url
        issuer = self.resolved_supabase_issuer
        return f"{issuer}/.well-known/jwks.json" if issuer else ""


@lru_cache
def get_settings() -> Settings:
    return Settings()
