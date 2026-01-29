"""Statistics calculation for bk-report skill.

Calculate weekly statistics from issue data.
"""

from datetime import date, datetime
from typing import Optional


def parse_date(date_str: Optional[str]) -> Optional[date]:
    """Parse date string to date object.

    Args:
        date_str: Date string in ISO format (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SSZ)

    Returns:
        date object or None
    """
    if not date_str:
        return None
    try:
        if "T" in date_str:
            return datetime.fromisoformat(date_str.replace("Z", "+00:00")).date()
        return date.fromisoformat(date_str)
    except (ValueError, TypeError):
        return None


def calculate_stats(
    issues: list[dict],
    closed_status_names: list[str] = None
) -> dict:
    """Calculate statistics from issues.

    Args:
        issues: List of issue dicts with status
        closed_status_names: Names of closed statuses

    Returns:
        Dict with:
            - total: Total issues count
            - completed: Closed issues count
            - in_progress: In progress count
            - open: Open/backlog count
            - late: Late issues count
            - completion_rate: Percentage
    """
    if closed_status_names is None:
        closed_status_names = ["Closed", "完了", "Done"]

    total = len(issues)
    completed = 0
    in_progress = 0
    open_count = 0
    late = 0

    today = date.today()

    for issue in issues:
        status_name = issue.get("status", {}).get("name", "")

        if status_name in closed_status_names:
            completed += 1
        elif status_name in ["In Progress", "進行中", "Doing", "処理中"]:
            in_progress += 1
        else:
            open_count += 1

        # Check if late
        if status_name not in closed_status_names:
            due_date = parse_date(issue.get("dueDate"))
            if due_date and due_date < today:
                late += 1

    completion_rate = (completed / total * 100) if total > 0 else 0

    return {
        "total": total,
        "completed": completed,
        "in_progress": in_progress,
        "open": open_count,
        "late": late,
        "completion_rate": round(completion_rate, 1),
    }


def filter_completed_this_week(
    issues: list[dict],
    week_start: date,
    week_end: date,
    closed_status_names: list[str] = None
) -> list[dict]:
    """Filter issues completed during the week.

    Args:
        issues: List of issue dicts
        week_start: Week start date
        week_end: Week end date
        closed_status_names: Names of closed statuses

    Returns:
        List of completed issue dicts with simplified structure
    """
    if closed_status_names is None:
        closed_status_names = ["Closed", "完了", "Done"]

    result = []
    for issue in issues:
        status_name = issue.get("status", {}).get("name", "")
        if status_name not in closed_status_names:
            continue

        updated = parse_date(issue.get("updated"))
        if updated and week_start <= updated <= week_end:
            result.append({
                "key": issue.get("issueKey", ""),
                "summary": issue.get("summary", ""),
                "assignee": issue.get("assignee", {}).get("name", "-") if issue.get("assignee") else "-",
                "status": status_name,
                "due_date": issue.get("dueDate", ""),
            })

    return result


def filter_in_progress(
    issues: list[dict],
    in_progress_names: list[str] = None
) -> list[dict]:
    """Filter in-progress issues.

    Args:
        issues: List of issue dicts
        in_progress_names: Names of in-progress statuses

    Returns:
        List of in-progress issue dicts
    """
    if in_progress_names is None:
        in_progress_names = ["In Progress", "進行中", "Doing", "処理中"]

    result = []
    for issue in issues:
        status_name = issue.get("status", {}).get("name", "")
        if status_name in in_progress_names:
            result.append({
                "key": issue.get("issueKey", ""),
                "summary": issue.get("summary", ""),
                "assignee": issue.get("assignee", {}).get("name", "-") if issue.get("assignee") else "-",
                "status": status_name,
                "due_date": issue.get("dueDate", ""),
            })

    return result


def filter_next_week_tasks(
    issues: list[dict],
    week_end: date,
    days_ahead: int = 7,
    closed_status_names: list[str] = None
) -> list[dict]:
    """Filter tasks due in the next week.

    Args:
        issues: List of issue dicts
        week_end: Current week end date
        days_ahead: Days to look ahead
        closed_status_names: Names of closed statuses

    Returns:
        List of next week task dicts
    """
    if closed_status_names is None:
        closed_status_names = ["Closed", "完了", "Done"]

    from datetime import timedelta
    next_week_end = week_end + timedelta(days=days_ahead)

    result = []
    for issue in issues:
        status_name = issue.get("status", {}).get("name", "")
        if status_name in closed_status_names:
            continue

        due_date = parse_date(issue.get("dueDate"))
        if due_date and week_end < due_date <= next_week_end:
            result.append({
                "key": issue.get("issueKey", ""),
                "summary": issue.get("summary", ""),
                "assignee": issue.get("assignee", {}).get("name", "-") if issue.get("assignee") else "-",
                "status": status_name,
                "due_date": issue.get("dueDate", ""),
            })

    return sorted(result, key=lambda x: x.get("due_date", ""))


def filter_late_tasks(
    issues: list[dict],
    today: date,
    closed_status_names: list[str] = None
) -> list[dict]:
    """Filter late tasks.

    Args:
        issues: List of issue dicts
        today: Current date
        closed_status_names: Names of closed statuses

    Returns:
        List of late task dicts with days_late
    """
    if closed_status_names is None:
        closed_status_names = ["Closed", "完了", "Done"]

    result = []
    for issue in issues:
        status_name = issue.get("status", {}).get("name", "")
        if status_name in closed_status_names:
            continue

        due_date = parse_date(issue.get("dueDate"))
        if due_date and due_date < today:
            days_late = (today - due_date).days
            result.append({
                "key": issue.get("issueKey", ""),
                "summary": issue.get("summary", ""),
                "assignee": issue.get("assignee", {}).get("name", "-") if issue.get("assignee") else "-",
                "status": status_name,
                "due_date": issue.get("dueDate", ""),
                "days_late": days_late,
            })

    return sorted(result, key=lambda x: x.get("days_late", 0), reverse=True)
