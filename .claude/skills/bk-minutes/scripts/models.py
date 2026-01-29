"""Data models for meeting minutes items.

Supports classification into:
- Task: Action items with assignee and deadline
- Issue: Bugs, problems that need fixing
- Risk: Potential problems, concerns
- Question: Items needing confirmation
"""

from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from typing import Optional


class ItemCategory(Enum):
    """Meeting item category classification."""
    TASK = "task"
    ISSUE = "issue"
    RISK = "risk"
    QUESTION = "question"


class Priority(Enum):
    """Item priority level."""
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"


@dataclass
class MeetingItem:
    """A classified item from meeting minutes."""
    description: str
    category: ItemCategory
    priority: Priority = Priority.NORMAL
    assignee: Optional[str] = None
    deadline: Optional[date] = None
    source_text: str = ""

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "description": self.description,
            "category": self.category.value,
            "priority": self.priority.value,
            "assignee": self.assignee,
            "deadline": self.deadline.isoformat() if self.deadline else None,
            "source_text": self.source_text,
        }


@dataclass
class MeetingInfo:
    """Basic meeting information."""
    date: Optional[date] = None
    duration_minutes: Optional[int] = None
    participants: list[str] = field(default_factory=list)
    agenda: list[str] = field(default_factory=list)


@dataclass
class MeetingMinutes:
    """Complete meeting minutes document."""
    info: MeetingInfo
    decisions: list[str] = field(default_factory=list)
    tasks: list[MeetingItem] = field(default_factory=list)
    issues: list[MeetingItem] = field(default_factory=list)
    risks: list[MeetingItem] = field(default_factory=list)
    questions: list[MeetingItem] = field(default_factory=list)
    next_steps: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "info": {
                "date": self.info.date.isoformat() if self.info.date else None,
                "duration_minutes": self.info.duration_minutes,
                "participants": self.info.participants,
                "agenda": self.info.agenda,
            },
            "decisions": self.decisions,
            "tasks": [t.to_dict() for t in self.tasks],
            "issues": [i.to_dict() for i in self.issues],
            "risks": [r.to_dict() for r in self.risks],
            "questions": [q.to_dict() for q in self.questions],
            "next_steps": self.next_steps,
        }

    def item_count(self) -> dict:
        """Get count of each item type."""
        return {
            "tasks": len(self.tasks),
            "issues": len(self.issues),
            "risks": len(self.risks),
            "questions": len(self.questions),
        }
