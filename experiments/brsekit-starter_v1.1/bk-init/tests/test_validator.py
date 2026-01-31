"""Tests for validator module."""

import sys
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

import os
import pytest
from unittest.mock import patch, MagicMock
from validator import (
    validate_backlog_connection,
    validate_config,
    validate_env_vars,
    BacklogAPIError
)


@pytest.fixture
def valid_config():
    """Sample valid configuration."""
    return {
        "project": {
            "name": "Test Project",
            "backlog_key": "TEST",
            "type": "project-based",
            "methodology": "waterfall"
        },
        "customer": {
            "name": "Test Customer",
            "industry": "Finance",
            "timezone": "JST",
            "communication_style": "formal"
        },
        "focus_areas": {
            "primary": ["change_request_tracking", "budget_monitoring"],
            "secondary": ["documentation_quality"]
        },
        "vault": {
            "enabled": True,
            "sources": ["email", "backlog"],
            "sync_schedule": "daily"
        }
    }


@pytest.fixture
def mock_backlog_client():
    """Mock BacklogClient for testing."""
    with patch('validator.BacklogClient') as mock:
        yield mock


class TestValidateBacklogConnection:
    """Test validate_backlog_connection function."""

    def test_validate_successful_connection(self, mock_backlog_client):
        """Test successful Backlog connection validation."""
        # Setup mock
        mock_client = MagicMock()
        mock_backlog_client.return_value = mock_client
        mock_project = MagicMock()
        mock_project.name = "Test Project"
        mock_project.key = "TEST"
        mock_client.get_project.return_value = mock_project

        success, message = validate_backlog_connection(
            "test-space.backlog.jp",
            "valid_api_key_12345",
            "TEST"
        )

        assert success is True
        assert "Connected" in message
        assert "Test Project" in message
        mock_client.get_project.assert_called_once_with("TEST")

    def test_validate_invalid_api_key(self, mock_backlog_client):
        """Test validation with invalid API key."""
        from validator import BacklogAPIError

        mock_client = MagicMock()
        mock_backlog_client.return_value = mock_client
        mock_client.get_project.side_effect = BacklogAPIError(
            "Invalid API key",
            status_code=401
        )

        success, message = validate_backlog_connection(
            "test-space.backlog.jp",
            "invalid_key",
            "TEST"
        )

        assert success is False
        assert "Invalid API key" in message

    def test_validate_project_not_found(self, mock_backlog_client):
        """Test validation with non-existent project."""
        from validator import BacklogAPIError

        mock_client = MagicMock()
        mock_backlog_client.return_value = mock_client
        mock_client.get_project.side_effect = BacklogAPIError(
            "Project not found",
            status_code=404
        )

        success, message = validate_backlog_connection(
            "test-space.backlog.jp",
            "valid_api_key_12345",
            "NONEXIST"
        )

        assert success is False
        assert "not found" in message
        assert "NONEXIST" in message

    def test_validate_api_error(self, mock_backlog_client):
        """Test validation with generic API error."""
        from validator import BacklogAPIError

        mock_client = MagicMock()
        mock_backlog_client.return_value = mock_client
        mock_client.get_project.side_effect = BacklogAPIError(
            "Server error",
            status_code=500
        )

        success, message = validate_backlog_connection(
            "test-space.backlog.jp",
            "valid_api_key_12345",
            "TEST"
        )

        assert success is False
        assert "API error" in message

    def test_validate_connection_failed(self, mock_backlog_client):
        """Test validation with connection failure."""
        mock_client = MagicMock()
        mock_backlog_client.return_value = mock_client
        mock_client.get_project.side_effect = Exception("Connection refused")

        success, message = validate_backlog_connection(
            "test-space.backlog.jp",
            "valid_api_key_12345",
            "TEST"
        )

        assert success is False
        assert "Connection failed" in message

    def test_validate_client_not_available(self):
        """Test validation when BacklogClient is not available."""
        with patch('validator.BacklogClient', None):
            success, message = validate_backlog_connection(
                "test-space.backlog.jp",
                "valid_api_key_12345",
                "TEST"
            )

            assert success is False
            assert "not available" in message


class TestValidateConfig:
    """Test validate_config function."""

    def test_valid_config_passes(self, valid_config):
        """Test that valid config passes validation."""
        success, message = validate_config(valid_config)
        assert success is True
        assert "valid" in message.lower()

    def test_missing_project_section(self, valid_config):
        """Test validation fails when project section is missing."""
        del valid_config["project"]
        success, message = validate_config(valid_config)
        assert success is False
        assert "project" in message

    def test_missing_customer_section(self, valid_config):
        """Test validation fails when customer section is missing."""
        del valid_config["customer"]
        success, message = validate_config(valid_config)
        assert success is False
        assert "customer" in message

    def test_missing_focus_areas_section(self, valid_config):
        """Test validation fails when focus_areas section is missing."""
        del valid_config["focus_areas"]
        success, message = validate_config(valid_config)
        assert success is False
        assert "focus_areas" in message

    def test_missing_vault_section(self, valid_config):
        """Test validation fails when vault section is missing."""
        del valid_config["vault"]
        success, message = validate_config(valid_config)
        assert success is False
        assert "vault" in message

    def test_missing_project_name(self, valid_config):
        """Test validation fails when project.name is missing."""
        del valid_config["project"]["name"]
        success, message = validate_config(valid_config)
        assert success is False
        assert "project" in message and "name" in message

    def test_missing_project_backlog_key(self, valid_config):
        """Test validation fails when project.backlog_key is missing."""
        del valid_config["project"]["backlog_key"]
        success, message = validate_config(valid_config)
        assert success is False
        assert "backlog_key" in message

    def test_missing_project_type(self, valid_config):
        """Test validation fails when project.type is missing."""
        del valid_config["project"]["type"]
        success, message = validate_config(valid_config)
        assert success is False
        assert "type" in message

    def test_missing_project_methodology(self, valid_config):
        """Test validation fails when project.methodology is missing."""
        del valid_config["project"]["methodology"]
        success, message = validate_config(valid_config)
        assert success is False
        assert "methodology" in message

    def test_missing_customer_name(self, valid_config):
        """Test validation fails when customer.name is missing."""
        del valid_config["customer"]["name"]
        success, message = validate_config(valid_config)
        assert success is False
        assert "customer" in message and "name" in message

    def test_missing_customer_industry(self, valid_config):
        """Test validation fails when customer.industry is missing."""
        del valid_config["customer"]["industry"]
        success, message = validate_config(valid_config)
        assert success is False
        assert "industry" in message

    def test_missing_customer_timezone(self, valid_config):
        """Test validation fails when customer.timezone is missing."""
        del valid_config["customer"]["timezone"]
        success, message = validate_config(valid_config)
        assert success is False
        assert "timezone" in message

    def test_missing_customer_communication_style(self, valid_config):
        """Test validation fails when customer.communication_style is missing."""
        del valid_config["customer"]["communication_style"]
        success, message = validate_config(valid_config)
        assert success is False
        assert "communication_style" in message

    def test_missing_primary_focus(self, valid_config):
        """Test validation fails when focus_areas.primary is missing."""
        del valid_config["focus_areas"]["primary"]
        success, message = validate_config(valid_config)
        assert success is False
        assert "primary" in message

    def test_missing_vault_enabled(self, valid_config):
        """Test validation fails when vault.enabled is missing."""
        del valid_config["vault"]["enabled"]
        success, message = validate_config(valid_config)
        assert success is False
        assert "vault" in message and "enabled" in message

    def test_primary_focus_not_list(self, valid_config):
        """Test validation fails when focus_areas.primary is not a list."""
        valid_config["focus_areas"]["primary"] = "not_a_list"
        success, message = validate_config(valid_config)
        assert success is False
        assert "list" in message.lower()

    def test_vault_enabled_not_boolean(self, valid_config):
        """Test validation fails when vault.enabled is not boolean."""
        valid_config["vault"]["enabled"] = "yes"
        success, message = validate_config(valid_config)
        assert success is False
        assert "boolean" in message.lower()

    def test_valid_with_empty_primary_focus_list(self, valid_config):
        """Test that empty primary focus list is technically valid (has the key)."""
        valid_config["focus_areas"]["primary"] = []
        success, message = validate_config(valid_config)
        assert success is True

    def test_valid_with_empty_secondary_focus(self, valid_config):
        """Test that missing secondary focus is valid (not required)."""
        del valid_config["focus_areas"]["secondary"]
        # This should still pass because secondary is not in required keys
        success, message = validate_config(valid_config)
        assert success is True

    def test_minimal_valid_config(self):
        """Test minimal valid configuration."""
        minimal_config = {
            "project": {
                "name": "Project",
                "backlog_key": "TEST",
                "type": "project-based",
                "methodology": "waterfall"
            },
            "customer": {
                "name": "Customer",
                "industry": "Tech",
                "timezone": "JST",
                "communication_style": "formal"
            },
            "focus_areas": {
                "primary": ["change_request_tracking"]
            },
            "vault": {
                "enabled": False
            }
        }
        success, message = validate_config(minimal_config)
        assert success is True


class TestValidateEnvVars:
    """Test validate_env_vars function."""

    def test_valid_env_vars(self):
        """Test validation passes with required env vars set."""
        env_vars = {
            "BACKLOG_SPACE_URL": "test-space.backlog.jp",
            "BACKLOG_API_KEY": "test-api-key-12345"
        }
        with patch.dict(os.environ, env_vars, clear=True):
            success, message = validate_env_vars()
            assert success is True
            assert "Environment variables set" in message

    def test_missing_space_url(self):
        """Test validation fails when BACKLOG_SPACE_URL is missing."""
        env_vars = {"BACKLOG_API_KEY": "test-api-key"}
        with patch.dict(os.environ, env_vars, clear=True):
            success, message = validate_env_vars()
            assert success is False
            assert "BACKLOG_SPACE_URL" in message

    def test_missing_api_key(self):
        """Test validation fails when BACKLOG_API_KEY is missing."""
        env_vars = {"BACKLOG_SPACE_URL": "test-space.backlog.jp"}
        with patch.dict(os.environ, env_vars, clear=True):
            success, message = validate_env_vars()
            assert success is False
            assert "BACKLOG_API_KEY" in message

    def test_both_vars_missing(self):
        """Test validation fails when both env vars are missing."""
        with patch.dict(os.environ, {}, clear=True):
            success, message = validate_env_vars()
            assert success is False
            assert "BACKLOG_SPACE_URL" in message
            assert "BACKLOG_API_KEY" in message

    def test_empty_space_url(self):
        """Test validation fails with empty BACKLOG_SPACE_URL."""
        env_vars = {
            "BACKLOG_SPACE_URL": "",
            "BACKLOG_API_KEY": "test-api-key"
        }
        with patch.dict(os.environ, env_vars, clear=True):
            success, message = validate_env_vars()
            assert success is False
            assert "BACKLOG_SPACE_URL" in message

    def test_empty_api_key(self):
        """Test validation fails with empty BACKLOG_API_KEY."""
        env_vars = {
            "BACKLOG_SPACE_URL": "test-space.backlog.jp",
            "BACKLOG_API_KEY": ""
        }
        with patch.dict(os.environ, env_vars, clear=True):
            success, message = validate_env_vars()
            assert success is False
            assert "BACKLOG_API_KEY" in message
