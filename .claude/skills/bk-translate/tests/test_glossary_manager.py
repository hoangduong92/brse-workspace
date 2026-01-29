"""Tests for GlossaryManager."""

import json
import pytest
from pathlib import Path
import tempfile
import sys

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))

from glossary_manager import GlossaryManager


class TestGlossaryManager:
    """Test cases for GlossaryManager."""

    def test_init_empty(self):
        """Test initialization with empty glossary."""
        manager = GlossaryManager()
        assert manager.glossary == {}
        assert manager.list_terms() == {}

    def test_load_valid_glossary(self, tmp_path):
        """Test loading valid glossary file."""
        glossary_data = {
            "バグ": "lỗi",
            "テスト": "kiểm thử",
            "実装": "triển khai"
        }

        glossary_file = tmp_path / "test.json"
        glossary_file.write_text(json.dumps(glossary_data, ensure_ascii=False), encoding='utf-8')

        manager = GlossaryManager()
        manager.load(str(glossary_file))

        assert manager.glossary == glossary_data
        assert len(manager.list_terms()) == 3

    def test_load_nonexistent_file(self):
        """Test loading nonexistent file raises error."""
        manager = GlossaryManager()
        with pytest.raises(FileNotFoundError):
            manager.load("nonexistent.json")

    def test_load_invalid_json(self, tmp_path):
        """Test loading invalid JSON raises error."""
        invalid_file = tmp_path / "invalid.json"
        invalid_file.write_text("not valid json", encoding='utf-8')

        manager = GlossaryManager()
        with pytest.raises(json.JSONDecodeError):
            manager.load(str(invalid_file))

    def test_add_term(self):
        """Test adding terms to glossary."""
        manager = GlossaryManager()

        manager.add_term("バグ", "lỗi")
        assert manager.glossary["バグ"] == "lỗi"

        manager.add_term("テスト", "kiểm thử")
        assert len(manager.glossary) == 2

    def test_add_term_update_existing(self):
        """Test updating existing term."""
        manager = GlossaryManager()
        manager.add_term("バグ", "lỗi")
        manager.add_term("バグ", "bug")

        assert manager.glossary["バグ"] == "bug"
        assert len(manager.glossary) == 1

    def test_remove_term_existing(self):
        """Test removing existing term."""
        manager = GlossaryManager()
        manager.add_term("バグ", "lỗi")
        manager.add_term("テスト", "kiểm thử")

        result = manager.remove_term("バグ")

        assert result is True
        assert "バグ" not in manager.glossary
        assert len(manager.glossary) == 1

    def test_remove_term_nonexistent(self):
        """Test removing nonexistent term returns False."""
        manager = GlossaryManager()
        manager.add_term("バグ", "lỗi")

        result = manager.remove_term("存在しない")

        assert result is False
        assert len(manager.glossary) == 1

    def test_list_terms(self):
        """Test listing all terms."""
        manager = GlossaryManager()
        manager.add_term("バグ", "lỗi")
        manager.add_term("テスト", "kiểm thử")

        terms = manager.list_terms()

        assert isinstance(terms, dict)
        assert len(terms) == 2
        assert terms["バグ"] == "lỗi"
        assert terms["テスト"] == "kiểm thử"

    def test_list_terms_returns_copy(self):
        """Test that list_terms returns a copy, not reference."""
        manager = GlossaryManager()
        manager.add_term("バグ", "lỗi")

        terms = manager.list_terms()
        terms["新しい"] = "mới"

        assert "新しい" not in manager.glossary

    def test_format_for_prompt_empty(self):
        """Test formatting empty glossary."""
        manager = GlossaryManager()
        result = manager.format_for_prompt()

        assert result == "(No glossary terms loaded)"

    def test_format_for_prompt_single_term(self):
        """Test formatting single term."""
        manager = GlossaryManager()
        manager.add_term("バグ", "lỗi")

        result = manager.format_for_prompt()

        assert result == "バグ → lỗi"

    def test_format_for_prompt_multiple_terms(self):
        """Test formatting multiple terms."""
        manager = GlossaryManager()
        manager.add_term("テスト", "kiểm thử")
        manager.add_term("バグ", "lỗi")
        manager.add_term("実装", "triển khai")

        result = manager.format_for_prompt()

        # Should be sorted
        lines = result.split("\n")
        assert len(lines) == 3
        assert "バグ → lỗi" in lines
        assert "テスト → kiểm thử" in lines
        assert "実装 → triển khai" in lines

    def test_save_glossary(self, tmp_path):
        """Test saving glossary to file."""
        manager = GlossaryManager()
        manager.add_term("バグ", "lỗi")
        manager.add_term("テスト", "kiểm thử")

        save_path = tmp_path / "output.json"
        manager.save(str(save_path))

        assert save_path.exists()

        # Verify content
        with open(save_path, 'r', encoding='utf-8') as f:
            saved_data = json.load(f)

        assert saved_data == manager.glossary

    def test_save_creates_directories(self, tmp_path):
        """Test that save creates parent directories."""
        manager = GlossaryManager()
        manager.add_term("バグ", "lỗi")

        save_path = tmp_path / "nested" / "directory" / "output.json"
        manager.save(str(save_path))

        assert save_path.exists()

    def test_roundtrip_load_save(self, tmp_path):
        """Test loading and saving preserves data."""
        original_data = {
            "バグ": "lỗi",
            "テスト": "kiểm thử",
            "実装": "triển khai"
        }

        # Save original
        original_file = tmp_path / "original.json"
        original_file.write_text(json.dumps(original_data, ensure_ascii=False), encoding='utf-8')

        # Load and save
        manager = GlossaryManager()
        manager.load(str(original_file))

        output_file = tmp_path / "output.json"
        manager.save(str(output_file))

        # Load saved file
        manager2 = GlossaryManager()
        manager2.load(str(output_file))

        assert manager2.glossary == original_data
