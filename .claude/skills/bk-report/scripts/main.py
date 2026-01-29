"""Entry point for bk-report skill."""

import os
import sys
import argparse
from datetime import datetime, date, timedelta
from pathlib import Path

# Add parent dirs to path for imports
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "common"))

from backlog.client import BacklogClient, BacklogAPIError
from backlog.models import Issue

from report_templates import generate_report, get_lang_from_master_yaml, SUPPORTED_LANGS
from report_stats import (
    calculate_stats,
    filter_completed_this_week,
    filter_in_progress,
    filter_next_week_tasks,
    filter_late_tasks,
)


def load_dotenv_file():
    """Load .env file from skill directory."""
    skill_dir = Path(__file__).parent.parent
    env_file = skill_dir / ".env"
    if env_file.exists():
        with open(env_file, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, _, value = line.partition("=")
                    os.environ.setdefault(key.strip(), value.strip())


def load_env() -> tuple[str, str, str]:
    """Load environment variables.

    Returns:
        Tuple of (space_url, api_key, project_id)
    """
    space_url = os.getenv("NULAB_SPACE_URL")
    api_key = os.getenv("NULAB_API_KEY")
    project_id = os.getenv("NULAB_PROJECT_ID")

    missing = []
    if not space_url:
        missing.append("NULAB_SPACE_URL")
    if not api_key:
        missing.append("NULAB_API_KEY")
    if not project_id:
        missing.append("NULAB_PROJECT_ID")

    if missing:
        print(f"Error: Missing environment variables: {', '.join(missing)}")
        print("\nSet in .env file:")
        print("  NULAB_SPACE_URL=yourspace.backlog.com")
        print("  NULAB_API_KEY=your-api-key")
        print("  NULAB_PROJECT_ID=PROJECTKEY")
        sys.exit(1)

    return space_url, api_key, project_id


def parse_period(period_str: str) -> tuple[date, date]:
    """Parse period string to start and end dates.

    Args:
        period_str: Period in format 'YYYY-MM-DD:YYYY-MM-DD'

    Returns:
        Tuple of (start_date, end_date)
    """
    parts = period_str.split(":")
    if len(parts) != 2:
        raise ValueError(f"Invalid period format: {period_str}. Use YYYY-MM-DD:YYYY-MM-DD")

    start = date.fromisoformat(parts[0])
    end = date.fromisoformat(parts[1])
    return start, end


def get_default_week() -> tuple[date, date]:
    """Get default week period (last 7 days).

    Returns:
        Tuple of (start_date, end_date)
    """
    today = date.today()
    # Default: last Monday to today (or previous Sunday)
    days_since_monday = today.weekday()
    week_start = today - timedelta(days=days_since_monday + 7)
    week_end = week_start + timedelta(days=6)
    return week_start, week_end


def get_output_path(project_name: str) -> Path:
    """Generate output path with timestamp.

    Args:
        project_name: Project name for filename

    Returns:
        Path to output file
    """
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    safe_name = project_name.replace(" ", "-").replace("/", "-")
    output_dir = Path("./weekly-reports")
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir / f"{timestamp}_{safe_name}-weekly.md"


def main():
    """Run weekly report generation."""
    parser = argparse.ArgumentParser(description="Generate weekly progress report")
    parser.add_argument(
        "--lang",
        type=str,
        default=None,
        choices=SUPPORTED_LANGS,
        help="Report language: ja (Japanese), vi (Vietnamese), en (English)"
    )
    parser.add_argument(
        "--period",
        type=str,
        default=None,
        help="Report period: YYYY-MM-DD:YYYY-MM-DD (default: last week)"
    )
    parser.add_argument(
        "--reporter",
        type=str,
        default=None,
        help="Reporter name"
    )
    args = parser.parse_args()

    # Load config from .env file
    load_dotenv_file()
    space_url, api_key, project_id = load_env()

    # Determine report language
    if args.lang:
        report_lang = args.lang
    else:
        report_lang = get_lang_from_master_yaml()
    print(f"Report language: {report_lang}")

    # Determine period
    if args.period:
        try:
            week_start, week_end = parse_period(args.period)
        except ValueError as e:
            print(f"Error: {e}")
            sys.exit(1)
    else:
        week_start, week_end = get_default_week()

    print(f"Report period: {week_start} to {week_end}")

    try:
        # Initialize API client
        client = BacklogClient(space_url, api_key)

        # Fetch data
        print(f"Fetching data for project {project_id}...")
        project = client.get_project(project_id)
        issues_raw = client.list_issues(project.id)

        # Convert Issue objects to dicts for processing
        issues = []
        for issue in issues_raw:
            issues.append({
                "id": issue.id,
                "issueKey": issue.key_id,
                "summary": issue.summary,
                "status": {"id": issue.status_id, "name": get_status_name(client, project_id, issue.status_id)},
                "assignee": {"id": issue.assignee_id, "name": get_assignee_name(client, project_id, issue.assignee_id)} if issue.assignee_id else None,
                "dueDate": issue.due_date,
                "estimatedHours": issue.estimated_hours,
                "actualHours": issue.actual_hours,
                "created": issue.created,
                "updated": issue.updated,
            })

        print(f"Found {len(issues)} issues")

        today = date.today()

        # Calculate statistics
        stats = calculate_stats(issues)
        print(f"Stats: {stats['completed']}/{stats['total']} completed ({stats['completion_rate']}%)")

        # Filter tasks
        completed_tasks = filter_completed_this_week(issues, week_start, week_end)
        in_progress_tasks = filter_in_progress(issues)
        next_week_tasks = filter_next_week_tasks(issues, week_end)
        late_tasks = filter_late_tasks(issues, today)

        print(f"Completed this week: {len(completed_tasks)}")
        print(f"In progress: {len(in_progress_tasks)}")
        print(f"Next week: {len(next_week_tasks)}")
        print(f"Late: {len(late_tasks)}")

        # Generate report
        report_data = {
            "project_name": project.name,
            "period_start": week_start.isoformat(),
            "period_end": week_end.isoformat(),
            "stats": stats,
            "completed_tasks": completed_tasks,
            "in_progress_tasks": in_progress_tasks,
            "next_week_tasks": next_week_tasks,
            "late_tasks": late_tasks,
        }

        report = generate_report(report_data, lang=report_lang, reporter=args.reporter)

        # Save to file
        output_path = get_output_path(project.name)
        output_path.write_text(report, encoding="utf-8")
        print(f"\nReport saved to: {output_path}")

    except BacklogAPIError as e:
        print(f"API Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


# Cache for status and user lookups
_status_cache = {}
_user_cache = {}


def get_status_name(client: BacklogClient, project_id: str, status_id: int) -> str:
    """Get status name from ID with caching."""
    global _status_cache
    if project_id not in _status_cache:
        statuses = client.get_project_statuses(project_id)
        _status_cache[project_id] = {s.id: s.name for s in statuses}
    return _status_cache[project_id].get(status_id, f"Status-{status_id}")


def get_assignee_name(client: BacklogClient, project_id: str, assignee_id: int) -> str:
    """Get assignee name from ID with caching."""
    global _user_cache
    if project_id not in _user_cache:
        users = client.get_project_users(project_id)
        _user_cache[project_id] = {u.id: u.name for u in users}
    return _user_cache[project_id].get(assignee_id, f"User-{assignee_id}")


if __name__ == "__main__":
    main()
