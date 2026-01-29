"""
Tests for test_case_generator module.
"""

import pytest
from pathlib import Path
import sys

# Add scripts directory to path
scripts_dir = Path(__file__).parent.parent / 'scripts'
sys.path.insert(0, str(scripts_dir))

from test_case_generator import build_test_case_prompt, generate_test_cases


class TestTestCaseGenerator:
    """Test cases for test case generation."""

    @pytest.fixture
    def sample_requirements(self):
        """Load sample requirements fixture."""
        fixture_path = Path(__file__).parent / 'fixtures' / 'sample_requirements.md'
        return fixture_path.read_text(encoding='utf-8')

    @pytest.fixture
    def sample_viewpoints(self):
        """Sample viewpoints for test cases."""
        return """
## 機能テスト

### FT-001: ログイン成功確認
- **目的**: 正しい認証情報でログインできることを確認
- **確認項目**: メールアドレスとパスワードでログイン可能
- **優先度**: 高
"""

    def test_build_test_case_prompt_contains_requirements(self, sample_requirements):
        """Test that the prompt contains the requirements."""
        prompt = build_test_case_prompt(sample_requirements)

        assert '要件定義書' in prompt
        assert 'ユーザー認証機能' in prompt
        assert 'ログイン機能' in prompt

    def test_build_test_case_prompt_with_viewpoints(self, sample_requirements, sample_viewpoints):
        """Test prompt generation with viewpoints."""
        prompt = build_test_case_prompt(sample_requirements, sample_viewpoints)

        assert '要件定義書' in prompt
        assert 'テスト観点' in prompt
        assert 'FT-001' in sample_viewpoints
        assert 'ログイン成功確認' in sample_viewpoints

    def test_build_test_case_prompt_includes_table_format(self, sample_requirements):
        """Test that the prompt includes table format."""
        prompt = build_test_case_prompt(sample_requirements)

        assert 'テストケースID' in prompt
        assert '分類' in prompt
        assert 'テスト項目' in prompt
        assert '前提条件' in prompt
        assert 'テスト手順' in prompt
        assert '期待結果' in prompt
        assert '優先度' in prompt

    def test_build_test_case_prompt_includes_categories(self, sample_requirements):
        """Test that the prompt includes test categories."""
        prompt = build_test_case_prompt(sample_requirements)

        assert '機能テスト' in prompt
        assert '境界値テスト' in prompt
        assert '異常系テスト' in prompt
        assert 'セキュリティテスト' in prompt

    def test_build_test_case_prompt_includes_instructions(self, sample_requirements):
        """Test that the prompt includes clear instructions."""
        prompt = build_test_case_prompt(sample_requirements)

        assert 'TC-001' in prompt  # Test case ID format
        assert '重要な注意事項' in prompt
        assert 'テストケースIDは連番で採番' in prompt

    def test_generate_test_cases_without_viewpoints(self, sample_requirements):
        """Test generate_test_cases without viewpoints."""
        prompt = generate_test_cases(sample_requirements)

        assert '要件定義書' in prompt
        assert 'テストケースID' in prompt
        # Should not have viewpoints section
        assert prompt.count('テスト観点') == 0

    def test_generate_test_cases_with_viewpoints(self, sample_requirements, sample_viewpoints):
        """Test generate_test_cases with viewpoints."""
        prompt = generate_test_cases(sample_requirements, sample_viewpoints)

        assert '要件定義書' in prompt
        assert 'テスト観点' in prompt
        assert 'FT-001' in sample_viewpoints
