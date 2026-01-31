"""Task parser for bk-capture - parse unstructured text to tasks."""
import re
from datetime import date
from typing import Optional
from classifiers import PMClassifier, PriorityDetector, Priority


class TaskParser:
    """Parse unstructured Japanese/Vietnamese/English text into structured tasks."""

    def __init__(self):
        self.classifier = PMClassifier()
        self.priority_detector = PriorityDetector()

        # Task keywords for extraction
        self.keywords_ja = ["タスク", "対応", "依頼", "作業", "実装", "修正", "確認", "調査"]
        self.keywords_vi = ["task", "việc", "công việc", "xử lý", "yêu cầu", "thực hiện"]
        self.keywords_en = ["task", "todo", "action", "implement", "fix", "create"]

        # Bullet point markers
        self.bullet_markers = ["-", "•", "*", "・", "◦", "○", "□"]

    def parse(self, text: str) -> list[dict]:
        """Parse text into task items.

        Args:
            text: Unstructured text with tasks

        Returns:
            List of task dicts with keys: title, description, priority, deadline, assignee
        """
        tasks = []
        lines = self._split_into_lines(text)

        for line in lines:
            if not line or len(line) < 3:
                continue

            # Extract task info
            title = self.extract_title(line)
            if not title:
                continue

            priority, deadline = self.priority_detector.detect(line)
            assignee = self.detect_assignee(line)

            tasks.append({
                "title": title,
                "description": line,
                "priority": priority.value,
                "deadline": deadline.isoformat() if deadline else None,
                "assignee": assignee
            })

        return tasks

    def _split_into_lines(self, text: str) -> list[str]:
        """Split text into task lines.

        Handles:
        - Newlines
        - Bullet points
        - Numbered lists (1., 2., etc.)
        """
        lines = []

        # Split by newlines first
        for line in text.split("\n"):
            line = line.strip()
            if not line:
                continue

            # Remove bullet markers
            for marker in self.bullet_markers:
                if line.startswith(marker):
                    line = line[len(marker):].strip()
                    break

            # Remove numbered list markers (1., 2., etc.)
            numbered = re.match(r"^\d+\.\s*(.+)", line)
            if numbered:
                line = numbered.group(1).strip()

            lines.append(line)

        return lines

    def extract_title(self, line: str) -> str:
        """Extract task title from line.

        Removes priority markers, assignee info, deadline info.
        """
        title = line

        # Remove common prefixes
        prefixes = ["TODO:", "TASK:", "タスク:", "依頼:"]
        for prefix in prefixes:
            if title.startswith(prefix):
                title = title[len(prefix):].strip()

        # Remove assignee pattern (@name, 担当:X, etc.)
        title = re.sub(r"@\w+", "", title)
        title = re.sub(r"担当[:：]\s*\w+", "", title)
        title = re.sub(r"Assignee[:：]\s*\w+", "", title)

        # Remove deadline pattern (MM/DD, YYYY/MM/DD, etc.)
        title = re.sub(r"\d{4}/\d{1,2}/\d{1,2}", "", title)
        title = re.sub(r"\d{1,2}/\d{1,2}", "", title)

        return title.strip()

    def detect_assignee(self, text: str) -> Optional[str]:
        """Detect assignee pattern from text.

        Supports:
        - @username
        - 担当: Name
        - Assignee: Name
        """
        # @username pattern
        at_match = re.search(r"@(\w+)", text)
        if at_match:
            return at_match.group(1)

        # Japanese pattern: 担当: Name
        ja_match = re.search(r"担当[:：]\s*(\w+)", text)
        if ja_match:
            return ja_match.group(1)

        # English pattern: Assignee: Name
        en_match = re.search(r"Assignee[:：]\s*(\w+)", text, re.IGNORECASE)
        if en_match:
            return en_match.group(1)

        return None
