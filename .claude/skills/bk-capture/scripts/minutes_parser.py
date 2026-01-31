"""Meeting minutes parser for bk-capture."""
import re
from datetime import date
from typing import Optional
from classifiers import PMClassifier, PriorityDetector


class MinutesParser:
    """Parse meeting transcripts into structured minutes."""

    def __init__(self):
        self.classifier = PMClassifier()
        self.priority_detector = PriorityDetector()

    def parse(self, transcript: str) -> dict:
        """Parse transcript into minutes structure.

        Args:
            transcript: Raw meeting transcript

        Returns:
            {
                title: str,
                date: str,
                attendees: list[str],
                agenda: list[str],
                discussion: list[dict],
                action_items: list[dict],
                next_meeting: str | None
            }
        """
        lines = [line.strip() for line in transcript.split("\n") if line.strip()]

        # Extract components
        title = self.extract_title(lines)
        meeting_date = self.extract_date(transcript)
        attendees = self.extract_attendees(transcript)
        agenda = self.extract_agenda(lines)
        discussion = self.extract_discussion(lines)
        action_items = self.extract_action_items(transcript)
        next_meeting = self.extract_next_meeting(transcript)

        return {
            "title": title,
            "date": meeting_date,
            "attendees": attendees,
            "agenda": agenda,
            "discussion": discussion,
            "action_items": action_items,
            "next_meeting": next_meeting
        }

    def extract_title(self, lines: list[str]) -> str:
        """Extract meeting title from first meaningful line."""
        for line in lines:
            # Skip empty lines and common headers
            if len(line) < 5:
                continue
            if line.lower().startswith(("date:", "attendees:", "参加者:")):
                continue
            return line

        return "Meeting Minutes"

    def extract_date(self, text: str) -> str:
        """Extract meeting date from text."""
        # Look for date patterns: YYYY/MM/DD, MM/DD, etc.
        date_match = re.search(r"(\d{4})[/-](\d{1,2})[/-](\d{1,2})", text)
        if date_match:
            return f"{date_match.group(1)}-{date_match.group(2).zfill(2)}-{date_match.group(3).zfill(2)}"

        # Fallback to today
        return date.today().isoformat()

    def extract_attendees(self, text: str) -> list[str]:
        """Extract attendee names from text.

        Looks for patterns like:
        - Attendees: A, B, C
        - 参加者: A, B, C
        - @username mentions
        """
        attendees = []

        # Pattern 1: Attendees: A, B, C (only from header, not action items)
        lines = text.split("\n")
        for i, line in enumerate(lines[:10]):  # Check only first 10 lines
            attendee_match = re.search(r"(?:Attendees|参加者)[:：]\s*(.+)", line, re.IGNORECASE)
            if attendee_match:
                names = attendee_match.group(1).split(",")
                for n in names:
                    # Remove @ prefix if present
                    clean_name = n.strip().lstrip("@")
                    attendees.append(clean_name)
                break

        # Remove duplicates while preserving order
        seen = set()
        unique_attendees = []
        for a in attendees:
            if a not in seen:
                seen.add(a)
                unique_attendees.append(a)

        return unique_attendees

    def extract_agenda(self, lines: list[str]) -> list[str]:
        """Extract agenda items from lines."""
        agenda = []
        in_agenda_section = False

        for line in lines:
            # Detect agenda section start
            if re.match(r"^(?:Agenda|議題|アジェンダ)[:：]?$", line, re.IGNORECASE):
                in_agenda_section = True
                continue

            # Detect agenda section end
            if in_agenda_section and re.match(r"^(?:Discussion|Discussion Points|議論)[:：]?$", line, re.IGNORECASE):
                break

            # Collect agenda items (numbered or bulleted)
            if in_agenda_section:
                # Remove bullet/number prefix
                clean_line = re.sub(r"^[\d\.\-\*•・]+\s*", "", line).strip()
                if clean_line:
                    agenda.append(clean_line)

        return agenda

    def extract_discussion(self, lines: list[str]) -> list[dict]:
        """Extract discussion points with speaker if available."""
        discussion = []

        for line in lines:
            # Speaker pattern: "Name: discussion point" or "Name said: ..."
            speaker_match = re.match(r"^(\w+)[:：]\s*(.+)", line)
            if speaker_match:
                discussion.append({
                    "speaker": speaker_match.group(1),
                    "content": speaker_match.group(2)
                })
            elif len(line) > 10 and not re.match(r"^(?:Agenda|Attendees|Action|Next)[:：]", line, re.IGNORECASE):
                discussion.append({
                    "speaker": None,
                    "content": line
                })

        return discussion

    def extract_action_items(self, text: str) -> list[dict]:
        """Extract action items with assignees and deadlines."""
        action_items = []
        lines = text.split("\n")

        in_action_section = False
        for line in lines:
            line = line.strip()

            # Detect action items section
            if re.match(r"^(?:Action Items|Actions|TODO|タスク)[:：]?$", line, re.IGNORECASE):
                in_action_section = True
                continue

            # Stop at next section
            if in_action_section and re.match(r"^(?:Next Meeting|次回|Conclusion).*[:：]", line, re.IGNORECASE):
                break

            # Extract action items
            if in_action_section and line:
                # Skip section header lines
                if re.match(r"^[\-\*•・]+\s*$", line):  # Just bullet markers
                    continue

                priority, deadline = self.priority_detector.detect(line)
                assignee = self._extract_assignee_from_line(line)

                # Clean action text
                action_text = re.sub(r"@\w+", "", line)
                action_text = re.sub(r"担当[:：]\s*\w+", "", action_text)
                action_text = re.sub(r"^[\d\.\-\*•・]+\s*", "", action_text).strip()

                # Skip empty after cleaning
                if not action_text:
                    continue

                action_items.append({
                    "action": action_text,
                    "assignee": assignee,
                    "priority": priority.value,
                    "deadline": deadline.isoformat() if deadline else None
                })

        return action_items

    def extract_next_meeting(self, text: str) -> Optional[str]:
        """Extract next meeting date if mentioned."""
        # Pattern: "Next meeting: YYYY/MM/DD"
        next_match = re.search(r"(?:Next Meeting|次回)[:：]\s*(\d{4}[/-]\d{1,2}[/-]\d{1,2})", text, re.IGNORECASE)
        if next_match:
            return next_match.group(1)

        return None

    def _extract_assignee_from_line(self, line: str) -> Optional[str]:
        """Extract assignee from action item line."""
        # @username
        at_match = re.search(r"@(\w+)", line)
        if at_match:
            return at_match.group(1)

        # 担当: Name
        ja_match = re.search(r"担当[:：]\s*(\w+)", line)
        if ja_match:
            return ja_match.group(1)

        return None

    def format_markdown(self, minutes: dict) -> str:
        """Format minutes as markdown document.

        Args:
            minutes: Parsed minutes dict

        Returns:
            Markdown formatted minutes
        """
        md = []

        # Title and metadata
        md.append(f"# {minutes['title']}\n")
        md.append(f"**Date:** {minutes['date']}\n")

        # Attendees
        if minutes['attendees']:
            md.append(f"**Attendees:** {', '.join(minutes['attendees'])}\n")

        # Agenda
        if minutes['agenda']:
            md.append("\n## Agenda\n")
            for i, item in enumerate(minutes['agenda'], 1):
                md.append(f"{i}. {item}")
            md.append("")

        # Discussion
        if minutes['discussion']:
            md.append("\n## Discussion\n")
            for point in minutes['discussion']:
                if point['speaker']:
                    md.append(f"**{point['speaker']}:** {point['content']}")
                else:
                    md.append(f"- {point['content']}")
            md.append("")

        # Action Items
        if minutes['action_items']:
            md.append("\n## Action Items\n")
            for item in minutes['action_items']:
                assignee = f" (@{item['assignee']})" if item['assignee'] else ""
                deadline = f" [Due: {item['deadline']}]" if item['deadline'] else ""
                priority = f" **[{item['priority'].upper()}]**" if item['priority'] == "high" else ""
                md.append(f"- {item['action']}{assignee}{deadline}{priority}")
            md.append("")

        # Next Meeting
        if minutes['next_meeting']:
            md.append(f"\n**Next Meeting:** {minutes['next_meeting']}\n")

        return "\n".join(md)
