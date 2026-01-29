"""Parse meeting transcript into structured meeting minutes.

Extracts:
- Meeting info (date, participants, agenda)
- Action items classified by category
- Decisions made
"""

import re
from datetime import date, datetime
from typing import Optional

from models import MeetingInfo, MeetingItem, MeetingMinutes, ItemCategory
from item_classifier import ItemClassifier


class MeetingParser:
    """Parse meeting transcript into structured data."""

    def __init__(self):
        self.classifier = ItemClassifier()

    def parse(self, transcript: str) -> MeetingMinutes:
        """Parse transcript into MeetingMinutes.

        Args:
            transcript: Raw meeting transcript text

        Returns:
            MeetingMinutes with extracted info and classified items
        """
        info = self._extract_meeting_info(transcript)
        decisions = self._extract_decisions(transcript)
        items = self._extract_and_classify_items(transcript)

        # Separate items by category
        tasks = [i for i in items if i.category == ItemCategory.TASK]
        issues = [i for i in items if i.category == ItemCategory.ISSUE]
        risks = [i for i in items if i.category == ItemCategory.RISK]
        questions = [i for i in items if i.category == ItemCategory.QUESTION]

        return MeetingMinutes(
            info=info,
            decisions=decisions,
            tasks=tasks,
            issues=issues,
            risks=risks,
            questions=questions,
        )

    def _extract_meeting_info(self, transcript: str) -> MeetingInfo:
        """Extract meeting date, participants, and agenda."""
        meeting_date = self._extract_date(transcript)
        participants = self._extract_participants(transcript)
        agenda = self._extract_agenda(transcript)
        duration = self._extract_duration(transcript)

        return MeetingInfo(
            date=meeting_date,
            participants=participants,
            agenda=agenda,
            duration_minutes=duration,
        )

    def _extract_date(self, text: str) -> Optional[date]:
        """Extract meeting date from text."""
        # Pattern: 2026年1月29日 or 2026/1/29
        patterns = [
            r'(\d{4})年(\d{1,2})月(\d{1,2})日',
            r'(\d{4})[/\-](\d{1,2})[/\-](\d{1,2})',
        ]

        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    year = int(match.group(1))
                    month = int(match.group(2))
                    day = int(match.group(3))
                    return date(year, month, day)
                except ValueError:
                    continue

        return None

    def _extract_duration(self, text: str) -> Optional[int]:
        """Extract meeting duration in minutes."""
        # Pattern: 10:00-11:00 (60 min)
        match = re.search(r'(\d{1,2}):(\d{2})\s*[-~]\s*(\d{1,2}):(\d{2})', text)
        if match:
            start_h, start_m = int(match.group(1)), int(match.group(2))
            end_h, end_m = int(match.group(3)), int(match.group(4))
            start_total = start_h * 60 + start_m
            end_total = end_h * 60 + end_m
            if end_total > start_total:
                return end_total - start_total

        # Pattern: 60分 or 60 min
        match = re.search(r'(\d+)\s*(分|min)', text, re.IGNORECASE)
        if match:
            return int(match.group(1))

        return None

    def _extract_participants(self, text: str) -> list[str]:
        """Extract participant names."""
        participants = []

        # Pattern: 参加者: A, B, C or 出席者: A、B、C
        match = re.search(r'(?:参加者|出席者)[：:]\s*(.+?)(?:\n|$)', text)
        if match:
            names_str = match.group(1)
            # Split by Japanese/English comma
            names = re.split(r'[、,]', names_str)
            participants = [n.strip() for n in names if n.strip()]

        # Fallback: extract speaker names from dialogue
        if not participants:
            # Pattern: [timestamp] Speaker N: or 田中: or Nguyen:
            # Handle both timestamped and non-timestamped formats
            speakers = re.findall(
                r'(?:\[\d{1,2}:\d{2}\]\s*)?(Speaker\s*\d+|[A-Za-z\u4e00-\u9fff]+)[：:]',
                text, re.MULTILINE
            )
            # Deduplicate while preserving order
            seen = set()
            for s in speakers:
                s = s.strip()
                if s not in seen and len(s) <= 15:
                    participants.append(s)
                    seen.add(s)

        return participants

    def _extract_agenda(self, text: str) -> list[str]:
        """Extract agenda items."""
        agenda = []

        # Pattern: アジェンダ section or bullet list after アジェンダ
        agenda_match = re.search(
            r'(?:アジェンダ|agenda|議題)[：:]?\s*\n?((?:[-・•]\s*.+\n?)+)',
            text, re.IGNORECASE
        )
        if agenda_match:
            items_text = agenda_match.group(1)
            items = re.findall(r'[-・•]\s*(.+)', items_text)
            agenda = [i.strip() for i in items if i.strip()]
            return agenda

        # Pattern: numbered list after agenda keyword
        agenda_match = re.search(
            r'(?:アジェンダ|agenda|議題)[：:]?\s*\n?((?:\d+[\.）]\s*.+\n?)+)',
            text, re.IGNORECASE
        )
        if agenda_match:
            items_text = agenda_match.group(1)
            items = re.findall(r'\d+[\.）]\s*(.+)', items_text)
            agenda = [i.strip() for i in items if i.strip()]

        return agenda

    def _extract_decisions(self, text: str) -> list[str]:
        """Extract decisions made in the meeting."""
        decisions = []

        # Pattern: 決定事項 section
        decision_match = re.search(
            r'(?:決定事項|決定|approved)[：:]?\s*\n?((?:[-・•]\s*.+\n?)+)',
            text, re.IGNORECASE
        )
        if decision_match:
            items_text = decision_match.group(1)
            items = re.findall(r'[-・•]\s*(.+)', items_text)
            decisions = [i.strip() for i in items if i.strip()]

        return decisions

    def _extract_and_classify_items(self, text: str) -> list[MeetingItem]:
        """Extract action items from transcript and classify them."""
        items = []
        lines = text.split('\n')

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Skip header lines
            if self._is_header_line(line):
                continue

            # Check if line contains actionable content
            if self._is_actionable(line):
                item = self.classifier.classify(line)
                if item.description:
                    items.append(item)

        return items

    def _is_header_line(self, line: str) -> bool:
        """Check if line is a header/metadata line."""
        header_patterns = [
            r'^=+',  # === markers
            r'^会議日時',
            r'^参加者',
            r'^出席者',
            r'^アジェンダ',
            r'^議題',
        ]
        for pattern in header_patterns:
            if re.match(pattern, line):
                return True
        return False

    def _is_actionable(self, line: str) -> bool:
        """Check if line contains actionable content."""
        # Remove timestamp prefix if present [MM:SS]
        line = re.sub(r'^\[\d{1,2}:\d{2}\]\s*', '', line)

        # Must have dialogue format (Speaker: content) or be substantial
        if ':' in line or '：' in line:
            # Extract content after speaker
            content = re.sub(r'^[^:：]+[：:]', '', line).strip()
            # Must be long enough and contain action keywords
            if len(content) >= 10:
                action_keywords = [
                    # Japanese
                    '対応', '実装', '作成', '確認', '調査', 'お願い',
                    '担当', 'します', 'ください', '完了', '必要',
                    'エラー', '不具合', '問題', 'リスク', '心配',
                    '質問', '聞いて', '教えて',  # Question keywords
                    # Vietnamese
                    'làm', 'tạo', 'xác nhận', 'lỗi', 'rủi ro', 'hỏi',
                    # English
                    'implement', 'create', 'check', 'fix', 'bug', 'error', 'question',
                ]
                for kw in action_keywords:
                    if kw.lower() in content.lower():
                        return True
        return False


def parse_meeting(transcript: str) -> MeetingMinutes:
    """Convenience function to parse a meeting transcript."""
    parser = MeetingParser()
    return parser.parse(transcript)
