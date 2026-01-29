"""Generate meeting minutes document in Markdown format.

Output format follows standard Japanese business meeting minutes template.
"""

from datetime import date
from typing import Optional

from models import MeetingMinutes, MeetingItem, ItemCategory


class MMGenerator:
    """Generate meeting minutes Markdown document."""

    def generate(self, minutes: MeetingMinutes, title: Optional[str] = None) -> str:
        """Generate full meeting minutes document.

        Args:
            minutes: Parsed meeting minutes data
            title: Optional custom title

        Returns:
            Markdown formatted meeting minutes
        """
        sections = []

        # Title
        meeting_date = minutes.info.date or date.today()
        title = title or f"Meeting Minutes - {meeting_date.isoformat()}"
        sections.append(f"# {title}\n")

        # Basic info
        sections.append(self._generate_info_section(minutes))

        # Agenda
        if minutes.info.agenda:
            sections.append(self._generate_agenda_section(minutes.info.agenda))

        # Decisions
        if minutes.decisions:
            sections.append(self._generate_decisions_section(minutes.decisions))

        # Tasks
        if minutes.tasks:
            sections.append(self._generate_items_section(
                "📋 TASKS", minutes.tasks
            ))

        # Issues
        if minutes.issues:
            sections.append(self._generate_items_section(
                "🐛 ISSUES", minutes.issues
            ))

        # Risks
        if minutes.risks:
            sections.append(self._generate_items_section(
                "⚠️ RISKS", minutes.risks
            ))

        # Questions
        if minutes.questions:
            sections.append(self._generate_items_section(
                "❓ NEED CONFIRMATION", minutes.questions
            ))

        # Summary
        sections.append(self._generate_summary(minutes))

        return "\n".join(sections)

    def _generate_info_section(self, minutes: MeetingMinutes) -> str:
        """Generate basic meeting info section."""
        lines = ["## 基本情報 / Basic Info\n"]

        if minutes.info.date:
            lines.append(f"- **Date:** {minutes.info.date.isoformat()}")

        if minutes.info.duration_minutes:
            lines.append(f"- **Duration:** {minutes.info.duration_minutes} min")

        if minutes.info.participants:
            participants = ", ".join(minutes.info.participants)
            lines.append(f"- **Participants:** {participants}")

        lines.append("")
        return "\n".join(lines)

    def _generate_agenda_section(self, agenda: list[str]) -> str:
        """Generate agenda section."""
        lines = ["## アジェンダ / Agenda\n"]
        for i, item in enumerate(agenda, 1):
            lines.append(f"{i}. {item}")
        lines.append("")
        return "\n".join(lines)

    def _generate_decisions_section(self, decisions: list[str]) -> str:
        """Generate decisions section."""
        lines = ["## 決定事項 / Decisions\n"]
        for decision in decisions:
            lines.append(f"- [x] {decision}")
        lines.append("")
        return "\n".join(lines)

    def _generate_items_section(
        self,
        header: str,
        items: list[MeetingItem]
    ) -> str:
        """Generate items section with table format."""
        lines = [f"## {header} ({len(items)})\n"]

        # Different table format based on category
        if items and items[0].category == ItemCategory.TASK:
            lines.append("| # | Description | Assignee | Priority |")
            lines.append("|---|-------------|----------|----------|")
            for i, item in enumerate(items, 1):
                assignee = item.assignee or "-"
                priority = item.priority.value.capitalize()
                lines.append(f"| {i} | {item.description} | {assignee} | {priority} |")

        elif items and items[0].category == ItemCategory.ISSUE:
            lines.append("| # | Description | Priority |")
            lines.append("|---|-------------|----------|")
            for i, item in enumerate(items, 1):
                priority = item.priority.value.capitalize()
                lines.append(f"| {i} | {item.description} | {priority} |")

        elif items and items[0].category == ItemCategory.RISK:
            lines.append("| # | Description | Priority | Mitigation |")
            lines.append("|---|-------------|----------|------------|")
            for i, item in enumerate(items, 1):
                priority = item.priority.value.capitalize()
                lines.append(f"| {i} | {item.description} | {priority} | - |")

        elif items and items[0].category == ItemCategory.QUESTION:
            lines.append("| # | Question | Ask to |")
            lines.append("|---|----------|--------|")
            for i, item in enumerate(items, 1):
                assignee = item.assignee or "-"
                lines.append(f"| {i} | {item.description} | {assignee} |")

        lines.append("")
        return "\n".join(lines)

    def _generate_summary(self, minutes: MeetingMinutes) -> str:
        """Generate summary section."""
        counts = minutes.item_count()
        total = sum(counts.values())

        lines = ["## Summary\n"]
        lines.append(f"- **Total items:** {total}")
        lines.append(f"  - Tasks: {counts['tasks']}")
        lines.append(f"  - Issues: {counts['issues']}")
        lines.append(f"  - Risks: {counts['risks']}")
        lines.append(f"  - Questions: {counts['questions']}")
        lines.append("")

        # Next steps
        lines.append("## Next Steps\n")
        if counts['questions'] > 0:
            lines.append("- [ ] Follow up on NEED CONFIRMATION items")
        if counts['tasks'] > 0:
            lines.append("- [ ] Create Backlog tasks for approved TASKS")
        if counts['issues'] > 0:
            lines.append("- [ ] Address ISSUES by priority")
        if counts['risks'] > 0:
            lines.append("- [ ] Define mitigation plans for RISKS")

        lines.append("")
        return "\n".join(lines)

    def generate_preview(self, minutes: MeetingMinutes) -> str:
        """Generate short preview for confirmation."""
        lines = ["## Preview\n"]

        counts = minutes.item_count()
        lines.append(f"Found {sum(counts.values())} items:\n")

        if counts['tasks'] > 0:
            lines.append(f"- 📋 Tasks: {counts['tasks']}")
        if counts['issues'] > 0:
            lines.append(f"- 🐛 Issues: {counts['issues']}")
        if counts['risks'] > 0:
            lines.append(f"- ⚠️ Risks: {counts['risks']}")
        if counts['questions'] > 0:
            lines.append(f"- ❓ Questions: {counts['questions']}")

        lines.append("")
        return "\n".join(lines)


def generate_minutes(minutes: MeetingMinutes, title: Optional[str] = None) -> str:
    """Convenience function to generate meeting minutes."""
    generator = MMGenerator()
    return generator.generate(minutes, title)
