"""Shared fixtures for benchmark tests."""
import os
import pytest


@pytest.fixture
def base_url():
    return os.getenv("BENCHMARK_URL", "https://eduhu-assistant.onrender.com")


@pytest.fixture
def teacher_id():
    return os.getenv("BENCHMARK_TEACHER_ID", "a4d218bd-4ac8-4ce3-8d41-c85db8be6e32")
