"""Report templates for bk-report skill.

Multi-language templates for weekly progress reports (ja, vi, en).
"""

from typing import Optional

SUPPORTED_LANGS = ["ja", "vi", "en"]


TEMPLATES = {
    "ja": {
        "title": "週次進捗報告",
        "project": "プロジェクト",
        "period": "期間",
        "reporter": "報告者",
        "summary": "概要",
        "completed_tasks": "完了タスク",
        "in_progress": "進行中",
        "open_tasks": "未着手",
        "late_tasks": "遅延",
        "progress_rate": "進捗率",
        "accomplishments": "今週の成果",
        "current_work": "進行中のタスク",
        "next_week": "来週の予定",
        "issues_risks": "課題・リスク",
        "comments": "所感",
        "table_headers": {
            "id": "ID",
            "task": "タスク",
            "assignee": "担当",
            "status": "ステータス",
            "due_date": "予定日",
            "days_late": "遅延日数",
        },
        "status_names": {
            "completed": "完了",
            "in_progress": "進行中",
            "open": "未着手",
            "late": "遅延",
        },
        "no_data": "該当なし",
        "days_late_suffix": "日遅延",
    },
    "vi": {
        "title": "Báo Cáo Tiến Độ Tuần",
        "project": "Dự án",
        "period": "Kỳ báo cáo",
        "reporter": "Người báo cáo",
        "summary": "Tổng quan",
        "completed_tasks": "Task hoàn thành",
        "in_progress": "Đang thực hiện",
        "open_tasks": "Chưa bắt đầu",
        "late_tasks": "Trễ hạn",
        "progress_rate": "Tỷ lệ hoàn thành",
        "accomplishments": "Kết quả tuần này",
        "current_work": "Task đang thực hiện",
        "next_week": "Kế hoạch tuần tới",
        "issues_risks": "Vấn đề & Rủi ro",
        "comments": "Nhận xét",
        "table_headers": {
            "id": "ID",
            "task": "Task",
            "assignee": "Phụ trách",
            "status": "Trạng thái",
            "due_date": "Ngày dự kiến",
            "days_late": "Số ngày trễ",
        },
        "status_names": {
            "completed": "Hoàn thành",
            "in_progress": "Đang làm",
            "open": "Chưa bắt đầu",
            "late": "Trễ hạn",
        },
        "no_data": "Không có",
        "days_late_suffix": " ngày trễ",
    },
    "en": {
        "title": "Weekly Progress Report",
        "project": "Project",
        "period": "Period",
        "reporter": "Reporter",
        "summary": "Summary",
        "completed_tasks": "Completed",
        "in_progress": "In Progress",
        "open_tasks": "Open",
        "late_tasks": "Late",
        "progress_rate": "Progress Rate",
        "accomplishments": "This Week's Accomplishments",
        "current_work": "Current Work",
        "next_week": "Next Week Plan",
        "issues_risks": "Issues & Risks",
        "comments": "Comments",
        "table_headers": {
            "id": "ID",
            "task": "Task",
            "assignee": "Assignee",
            "status": "Status",
            "due_date": "Due Date",
            "days_late": "Days Late",
        },
        "status_names": {
            "completed": "Completed",
            "in_progress": "In Progress",
            "open": "Open",
            "late": "Late",
        },
        "no_data": "None",
        "days_late_suffix": " days late",
    },
}


def get_template(lang: str) -> dict:
    """Get template for specified language.

    Args:
        lang: Language code (ja, vi, en)

    Returns:
        Template dictionary
    """
    if lang not in SUPPORTED_LANGS:
        lang = "ja"  # Default to Japanese
    return TEMPLATES[lang]


def get_lang_from_master_yaml() -> str:
    """Get default language from brsekit/master.yaml.

    Returns:
        Language code (ja, vi, en), defaults to 'ja'
    """
    from pathlib import Path
    import yaml

    skill_dir = Path(__file__).parent.parent.parent
    yaml_path = skill_dir / "brsekit" / "master.yaml"

    if not yaml_path.exists():
        return "ja"

    try:
        with open(yaml_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return data.get("defaults", {}).get("report_language", "ja")
    except Exception:
        return "ja"


def format_tasks_table(
    tasks: list[dict],
    lang: str,
    include_days_late: bool = False
) -> str:
    """Format tasks as markdown table.

    Args:
        tasks: List of task dicts with keys: key, summary, assignee, status, due_date
        lang: Language code
        include_days_late: Include days late column

    Returns:
        Markdown table string
    """
    t = get_template(lang)
    h = t["table_headers"]

    if not tasks:
        return f"*{t['no_data']}*"

    # Build header
    if include_days_late:
        header = f"| {h['id']} | {h['task']} | {h['assignee']} | {h['status']} | {h['days_late']} |"
        separator = "|------|------|------|------|------|"
    else:
        header = f"| {h['id']} | {h['task']} | {h['assignee']} | {h['due_date']} |"
        separator = "|------|------|------|------|"

    rows = [header, separator]

    for task in tasks:
        assignee = task.get("assignee", "-")
        if include_days_late:
            days_late = task.get("days_late", 0)
            late_str = f"{days_late}{t['days_late_suffix']}" if days_late > 0 else "-"
            row = f"| {task['key']} | {task['summary'][:30]} | {assignee} | {task['status']} | {late_str} |"
        else:
            due = task.get("due_date", "-")
            if due and len(due) > 10:
                due = due[:10]  # Format: YYYY-MM-DD
            row = f"| {task['key']} | {task['summary'][:30]} | {assignee} | {due} |"
        rows.append(row)

    return "\n".join(rows)


def generate_report(
    data: dict,
    lang: str = "ja",
    reporter: Optional[str] = None
) -> str:
    """Generate weekly report markdown.

    Args:
        data: Report data with keys:
            - project_name: Project name
            - period_start: Start date (YYYY-MM-DD)
            - period_end: End date (YYYY-MM-DD)
            - stats: Dict with completed, in_progress, open, late counts
            - completed_tasks: List of completed task dicts
            - in_progress_tasks: List of in-progress task dicts
            - next_week_tasks: List of next week task dicts
            - late_tasks: List of late task dicts with days_late
        lang: Language code (ja, vi, en)
        reporter: Reporter name

    Returns:
        Markdown report string
    """
    t = get_template(lang)
    stats = data.get("stats", {})

    # Calculate progress rate
    total = stats.get("total", 0)
    completed = stats.get("completed", 0)
    progress_rate = (completed / total * 100) if total > 0 else 0

    # Build report
    lines = [
        f"# {t['title']}",
        "",
        f"**{t['project']}:** {data.get('project_name', 'N/A')}  ",
        f"**{t['period']}:** {data.get('period_start')} - {data.get('period_end')}  ",
    ]

    if reporter:
        lines.append(f"**{t['reporter']}:** {reporter}  ")

    lines.extend([
        "",
        f"## 1. {t['summary']}",
        "",
        f"- {t['completed_tasks']}: {completed}",
        f"- {t['in_progress']}: {stats.get('in_progress', 0)}",
        f"- {t['open_tasks']}: {stats.get('open', 0)}",
        f"- {t['late_tasks']}: {stats.get('late', 0)}",
        f"- {t['progress_rate']}: {progress_rate:.0f}%",
        "",
        f"## 2. {t['accomplishments']}",
        "",
        format_tasks_table(data.get("completed_tasks", []), lang),
        "",
        f"## 3. {t['current_work']}",
        "",
        format_tasks_table(data.get("in_progress_tasks", []), lang),
        "",
        f"## 4. {t['next_week']}",
        "",
        format_tasks_table(data.get("next_week_tasks", []), lang),
        "",
        f"## 5. {t['issues_risks']}",
        "",
    ])

    late_tasks = data.get("late_tasks", [])
    if late_tasks:
        lines.append(format_tasks_table(late_tasks, lang, include_days_late=True))
    else:
        lines.append(f"*{t['no_data']}*")

    lines.extend([
        "",
        f"## 6. {t['comments']}",
        "",
        "(User input here)",
        "",
    ])

    return "\n".join(lines)
