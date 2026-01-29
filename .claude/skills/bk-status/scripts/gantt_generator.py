"""Gantt schedule generator for bk-status skill.

Contains: Gantt-style daily schedule generation with capacity analysis.
"""

from datetime import date
from typing import Optional

# Import translations
import sys
from pathlib import Path
_scripts_dir = Path(__file__).parent
if str(_scripts_dir) not in sys.path:
    sys.path.insert(0, str(_scripts_dir))
try:
    from translations import Translator, DEFAULT_LANG
except ImportError:
    from .translations import Translator, DEFAULT_LANG


def generate_gantt_schedule(
    member_capacity: list[dict],
    today: date,
    hours_per_day: float,
    sprint_end: Optional[date],
    get_working_days_list_fn,
    lang: str = DEFAULT_LANG
) -> str:
    """Generate Gantt-style daily schedule for each member.

    Args:
        member_capacity: Output from analyze_member_capacity
        today: Current date
        hours_per_day: Working hours per day
        sprint_end: Sprint end date for schedule boundary
        get_working_days_list_fn: Function to get working days list
        lang: Report language (en, vi)

    Returns:
        Markdown formatted Gantt schedule string
    """
    gantt, _ = generate_gantt_schedule_with_analysis(
        member_capacity, today, hours_per_day, sprint_end,
        get_working_days_list_fn, lang
    )
    return gantt


def generate_gantt_schedule_with_analysis(
    member_capacity: list[dict],
    today: date,
    hours_per_day: float,
    sprint_end: Optional[date],
    get_working_days_list_fn,
    lang: str = DEFAULT_LANG
) -> tuple[str, Optional[dict]]:
    """Generate Gantt schedule with capacity analysis.

    Args:
        member_capacity: Output from analyze_member_capacity
        today: Current date
        hours_per_day: Working hours per day
        sprint_end: Sprint end date for schedule boundary
        get_working_days_list_fn: Function to get working days list
        lang: Report language (en, vi)

    Returns:
        Tuple of (markdown string, analysis dict with unscheduled info)
    """
    if not member_capacity:
        return "", None

    tr = Translator(lang)
    lines = [
        f"## {tr.t('daily_schedule')}",
        "",
        tr.t('daily_schedule_note'),
        "",
    ]

    # Day name abbreviations
    day_abbrev = ["M", "T", "W", "T", "F", "S", "S"]

    # Track all unscheduled tasks across members
    all_unscheduled: list[dict] = []
    all_proposed: list[dict] = []  # Tasks with completion > due_date
    total_remaining_all = 0.0
    total_available_all = 0.0

    for mc in member_capacity:
        if not mc["tasks"]:
            continue

        # Determine schedule range
        tasks_with_due = [t for t in mc["tasks"] if t["due_date"]]
        if not tasks_with_due:
            continue

        # Schedule from today to sprint_end or latest due date
        latest_due = max(t["due_date"] for t in tasks_with_due)
        schedule_end = sprint_end if sprint_end and sprint_end >= latest_due else latest_due

        # Get working days list
        working_days = get_working_days_list_fn(today, schedule_end)
        if not working_days:
            continue

        # Calculate capacity for this member (use per-member capacity if available)
        member_hours = mc.get('hours_per_day', hours_per_day)
        member_available = len(working_days) * member_hours
        total_available_all += member_available

        # Limit to 14 days for readability
        truncated = len(working_days) > 14
        if truncated:
            working_days = working_days[:14]

        # Build task schedule simulation - sort by start_date (earliest first)
        # If no start_date, fall back to due_date
        sorted_tasks = sorted(
            [t for t in mc["tasks"] if t["remaining_hours"] is not None],
            key=lambda x: (x.get("start_date") or x["due_date"] or date.max)
        )

        # Track total remaining for this member
        member_remaining = sum(t["remaining_hours"] or 0 for t in sorted_tasks)
        total_remaining_all += member_remaining

        # Initialize remaining hours per task
        task_remaining = {
            t["issue_key"]: t["remaining_hours"] or 0
            for t in sorted_tasks
        }

        # Schedule matrix: task_key -> {date -> hours_worked}
        schedule: dict[str, dict[date, float]] = {
            t["issue_key"]: {} for t in sorted_tasks
        }

        # Simulate day-by-day allocation (use per-member capacity)
        for day in working_days:
            available_today = member_hours

            for t in sorted_tasks:
                if available_today <= 0:
                    break

                key = t["issue_key"]
                remaining = task_remaining[key]

                if remaining <= 0:
                    continue

                # Don't schedule work before task's start_date
                task_start = t.get("start_date")
                if task_start and day < task_start:
                    continue

                # Allocate hours
                work_hours = min(remaining, available_today)
                schedule[key][day] = work_hours
                task_remaining[key] -= work_hours
                available_today -= work_hours

        # Build Gantt table (use per-member capacity)
        lines.append(f"### {mc['name']} ({member_hours:.0f}h/day)")
        lines.append("")

        # Header row with dates
        header_dates = [f"{d.day:02d}{day_abbrev[d.weekday()]}" for d in working_days]
        header = "| Task | " + " | ".join(header_dates) + " |"
        lines.append(header)

        # Separator
        sep = "|------|" + "|".join(["----"] * len(working_days)) + "|"
        lines.append(sep)

        # Task rows - track tasks with incomplete scheduling
        unscheduled_tasks = []
        incomplete_tasks = []
        proposed_tasks = []  # Track tasks with proposed schedule (extended beyond due)

        for t in sorted_tasks:
            key = t["issue_key"]
            remaining = t["remaining_hours"] or 0
            due_date = t["due_date"]

            # Calculate total scheduled hours for this task
            total_scheduled = sum(schedule[key].get(d, 0) for d in working_days)
            shortfall = remaining - total_scheduled

            # Find actual completion date (last day with work scheduled)
            completion_date = None
            for d in reversed(working_days):
                if schedule[key].get(d, 0) > 0:
                    completion_date = d
                    break

            # Check if this is a proposed schedule (completion beyond due_date)
            is_proposed = (
                completion_date and due_date and completion_date > due_date
            )

            # Track tasks that couldn't be fully scheduled
            if total_scheduled == 0:
                # Completely unscheduled
                unscheduled_tasks.append({
                    "issue_key": key,
                    "remaining": remaining,
                    "scheduled": 0,
                    "shortfall": remaining,
                    "due_date": due_date,
                    "assignee": mc["name"]
                })
                task_label = f"🔴 {key} ({remaining:.0f}h)"
                cells = [""] * len(working_days)
                cells[-1] = f"↑{remaining:.0f}h"
                row = f"| {task_label} | " + " | ".join(cells) + " |"
                lines.append(row)
                continue
            elif shortfall > 0:
                # Partially scheduled (incomplete)
                incomplete_tasks.append({
                    "issue_key": key,
                    "remaining": remaining,
                    "scheduled": total_scheduled,
                    "shortfall": shortfall,
                    "due_date": due_date,
                    "assignee": mc["name"]
                })

            # Build cells for each day
            cells = []
            cumulative = 0
            for d in working_days:
                hours = schedule[key].get(d, 0)
                if hours > 0:
                    cumulative += hours
                    if cumulative >= (t["remaining_hours"] or 0):
                        # Task completes on this day - use different emoji for late vs on-time
                        if is_proposed:
                            cells.append(f"{hours:.0f}⚠️")  # Late completion
                        else:
                            cells.append(f"{hours:.0f}✅")  # On-time completion
                    else:
                        cells.append(f"{hours:.0f}")
                else:
                    cells.append("")

            # Determine task label based on status
            if shortfall > 0:
                # Incomplete task - add deficit indicator
                for i in range(len(cells) - 1, -1, -1):
                    if cells[i]:
                        cells[i] = cells[i] + f"↑{shortfall:.0f}h"
                        break
                task_label = f"⚠️ {key} ({remaining:.0f}h)"
            elif is_proposed:
                # Proposed schedule (extended beyond due_date) - BOLD
                task_label = f"**📅 {key} ({remaining:.0f}h)**"
                proposed_tasks.append({
                    "issue_key": key,
                    "summary": t.get("summary", "")[:30],
                    "due_date": due_date,
                    "completion_date": completion_date,
                    "remaining": remaining,
                    "assignee": mc["name"],
                    "hours_per_day": mc.get("hours_per_day", hours_per_day)
                })
            else:
                task_label = f"{key} ({remaining:.0f}h)"

            row = f"| {task_label} | " + " | ".join(cells) + " |"
            lines.append(row)

        # Daily total row
        totals = []
        for d in working_days:
            day_total = sum(schedule[key].get(d, 0) for key in schedule)
            totals.append(f"{day_total:.0f}h" if day_total > 0 else "")

        lines.append("|" + "-" * 6 + "|" + "|".join(["----"] * len(working_days)) + "|")
        lines.append(f"| {tr.t('daily_total')} | " + " | ".join(totals) + " |")
        lines.append("")

        if truncated:
            lines.append(tr.t("schedule_truncated", end=schedule_end))
            lines.append("")

        # Track unscheduled tasks for overall analysis
        if unscheduled_tasks or incomplete_tasks:
            all_unscheduled.extend(unscheduled_tasks)
            all_unscheduled.extend(incomplete_tasks)

        # Track proposed tasks (completion > due_date)
        if proposed_tasks:
            all_proposed.extend(proposed_tasks)

        # Show legend when there are special indicators (unscheduled, incomplete, or proposed)
        if unscheduled_tasks or incomplete_tasks or proposed_tasks:
            lines.append("")
            lines.append(tr.t("gantt_legend"))
            lines.append("")

    # Build analysis info
    deficit = total_remaining_all - total_available_all
    analysis = {
        "has_unscheduled": len(all_unscheduled) > 0,
        "unscheduled_tasks": all_unscheduled,
        "proposed_tasks": all_proposed,  # Tasks with completion > due_date
        "total_remaining": total_remaining_all,
        "total_available": total_available_all,
        "deficit": max(0, deficit)
    }

    return "\n".join(lines), analysis
