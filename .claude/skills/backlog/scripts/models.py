"""Data models for Nulab Backlog API entities."""

from dataclasses import dataclass, field
from typing import Optional
from enum import Enum


class Language(Enum):
    """Supported languages for translation."""
    JAPANESE = "ja"
    VIETNAMESE = "vi"


class TaskType(Enum):
    """Task types with associated templates."""
    FEATURE_DEV = "feature-dev"
    UPLOAD_SCENARIO = "upload-scenario"
    INVESTIGATE_ISSUE = "investigate-issue"


@dataclass
class Attachment:
    """Represents a Backlog attachment."""
    id: int
    name: str
    size: int
    created: str

    @classmethod
    def from_dict(cls, data: dict) -> "Attachment":
        return cls(
            id=data["id"],
            name=data["name"],
            size=data.get("size", 0),
            created=data.get("created", "")
        )


@dataclass
class Issue:
    """Represents a Backlog issue."""
    id: int
    project_id: int
    key_id: str
    summary: str
    description: str
    issue_type_id: int
    priority_id: int
    status_id: int
    assignee_id: Optional[int] = None
    parent_issue_id: Optional[int] = None
    created: str = ""
    updated: str = ""
    attachments: list[Attachment] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict) -> "Issue":
        attachments = [Attachment.from_dict(a) for a in data.get("attachments", [])]
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
            parent_issue_id=data.get("parentIssueId"),
            created=data.get("created", ""),
            updated=data.get("updated", ""),
            attachments=attachments
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
class Comment:
    """Represents a Backlog comment."""
    id: int
    content: str
    created: str

    @classmethod
    def from_dict(cls, data: dict) -> "Comment":
        return cls(
            id=data["id"],
            content=data.get("content", ""),
            created=data.get("created", "")
        )


@dataclass
class SubtaskTemplate:
    """Template for creating subtasks."""
    subject_template: str
    estimated_hours: float = 0.0
    default_assignee: Optional[int] = None
    assignee_key: Optional[str] = None


@dataclass
class Template:
    """Task template with subtasks and assignee mapping."""
    name: str
    summary_template: str
    description_template: str
    subtasks: list[SubtaskTemplate] = field(default_factory=list)
    default_assignee: Optional[int] = None
    default_priority: str = "normal"
    assignee_mapping: dict[str, int] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict) -> "Template":
        subtasks = [
            SubtaskTemplate(
                subject_template=s["subject_template"],
                estimated_hours=s.get("estimated_hours", 0.0),
                default_assignee=s.get("default_assignee"),
                assignee_key=s.get("assignee_key")
            )
            for s in data.get("subtasks", [])
        ]
        return cls(
            name=data["name"],
            summary_template=data["summary_template"],
            description_template=data["description_template"],
            subtasks=subtasks,
            default_assignee=data.get("default_assignee"),
            default_priority=data.get("default_priority", "normal"),
            assignee_mapping=data.get("assignee_mapping", {})
        )


@dataclass
class Result:
    """Result of ticket creation operation."""
    success: bool
    source_issue: Optional[Issue] = None
    destination_issue: Optional[Issue] = None
    subtasks: list[Issue] = field(default_factory=list)
    attachments_copied: int = 0
    error: Optional[str] = None
    dry_run: bool = False
    data: Optional[dict] = None
