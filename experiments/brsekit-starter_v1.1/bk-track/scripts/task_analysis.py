"""Task analysis functions for bk-status skill.

Contains: late tasks detection, at-risk tasks detection, schedule warnings.
"""

from datetime import date
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from calendar_utils import CalendarConfig

# Import from models
import sys
from pathlib import Path
_scripts_dir = Path(__file__).parent
if str(_scripts_dir) not in sys.path:
    sys.path.insert(0, str(_scripts_dir))
from models import RiskLevel


def get_late_tasks(
    issues: list[dict],
    today: date,
    is_closed_fn,
    parse_date_fn,
    get_status_id_fn
) -> list[dict]:
    """Get tasks that are past due date but not closed.

    Args:
        issues: List of issue dicts
        today: Current date for comparison
        is_closed_fn: Function to check if status is closed
        parse_date_fn: Function to parse date strings
        get_status_id_fn: Function to extract status ID

    Returns:
        List of late tasks with days_overdue added
    """
    late = []

    for issue in issues:
        due_date = parse_date_fn(issue.get("dueDate"))
        if not due_date:
            continue  # No due date = not late

        status_id = get_status_id_fn(issue)
        if is_closed_fn(status_id):
            continue  # Already closed

        if due_date < today:
            days_overdue = (today - due_date).days
            late.append({
                **issue,
                "days_overdue": days_overdue
            })

    # Sort by days overdue (most overdue first)
    return sorted(late, key=lambda x: x["days_overdue"], reverse=True)


def assess_task_risk(
    issue: dict,
    today: date,
    capacity: float,
    is_closed_fn,
    parse_date_fn,
    get_status_id_fn,
    count_working_days_fn=None
) -> dict:
    """Assess risk level for a task based on velocity requirements.

    Args:
        issue: Issue dict with dueDate, estimatedHours, actualHours
        today: Current date
        capacity: Hours per day capacity
        is_closed_fn: Function to check if status is closed
        parse_date_fn: Function to parse date strings
        get_status_id_fn: Function to extract status ID
        count_working_days_fn: Optional function(today, due_date) -> int
            Counts working days considering calendar and daily_standup.
            If None, falls back to calendar days.

    Returns:
        Dict with level (RiskLevel), required_velocity, working_days_remaining
    """
    due_date = parse_date_fn(issue.get("dueDate"))
    status_id = get_status_id_fn(issue)

    # Closed tasks have no risk
    if is_closed_fn(status_id):
        return {"level": None, "reason": "closed"}

    # No due date = cannot assess
    if not due_date:
        return {"level": None, "reason": "no_due_date"}

    # Calculate working days remaining (considers holidays, weekends, daily_standup)
    if count_working_days_fn:
        working_days_remaining = count_working_days_fn(today, due_date)
    else:
        # Fallback: simple calendar days
        working_days_remaining = (due_date - today).days

    # LATE: due_date < today (no working days left)
    if due_date < today:
        return {
            "level": RiskLevel.LATE,
            "days_overdue": (today - due_date).days
        }

    # Calculate velocity if hours available
    estimated = issue.get("estimatedHours") or 0
    actual = issue.get("actualHours") or 0
    hours_remaining = max(0, estimated - actual)

    # Handle same-day or no working days left
    effective_days = working_days_remaining if working_days_remaining > 0 else 0.5

    if hours_remaining > 0:
        required_velocity = hours_remaining / effective_days

        if required_velocity <= capacity:
            return {
                "level": RiskLevel.ON_TRACK,
                "required_velocity": round(required_velocity, 2),
                "days_remaining": working_days_remaining
            }
        else:
            return {
                "level": RiskLevel.AT_RISK,
                "required_velocity": round(required_velocity, 2),
                "days_remaining": working_days_remaining,
                "capacity_gap": round(required_velocity - capacity, 2)
            }

    # No hours data but future due date = ON_TRACK
    return {"level": RiskLevel.ON_TRACK, "days_remaining": working_days_remaining}


def get_at_risk_tasks(
    issues: list[dict],
    today: date,
    capacity: float,
    is_closed_fn,
    parse_date_fn,
    get_status_id_fn,
    count_working_days_fn=None
) -> list[dict]:
    """Get tasks that are at risk of missing deadline.

    Args:
        issues: List of issue dicts
        today: Current date
        capacity: Hours per day capacity
        is_closed_fn: Function to check if status is closed
        parse_date_fn: Function to parse date strings
        get_status_id_fn: Function to extract status ID
        count_working_days_fn: Optional function(today, due_date) -> int
            Counts working days considering calendar and daily_standup.

    Returns:
        List of at-risk tasks with risk info attached, sorted by urgency
    """
    at_risk = []

    for issue in issues:
        risk = assess_task_risk(
            issue, today, capacity,
            is_closed_fn, parse_date_fn, get_status_id_fn,
            count_working_days_fn
        )
        if risk.get("level") == RiskLevel.AT_RISK:
            at_risk.append({**issue, "risk": risk})

    # Sort by required_velocity descending (most urgent first)
    return sorted(
        at_risk,
        key=lambda x: x["risk"].get("required_velocity", 0),
        reverse=True
    )


def get_schedule_warnings(
    issues: list[dict],
    calendar: Optional["CalendarConfig"],
    parse_date_fn
) -> list[dict]:
    """Detect tasks with dates falling on non-working days.

    Checks startDate and dueDate against calendar config.
    Warns when dates fall on weekends/holidays but project works Mon-Fri.

    Args:
        issues: List of issue dicts
        calendar: CalendarConfig for checking working days
        parse_date_fn: Function to parse date strings

    Returns:
        List of warning dicts with issue_key, date_type, date, reason
    """
    if not calendar:
        return []

    warnings = []

    for issue in issues:
        issue_key = issue.get("issueKey", issue.get("key_id", "?"))
        summary = issue.get("summary", "")[:40]

        # Check startDate
        start_str = issue.get("startDate")
        if start_str:
            start_date = parse_date_fn(start_str)
            if start_date:
                reason = calendar.check_date_warning(start_date)
                if reason:
                    warnings.append({
                        "issue_key": issue_key,
                        "summary": summary,
                        "date_type": "startDate",
                        "date": start_date,
                        "reason": reason
                    })

        # Check dueDate
        due_str = issue.get("dueDate")
        if due_str:
            due_date = parse_date_fn(due_str)
            if due_date:
                reason = calendar.check_date_warning(due_date)
                if reason:
                    warnings.append({
                        "issue_key": issue_key,
                        "summary": summary,
                        "date_type": "dueDate",
                        "date": due_date,
                        "reason": reason
                    })

    return warnings
