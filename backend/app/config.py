"""Configuration loaded from environment."""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    database_url: str  # postgresql://user:password@host:5432/dbname
    anthropic_api_key: str
    brave_api_key: str = ""
    openai_api_key: str = ""
    pixabay_api_key: str = ""
    gemini_api_key: str = ""
    elevenlabs_api_key: str = ""
    webshare_proxy_url: str = ""  # format: http://user-1:pass@p.webshare.io:80
    logfire_token: str = ""
    log_level: str = "INFO"
    # CORS & Frontend
    cors_origins: str = ""  # comma-separated, e.g. https://eduhu.example.com
    frontend_url: str = ""  # for share links, e.g. https://eduhu.example.com
    # Chunking defaults
    chunk_size: int = 1500
    chunk_overlap: int = 200
    # Sub-agent resilience
    sub_agent_timeout_seconds: int = 120
    sub_agent_max_retries: int = 1

    # Auth
    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7
    # Mail (SMTP via Hetzner)
    mail_username: str = ""
    mail_password: str = ""
    mail_from: str = "noreply@eduhu.app"
    mail_server: str = ""
    mail_port: int = 587
    mail_from_name: str = "eduhu"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
