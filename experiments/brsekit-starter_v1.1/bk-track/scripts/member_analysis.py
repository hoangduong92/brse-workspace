"""Member analysis functions for bk-status skill.

Contains: workload calculation, overloaded members, member progress, capacity analysis.
"""

from datetime import date
from typing import Optional
from enum import Enum


class MemberStatus(Enum):
    """Member capacity status."""
    SURPLUS = "surplus"      # Has extra capacity, can help others
    ON_TRACK = "on_track"    # Just enough capacity
    AT_RISK = "at_risk"      # Needs more capacity than available
    OVERLOADED = "overloaded"  # Severely over capacity


def get_workload(
    issues: list[dict],
    users: list[dict],
    is_closed_fn,
    get_status_id_fn,
    get_assignee_id_fn
) -> dict:
    """Calculate workload per assignee.

    Args:
        issues: List of issue dicts
        users: List of user dicts
        is_closed_fn: Function to check if status is closed
        get_status_id_fn: Function to extract status ID
        get_assignee_id_fn: Function to extract assignee ID

    Returns:
        Dict mapping assignee_id -> {name, open_count}
    """
    # Initialize with all users
    workload = {
        u["id"]: {"name": u["name"], "open_count": 0}
        for u in users
    }
    workload["unassigned"] = {"name": "Unassigned", "open_count": 0}

    for issue in issues:
        status_id = get_status_id_fn(issue)
        if is_closed_fn(status_id):
            continue  # Don't count closed issues

        assignee_id = get_assignee_id_fn(issue)
        if assignee_id and assignee_id in workload:
            workload[assignee_id]["open_count"] += 1
        else:
            workload["unassigned"]["open_count"] += 1

    return workload


def get_overloaded_members(
    issues: list[dict],
    users: list[dict],
    threshold: int,
    is_closed_fn,
    get_status_id_fn,
    get_assignee_id_fn
) -> list[dict]:
    """Get members with more than threshold open issues.

    Args:
        issues: List of issue dicts
        users: List of user dicts
        threshold: Max acceptable open issues
        is_closed_fn: Function to check if status is closed
        get_status_id_fn: Function to extract status ID
        get_assignee_id_fn: Function to extract assignee ID

    Returns:
        List of overloaded member dicts
    """
    workload = get_workload(
        issues, users, is_closed_fn, get_status_id_fn, get_assignee_id_fn
    )

    overloaded = []
    for user_id, data in workload.items():
        if user_id == "unassigned":
            continue
        if data["open_count"] > threshold:
            overloaded.append({
                "id": user_id,
                "name": data["name"],
                "open_count": data["open_count"]
            })

    return sorted(overloaded, key=lambda x: x["open_count"], reverse=True)


def get_member_progress(
    issues: list[dict],
    users: list[dict],
    is_closed_fn,
    get_status_id_fn,
    get_assignee_id_fn
) -> list[dict]:
    """Calculate progress per member.

    Args:
        issues: List of issue dicts
        users: List of user dicts
        is_closed_fn: Function to check if status is closed
        get_status_id_fn: Function to extract status ID
        get_assignee_id_fn: Function to extract assignee ID

    Returns:
        List of member progress dicts sorted by progress ascending
    """
    # Initialize tracking per user
    member_data = {
        u["id"]: {
            "name": u["name"],
            "total": 0,
            "closed": 0,
            "estimated_hours": 0.0,
            "actual_hours": 0.0
        }
        for u in users
    }

    for issue in issues:
        assignee_id = get_assignee_id_fn(issue)
        if not assignee_id or assignee_id not in member_data:
            continue

        member_data[assignee_id]["total"] += 1

        status_id = get_status_id_fn(issue)
        if is_closed_fn(status_id):
            member_data[assignee_id]["closed"] += 1

        est = issue.get("estimatedHours") or 0
        act = issue.get("actualHours") or 0
        member_data[assignee_id]["estimated_hours"] += est
        member_data[assignee_id]["actual_hours"] += act

    # Build result with progress calculations
    result = []
    for user_id, data in member_data.items():
        if data["total"] == 0:
            continue  # Skip members with no issues

        count_progress = round((data["closed"] / data["total"] * 100), 1) if data["total"] > 0 else 0
        hours_progress = None
        if data["estimated_hours"] > 0:
            hours_progress = round((data["actual_hours"] / data["estimated_hours"] * 100), 1)

        result.append({
            "id": user_id,
            "name": data["name"],
            "total": data["total"],
            "closed": data["closed"],
            "open": data["total"] - data["closed"],
            "count_progress": count_progress,
            "estimated_hours": data["estimated_hours"],
            "actual_hours": data["actual_hours"],
            "hours_progress": hours_progress
        })

    # Sort by hours_progress ascending (lowest first = needs attention)
    return sorted(result, key=lambda x: x["hours_progress"] or 0)


def analyze_member_capacity(
    issues: list[dict],
    users: list[dict],
    today: date,
    hours_per_day: float,
    sprint_end: Optional[date],
    statuses: dict[int, str],
    is_closed_fn,
    parse_date_fn,
    get_status_id_fn,
    get_assignee_id_fn,
    count_working_days_fn,
    member_capacities: Optional[dict[str, float]] = None
) -> list[dict]:
    """Analyze capacity per member with BrSE-level insights.

    Uses cumulative gap calculation: sum of individual task gaps.
    Each task's gap = available hours until its due date - remaining hours.

    Args:
        issues: List of issue dicts
        users: List of user dicts
        today: Current date (after daily standup)
        hours_per_day: Default working hours per day (fallback if no per-member config)
        sprint_end: Sprint end date for overall capacity calculation
        statuses: Dict mapping status_id -> status_name
        is_closed_fn: Function to check if status is closed
        parse_date_fn: Function to parse date strings
        get_status_id_fn: Function to extract status ID
        get_assignee_id_fn: Function to extract assignee ID
        count_working_days_fn: Function to count working days
        member_capacities: Optional dict mapping member_name -> capacity_hours_per_day
            If provided, uses per-member capacity; falls back to hours_per_day if not found

    Returns:
        List of member capacity analysis dicts
    """
    member_capacities = member_capacities or {}

    # Group issues by assignee with due date info
    member_tasks: dict[int, list[dict]] = {u["id"]: [] for u in users}
    member_names = {u["id"]: u["name"] for u in users}

    for issue in issues:
        assignee_id = get_assignee_id_fn(issue)
        if not assignee_id or assignee_id not in member_tasks:
            continue

        status_id = get_status_id_fn(issue)
        if is_closed_fn(status_id):
            continue  # Skip closed tasks

        start_date = parse_date_fn(issue.get("startDate"))
        due_date = parse_date_fn(issue.get("dueDate"))
        est = issue.get("estimatedHours") or 0
        act = issue.get("actualHours") or 0

        # Detect overrun: actual >= estimate means we can't calculate remaining
        is_overrun = (est > 0 and act >= est) or (est == 0 and act > 0)
        needs_reestimate = is_overrun

        # Calculate remaining hours
        if is_overrun:
            remaining = None
            remaining_for_calc = 0
        else:
            remaining = max(0, est - act)
            remaining_for_calc = remaining

        # Calculate overtime percentage
        overtime_percent = (act / est * 100) if est > 0 else 0

        # Calculate working days considering start_date
        # Available time is from max(today, start_date) to due_date
        if due_date:
            effective_start = max(today, start_date) if start_date else today
            working_days = count_working_days_fn(effective_start, due_date)
        else:
            working_days = None

        # Detect impossible schedule: start_date = due_date but remaining > capacity
        # Note: We can't check per-member capacity here yet, so use default
        # This will be recalculated in per-member analysis loop
        needs_reschedule = False
        if start_date and due_date and start_date == due_date:
            if remaining_for_calc > hours_per_day:
                needs_reschedule = True

        member_tasks[assignee_id].append({
            "issue": issue,
            "start_date": start_date,
            "due_date": due_date,
            "estimated": est,
            "actual": act,
            "remaining": remaining,
            "remaining_for_calc": remaining_for_calc,
            "working_days": working_days,
            "overtime_percent": overtime_percent,
            "is_overrun": is_overrun,
            "needs_reestimate": needs_reestimate,
            "needs_reschedule": needs_reschedule
        })

    result = []
    for user_id, tasks in member_tasks.items():
        if not tasks:
            continue

        name = member_names.get(user_id, "Unknown")
        # Use per-member capacity if available, fallback to default
        member_hours_per_day = member_capacities.get(name, hours_per_day)
        total_remaining = sum(t["remaining_for_calc"] for t in tasks)
        tasks_need_reestimate = [t for t in tasks if t["needs_reestimate"]]

        # Find earliest and latest due dates
        tasks_with_due = [t for t in tasks if t["due_date"]]
        if tasks_with_due:
            earliest_due = min(t["due_date"] for t in tasks_with_due)
            latest_due = max(t["due_date"] for t in tasks_with_due)
        else:
            earliest_due = None
            latest_due = None

        # Per-task analysis with individual gaps
        # Sort by start_date (or due_date if no start_date)
        task_analysis = []
        cumulative_gap = 0.0
        tasks_needing_reschedule = []

        for t in sorted(tasks, key=lambda x: (x["start_date"] or x["due_date"] or date.max)):
            issue = t["issue"]
            issue_key = issue.get("issueKey", issue.get("key_id", "?"))
            summary = issue.get("summary", "")[:40]
            wd = t["working_days"]
            task_available = wd * member_hours_per_day if wd else 0
            task_gap = task_available - t["remaining_for_calc"]

            # Recalculate needs_reschedule with member-specific capacity
            needs_reschedule = False
            if t["start_date"] and t["due_date"] and t["start_date"] == t["due_date"]:
                if t["remaining_for_calc"] > member_hours_per_day:
                    needs_reschedule = True

            if not t["needs_reestimate"] and not needs_reschedule:
                cumulative_gap += task_gap

            if needs_reschedule:
                tasks_needing_reschedule.append(issue_key)

            task_analysis.append({
                "issue_key": issue_key,
                "summary": summary,
                "start_date": t["start_date"],
                "due_date": t["due_date"],
                "working_days": wd,
                "estimated": t["estimated"],
                "actual": t["actual"],
                "remaining_hours": t["remaining"],
                "remaining_for_calc": t["remaining_for_calc"],
                "available_hours": task_available,
                "gap": task_gap if not t["needs_reestimate"] else None,
                "overtime_percent": t["overtime_percent"],
                "is_overrun": t["is_overrun"],
                "needs_reestimate": t["needs_reestimate"],
                "needs_reschedule": needs_reschedule,
                "status": statuses.get(get_status_id_fn(issue), "?")
            })

        # Calculate REAL sprint capacity using member-specific hours_per_day
        effective_end = sprint_end or latest_due
        if effective_end:
            sprint_working_days = count_working_days_fn(today, effective_end)
            sprint_available = sprint_working_days * member_hours_per_day
        else:
            sprint_working_days = 0
            sprint_available = 0

        sprint_gap = sprint_available - total_remaining
        gap = sprint_gap

        # Determine status based on REAL sprint gap (using member-specific capacity)
        if not tasks_with_due:
            status = MemberStatus.AT_RISK if total_remaining > 0 else MemberStatus.ON_TRACK
        elif sprint_gap >= member_hours_per_day:
            status = MemberStatus.SURPLUS
        elif sprint_gap >= 0:
            status = MemberStatus.ON_TRACK
        elif sprint_gap >= -member_hours_per_day:
            status = MemberStatus.AT_RISK
        else:
            status = MemberStatus.OVERLOADED

        total_available = sprint_available

        # Required velocity
        if effective_end:
            working_days_to_end = count_working_days_fn(today, effective_end)
            required_velocity = total_remaining / working_days_to_end if working_days_to_end > 0 else float('inf')
        else:
            working_days_to_end = 0
            required_velocity = float('inf')

        result.append({
            "id": user_id,
            "name": name,
            "task_count": len(tasks),
            "total_remaining_hours": total_remaining,
            "total_available_hours": total_available,
            "earliest_due": earliest_due,
            "latest_due": latest_due,
            "sprint_end": sprint_end,
            "working_days": working_days_to_end,
            "available_hours": total_available,
            "gap": gap,
            "cumulative_task_gap": cumulative_gap,
            "status": status,
            "required_velocity": round(required_velocity, 1) if required_velocity != float('inf') else None,
            "hours_per_day": member_hours_per_day,  # Per-member capacity
            "tasks": task_analysis,
            "tasks_need_reestimate": len(tasks_need_reestimate),
            "tasks_need_reschedule": tasks_needing_reschedule
        })

    # Sort: OVERLOADED first, then AT_RISK, ON_TRACK, SURPLUS last
    priority = {
        MemberStatus.OVERLOADED: 0,
        MemberStatus.AT_RISK: 1,
        MemberStatus.ON_TRACK: 2,
        MemberStatus.SURPLUS: 3
    }
    return sorted(result, key=lambda x: priority.get(x["status"], 99))
