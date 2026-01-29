"""Classify meeting items into Task/Issue/Risk/Question.

Supports Japanese and Vietnamese keywords with PM mindset.
Classification priority: ISSUE > RISK > QUESTION > TASK
"""

import re
from typing import Optional

from models import ItemCategory, MeetingItem, Priority


class ItemClassifier:
    """Classify meeting items by keywords and context."""

    # Issue/Bug keywords (highest priority - errors must be addressed first)
    ISSUE_KEYWORDS = [
        # Japanese
        "不具合", "バグ", "エラー", "障害", "問題",
        "動かない", "表示されない", "消失", "失敗",
        # Vietnamese
        "lỗi", "bug", "vấn đề",
        # English
        "error", "bug", "fail", "broken", "crash",
    ]

    # Risk keywords
    RISK_KEYWORDS = [
        # Japanese
        "リスク", "心配", "懸念", "もしかして", "危険",
        "遅れ", "間に合わない",
        # Vietnamese
        "rủi ro", "lo lắng", "có thể",
        # English
        "risk", "concern", "worry",
    ]

    # Risk context patterns (require more context)
    RISK_PATTERNS = [
        r"nếu.+thì",  # Vietnamese if-then
        r"もし.+たら",  # Japanese if-then
        r"スケジュール.+タイト",  # tight schedule
    ]

    # Question/Confirmation keywords
    QUESTION_KEYWORDS = [
        # Japanese
        "確認", "質問", "聞いて", "教えて",
        # Vietnamese
        "xác nhận", "hỏi", "cần biết", "chưa rõ",
        # Symbols
        "？", "?",
    ]

    # Task keywords (default category)
    TASK_KEYWORDS = [
        # Japanese
        "作成", "実装", "対応", "完了", "担当", "お願い",
        "やる", "する", "します",
        # Vietnamese
        "làm", "tạo", "implement", "hoàn thành",
        # English
        "create", "implement", "do", "complete", "finish",
    ]

    # High priority keywords
    HIGH_PRIORITY_KEYWORDS = [
        # Japanese
        "至急", "緊急", "今日中", "今すぐ", "即時", "ASAP",
        # Vietnamese
        "gấp", "urgent", "ngay",
    ]

    # Assignee patterns (Japanese names with honorifics)
    ASSIGNEE_PATTERNS = [
        r"([\u4e00-\u9fff]{1,5})(さん|くん|君|氏)",  # Kanji name + honorific
        r"([\u4e00-\u9fff]{1,5})(が担当|にお願い|が対応)",  # Kanji name + action
    ]

    def classify(self, text: str) -> MeetingItem:
        """Classify text into a MeetingItem.

        Args:
            text: Text to classify

        Returns:
            MeetingItem with category, priority, and optional assignee
        """
        if not text:
            return MeetingItem(
                description="",
                category=ItemCategory.TASK,
                priority=Priority.NORMAL,
            )

        # Detect category (priority order: ISSUE > RISK > QUESTION > TASK)
        category = self._detect_category(text)

        # Detect priority
        priority = self._detect_priority(text)

        # Extract assignee
        assignee = self._extract_assignee(text)

        # Generate description (clean up text)
        description = self._generate_description(text)

        return MeetingItem(
            description=description,
            category=category,
            priority=priority,
            assignee=assignee,
            source_text=text,
        )

    def _detect_category(self, text: str) -> ItemCategory:
        """Detect item category from keywords.

        Priority order ensures critical items (issues) are caught first.
        """
        text_lower = text.lower()

        # Check issue keywords first (highest priority)
        for kw in self.ISSUE_KEYWORDS:
            if kw.lower() in text_lower:
                return ItemCategory.ISSUE

        # Check risk keywords
        for kw in self.RISK_KEYWORDS:
            if kw.lower() in text_lower:
                return ItemCategory.RISK

        # Check risk patterns (contextual)
        for pattern in self.RISK_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                return ItemCategory.RISK

        # Check question keywords
        for kw in self.QUESTION_KEYWORDS:
            if kw.lower() in text_lower:
                return ItemCategory.QUESTION

        # Default to task (or check task keywords explicitly)
        return ItemCategory.TASK

    def _detect_priority(self, text: str) -> Priority:
        """Detect priority from keywords."""
        text_lower = text.lower()

        for kw in self.HIGH_PRIORITY_KEYWORDS:
            if kw.lower() in text_lower:
                return Priority.HIGH

        return Priority.NORMAL

    def _extract_assignee(self, text: str) -> Optional[str]:
        """Extract assignee from Japanese name patterns."""
        for pattern in self.ASSIGNEE_PATTERNS:
            match = re.search(pattern, text)
            if match:
                return match.group(1)

        return None

    def _generate_description(self, text: str, max_length: int = 100) -> str:
        """Generate clean description from text."""
        # Remove common filler phrases
        text = re.sub(r'^(はい|えーと|あの|まあ)[\s、。]+', '', text)
        text = re.sub(r'^(Vâng|À|Ừm)[\s,\.]+', '', text, flags=re.IGNORECASE)

        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text).strip()

        # Truncate if too long
        if len(text) > max_length:
            text = text[:max_length - 3] + "..."

        return text


def classify_item(text: str) -> MeetingItem:
    """Convenience function to classify a single item."""
    classifier = ItemClassifier()
    return classifier.classify(text)


def classify_items(texts: list[str]) -> list[MeetingItem]:
    """Classify multiple items."""
    classifier = ItemClassifier()
    return [classifier.classify(text) for text in texts]