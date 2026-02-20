"""Zentrale Model-Factory — setzt den API-Key einmal, liefert Model-Instanzen."""

import os
from functools import lru_cache

from pydantic_ai.models.anthropic import AnthropicModel

from app.config import get_settings


def _ensure_api_key() -> None:
    if "ANTHROPIC_API_KEY" not in os.environ:
        os.environ["ANTHROPIC_API_KEY"] = get_settings().anthropic_api_key


@lru_cache
def get_sonnet() -> AnthropicModel:
    _ensure_api_key()
    return AnthropicModel("claude-sonnet-4-20250514")


@lru_cache
def get_haiku() -> AnthropicModel:
    _ensure_api_key()
    return AnthropicModel("claude-haiku-4-5-20251001")
