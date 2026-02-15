"""Configuration loaded from environment."""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    supabase_url: str
    supabase_service_role_key: str
    anthropic_api_key: str
    brave_api_key: str = ""
    openai_api_key: str = ""
    pixabay_api_key: str = ""
    logfire_token: str = ""
    log_level: str = "INFO"
    # Chunking defaults
    chunk_size: int = 1500
    chunk_overlap: int = 200
    # Sub-agent resilience
    sub_agent_timeout_seconds: int = 120
    sub_agent_max_retries: int = 1

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
