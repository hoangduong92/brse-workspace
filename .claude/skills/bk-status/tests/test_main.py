"""Tests for main.py entry point."""

import os
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from main import load_env, get_output_path


class TestLoadEnv:
    """Tests for load_env function."""

    def test_load_env_success(self):
        """All env vars present returns tuple."""
        with patch.dict(os.environ, {
            "NULAB_SPACE_URL": "test.backlog.com",
            "NULAB_API_KEY": "test-api-key",
            "NULAB_PROJECT_ID": "TEST"
        }):
            space, key, project = load_env()
            assert space == "test.backlog.com"
            assert key == "test-api-key"
            assert project == "TEST"

    def test_load_env_missing_all(self):
        """Missing all env vars exits with code 1."""
        with patch.dict(os.environ, {}, clear=True):
            # Clear NULAB vars specifically
            env = {k: v for k, v in os.environ.items()
                   if not k.startswith("NULAB_")}
            with patch.dict(os.environ, env, clear=True):
                with pytest.raises(SystemExit) as exc:
                    load_env()
                assert exc.value.code == 1

    def test_load_env_missing_one(self):
        """Missing one env var exits with code 1."""
        with patch.dict(os.environ, {
            "NULAB_SPACE_URL": "test.backlog.com",
            "NULAB_API_KEY": "test-api-key"
            # Missing NULAB_PROJECT_ID
        }, clear=True):
            with pytest.raises(SystemExit) as exc:
                load_env()
            assert exc.value.code == 1


class TestGetOutputPath:
    """Tests for get_output_path function."""

    def test_creates_output_directory(self, tmp_path):
        """Creates project-status directory if not exists."""
        with patch("main.Path") as mock_path:
            mock_output_dir = MagicMock()
            mock_path.return_value = mock_output_dir
            mock_output_dir.__truediv__ = lambda self, x: tmp_path / x

            path = get_output_path("MyProject")
            assert "MyProject" in str(path) or "status.md" in str(path)

    def test_sanitizes_project_name(self):
        """Replaces spaces and slashes in project name."""
        path = get_output_path("My Project/Test")
        filename = path.name
        assert " " not in filename
        assert "/" not in filename
        assert "My-Project-Test" in filename

    def test_includes_timestamp(self):
        """Output filename includes timestamp."""
        path = get_output_path("Test")
        filename = path.name
        # Should match pattern: YYYYMMDD-HHMMSS_Test-status.md
        assert "-status.md" in filename
        assert len(filename) > 20  # Has timestamp
