"""Priority and deadline detector for bk-capture."""
from enum import Enum
from datetime import date, timedelta
from typing import Optional, Tuple
import re


class Priority(Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class PriorityDetector:
    """Detect priority and deadline from text."""

    # Priority keywords
    HIGH_PRIORITY = {
        "ja": ["至急", "緊急", "ASAP", "優先度高", "すぐに", "今すぐ"],
        "en": ["urgent", "asap", "critical", "high priority", "immediately"],
        "vi": ["khẩn cấp", "gấp", "ngay lập tức"]
    }

    MEDIUM_PRIORITY = {
        "ja": ["なるべく早く", "できれば", "優先"],
        "en": ["soon", "priority", "important"],
        "vi": ["sớm", "quan trọng"]
    }

    # Deadline patterns
    DEADLINE_PATTERNS = {
        "ja": {
            r"明日": 1,
            r"今週中": 5,
            r"来週": 7,
            r"今月中": 30,
            r"(\d+)日まで": None,  # Specific day
            r"(\d+)/(\d+)まで": None,  # MM/DD
        },
        "en": {
            r"tomorrow": 1,
            r"this week": 5,
            r"next week": 7,
            r"by friday": None,
            r"end of month": 30,
        }
    }

    def detect_priority(self, text: str) -> Priority:
        """Detect priority from text.

        Args:
            text: Input text

        Returns:
            Priority level
        """
        text_lower = text.lower()

        # Check high priority keywords
        for lang_keywords in self.HIGH_PRIORITY.values():
            for keyword in lang_keywords:
                if keyword.lower() in text_lower:
                    return Priority.HIGH

        # Check medium priority keywords
        for lang_keywords in self.MEDIUM_PRIORITY.values():
            for keyword in lang_keywords:
                if keyword.lower() in text_lower:
                    return Priority.MEDIUM

        return Priority.LOW

    def detect_deadline(self, text: str) -> Optional[date]:
        """Detect deadline from text.

        Args:
            text: Input text

        Returns:
            Deadline date or None
        """
        today = date.today()

        # Check relative dates (Japanese)
        if "明日" in text:
            return today + timedelta(days=1)
        if "今週中" in text:
            days_until_friday = (4 - today.weekday()) % 7
            return today + timedelta(days=max(1, days_until_friday))
        if "来週" in text:
            return today + timedelta(days=7)
        if "今月中" in text:
            # Last day of current month
            if today.month == 12:
                return date(today.year + 1, 1, 1) - timedelta(days=1)
            return date(today.year, today.month + 1, 1) - timedelta(days=1)

        # Check relative dates (English)
        text_lower = text.lower()
        if "tomorrow" in text_lower:
            return today + timedelta(days=1)
        if "this week" in text_lower:
            days_until_friday = (4 - today.weekday()) % 7
            return today + timedelta(days=max(1, days_until_friday))
        if "next week" in text_lower:
            return today + timedelta(days=7)

        # Check specific date patterns (MM/DD)
        date_match = re.search(r"(\d{1,2})/(\d{1,2})", text)
        if date_match:
            month, day = int(date_match.group(1)), int(date_match.group(2))
            try:
                return date(today.year, month, day)
            except ValueError:
                pass

        return None

    def detect(self, text: str) -> Tuple[Priority, Optional[date]]:
        """Detect both priority and deadline.

        Args:
            text: Input text

        Returns:
            Tuple of (Priority, deadline)
        """
        return self.detect_priority(text), self.detect_deadline(text)
