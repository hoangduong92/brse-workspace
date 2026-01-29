"""
Tests for main module.
"""

import pytest
from pathlib import Path
import sys
from io import StringIO

# Add scripts directory to path
scripts_dir = Path(__file__).parent.parent / 'scripts'
sys.path.insert(0, str(scripts_dir))

from main import read_file


class TestMain:
    """Test cases for main module."""

    @pytest.fixture
    def sample_requirements_path(self):
        """Path to sample requirements fixture."""
        return Path(__file__).parent / 'fixtures' / 'sample_requirements.md'

    def test_read_file_success(self, sample_requirements_path):
        """Test reading a valid file."""
        content = read_file(str(sample_requirements_path))

        assert content is not None
        assert len(content) > 0
        assert 'ユーザー認証機能' in content

    def test_read_file_nonexistent(self, capsys):
        """Test reading a non-existent file."""
        with pytest.raises(SystemExit) as exc_info:
            read_file('nonexistent_file.md')

        assert exc_info.value.code == 1

        captured = capsys.readouterr()
        assert 'Error: File not found' in captured.err

    def test_read_file_handles_utf8(self, sample_requirements_path):
        """Test that file reading handles UTF-8 encoding."""
        content = read_file(str(sample_requirements_path))

        # Check for Japanese characters
        assert 'ユーザー' in content
        assert 'メールアドレス' in content
        assert 'パスワード' in content