"""Tests for main translation prompt builder."""

import pytest
from pathlib import Path
import sys

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'backlog' / 'scripts'))
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))

from main import build_translation_prompt
from models import Language


class TestBuildTranslationPrompt:
    """Test cases for build_translation_prompt function."""

    def test_japanese_to_vietnamese(self):
        """Test building prompt for JA→VI translation."""
        text = "テストを実施しました"
        glossary_text = "テスト → kiểm thử"
        preservation_note = ""

        prompt = build_translation_prompt(
            text,
            Language.JAPANESE,
            Language.VIETNAMESE,
            glossary_text,
            preservation_note
        )

        assert "Japanese↔Vietnamese translator" in prompt
        assert "from Japanese to Vietnamese" in prompt
        assert glossary_text in prompt
        assert text in prompt
        assert "Provide ONLY the translated text" in prompt

    def test_vietnamese_to_japanese(self):
        """Test building prompt for VI→JA translation."""
        text = "Đã thực hiện kiểm thử"
        glossary_text = "kiểm thử → テスト"
        preservation_note = ""

        prompt = build_translation_prompt(
            text,
            Language.VIETNAMESE,
            Language.JAPANESE,
            glossary_text,
            preservation_note
        )

        assert "Vietnamese↔Japanese translator" in prompt
        assert "from Vietnamese to Japanese" in prompt
        assert glossary_text in prompt
        assert text in prompt

    def test_with_preservation_note(self):
        """Test prompt with preservation note."""
        text = "Run [CODE_0] command"
        glossary_text = "command → コマンド"
        preservation_note = "## Preserved Elements:\n- [CODE_0]: `npm test`\n"

        prompt = build_translation_prompt(
            text,
            Language.JAPANESE,
            Language.VIETNAMESE,
            glossary_text,
            preservation_note
        )

        assert preservation_note in prompt
        assert "[CODE_0]" in prompt

    def test_glossary_section(self):
        """Test glossary section formatting."""
        text = "テスト"
        glossary_text = "バグ → lỗi\nテスト → kiểm thử"
        preservation_note = ""

        prompt = build_translation_prompt(
            text,
            Language.JAPANESE,
            Language.VIETNAMESE,
            glossary_text,
            preservation_note
        )

        assert "## Glossary (MUST use these exact translations):" in prompt
        assert glossary_text in prompt

    def test_instructions_section(self):
        """Test instructions section."""
        text = "テスト"
        glossary_text = "テスト → kiểm thử"
        preservation_note = ""

        prompt = build_translation_prompt(
            text,
            Language.JAPANESE,
            Language.VIETNAMESE,
            glossary_text,
            preservation_note
        )

        assert "## Instructions:" in prompt
        assert "Use glossary terms exactly as specified" in prompt
        assert "Preserve all [CODE_N] and [URL_N] placeholders" in prompt
        assert "Maintain the same formatting and structure" in prompt

    def test_output_section(self):
        """Test output section."""
        text = "テスト"
        glossary_text = "テスト → kiểm thử"
        preservation_note = ""

        prompt = build_translation_prompt(
            text,
            Language.JAPANESE,
            Language.VIETNAMESE,
            glossary_text,
            preservation_note
        )

        assert "## Output:" in prompt
        assert "Provide ONLY the translated text without any explanations or notes" in prompt

    def test_text_to_translate_section(self):
        """Test text to translate section."""
        text = "複数行のテキスト\n2行目です"
        glossary_text = ""
        preservation_note = ""

        prompt = build_translation_prompt(
            text,
            Language.JAPANESE,
            Language.VIETNAMESE,
            glossary_text,
            preservation_note
        )

        assert "## Text to Translate:" in prompt
        assert text in prompt

    def test_empty_glossary(self):
        """Test with empty glossary."""
        text = "テスト"
        glossary_text = "(No glossary terms loaded)"
        preservation_note = ""

        prompt = build_translation_prompt(
            text,
            Language.JAPANESE,
            Language.VIETNAMESE,
            glossary_text,
            preservation_note
        )

        assert glossary_text in prompt
        assert "## Glossary" in prompt

    def test_real_world_scenario(self):
        """Test real-world translation scenario."""
        text = "バグ [CODE_0] を修正しました。\n詳細: [URL_0]"
        glossary_text = "バグ → lỗi\n修正 → sửa"
        preservation_note = """## Preserved Elements (DO NOT translate):
- 1 code block(s): [CODE_0]
- 1 URL(s): [URL_0]

"""

        prompt = build_translation_prompt(
            text,
            Language.JAPANESE,
            Language.VIETNAMESE,
            glossary_text,
            preservation_note
        )

        # Verify all components present
        assert "Japanese↔Vietnamese translator" in prompt
        assert glossary_text in prompt
        assert preservation_note in prompt
        assert text in prompt
        assert "[CODE_0]" in prompt
        assert "[URL_0]" in prompt

    def test_prompt_structure_order(self):
        """Test that prompt sections are in correct order."""
        text = "テスト"
        glossary_text = "テスト → kiểm thử"
        preservation_note = "## Preserved Elements:\n- [CODE_0]\n\n"

        prompt = build_translation_prompt(
            text,
            Language.JAPANESE,
            Language.VIETNAMESE,
            glossary_text,
            preservation_note
        )

        # Check order of sections
        glossary_pos = prompt.find("## Glossary")
        preservation_pos = prompt.find("## Preserved Elements")
        instructions_pos = prompt.find("## Instructions:")
        text_pos = prompt.find("## Text to Translate:")
        output_pos = prompt.find("## Output:")

        # Glossary should come first
        assert glossary_pos < instructions_pos
        # Preservation note between glossary and instructions
        assert glossary_pos < preservation_pos < instructions_pos
        # Instructions before text
        assert instructions_pos < text_pos
        # Text before output
        assert text_pos < output_pos
