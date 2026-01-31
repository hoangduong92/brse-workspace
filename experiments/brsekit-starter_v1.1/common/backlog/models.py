"""Data models for Backlog API integration.

Shared dataclasses for BrseKit skills:
- User: Backlog user/member
- Status: Issue status
- Project: Backlog project
- Issue: Backlog issue with tracking fields
- RiskLevel: Task deadline risk assessment
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class RiskLevel(Enum):
    """Risk level for task deadline assessment."""
    ON_TRACK = "on_track"
    AT_RISK = "at_risk"
    LATE = "late"


@dataclass
class User:
    """Represents a Backlog user/member."""
    id: int
    user_id: str
    name: str
    role_type: int = 1
    email: str = ""

    @classmethod
    def from_dict(cls, data: dict) -> "User":
        return cls(
            id=data["id"],
            user_id=data.get("userId", ""),
            name=data["name"],
            role_type=data.get("roleType", 1),
            email=data.get("mailAddress", "")
        )


@dataclass
class Status:
    """Represents a Backlog status."""
    id: int
    name: str
    project_id: int = 0
    display_order: int = 0

    @classmethod
    def from_dict(cls, data: dict) -> "Status":
        return cls(
            id=data["id"],
            name=data["name"],
            project_id=data.get("projectId", 0),
            display_order=data.get("displayOrder", 0)
        )


@dataclass
class Project:
    """Represents a Backlog project."""
    id: int
    project_key: str
    name: str

    @classmethod
    def from_dict(cls, data: dict) -> "Project":
        return cls(
            id=data["id"],
            project_key=data["projectKey"],
            name=data["name"]
        )


@dataclass
class Issue:
    """Represents a Backlog issue with dueDate and hours tracking."""
    id: int
    project_id: int
    key_id: str
    summary: str
    description: str
    issue_type_id: int
    priority_id: int
    status_id: int
    assignee_id: Optional[int] = None
    start_date: Optional[str] = None  # yyyy-MM-dd format
    due_date: Optional[str] = None  # yyyy-MM-dd format
    estimated_hours: Optional[float] = None
    actual_hours: Optional[float] = None
    created: str = ""
    updated: str = ""

    @classmethod
    def from_dict(cls, data: dict) -> "Issue":
        return cls(
            id=data["id"],
            project_id=data["projectId"],
            key_id=data.get("issueKey", ""),
            summary=data["summary"],
            description=data.get("description", ""),
            issue_type_id=data["issueType"]["id"],
            priority_id=data["priority"]["id"],
            status_id=data["status"]["id"],
            assignee_id=data.get("assignee", {}).get("id") if data.get("assignee") else None,
            start_date=data.get("startDate"),
            due_date=data.get("dueDate"),
            estimated_hours=data.get("estimatedHours"),
            actual_hours=data.get("actualHours"),
            created=data.get("created", ""),
            updated=data.get("updated", "")
        )
