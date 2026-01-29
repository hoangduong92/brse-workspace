"""
Tests for test_plan_generator module.
"""

import pytest
from pathlib import Path
import sys

# Add scripts directory to path
scripts_dir = Path(__file__).parent.parent / 'scripts'
sys.path.insert(0, str(scripts_dir))

from test_plan_generator import build_test_plan_prompt, generate_test_plan


class TestTestPlanGenerator:
    """Test cases for test plan generation."""

    @pytest.fixture
    def sample_requirements(self):
        """Load sample requirements fixture."""
        fixture_path = Path(__file__).parent / 'fixtures' / 'sample_requirements.md'
        return fixture_path.read_text(encoding='utf-8')

    def test_build_test_plan_prompt_contains_requirements(self, sample_requirements):
        """Test that the prompt contains the requirements."""
        prompt = build_test_plan_prompt(sample_requirements)

        assert '要件定義書' in prompt
        assert 'ユーザー認証機能' in prompt

    def test_build_test_plan_prompt_contains_project_name(self, sample_requirements):
        """Test that the prompt contains the project name."""
        project_name = "認証システム"
        prompt = build_test_plan_prompt(sample_requirements, project_name)

        assert project_name in prompt

    def test_build_test_plan_prompt_uses_default_project_name(self, sample_requirements):
        """Test default project name."""
        prompt = build_test_plan_prompt(sample_requirements)

        assert 'プロジェクト' in prompt

    def test_build_test_plan_prompt_includes_structure(self, sample_requirements):
        """Test that the prompt includes test plan structure."""
        prompt = build_test_plan_prompt(sample_requirements)

        # Main sections
        assert 'テスト概要' in prompt
        assert 'テスト戦略' in prompt
        assert 'テストスケジュール' in prompt
        assert 'テスト環境' in prompt
        assert '終了基準' in prompt
        assert 'リスクと対応策' in prompt
        assert '役割と責任' in prompt
        assert '成果物' in prompt

    def test_build_test_plan_prompt_includes_test_levels(self, sample_requirements):
        """Test that the prompt includes test levels."""
        prompt = build_test_plan_prompt(sample_requirements)

        assert '単体テスト' in prompt
        assert '結合テスト' in prompt
        assert 'システムテスト' in prompt
        assert '受入テスト' in prompt

    def test_build_test_plan_prompt_includes_test_types(self, sample_requirements):
        """Test that the prompt includes test types."""
        prompt = build_test_plan_prompt(sample_requirements)

        assert '機能テスト' in prompt
        assert '非機能テスト' in prompt

    def test_generate_test_plan_with_custom_project(self, sample_requirements):
        """Test generate_test_plan with custom project name."""
        project_name = "カスタムプロジェクト"
        prompt = generate_test_plan(sample_requirements, project_name)

        assert project_name in prompt
        assert 'テスト計画書' in prompt

    def test_generate_test_plan_with_default_project(self, sample_requirements):
        """Test generate_test_plan with default project name."""
        prompt = generate_test_plan(sample_requirements)

        assert 'プロジェクト' in prompt
        assert 'テスト計画書' in prompt
