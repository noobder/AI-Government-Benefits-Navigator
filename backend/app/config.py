from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration, loaded from environment variables / .env."""

    # env_ignore_empty means an env var set to "" (common in .env templates
    # and some PaaS dashboards) falls back to the field default instead of
    # overriding it with an empty string.
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", env_ignore_empty=True)

    # Deployment
    environment: str = "development"  # "development" | "production"

    # Database
    database_url: str = "sqlite:///./benefits_navigator.db"

    # LLM provider: "mock" (default, no API key needed), "gemini", or "openai".
    # llm_model defaults per provider (gemini-2.5-flash / gpt-4o-mini) when unset.
    llm_provider: str = "mock"
    llm_api_key: str | None = None
    llm_model: str | None = None

    # Embedding provider: "keyword" (default, no API key needed) or "openai"
    embedding_provider: str = "keyword"
    embedding_api_key: str | None = None

    # Voice providers: "mock" (browser-based fallback) or "cloud"
    speech_to_text_api_key: str | None = None
    text_to_speech_api_key: str | None = None

    # Seed data
    seed_data_path: str = "../data/seed_schemes.json"

    # Kept as a plain string (not list[str]) because pydantic-settings tries to
    # JSON-decode env values for complex/list-typed fields, which breaks a
    # simple comma-separated env var like CORS_ORIGINS=https://a.com,https://b.com
    # or CORS_ORIGINS=*. Use `cors_origins` (the parsed property) everywhere else.
    cors_origins_raw: str = Field(
        default="http://localhost:5173,http://127.0.0.1:5173", validation_alias="CORS_ORIGINS"
    )

    log_level: str = "INFO"

    # Auth. secret_key MUST be overridden via env in any real deployment —
    # this default only exists so local dev works with zero setup.
    secret_key: str = "dev-insecure-secret-change-me"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 30

    # First-admin seeding: if both are set and no account with this email
    # exists yet, an admin account is created idempotently on startup.
    # There is no open admin self-registration endpoint.
    admin_email: str | None = None
    admin_password: str | None = None

    # Explicit override for the auth cookies' Secure flag. Browsers never
    # send a Secure cookie over plain HTTP, so this must stay False for any
    # deployment (like this repo's own docker-compose demo) that isn't
    # actually behind TLS yet, even if ENVIRONMENT=production otherwise.
    # None (default) means "follow is_production".
    cookie_secure: bool | None = None

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins_raw.split(",") if origin.strip()]

    @property
    def is_production(self) -> bool:
        return self.environment.lower() == "production"

    @property
    def cookie_secure_effective(self) -> bool:
        return self.is_production if self.cookie_secure is None else self.cookie_secure


@lru_cache
def get_settings() -> Settings:
    return Settings()
