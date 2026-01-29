"""Status analyzer for bk-status skill.

Orchestrates task analysis, member analysis, and report generation.
This is the main entry point for status analysis.
"""

from datetime import date, datetime, timedelta
from typing import Optional, TYPE_CHECKING

# Import modules
import sys
from pathlib import Path
_scripts_dir = Path(__file__).parent
if str(_scripts_dir) not in sys.path:
    sys.path.insert(0, str(_scripts_dir))

from models import RiskLevel
from member_analysis import MemberStatus, get_workload, get_overloaded_members, get_member_progress, analyze_member_capacity
from task_analysis import get_late_tasks, get_at_risk_tasks, assess_task_risk, get_schedule_warnings
from report_generator import generate_report as _generate_report
from gantt_generator import generate_gantt_schedule, generate_gantt_schedule_with_analysis

try:
    from translations import DEFAULT_LANG
except ImportError:
    from .translations import DEFAULT_LANG

# Conditional import for type checking
if TYPE_CHECKING:
    from calendar_utils import CalendarConfig

# Default closed status names (user-validated: only "Closed")
DEFAULT_CLOSED_STATUSES = ["Closed"]


class StatusAnalyzer:
    """Analyzes project status from Backlog issues.

    This class orchestrates various analysis modules and provides
    a unified interface for status analysis.
    """

    def __init__(
        self,
        statuses: list[dict],
        closed_status_names: Optional[list[str]] = None,
        calendar: Optional["CalendarConfig"] = None
    ):
        """Initialize analyzer.

        Args:
            statuses: List of status dicts from API
            closed_status_names: Names considered "closed" (default: ["Closed"])
            calendar: CalendarConfig for working days (optional)
        """
        self.statuses = {s["id"]: s["name"] for s in statuses}
        self.closed_status_names = closed_status_names or DEFAULT_CLOSED_STATUSES
        self.closed_status_ids = {
            sid for sid, name in self.statuses.items()
            if name in self.closed_status_names
        }
        self.calendar = calendar

    # === Helper methods ===

    def _is_closed(self, status_id: int) -> bool:
        """Check if status is considered closed."""
        return status_id in self.closed_status_ids

    def _parse_date(self, date_str: Optional[str]) -> Optional[date]:
        """Parse date string to date object."""
        if not date_str:
            return None
        try:
            if "T" in date_str:
                return datetime.fromisoformat(date_str.replace("Z", "+00:00")).date()
            return date.fromisoformat(date_str)
        except (ValueError, TypeError):
            return None

    def _count_working_days(self, start: date, end: date) -> int:
        """Count working days between two dates (inclusive)."""
        if end < start:
            return 0
        if self.calendar:
            return self.calendar.count_working_days(start, end)
        # Fallback: skip weekends only
        working_days = 0
        current = start
        while current <= end:
            if current.weekday() < 5:
                working_days += 1
            current += timedelta(days=1)
        return working_days

    def _get_status_id(self, issue: dict) -> int:
        """Extract status ID from issue dict."""
        status = issue.get("status", {})
        if isinstance(status, dict):
            return status.get("id", 0)
        return issue.get("status_id", 0)

    def _get_assignee_id(self, issue: dict) -> Optional[int]:
        """Extract assignee ID from issue dict."""
        assignee = issue.get("assignee")
        if isinstance(assignee, dict):
            return assignee.get("id")
        return issue.get("assignee_id")

    def _get_working_days_list(self, start: date, end: date) -> list[date]:
        """Get list of working days between two dates."""
        if end < start:
            return []
        if self.calendar:
            return self.calendar.get_working_days_list(start, end)
        # Fallback: Mon-Fri
        result = []
        current = start
        while current <= end:
            if current.weekday() < 5:
                result.append(current)
            current += timedelta(days=1)
        return result

    # === Public API - delegates to modules ===

    def get_late_tasks(self, issues: list[dict], today: date) -> list[dict]:
        """Get tasks that are past due date but not closed."""
        return get_late_tasks(
            issues, today,
            self._is_closed, self._parse_date, self._get_status_id
        )

    def get_workload(self, issues: list[dict], users: list[dict]) -> dict:
        """Calculate workload per assignee."""
        return get_workload(
            issues, users,
            self._is_closed, self._get_status_id, self._get_assignee_id
        )

    def get_overloaded_members(
        self,
        issues: list[dict],
        users: list[dict],
        threshold: int = 5
    ) -> list[dict]:
        """Get members with more than threshold open issues."""
        return get_overloaded_members(
            issues, users, threshold,
            self._is_closed, self._get_status_id, self._get_assignee_id
        )

    def get_member_progress(self, issues: list[dict], users: list[dict]) -> list[dict]:
        """Calculate progress per member."""
        return get_member_progress(
            issues, users,
            self._is_closed, self._get_status_id, self._get_assignee_id
        )

    def analyze_member_capacity(
        self,
        issues: list[dict],
        users: list[dict],
        today: date,
        hours_per_day: float = 6.0,
        sprint_end: Optional[date] = None,
        member_capacities: Optional[dict[str, float]] = None
    ) -> list[dict]:
        """Analyze capacity per member with BrSE-level insights.

        Args:
            member_capacities: Optional dict mapping member_name -> capacity_hours_per_day
                If provided, uses per-member capacity; falls back to hours_per_day if not found
        """
        return analyze_member_capacity(
            issues, users, today, hours_per_day, sprint_end,
            self.statuses,
            self._is_closed, self._parse_date, self._get_status_id,
            self._get_assignee_id, self._count_working_days,
            member_capacities
        )

    def get_summary(self, issues: list[dict]) -> dict:
        """Get project summary with status counts and hours progress."""
        if not issues:
            return {
                "total": 0, "by_status": {}, "closed_count": 0,
                "progress_percent": 0, "hours_progress_percent": None,
                "total_estimated_hours": None, "total_actual_hours": None
            }

        by_status = {}
        closed_count = 0
        total_estimated = 0.0
        total_actual = 0.0
        has_hours_data = False

        for issue in issues:
            status_id = self._get_status_id(issue)
            status_name = self.statuses.get(status_id, "Unknown")
            by_status[status_name] = by_status.get(status_name, 0) + 1

            if self._is_closed(status_id):
                closed_count += 1

            est = issue.get("estimatedHours") or 0
            act = issue.get("actualHours") or 0
            if est > 0:
                has_hours_data = True
                total_estimated += est
                total_actual += act

        total = len(issues)
        progress = round((closed_count / total * 100), 2) if total > 0 else 0.0
        hours_progress = round((total_actual / total_estimated * 100), 2) if has_hours_data and total_estimated > 0 else None

        return {
            "total": total, "by_status": by_status, "closed_count": closed_count,
            "progress_percent": progress, "hours_progress_percent": hours_progress,
            "total_estimated_hours": total_estimated if has_hours_data else None,
            "total_actual_hours": total_actual if has_hours_data else None
        }

    def _count_remaining_working_days(self, today: date, due_date: date) -> int:
        """Count remaining working days considering daily_standup timing."""
        if self.calendar:
            return self.calendar.count_remaining_working_days(today, due_date)
        # Fallback: simple calendar days
        return max(0, (due_date - today).days)

    def assess_task_risk(self, issue: dict, today: date, capacity: float = 6.0) -> dict:
        """Assess risk level for a task based on velocity requirements."""
        return assess_task_risk(
            issue, today, capacity,
            self._is_closed, self._parse_date, self._get_status_id,
            self._count_remaining_working_days
        )

    def get_at_risk_tasks(
        self,
        issues: list[dict],
        today: date,
        capacity: float = 6.0
    ) -> list[dict]:
        """Get tasks that are at risk of missing deadline."""
        return get_at_risk_tasks(
            issues, today, capacity,
            self._is_closed, self._parse_date, self._get_status_id,
            self._count_remaining_working_days
        )

    def get_schedule_warnings(self, issues: list[dict]) -> list[dict]:
        """Detect tasks with dates falling on non-working days."""
        return get_schedule_warnings(issues, self.calendar, self._parse_date)

    def generate_gantt_schedule(
        self,
        member_capacity: list[dict],
        today: date,
        hours_per_day: float = 6.0,
        sprint_end: Optional[date] = None,
        lang: str = DEFAULT_LANG
    ) -> str:
        """Generate Gantt-style daily schedule for each member."""
        return generate_gantt_schedule(
            member_capacity, today, hours_per_day, sprint_end,
            self._get_working_days_list, lang
        )

    def generate_gantt_schedule_with_analysis(
        self,
        member_capacity: list[dict],
        today: date,
        hours_per_day: float = 6.0,
        sprint_end: Optional[date] = None,
        lang: str = DEFAULT_LANG
    ) -> tuple[str, Optional[dict]]:
        """Generate Gantt schedule with capacity analysis."""
        return generate_gantt_schedule_with_analysis(
            member_capacity, today, hours_per_day, sprint_end,
            self._get_working_days_list, lang
        )

    def generate_report(
        self,
        issues: list[dict],
        users: list[dict],
        today: date,
        project_name: str = "Project",
        capacity: float = 6.0,
        hours_per_day: float = 6.0,
        sprint_end: Optional[date] = None,
        lang: str = DEFAULT_LANG,
        member_capacities: Optional[dict[str, float]] = None
    ) -> str:
        """Generate Markdown status report with BrSE insights.

        Args:
            member_capacities: Optional dict mapping member_name -> capacity_hours_per_day
                If provided, uses per-member capacity; falls back to hours_per_day if not found
        """
        # Pre-compute analysis results
        late_tasks = self.get_late_tasks(issues, today)
        at_risk_tasks = self.get_at_risk_tasks(issues, today, capacity)
        summary = self.get_summary(issues)
        member_capacity = self.analyze_member_capacity(
            issues, users, today, hours_per_day, sprint_end, member_capacities
        )
        schedule_warnings = self.get_schedule_warnings(issues)

        return _generate_report(
            issues, users, today, project_name, capacity, hours_per_day, sprint_end, lang,
            late_tasks, at_risk_tasks, summary, member_capacity, schedule_warnings,
            self._get_working_days_list
        )
