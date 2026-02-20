"""Shared test fixtures."""

import pytest


@pytest.fixture
def api_key():
    return "fv_test_abc123"


@pytest.fixture
def base_url():
    return "https://api.facevault.id"


@pytest.fixture
def webapp_base():
    return "https://app.facevault.id"
