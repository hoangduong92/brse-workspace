"""Parse unstructured Japanese input into structured tasks.

Supports:
- Task type detection (bug, feature, question, improvement)
- Priority detection (high, normal, low)
- Deadline detection (today, tomorrow, end_of_week, specific date)
- Estimated hours extraction
- Assignee hint extraction
- Multiple task parsing from bullet lists
"""

import re
from dataclasses import dataclass, field
from datetime import date, timedelta
from enum import Enum
from typing import Optional


class TaskType(Enum):
    """Task type classification."""
    BUG = "bug"
    FEATURE = "feature"
    QUESTION = "question"
    IMPROVEMENT = "improvement"


class Priority(Enum):
    """Task priority level."""
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"


class DeadlineType(Enum):
    """Deadline type classification."""
    TODAY = "today"
    TOMORROW = "tomorrow"
    END_OF_WEEK = "end_of_week"
    END_OF_NEXT_WEEK = "end_of_next_week"
    SPECIFIC = "specific"
    UNCLEAR = "unclear"


@dataclass
class DeadlineResult:
    """Result of deadline detection."""
    deadline_type: DeadlineType
    deadline_date: Optional[date] = None


@dataclass
class ParsedTask:
    """Structured task parsed from unstructured input."""
    summary: str
    task_type: TaskType = TaskType.FEATURE
    priority: Priority = Priority.NORMAL
    deadline_type: DeadlineType = DeadlineType.UNCLEAR
    deadline_date: Optional[date] = None
    estimated_hours: Optional[float] = None
    assignee_hint: Optional[str] = None
    description: str = ""
    warnings: list[str] = field(default_factory=list)
    source_type: str = "comment"

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "summary": self.summary,
            "task_type": self.task_type.value,
            "priority": self.priority.value,
            "deadline_type": self.deadline_type.value,
            "deadline_date": self.deadline_date.isoformat() if self.deadline_date else None,
            "estimated_hours": self.estimated_hours,
            "assignee_hint": self.assignee_hint,
            "description": self.description,
            "warnings": self.warnings,
            "source_type": self.source_type,
        }

    def to_markdown(self) -> str:
        """Generate markdown preview for user confirmation (CLI)."""
        lines = ["## Parsed Task", ""]
        lines.append(f"**Summary:** {self.summary}")
        lines.append(f"**Type:** {self.task_type.value.capitalize()}")
        lines.append(f"**Priority:** {self.priority.value.capitalize()}")

        if self.assignee_hint:
            lines.append(f"**Assignee:** {self.assignee_hint} (suggested)")

        if self.deadline_date:
            lines.append(f"**Due Date:** {self.deadline_date.isoformat()}")
        elif self.deadline_type != DeadlineType.UNCLEAR:
            lines.append(f"**Due Date:** {self.deadline_type.value.replace('_', ' ').title()}")

        if self.estimated_hours:
            lines.append(f"**Estimate:** {self.estimated_hours}h")

        if self.description:
            lines.append("")
            lines.append("**Description:**")
            lines.append(self.description)

        if self.warnings:
            lines.append("")
            lines.append("**Warnings:**")
            for w in self.warnings:
                lines.append(f"- {w}")

        lines.append("")
        lines.append("**Create on Backlog?** [Yes] [No] [Edit first]")

        return "\n".join(lines)

    def to_backlog_description(self) -> str:
        """Generate bilingual description using template for Backlog issue.

        Uses templates from ../templates/ directory based on task_type.
        Falls back to simple format if template not found.
        """
        try:
            from template_loader import render_template
        except ImportError:
            # Fallback for different import contexts
            import sys
            from pathlib import Path
            sys.path.insert(0, str(Path(__file__).parent))
            from template_loader import render_template

        # Build template variables
        template_vars = {
            "summary": self.summary,
            "summary_vn": self.summary,  # TODO: split VN/JA if available
            "summary_ja": self.summary,
            "description": self.description,
            "description_vn": self.description,
            "description_ja": "",
            "assignee": self.assignee_hint or "",
            "due_date": self.deadline_date.isoformat() if self.deadline_date else "",
            "estimate": f"{self.estimated_hours}h" if self.estimated_hours else "",
            "priority": self.priority.value.capitalize(),
        }

        return render_template(self.task_type.value, **template_vars)


class TaskParser:
    """Parse unstructured Japanese text into structured tasks."""

    # Task type keywords (order matters for detection priority)
    # Question keywords need to be specific to avoid matching "ご確認ください" in emails
    QUESTION_KEYWORDS = [
        "質問", "確認したい", "問い合わせ", "？", "question", "わからない", "教えて"
    ]
    BUG_KEYWORDS = [
        "不具合", "バグ", "エラー", "修正", "bug", "error", "fix",
        "障害", "消失", "動かない", "反応しない", "反応しません", "表示されない"
    ]
    FEATURE_KEYWORDS = [
        "機能追加", "実装", "新規", "作成", "追加", "開発",
        "feature", "implement", "create", "画面"
    ]
    IMPROVEMENT_KEYWORDS = [
        "改善", "最適化", "リファクタ", "向上", "enhance", "improve", "optimize"
    ]

    # Priority keywords
    HIGH_PRIORITY_KEYWORDS = [
        "至急", "緊急", "即時", "ASAP", "urgent", "asap", "即座", "今すぐ"
    ]
    LOW_PRIORITY_KEYWORDS = [
        "時間あれば", "余裕があれば", "余裕あれば", "できれば早めに", "できれば"
    ]

    # Deadline patterns
    TODAY_KEYWORDS = ["本日", "今日", "至急", "緊急", "即時", "ASAP"]
    TOMORROW_KEYWORDS = ["明日まで", "明日中"]
    END_OF_WEEK_KEYWORDS = ["今週中", "今週まで", "週末まで"]
    END_OF_NEXT_WEEK_KEYWORDS = ["来週まで", "来週中"]

    def detect_task_type(self, text: str) -> TaskType:
        """Detect task type from keywords in text.

        Order: BUG > QUESTION > IMPROVEMENT > FEATURE
        Bug detection takes priority because error reports are critical.
        """
        text_lower = text.lower()

        # Check bug keywords FIRST (highest priority for error reports)
        for kw in self.BUG_KEYWORDS:
            if kw.lower() in text_lower:
                return TaskType.BUG

        # Check question keywords
        for kw in self.QUESTION_KEYWORDS:
            if kw.lower() in text_lower:
                return TaskType.QUESTION

        # Check improvement keywords
        for kw in self.IMPROVEMENT_KEYWORDS:
            if kw.lower() in text_lower:
                return TaskType.IMPROVEMENT

        # Check feature keywords
        for kw in self.FEATURE_KEYWORDS:
            if kw.lower() in text_lower:
                return TaskType.FEATURE

        # Default to feature
        return TaskType.FEATURE

    def detect_priority(self, text: str) -> Priority:
        """Detect priority from keywords in text."""
        text_lower = text.lower()

        for kw in self.HIGH_PRIORITY_KEYWORDS:
            if kw.lower() in text_lower:
                return Priority.HIGH

        for kw in self.LOW_PRIORITY_KEYWORDS:
            if kw in text_lower:
                return Priority.LOW

        return Priority.NORMAL

    def detect_deadline(self, text: str) -> DeadlineResult:
        """Detect deadline from text."""
        today = date.today()

        # Check for specific date patterns first
        # Pattern: 2026年2月15日 or 2026/2/15
        specific_date = self._parse_specific_date(text, today)
        if specific_date:
            return DeadlineResult(DeadlineType.SPECIFIC, specific_date)

        # Check keyword-based deadlines
        for kw in self.TODAY_KEYWORDS:
            if kw in text:
                return DeadlineResult(DeadlineType.TODAY, today)

        for kw in self.TOMORROW_KEYWORDS:
            if kw in text:
                return DeadlineResult(DeadlineType.TOMORROW, today + timedelta(days=1))

        for kw in self.END_OF_WEEK_KEYWORDS:
            if kw in text:
                # Calculate days until Friday (weekday 4)
                days_until_friday = (4 - today.weekday()) % 7
                if days_until_friday == 0 and today.weekday() == 4:
                    days_until_friday = 0  # Already Friday
                friday = today + timedelta(days=days_until_friday)
                return DeadlineResult(DeadlineType.END_OF_WEEK, friday)

        for kw in self.END_OF_NEXT_WEEK_KEYWORDS:
            if kw in text:
                # Calculate days until next Friday
                days_until_friday = (4 - today.weekday()) % 7
                if days_until_friday == 0:
                    days_until_friday = 7
                next_friday = today + timedelta(days=days_until_friday + 7)
                return DeadlineResult(DeadlineType.END_OF_NEXT_WEEK, next_friday)

        return DeadlineResult(DeadlineType.UNCLEAR)

    def _parse_specific_date(self, text: str, today: date) -> Optional[date]:
        """Parse specific date from text."""
        # Pattern: 2026年2月15日
        match = re.search(r'(\d{4})年(\d{1,2})月(\d{1,2})日?', text)
        if match:
            year, month, day = int(match.group(1)), int(match.group(2)), int(match.group(3))
            try:
                return date(year, month, day)
            except ValueError:
                pass

        # Pattern: 2026/2/15 or 2026-2-15
        match = re.search(r'(\d{4})[/\-](\d{1,2})[/\-](\d{1,2})', text)
        if match:
            year, month, day = int(match.group(1)), int(match.group(2)), int(match.group(3))
            try:
                return date(year, month, day)
            except ValueError:
                pass

        # Pattern: 1月30日 (no year - infer current/next year)
        match = re.search(r'(\d{1,2})月(\d{1,2})日', text)
        if match:
            month, day = int(match.group(1)), int(match.group(2))
            try:
                target = date(today.year, month, day)
                # If date is in the past, use next year
                if target < today:
                    target = date(today.year + 1, month, day)
                return target
            except ValueError:
                pass

        # Pattern: 1/30 or 1/30まで
        match = re.search(r'(\d{1,2})/(\d{1,2})(?:まで)?', text)
        if match:
            month, day = int(match.group(1)), int(match.group(2))
            try:
                target = date(today.year, month, day)
                if target < today:
                    target = date(today.year + 1, month, day)
                return target
            except ValueError:
                pass

        return None

    def extract_estimated_hours(self, text: str) -> Optional[float]:
        """Extract estimated hours from text."""
        # Pattern: 8時間 or 2.5時間
        match = re.search(r'(\d+(?:\.\d+)?)\s*時間', text)
        if match:
            return float(match.group(1))

        # Pattern: 4h or 2.5h
        match = re.search(r'(\d+(?:\.\d+)?)\s*h\b', text, re.IGNORECASE)
        if match:
            return float(match.group(1))

        return None

    def extract_assignee_hint(self, text: str) -> Optional[str]:
        """Extract assignee hint from text."""
        # Pattern: 田中さん or 山田くん - only match Kanji names (1-5 chars) before honorifics
        # This avoids matching particles like に、を、が before the name
        # \u4e00-\u9fff: CJK Unified Ideographs (Kanji only for names)
        match = re.search(r'([\u4e00-\u9fff]{1,5})(さん|くん|君|氏)', text)
        if match:
            return match.group(1)

        # Pattern: 田中が担当 or 田中に (when followed by action verb context)
        match = re.search(r'([\u4e00-\u9fff]{1,5})(が担当|にお願い|が作成|が対応)', text)
        if match:
            return match.group(1)

        return None

    def generate_summary(self, text: str, max_length: int = 50) -> str:
        """Generate a concise summary from text."""
        # Remove common prefixes
        text = re.sub(r'^(お世話になっております。?|いつもお世話になっております。?)', '', text)
        text = re.sub(r'^(件名[:：].*?\n)', '', text)

        # Remove date/time patterns
        text = re.sub(r'\d{4}[年/\-]\d{1,2}[月/\-]\d{1,2}日?', '', text)
        text = re.sub(r'\d{1,2}[:/]\d{2}', '', text)

        # Remove assignee patterns (proper Unicode ranges)
        text = re.sub(r'[\u4e00-\u9fff\u3040-\u309f\u30a0-\u30ff]+(さん|くん|君|氏)(が|に|を)', '', text)

        # Remove time estimates
        text = re.sub(r'\d+(?:\.\d+)?\s*(時間|h)\b', '', text, flags=re.IGNORECASE)

        # Remove deadline keywords
        for kw in self.TODAY_KEYWORDS + self.TOMORROW_KEYWORDS + self.END_OF_WEEK_KEYWORDS:
            text = text.replace(kw, '')

        # Clean up whitespace and punctuation
        text = re.sub(r'\s+', ' ', text).strip()
        text = re.sub(r'^[。、\s]+', '', text)
        text = re.sub(r'[。、\s]+$', '', text)

        # Extract first meaningful sentence/phrase
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if line and len(line) >= 5:
                # Truncate if too long
                if len(line) > max_length:
                    line = line[:max_length-3] + "..."
                return line

        # Fallback: return truncated original
        if len(text) > max_length:
            return text[:max_length-3] + "..."
        return text or "タスク"

    def parse(self, text: str, source_type: str = "comment") -> ParsedTask:
        """Parse unstructured text into a structured task."""
        task_type = self.detect_task_type(text)
        priority = self.detect_priority(text)
        deadline_result = self.detect_deadline(text)
        estimated_hours = self.extract_estimated_hours(text)
        assignee_hint = self.extract_assignee_hint(text)
        summary = self.generate_summary(text)

        warnings = []
        if deadline_result.deadline_type == DeadlineType.UNCLEAR:
            warnings.append("deadline_unclear")

        # High priority keywords should set today deadline
        if priority == Priority.HIGH and deadline_result.deadline_type == DeadlineType.UNCLEAR:
            deadline_result = DeadlineResult(DeadlineType.TODAY, date.today())

        # Extract description (keep original text with some cleanup)
        description = self._extract_description(text, source_type)

        return ParsedTask(
            summary=summary,
            task_type=task_type,
            priority=priority,
            deadline_type=deadline_result.deadline_type,
            deadline_date=deadline_result.deadline_date,
            estimated_hours=estimated_hours,
            assignee_hint=assignee_hint,
            description=description,
            warnings=warnings,
            source_type=source_type,
        )

    def _extract_description(self, text: str, source_type: str) -> str:
        """Extract and format description based on source type."""
        if source_type == "email":
            # Keep most of the email content
            lines = text.split('\n')
            # Skip subject line if present
            if lines and lines[0].startswith("件名"):
                lines = lines[1:]
            return '\n'.join(line.strip() for line in lines if line.strip())

        if source_type == "minutes":
            # Extract action items section
            return text

        # Default: clean up and return
        return text.strip()


def parse_task(text: str, source_type: str = "comment") -> ParsedTask:
    """Convenience function to parse a single task."""
    parser = TaskParser()
    return parser.parse(text, source_type)


def parse_multiple_tasks(text: str, source_type: str = "comment") -> list[ParsedTask]:
    """Parse multiple tasks from bullet list or minutes."""
    parser = TaskParser()
    tasks = []

    # Detect bullet list patterns
    bullet_patterns = [
        r'^[・•\-\*]\s*(.+)$',  # Japanese/English bullets
        r'^\d+[\.）\)]\s*(.+)$',  # Numbered list
    ]

    lines = text.split('\n')

    # Check for meeting minutes 宿題 section
    if source_type == "minutes" or "宿題" in text:
        tasks.extend(_parse_minutes_tasks(lines, parser))
        if tasks:
            return tasks

    # Parse bullet list
    for line in lines:
        line = line.strip()
        for pattern in bullet_patterns:
            match = re.match(pattern, line)
            if match:
                item_text = match.group(1).strip()
                if len(item_text) >= 3:  # Skip very short items
                    task = parser.parse(item_text, source_type)
                    tasks.append(task)
                break

    # If no bullets found, try to parse as single task
    if not tasks:
        tasks.append(parser.parse(text, source_type))

    return tasks


def _parse_minutes_tasks(lines: list[str], parser: TaskParser) -> list[ParsedTask]:
    """Parse tasks from meeting minutes format."""
    tasks = []
    in_homework_section = False

    for line in lines:
        line = line.strip()

        # Detect 宿題 section
        if "宿題" in line or "アクション" in line:
            in_homework_section = True
            continue

        # End of section markers
        if line.startswith("■") and in_homework_section:
            in_homework_section = False
            continue

        if not in_homework_section:
            continue

        # Parse homework items: ・田中：ログイン機能の仕様書作成（1/30まで）
        match = re.match(r'^[・•\-]\s*([^：:]+)[：:]\s*(.+)$', line)
        if match:
            assignee = match.group(1).strip()
            task_text = match.group(2).strip()

            task = parser.parse(task_text, source_type="minutes")
            task.assignee_hint = assignee
            tasks.append(task)

    return tasks
