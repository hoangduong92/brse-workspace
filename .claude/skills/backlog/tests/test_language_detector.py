"""Tests for language detector."""

import pytest
import sys
from pathlib import Path

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from language_detector import LanguageDetector
from models import Language


class TestLanguageDetector:
    """Test cases for LanguageDetector."""

    def setup_method(self):
        """Set up test fixtures."""
        self.detector = LanguageDetector()

    def test_detect_japanese_hiragana(self):
        """Test detection of Japanese hiragana."""
        text = "これはテストです"
        assert self.detector.detect(text) == Language.JAPANESE

    def test_detect_japanese_katakana(self):
        """Test detection of Japanese katakana."""
        text = "テスト"
        assert self.detector.detect(text) == Language.JAPANESE

    def test_detect_japanese_kanji(self):
        """Test detection of Japanese kanji."""
        text = "新機能を追加する"
        assert self.detector.detect(text) == Language.JAPANESE

    def test_detect_japanese_mixed(self):
        """Test detection of mixed Japanese text."""
        text = "APIの新機能を実装してください"
        assert self.detector.detect(text) == Language.JAPANESE

    def test_detect_vietnamese_diacritics(self):
        """Test detection of Vietnamese with diacritics."""
        text = "Đây là một bài kiểm tra"
        assert self.detector.detect(text) == Language.VIETNAMESE

    def test_detect_vietnamese_plain(self):
        """Test detection of Vietnamese without special characters."""
        text = "Day la mot bai kiem tra"
        # Without diacritics and without Japanese, defaults to Vietnamese
        assert self.detector.detect(text) == Language.VIETNAMESE

    def test_detect_english_defaults_vietnamese(self):
        """Test that English text defaults to Vietnamese."""
        text = "This is a test"
        assert self.detector.detect(text) == Language.VIETNAMESE

    def test_detect_empty_string(self):
        """Test empty string defaults to Vietnamese."""
        assert self.detector.detect("") == Language.VIETNAMESE

    def test_get_target_language_from_japanese(self):
        """Test target language for Japanese source."""
        assert self.detector.get_target_language(Language.JAPANESE) == Language.VIETNAMESE

    def test_get_target_language_from_vietnamese(self):
        """Test target language for Vietnamese source."""
        assert self.detector.get_target_language(Language.VIETNAMESE) == Language.JAPANESE

    def test_detect_ticket_summary_japanese(self):
        """Test detection of typical Japanese ticket summary."""
        text = "【機能追加】ユーザー認証機能を実装する"
        assert self.detector.detect(text) == Language.JAPANESE

    def test_detect_ticket_summary_vietnamese(self):
        """Test detection of typical Vietnamese ticket summary."""
        text = "[Tính năng] Thêm chức năng xác thực người dùng"
        assert self.detector.detect(text) == Language.VIETNAMESE
