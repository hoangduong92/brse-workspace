"""Report generator for bk-status skill.

Contains: Markdown report generation functions.
"""

from datetime import date
from typing import Optional

# Import dependencies
import sys
from pathlib import Path
_scripts_dir = Path(__file__).parent
if str(_scripts_dir) not in sys.path:
    sys.path.insert(0, str(_scripts_dir))

try:
    from translations import Translator, DEFAULT_LANG
except ImportError:
    from .translations import Translator, DEFAULT_LANG

from member_analysis import MemberStatus
from gantt_generator import generate_gantt_schedule_with_analysis


def generate_report(
    issues: list[dict],
    users: list[dict],
    today: date,
    project_name: str,
    capacity: float,
    hours_per_day: float,
    sprint_end: Optional[date],
    lang: str,
    # Analysis results (pre-computed)
    late_tasks: list[dict],
    at_risk_tasks: list[dict],
    summary: dict,
    member_capacity: list[dict],
    schedule_warnings: list[dict],
    # Functions needed for Gantt
    get_working_days_list_fn
) -> str:
    """Generate Markdown status report with BrSE insights.

    Args:
        issues: List of issue dicts
        users: List of user dicts
        today: Current date
        project_name: Name for report header
        capacity: Hours per day capacity for risk calculation
        hours_per_day: Working hours per day for capacity
        sprint_end: Sprint end date for overall analysis
        lang: Report language (en, vi)
        late_tasks: Pre-computed late tasks
        at_risk_tasks: Pre-computed at-risk tasks
        summary: Pre-computed project summary
        member_capacity: Pre-computed member capacity analysis
        schedule_warnings: Pre-computed schedule warnings
        get_working_days_list_fn: Function to get working days list

    Returns:
        Markdown formatted report string
    """
    tr = Translator(lang)
    lines = []

    # Generate Gantt analysis FIRST to get proposed tasks info
    gantt_section = ""
    gantt_analysis = None
    if member_capacity:
        gantt_section, gantt_analysis = generate_gantt_schedule_with_analysis(
            member_capacity, today, hours_per_day, sprint_end,
            get_working_days_list_fn, lang
        )

    # Extract proposed tasks from gantt analysis
    proposed_tasks = gantt_analysis.get("proposed_tasks", []) if gantt_analysis else []

    # Header section
    lines.extend(_generate_header(tr, today, project_name, sprint_end))

    # Action Items section (Executive Summary) - FIRST for visibility
    lines.extend(_generate_action_items_section(
        tr, late_tasks, at_risk_tasks, member_capacity, capacity, proposed_tasks
    ))

    # Summary section
    lines.extend(_generate_summary_section(tr, summary))

    # BrSE Insights section
    if member_capacity:
        lines.extend(_generate_brse_insights_section(
            tr, today, hours_per_day, sprint_end, member_capacity
        ))

    # Schedule warnings section
    if schedule_warnings:
        lines.extend(_generate_schedule_warnings_section(tr, schedule_warnings))

    # Gantt schedule section
    if gantt_section:
        lines.append(gantt_section)

    # Capacity exceeded section
    if gantt_analysis and gantt_analysis.get("deficit", 0) > 0:
        lines.extend(_generate_capacity_exceeded_section(tr, gantt_analysis))

    return "\n".join(lines)


def _generate_action_items_section(
    tr: Translator,
    late_tasks: list[dict],
    at_risk_tasks: list[dict],
    member_capacity: list[dict],
    capacity: float,
    proposed_tasks: list[dict] = None
) -> list[str]:
    """Generate Action Items section (Executive Summary) at top of report."""
    lines = [
        f"## {tr.t('action_items')}",
        "",
    ]
    proposed_tasks = proposed_tasks or []

    # Collect all action items from different sources
    action_items = []

    # 1. Overdue tasks
    for task in late_tasks:
        issue_key = task.get("issueKey", task.get("key_id", "?"))
        summary = task.get("summary", "")[:30]
        assignee = task.get("assignee", {})
        assignee_name = assignee.get("name", tr.t("unassigned")) if assignee else tr.t("unassigned")
        days = task["days_overdue"]
        action_items.append({
            "issue": issue_key,
            "summary": summary,
            "type": tr.t("issue_overdue"),
            "detail": tr.t("overdue_detail", days=days),
            "assignee": assignee_name,
            "priority": 0  # Highest priority
        })

    # 2. Impossible schedule (start=due with remaining > capacity)
    if member_capacity:
        for mc in member_capacity:
            for t in mc["tasks"]:
                if t.get("needs_reschedule"):
                    remaining = t.get("remaining_hours") or t.get("remaining_for_calc", 0)
                    action_items.append({
                        "issue": t["issue_key"],
                        "summary": t["summary"][:30],
                        "type": tr.t("issue_impossible"),
                        "detail": tr.t("impossible_detail", hours=f"{remaining:.0f}"),
                        "assignee": mc["name"],
                        "priority": 1
                    })

    # 3. Needs re-estimate (actual >= estimated)
    if member_capacity:
        for mc in member_capacity:
            for t in mc["tasks"]:
                if t.get("needs_reestimate"):
                    action_items.append({
                        "issue": t["issue_key"],
                        "summary": t["summary"][:30],
                        "type": tr.t("issue_needs_reest"),
                        "detail": tr.t("reest_detail", actual=f"{t['actual']:.0f}", est=f"{t['estimated']:.0f}"),
                        "assignee": mc["name"],
                        "priority": 2
                    })

    # 4. Needs overtime (at-risk tasks)
    for task in at_risk_tasks:
        issue_key = task.get("issueKey", task.get("key_id", "?"))
        summary = task.get("summary", "")[:30]
        assignee = task.get("assignee", {})
        assignee_name = assignee.get("name", tr.t("unassigned")) if assignee else tr.t("unassigned")
        velocity = task["risk"]["required_velocity"]
        action_items.append({
            "issue": issue_key,
            "summary": summary,
            "type": tr.t("issue_needs_overtime"),
            "detail": tr.t("overtime_detail", velocity=f"{velocity:.1f}", capacity=f"{capacity:.0f}"),
            "assignee": assignee_name,
            "priority": 3
        })

    # 5. Proposed schedule (completion > due_date due to capacity)
    # Skip tasks already flagged as impossible (start=due)
    impossible_keys = set()
    if member_capacity:
        for mc in member_capacity:
            for t in mc["tasks"]:
                if t.get("needs_reschedule"):
                    impossible_keys.add(t["issue_key"])

    for pt in proposed_tasks:
        if pt["issue_key"] not in impossible_keys:
            due_str = pt["due_date"].strftime("%m/%d") if pt["due_date"] else "?"
            comp_str = pt["completion_date"].strftime("%m/%d") if pt["completion_date"] else "?"
            action_items.append({
                "issue": pt["issue_key"],
                "summary": pt["summary"],
                "type": tr.t("issue_will_miss"),
                "detail": tr.t("will_miss_detail", due=due_str, completion=comp_str),
                "assignee": pt["assignee"],
                "priority": 4
            })

    # Sort by priority and render
    if action_items:
        action_items.sort(key=lambda x: x["priority"])
        lines.append(tr.t("action_items_note"))
        lines.append("")
        lines.append(f"| {tr.t('issue')} | Summary | Type | Detail | {tr.t('assignee')} |")
        lines.append("|-------|---------|------|--------|----------|")
        for item in action_items:
            lines.append(
                f"| {item['issue']} | {item['summary']} | {item['type']} | {item['detail']} | {item['assignee']} |"
            )
        lines.append("")
    else:
        lines.append(tr.t("no_action_items"))
        lines.append("")

    # Status summary for clarity
    has_overdue = len(late_tasks) > 0
    has_overtime = len(at_risk_tasks) > 0
    has_impossible = any(
        t.get("needs_reschedule")
        for mc in (member_capacity or [])
        for t in mc["tasks"]
    )
    has_reest = any(
        t.get("needs_reestimate")
        for mc in (member_capacity or [])
        for t in mc["tasks"]
    )

    if not action_items:
        lines.extend([
            tr.t("status_ok_overdue"),
            tr.t("status_ok_overtime"),
            tr.t("status_ok_impossible"),
            tr.t("status_ok_reest"),
            "",
        ])

    return lines


def _generate_header(tr: Translator, today: date, project_name: str, sprint_end: Optional[date]) -> list[str]:
    """Generate report header section."""
    lines = [
        f"# {tr.t('report_title')}",
        "",
        f"**{tr.t('date')}:** {today.isoformat()}",
        f"**{tr.t('project')}:** {project_name}",
    ]
    if sprint_end:
        lines.append(f"**{tr.t('sprint_end')}:** {sprint_end.isoformat()}")
    lines.append("")
    return lines


def _generate_summary_section(tr: Translator, summary: dict) -> list[str]:
    """Generate summary section."""
    lines = []

    if summary.get("hours_progress_percent") is not None:
        lines.extend([
            f"## {tr.t('summary')}",
            "",
            f"| {tr.t('metric')} | {tr.t('value')} |",
            "|--------|-------|",
            f"| {tr.t('estimated_hours')} | {summary['total_estimated_hours']:.1f} |",
            f"| {tr.t('actual_hours')} | {summary['total_actual_hours']:.1f} |",
            f"| {tr.t('progress')} | {summary['hours_progress_percent']:.1f}% |",
            "",
        ])
    else:
        lines.extend([
            f"## {tr.t('summary')}",
            "",
            f"| {tr.t('metric')} | {tr.t('value')} |",
            "|--------|-------|",
            f"| {tr.t('total_issues')} | {summary['total']} |",
            f"| {tr.t('closed')} | {summary['closed_count']} |",
            f"| {tr.t('progress')} | {summary['progress_percent']:.1f}% |",
            "",
        ])

    # Status breakdown
    lines.append(f"### {tr.t('by_status')}")
    lines.append("")
    lines.append(f"| {tr.t('status')} | {tr.t('count')} |")
    lines.append("|--------|-------|")
    for status, count in summary["by_status"].items():
        lines.append(f"| {status} | {count} |")

    return lines


def _generate_at_risk_section(tr: Translator, at_risk_tasks: list[dict], capacity: float) -> list[str]:
    """Generate at-risk tasks section."""
    lines = [
        f"## {tr.t('at_risk_tasks')}",
        "",
    ]

    if at_risk_tasks:
        lines.append(f"| {tr.t('issue')} | Summary | {tr.t('required')} | {tr.t('capacity')} | {tr.t('days')} | {tr.t('reason')} |")
        lines.append("|-------|---------|----------|----------|------|--------|")
        for task in at_risk_tasks:
            issue_key = task.get("issueKey", task.get("key_id", "?"))
            summary_text = task.get("summary", "")[:40]
            velocity = task["risk"]["required_velocity"]
            days = task["risk"]["days_remaining"]
            gap = task["risk"].get("capacity_gap", velocity - capacity)
            reason = tr.t("at_risk_reason", velocity=velocity, capacity=capacity, gap=gap)
            lines.append(f"| {issue_key} | {summary_text} | {velocity:.1f}h/day | {capacity:.1f}h/day | {days} | {reason} |")
    else:
        lines.append(tr.t("no_at_risk_tasks"))

    lines.append("")
    return lines


def _generate_late_tasks_section(tr: Translator, late_tasks: list[dict]) -> list[str]:
    """Generate late tasks section."""
    lines = [
        f"## {tr.t('late_tasks')}",
        "",
    ]

    if late_tasks:
        lines.append(f"| {tr.t('issue')} | Summary | {tr.t('assignee')} | {tr.t('days_overdue')} |")
        lines.append("|-------|---------|----------|--------------|")
        for task in late_tasks:
            issue_key = task.get("issueKey", task.get("key_id", "?"))
            summary_text = task.get("summary", "")[:40]
            assignee = task.get("assignee", {})
            assignee_name = assignee.get("name", tr.t("unassigned")) if assignee else tr.t("unassigned")
            days = task["days_overdue"]
            lines.append(f"| {issue_key} | {summary_text} | {assignee_name} | {days} |")
    else:
        lines.append(tr.t("no_late_tasks"))

    lines.append("")
    return lines


def _generate_brse_insights_section(
    tr: Translator,
    today: date,
    hours_per_day: float,
    sprint_end: Optional[date],
    member_capacity: list[dict]
) -> list[str]:
    """Generate BrSE insights section."""
    lines = []

    sprint_info = f" | **{tr.t('sprint_end')}:** {sprint_end.isoformat()}" if sprint_end else ""
    lines.extend([
        f"## {tr.t('brse_insights_title')}",
        "",
        f"**{tr.t('analysis_date')}:** {today.isoformat()} | **{tr.t('capacity')}:** {hours_per_day}h/day{sprint_info}",
        "",
        tr.t("gap_note"),
        "",
    ])

    # Capacity overview table
    lines.append(f"### {tr.t('capacity_overview')}")
    lines.append("")
    lines.append(f"| {tr.t('member')} | {tr.t('status')} | {tr.t('tasks')} | {tr.t('workload')} | {tr.t('capacity')} | {tr.t('gap')} | {tr.t('velocity')} |")
    lines.append("|--------|--------|-------|----------|----------|-----|----------|")

    surplus_members = []
    deficit_members = []

    for mc in member_capacity:
        status_icon = {
            MemberStatus.SURPLUS: tr.t("status_surplus"),
            MemberStatus.ON_TRACK: tr.t("status_on_track"),
            MemberStatus.AT_RISK: tr.t("status_at_risk"),
            MemberStatus.OVERLOADED: tr.t("status_overloaded")
        }.get(mc["status"], "?")

        gap_str = f"+{mc['gap']:.0f}h" if mc["gap"] >= 0 else f"{mc['gap']:.0f}h"
        vel_str = f"{mc['required_velocity']}h/day" if mc["required_velocity"] else "-"

        lines.append(
            f"| {mc['name']} | {status_icon} | {mc['task_count']} | "
            f"{mc['total_remaining_hours']:.0f}h | {mc['available_hours']:.0f}h | "
            f"{gap_str} | {vel_str} |"
        )

        if mc["status"] == MemberStatus.SURPLUS:
            surplus_members.append(mc)
        elif mc["status"] in (MemberStatus.AT_RISK, MemberStatus.OVERLOADED):
            deficit_members.append(mc)

    lines.append("")

    # Detailed per-member analysis
    lines.extend(_generate_member_details(tr, member_capacity))

    # Re-estimation alerts
    lines.extend(_generate_reestimate_alerts(tr, member_capacity))

    # Reschedule alerts (impossible schedules: start=due with remaining > capacity)
    lines.extend(_generate_reschedule_alerts(tr, member_capacity))

    # Recommendations
    lines.extend(_generate_recommendations(tr, surplus_members, deficit_members, member_capacity))

    return lines


def _generate_member_details(tr: Translator, member_capacity: list[dict]) -> list[str]:
    """Generate detailed per-member analysis."""
    lines = []

    for mc in member_capacity:
        status_icon = {
            MemberStatus.SURPLUS: "✅",
            MemberStatus.ON_TRACK: "🟢",
            MemberStatus.AT_RISK: "⚠️",
            MemberStatus.OVERLOADED: "🔴"
        }.get(mc["status"], "")

        lines.extend([
            f"### {status_icon} {mc['name']}",
            "",
        ])

        # Capacity summary
        if mc["gap"] >= 0:
            gap_str = tr.t("gap_surplus", gap=mc["gap"])
        else:
            gap_str = tr.t("gap_deficit", gap=mc["gap"])

        earliest_str = mc["earliest_due"].isoformat() if mc["earliest_due"] else "-"
        latest_str = mc["latest_due"].isoformat() if mc.get("latest_due") else "-"

        lines.extend([
            f"- **{tr.t('tasks')}:** " + tr.t("tasks_open", count=mc['task_count']),
            f"- **{tr.t('workload')}:** " + tr.t("workload_remaining", hours=mc['total_remaining_hours']),
            f"- **{tr.t('capacity')}:** " + tr.t("capacity_detail", hours=mc['available_hours'], days=mc['working_days'], per_day=mc['hours_per_day']),
            f"- **{tr.t('gap')}:** {gap_str}",
            f"- **{tr.t('due_range')}:** {earliest_str} → {latest_str}",
            "",
        ])

        # Task details table
        if mc["tasks"]:
            lines.append(tr.t('task_gap_note'))
            lines.append("")
            lines.append(f"| {tr.t('issue')} | Summary | {tr.t('est')} | {tr.t('act')} | {tr.t('due')} | {tr.t('gap')} | {tr.t('alert')} |")
            lines.append("|-------|---------|-----|-----|-----|-----|-------|")
            for t in mc["tasks"]:
                due = t["due_date"].strftime("%m/%d") if t["due_date"] else "-"

                if t["gap"] is None:
                    gap = "?"
                elif t["gap"] >= 0:
                    gap = f"+{t['gap']:.0f}h"
                else:
                    gap = f"{t['gap']:.0f}h"

                if t.get("needs_reschedule"):
                    alert = tr.t("alert_resched")
                elif t["needs_reestimate"]:
                    alert = tr.t("alert_reest")
                elif t["gap"] is not None and t["gap"] < 0:
                    alert = tr.t("alert_deficit")
                else:
                    alert = tr.t("alert_ok")

                lines.append(
                    f"| {t['issue_key']} | {t['summary'][:25]} | "
                    f"{t['estimated']:.0f}h | {t['actual']:.0f}h | {due} | {gap} | {alert} |"
                )
            lines.append("")

    return lines


def _generate_reestimate_alerts(tr: Translator, member_capacity: list[dict]) -> list[str]:
    """Generate re-estimation alerts section."""
    lines = []

    reestimate_tasks = []
    for mc in member_capacity:
        for t in mc["tasks"]:
            if t["needs_reestimate"]:
                reestimate_tasks.append({
                    "member": mc["name"],
                    "issue_key": t["issue_key"],
                    "summary": t["summary"],
                    "estimated": t["estimated"],
                    "actual": t["actual"],
                    "overtime_percent": t["overtime_percent"],
                    "due_date": t["due_date"]
                })

    if reestimate_tasks:
        lines.extend([
            f"### {tr.t('reest_title')}",
            "",
            tr.t("reest_desc"),
            tr.t("reest_action"),
            "",
            f"| {tr.t('issue')} | Summary | {tr.t('est')} | {tr.t('act')} | {tr.t('over_pct')} | {tr.t('due')} | {tr.t('assignee')} |",
            "|-------|---------|-----|--------|-------|-----|----------|",
        ])
        for rt in sorted(reestimate_tasks, key=lambda x: x["overtime_percent"], reverse=True):
            due = rt["due_date"].strftime("%m/%d") if rt["due_date"] else "-"
            lines.append(
                f"| {rt['issue_key']} | {rt['summary'][:20]} | "
                f"{rt['estimated']:.0f}h | {rt['actual']:.0f}h | "
                f"**{rt['overtime_percent']:.0f}%** | {due} | {rt['member']} |"
            )
        lines.append("")

    return lines


def _generate_reschedule_alerts(tr: Translator, member_capacity: list[dict]) -> list[str]:
    """Generate reschedule alerts for impossible schedules (start=due with remaining > capacity)."""
    lines = []

    reschedule_tasks = []
    for mc in member_capacity:
        for t in mc["tasks"]:
            if t.get("needs_reschedule"):
                reschedule_tasks.append({
                    "member": mc["name"],
                    "issue_key": t["issue_key"],
                    "summary": t["summary"],
                    "start_date": t["start_date"],
                    "due_date": t["due_date"],
                    "remaining_hours": t["remaining_hours"],
                    "hours_per_day": mc["hours_per_day"]
                })

    if reschedule_tasks:
        lines.extend([
            f"### {tr.t('resched_title')}",
            "",
            tr.t("resched_desc"),
            tr.t("resched_action"),
            "",
            f"| {tr.t('issue')} | Summary | Start | {tr.t('due')} | Remaining | {tr.t('capacity')} | {tr.t('assignee')} |",
            "|-------|---------|-------|-----|-----------|----------|----------|",
        ])
        for rt in reschedule_tasks:
            start = rt["start_date"].strftime("%m/%d") if rt["start_date"] else "-"
            due = rt["due_date"].strftime("%m/%d") if rt["due_date"] else "-"
            lines.append(
                f"| {rt['issue_key']} | {rt['summary'][:20]} | "
                f"{start} | {due} | "
                f"**{rt['remaining_hours']:.0f}h** | {rt['hours_per_day']:.0f}h/day | {rt['member']} |"
            )
        lines.append("")

    return lines


def _generate_recommendations(
    tr: Translator,
    surplus_members: list[dict],
    deficit_members: list[dict],
    member_capacity: list[dict]
) -> list[str]:
    """Generate recommendations section."""
    lines = [
        f"### {tr.t('recommendations')}",
        "",
    ]

    # Check for re-estimate and reschedule tasks
    reestimate_count = sum(
        1 for mc in member_capacity for t in mc["tasks"] if t["needs_reestimate"]
    )
    reschedule_count = sum(
        1 for mc in member_capacity for t in mc["tasks"] if t.get("needs_reschedule")
    )

    if not deficit_members and not surplus_members and reestimate_count == 0 and reschedule_count == 0:
        lines.append(tr.t("on_track_msg"))
    else:
        if reschedule_count > 0:
            lines.append(tr.t("urgent_resched", count=reschedule_count))
        if reestimate_count > 0:
            lines.append(tr.t("urgent_reest", count=reestimate_count))

        if surplus_members:
            total_surplus = sum(m["gap"] for m in surplus_members)
            names = ", ".join(m["name"] for m in surplus_members)
            lines.append(tr.t("available_support", names=names, hours=total_surplus))

        if deficit_members:
            for m in deficit_members:
                lines.append(tr.t("needs_help", name=m['name'], hours=abs(m['gap'])))

        if surplus_members and deficit_members:
            lines.append("")
            lines.append(tr.t("suggested_action"))

    lines.append("")
    return lines


def _generate_schedule_warnings_section(tr: Translator, schedule_warnings: list[dict]) -> list[str]:
    """Generate schedule warnings section."""
    lines = [
        f"## {tr.t('schedule_warnings')}",
        "",
        tr.t("schedule_warnings_desc"),
        tr.t("schedule_warnings_action"),
        "",
        f"| {tr.t('issue')} | Summary | {tr.t('date_type')} | {tr.t('date')} | {tr.t('reason')} |",
        "|-------|---------|-----------|------|--------|",
    ]

    for w in schedule_warnings:
        date_str = w["date"].strftime("%Y-%m-%d (%a)")
        lines.append(
            f"| {w['issue_key']} | {w['summary']} | "
            f"{w['date_type']} | {date_str} | {w['reason']} |"
        )

    lines.extend([
        "",
        tr.t("action_required"),
        "",
    ])

    return lines


def _generate_capacity_exceeded_section(tr: Translator, unscheduled_info: dict) -> list[str]:
    """Generate capacity exceeded section."""
    lines = [
        "",
        f"## {tr.t('capacity_exceeded')}",
        "",
        f"**{tr.t('total_workload')}:** {unscheduled_info['total_remaining']:.0f}h",
        f"**{tr.t('available_capacity')}:** {unscheduled_info['total_available']:.0f}h",
        f"**{tr.t('deficit')}:** {unscheduled_info['deficit']:.0f}h",
        "",
    ]

    if unscheduled_info["unscheduled_tasks"]:
        lines.extend([
            tr.t("unscheduled_desc"),
            "",
            f"| {tr.t('issue')} | {tr.t('need')} | {tr.t('scheduled')} | {tr.t('shortfall')} | {tr.t('due')} | {tr.t('assignee')} |",
            "|-------|------|-----------|-----------|-----|----------|",
        ])
        for task in unscheduled_info["unscheduled_tasks"]:
            due_str = task["due_date"].strftime("%m/%d") if task.get("due_date") else "-"
            scheduled = task.get("scheduled", 0)
            shortfall = task.get("shortfall", task["remaining"])
            lines.append(
                f"| {task['issue_key']} | {task['remaining']:.0f}h | "
                f"{scheduled:.0f}h | {shortfall:.0f}h | {due_str} | {task['assignee']} |"
            )
        lines.append("")

    lines.extend([
        f"### {tr.t('priority_question_title')}",
        "",
        tr.t("priority_question_desc"),
        "",
        tr.t("priority_q1"),
        tr.t("priority_q2"),
        tr.t("priority_q3"),
        tr.t("priority_q4"),
        "",
        tr.t("priority_footer"),
        "",
    ])

    return lines
