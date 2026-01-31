"""Pytest configuration and fixtures for bk-spec tests."""
import sys
import os
from pathlib import Path

# Setup path to import modules from scripts directory
SCRIPTS_DIR = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

# Setup path to import vault modules
LIB_DIR = Path(__file__).parent.parent.parent / "lib"
sys.path.insert(0, str(LIB_DIR))


# Fixtures for common test data
import pytest


@pytest.fixture
def sample_requirements():
    """Sample requirements text for testing."""
    return """
    ユーザー登録機能が必要
    メール認証が必須
    パフォーマンスは1秒以内
    セキュリティ対策が必要
    """


@pytest.fixture
def sample_japanese_text():
    """Sample Japanese text."""
    return "ユーザー登録機能を実装する。メール認証が必要。"


@pytest.fixture
def sample_english_text():
    """Sample English text."""
    return "User registration feature is needed. Email verification is required."


@pytest.fixture
def sample_vietnamese_text():
    """Sample Vietnamese text."""
    return "Cần tính năng đăng ký người dùng. Xác minh email là bắt buộc."


@pytest.fixture
def sample_enriched_context():
    """Sample enriched context from ContextEnricher."""
    return {
        "keywords": ["ユーザー", "登録", "認証", "メール"],
        "related_items": [
            {
                "title": "認証システム設計",
                "content": "過去の認証システム実装例...",
                "source": "previous-project",
                "score": 0.85
            }
        ],
        "context_summary": "Found 1 related items in vault"
    }
