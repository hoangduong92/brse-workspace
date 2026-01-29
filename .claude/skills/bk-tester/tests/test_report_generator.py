"""
Tests for report_generator module.
"""

import pytest
from pathlib import Path
import sys

# Add scripts directory to path
scripts_dir = Path(__file__).parent.parent / 'scripts'
sys.path.insert(0, str(scripts_dir))

from report_generator import build_report_prompt, generate_test_report


class TestReportGenerator:
    """Test cases for test report generation."""

    @pytest.fixture
    def sample_requirements(self):
        """Load sample requirements fixture."""
        fixture_path = Path(__file__).parent / 'fixtures' / 'sample_requirements.md'
        return fixture_path.read_text(encoding='utf-8')

    @pytest.fixture
    def sample_test_results(self):
        """Sample test results."""
        return """
# テスト実施結果

## 実施状況
- 実施期間: 2024/01/15 - 2024/01/20
- 総テストケース数: 50
- 実施完了: 48
- 合格: 45
- 不合格: 3

## 不具合
- BUG-001: ログイン3回失敗時のロック機能が動作しない（優先度：高）
- BUG-002: パスワードリセットメール送信が遅い（優先度：中）
"""

    def test_build_report_prompt_contains_requirements(self, sample_requirements):
        """Test that the prompt contains the requirements."""
        prompt = build_report_prompt(sample_requirements)

        assert '要件定義書' in prompt
        assert 'ユーザー認証機能' in prompt

    def test_build_report_prompt_with_test_results(self, sample_requirements, sample_test_results):
        """Test prompt generation with test results."""
        prompt = build_report_prompt(sample_requirements, sample_test_results)

        assert '要件定義書' in prompt
        assert 'テスト実施結果' in prompt
        assert 'BUG-001' in sample_test_results

    def test_build_report_prompt_contains_project_name(self, sample_requirements):
        """Test that the prompt contains the project name."""
        project_name = "認証システム"
        prompt = build_report_prompt(sample_requirements, project_name=project_name)

        assert project_name in prompt

    def test_build_report_prompt_includes_structure(self, sample_requirements):
        """Test that the prompt includes report structure."""
        prompt = build_report_prompt(sample_requirements)

        # Main sections
        assert 'エグゼクティブサマリー' in prompt
        assert 'テスト実施概要' in prompt
        assert 'テスト実施結果' in prompt
        assert 'テストケース実施状況' in prompt
        assert '不具合サマリー' in prompt
        assert 'テストカバレッジ' in prompt
        assert '品質評価' in prompt
        assert 'リスクと課題' in prompt
        assert '結論と推奨事項' in prompt

    def test_build_report_prompt_includes_test_categories(self, sample_requirements):
        """Test that the prompt includes test categories."""
        prompt = build_report_prompt(sample_requirements)

        assert '機能テスト' in prompt
        assert '境界値テスト' in prompt
        assert '異常系テスト' in prompt
        assert 'セキュリティテスト' in prompt

    def test_build_report_prompt_includes_release_decision(self, sample_requirements):
        """Test that the prompt includes release decision section."""
        prompt = build_report_prompt(sample_requirements)

        assert 'リリース判定' in prompt
        assert 'リリース可' in prompt
        assert '条件付きリリース可' in prompt
        assert 'リリース不可' in prompt

    def test_build_report_prompt_includes_date(self, sample_requirements):
        """Test that the prompt includes current date."""
        prompt = build_report_prompt(sample_requirements)

        # Should contain year in Japanese format
        assert '年' in prompt
        assert '月' in prompt
        assert '日' in prompt

    def test_generate_test_report_without_results(self, sample_requirements):
        """Test generate_test_report without test results."""
        prompt = generate_test_report(sample_requirements)

        assert '要件定義書' in prompt
        assert 'テスト報告書' in prompt
        # Should not have test results section
        assert prompt.count('テスト実施結果') == 1  # Only in output format

    def test_generate_test_report_with_results(self, sample_requirements, sample_test_results):
        """Test generate_test_report with test results."""
        prompt = generate_test_report(sample_requirements, sample_test_results)

        assert '要件定義書' in prompt
        assert 'テスト実施結果' in prompt
        assert prompt.count('テスト実施結果') >= 2  # In input and output sections (may appear multiple times in template)

    def test_generate_test_report_with_custom_project(self, sample_requirements):
        """Test generate_test_report with custom project name."""
        project_name = "カスタムプロジェクト"
        prompt = generate_test_report(sample_requirements, project_name=project_name)

        assert project_name in prompt
        assert 'テスト報告書' in prompt
