"""
Tests for viewpoint_extractor module.
"""

import pytest
from pathlib import Path
import sys

# Add scripts directory to path
scripts_dir = Path(__file__).parent.parent / 'scripts'
sys.path.insert(0, str(scripts_dir))

from viewpoint_extractor import build_extraction_prompt, parse_viewpoints, CATEGORIES


class TestViewpointExtractor:
    """Test cases for viewpoint extraction."""

    @pytest.fixture
    def sample_requirements(self):
        """Load sample requirements fixture."""
        fixture_path = Path(__file__).parent / 'fixtures' / 'sample_requirements.md'
        return fixture_path.read_text(encoding='utf-8')

    def test_build_extraction_prompt_contains_requirements(self, sample_requirements):
        """Test that the prompt contains the requirements."""
        prompt = build_extraction_prompt(sample_requirements)

        assert 'ユーザー認証機能' in prompt
        assert 'REQ-001' in prompt
        assert 'ログイン機能' in prompt

    def test_build_extraction_prompt_contains_categories(self, sample_requirements):
        """Test that the prompt contains all test categories."""
        prompt = build_extraction_prompt(sample_requirements)

        # Check for Japanese category names
        assert '機能テスト' in prompt
        assert '境界値テスト' in prompt
        assert '異常系テスト' in prompt
        assert 'セキュリティテスト' in prompt
        assert '性能テスト' in prompt

    def test_build_extraction_prompt_has_output_format(self, sample_requirements):
        """Test that the prompt specifies output format."""
        prompt = build_extraction_prompt(sample_requirements)

        assert '出力形式' in prompt
        assert '観点ID' in prompt
        assert '目的' in prompt
        assert '確認項目' in prompt
        assert '優先度' in prompt

    def test_parse_viewpoints_with_valid_output(self):
        """Test parsing valid viewpoint output."""
        sample_output = """
## 機能テスト

### FT-001: ログイン成功確認
- **目的**: 正しい認証情報でログインできることを確認
- **確認項目**: メールアドレスとパスワードでログイン可能
- **優先度**: 高

### FT-002: セッション発行確認
- **目的**: ログイン成功時にセッションが発行されることを確認
- **確認項目**: セッショントークンの発行と有効期限
- **優先度**: 高

## 境界値テスト

### BT-001: パスワード最小文字数
- **目的**: パスワードの最小文字数制約を確認
- **確認項目**: 8文字未満のパスワードが拒否されること
- **優先度**: 中
"""
        viewpoints = parse_viewpoints(sample_output)

        assert len(viewpoints) == 3

        # Check first viewpoint
        assert viewpoints[0]['id'] == 'FT-001'
        assert viewpoints[0]['category'] == '機能テスト'
        assert viewpoints[0]['title'] == 'ログイン成功確認'
        assert '正しい認証情報' in viewpoints[0]['purpose']
        assert 'メールアドレスとパスワード' in viewpoints[0]['items']
        assert viewpoints[0]['priority'] == '高'

        # Check boundary test viewpoint
        assert viewpoints[2]['id'] == 'BT-001'
        assert viewpoints[2]['category'] == '境界値テスト'
        assert viewpoints[2]['priority'] == '中'

    def test_parse_viewpoints_with_empty_output(self):
        """Test parsing empty output."""
        viewpoints = parse_viewpoints("")
        assert viewpoints == []

    def test_parse_viewpoints_handles_missing_fields(self):
        """Test parsing output with missing fields."""
        sample_output = """
## 機能テスト

### FT-001: テスト項目
- **目的**: テスト目的
"""
        viewpoints = parse_viewpoints(sample_output)

        assert len(viewpoints) == 1
        assert viewpoints[0]['id'] == 'FT-001'
        assert viewpoints[0]['purpose'] == 'テスト目的'
        assert viewpoints[0]['items'] == ''
        assert viewpoints[0]['priority'] == ''

    def test_categories_constant(self):
        """Test that CATEGORIES constant is defined correctly."""
        assert 'functional' in CATEGORIES
        assert 'boundary' in CATEGORIES
        assert 'error' in CATEGORIES
        assert 'security' in CATEGORIES
        assert 'performance' in CATEGORIES

        assert CATEGORIES['functional'] == '機能テスト'
        assert CATEGORIES['boundary'] == '境界値テスト'
        assert CATEGORIES['error'] == '異常系テスト'
        assert CATEGORIES['security'] == 'セキュリティテスト'
        assert CATEGORIES['performance'] == '性能テスト'