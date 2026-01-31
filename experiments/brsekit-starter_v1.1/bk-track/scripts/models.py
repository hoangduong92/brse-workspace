"""Data models for bk-track skill.

Re-exports models from common/backlog for consistency.
"""

import sys
from dataclasses import dataclass
from pathlib import Path

# Add common to path
_common_dir = Path(__file__).parent.parent.parent / "common"
if str(_common_dir) not in sys.path:
    sys.path.insert(0, str(_common_dir))

# Re-export all models from common
from backlog.models import (
    RiskLevel,
    User,
    Status,
    Project,
    Issue,
)


@dataclass
class TaskStatus:
    """Task with status tracking (flat structure for reporting)."""
    issue_key: str
    summary: str
    status: str
    assignee: str = None
    due_date: str = None
    days_late: int = 0
    risk_level: str = "low"


@dataclass
class MemberLoad:
    """Member workload data (flat structure for reporting)."""
    name: str
    total_tasks: int
    completed: int
    in_progress: int
    overdue: int


@dataclass
class ProjectHealth:
    """Project health summary."""
    total_issues: int
    completed: int
    in_progress: int
    late_count: int
    at_risk_count: int = 0
    health_score: float = 0.0


@dataclass
class ReportData:
    """Weekly report data container."""
    project_name: str
    date_range: str
    health: ProjectHealth
    completed_tasks: list
    in_progress_tasks: list
    late_tasks: list
    member_loads: list
    at_risk_tasks: list = None
    next_week_tasks: list = None
    metrics: dict = None


__all__ = [
    "RiskLevel",
    "User",
    "Status",
    "Project",
    "Issue",
    "TaskStatus",
    "MemberLoad",
    "ProjectHealth",
    "ReportData",
]
