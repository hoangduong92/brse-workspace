"""Pytest configuration and shared fixtures for bk-recall tests."""
import os
import sys
import pytest
from unittest.mock import MagicMock, patch

# Add scripts and lib paths for all tests
test_dir = os.path.dirname(__file__)
scripts_path = os.path.join(test_dir, "../scripts")
lib_path = os.path.join(test_dir, "../../lib")

if scripts_path not in sys.path:
    sys.path.insert(0, scripts_path)
if lib_path not in sys.path:
    sys.path.insert(0, lib_path)


@pytest.fixture
def mock_vault_store():
    """Fixture for mocked VaultStore."""
    with patch("vault.VaultStore") as mock:
        yield mock


@pytest.fixture
def mock_vault_search():
    """Fixture for mocked VaultSearch."""
    with patch("vault.VaultSearch") as mock:
        yield mock


@pytest.fixture
def mock_gemini_embedder():
    """Fixture for mocked GeminiEmbedder."""
    with patch("vault.GeminiEmbedder") as mock:
        yield mock


@pytest.fixture
def sample_vault_item():
    """Fixture for sample VaultItem."""
    from vault import VaultItem
    return VaultItem(
        id="test-123",
        source="email",
        title="Test Email",
        content="This is test email content",
        metadata={
            "from": "sender@example.com",
            "date": "2026-01-30"
        }
    )


@pytest.fixture
def sample_search_result(sample_vault_item):
    """Fixture for sample SearchResult."""
    from vault import SearchResult
    return SearchResult(item=sample_vault_item, score=0.85)


def pytest_configure(config):
    """Configure pytest."""
    # Add custom markers
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests (deselect with '-m \"not integration\"')"
    )
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
