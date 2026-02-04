"""Pytest configuration and shared fixtures for compass-engine tests."""

from pathlib import Path

import pytest


@pytest.fixture
def project_root() -> Path:
    """Return the project root directory."""
    return Path(__file__).parent.parent


@pytest.fixture
def tests_dir() -> Path:
    """Return the tests directory."""
    return Path(__file__).parent


@pytest.fixture
def fixtures_dir(tests_dir: Path) -> Path:
    """Return the test fixtures directory."""
    fixtures_path = tests_dir / "fixtures"
    fixtures_path.mkdir(exist_ok=True)
    return fixtures_path


@pytest.fixture
def tmp_project_dir(tmp_path: Path) -> Path:
    """Create a temporary project directory for testing."""
    return tmp_path
