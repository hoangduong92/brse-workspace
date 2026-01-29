"""Tests for meeting item classification.

TDD approach - tests written first, then implementation.
"""

import pytest
import sys
from pathlib import Path

# Add scripts to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from models import ItemCategory, Priority


class TestItemClassifier:
    """Test item classification with Japanese and Vietnamese keywords."""

    @pytest.fixture
    def classifier(self):
        """Create classifier instance."""
        from item_classifier import ItemClassifier
        return ItemClassifier()

    # === Task Detection ===

    def test_detect_task_japanese_create(self, classifier):
        """Detect task from Japanese 作成 keyword."""
        text = "APIの実装を田中さんが作成する"
        result = classifier.classify(text)
        assert result.category == ItemCategory.TASK

    def test_detect_task_japanese_implement(self, classifier):
        """Detect task from Japanese 実装 keyword."""
        text = "ログイン機能を実装してください"
        result = classifier.classify(text)
        assert result.category == ItemCategory.TASK

    def test_detect_task_japanese_respond(self, classifier):
        """Detect task from Japanese 対応 keyword."""
        text = "この件は山田さんが対応します"
        result = classifier.classify(text)
        assert result.category == ItemCategory.TASK

    def test_detect_task_vietnamese_lam(self, classifier):
        """Detect task from Vietnamese làm keyword."""
        text = "Tôi sẽ làm feature này trong tuần sau"
        result = classifier.classify(text)
        assert result.category == ItemCategory.TASK

    def test_detect_task_vietnamese_implement(self, classifier):
        """Detect task from Vietnamese implement keyword."""
        text = "Cần implement API trước deadline"
        result = classifier.classify(text)
        assert result.category == ItemCategory.TASK

    # === Issue/Bug Detection ===

    def test_detect_issue_japanese_bug(self, classifier):
        """Detect issue from Japanese 不具合 keyword."""
        text = "stagingで不具合が発生しています"
        result = classifier.classify(text)
        assert result.category == ItemCategory.ISSUE

    def test_detect_issue_japanese_error(self, classifier):
        """Detect issue from Japanese エラー keyword."""
        text = "Payment timeout errorが起きています"
        result = classifier.classify(text)
        assert result.category == ItemCategory.ISSUE

    def test_detect_issue_vietnamese_loi(self, classifier):
        """Detect issue from Vietnamese lỗi keyword."""
        text = "Có lỗi trên staging environment"
        result = classifier.classify(text)
        assert result.category == ItemCategory.ISSUE

    def test_detect_issue_english_bug(self, classifier):
        """Detect issue from English bug keyword."""
        text = "Found a critical bug in production"
        result = classifier.classify(text)
        assert result.category == ItemCategory.ISSUE

    # === Risk Detection ===

    def test_detect_risk_japanese_risk(self, classifier):
        """Detect risk from Japanese リスク keyword."""
        text = "スケジュールのリスクがあります"
        result = classifier.classify(text)
        assert result.category == ItemCategory.RISK

    def test_detect_risk_japanese_worry(self, classifier):
        """Detect risk from Japanese 心配 keyword."""
        text = "Phase 2のdeadlineについて心配があります"
        result = classifier.classify(text)
        assert result.category == ItemCategory.RISK

    def test_detect_risk_vietnamese_ruiro(self, classifier):
        """Detect risk from Vietnamese rủi ro keyword."""
        text = "Đây là rủi ro lớn cho project"
        result = classifier.classify(text)
        assert result.category == ItemCategory.RISK

    def test_detect_risk_vietnamese_if(self, classifier):
        """Detect risk from Vietnamese nếu (if) keyword in context."""
        # Note: "vấn đề" is issue keyword, use different text
        text = "Nếu không kịp deadline thì sẽ delay toàn bộ"
        result = classifier.classify(text)
        assert result.category == ItemCategory.RISK

    # === Question Detection ===

    def test_detect_question_japanese_confirm(self, classifier):
        """Detect question from Japanese 確認 keyword."""
        text = "Budget cho serverの件、確認が必要ですね"
        result = classifier.classify(text)
        assert result.category == ItemCategory.QUESTION

    def test_detect_question_question_mark(self, classifier):
        """Detect question from question mark."""
        text = "この機能は必要ですか？"
        result = classifier.classify(text)
        assert result.category == ItemCategory.QUESTION

    def test_detect_question_vietnamese_xacnhan(self, classifier):
        """Detect question from Vietnamese xác nhận keyword."""
        text = "Cần xác nhận với customer về requirement này"
        result = classifier.classify(text)
        assert result.category == ItemCategory.QUESTION

    # === Priority Detection ===

    def test_detect_high_priority_urgent_ja(self, classifier):
        """Detect high priority from Japanese 至急 keyword."""
        text = "至急対応が必要です"
        result = classifier.classify(text)
        assert result.priority == Priority.HIGH

    def test_detect_high_priority_today_ja(self, classifier):
        """Detect high priority from Japanese 今日中 keyword."""
        text = "今日中に調査をお願いします"
        result = classifier.classify(text)
        assert result.priority == Priority.HIGH

    def test_detect_normal_priority_default(self, classifier):
        """Default to normal priority."""
        text = "タスクを完了してください"
        result = classifier.classify(text)
        assert result.priority == Priority.NORMAL

    # === Assignee Extraction ===

    def test_extract_assignee_japanese(self, classifier):
        """Extract assignee from Japanese name pattern."""
        text = "田中さんが担当します"
        result = classifier.classify(text)
        assert result.assignee == "田中"

    def test_extract_assignee_vietnamese(self, classifier):
        """Extract assignee from Vietnamese pattern."""
        text = "Nguyen sẽ làm task này"
        result = classifier.classify(text)
        # Should extract or None - depends on impl
        # For now just verify it doesn't crash

    # === Edge Cases ===

    def test_empty_text(self, classifier):
        """Handle empty text gracefully."""
        text = ""
        result = classifier.classify(text)
        assert result.category == ItemCategory.TASK  # Default
        assert result.priority == Priority.NORMAL

    def test_mixed_language(self, classifier):
        """Handle mixed Japanese-Vietnamese text."""
        text = "staging環境でエラー、cần fix urgent"
        result = classifier.classify(text)
        assert result.category == ItemCategory.ISSUE  # Issue takes priority

    def test_priority_keywords_order(self, classifier):
        """Issue detection should take priority over task keywords."""
        text = "バグを修正して実装してください"  # Has both bug and implement
        result = classifier.classify(text)
        assert result.category == ItemCategory.ISSUE  # Bug takes priority