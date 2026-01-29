"""Entry point for bk-status skill."""

import os
import sys
import argparse
from datetime import datetime, date
from pathlib import Path

# Add parent dir to path for relative imports
sys.path.insert(0, str(Path(__file__).parent))

from backlog_client import BacklogClient, BacklogAPIError
from status_analyzer import StatusAnalyzer
from calendar_utils import CalendarConfig, get_sprint_info, get_all_member_capacities, sync_sprint_from_api
from translations import get_lang_from_master_yaml, SUPPORTED_LANGS
import yaml


def load_dotenv_file():
    """Load .env file from brsekit directory (shared master data).

    Hierarchy: brsekit/.env (shared) -> skill-specific/.env (override)
    """
    skills_dir = Path(__file__).parent.parent.parent  # .claude/skills/

    # Load shared brsekit/.env first
    brsekit_env = skills_dir / "brsekit" / ".env"
    if brsekit_env.exists():
        with open(brsekit_env, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, _, value = line.partition("=")
                    os.environ.setdefault(key.strip(), value.strip())

    # Load skill-specific .env (can override shared values)
    skill_env = skills_dir / "bk-status" / ".env"
    if skill_env.exists():
        with open(skill_env, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, _, value = line.partition("=")
                    os.environ[key.strip()] = value.strip()  # Override


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


def parse_backlog_date(date_str: str) -> date | None:
    """Parse Backlog API date string to date object.

    Backlog API returns dates in ISO datetime format: '2026-02-16T00:00:00Z'

    Args:
        date_str: Date string from Backlog API

    Returns:
        date object or None if parsing fails
    """
    if not date_str:
        return None
    try:
        # Handle ISO datetime format: 2026-02-16T00:00:00Z
        if "T" in date_str:
            return datetime.fromisoformat(date_str.replace("Z", "+00:00")).date()
        # Handle simple date format: 2026-02-16
        return date.fromisoformat(date_str)
    except (ValueError, TypeError):
        return None


def get_active_milestone_end_date(milestones: list[dict], today: date) -> tuple[date | None, str | None]:
    """Find active milestone and return its end date.

    An active milestone is:
    - Not archived
    - Has releaseDueDate >= today (not past)

    If multiple active milestones, return the one with earliest releaseDueDate.

    Args:
        milestones: List of milestone dicts from Backlog API
        today: Current date

    Returns:
        Tuple of (end_date, milestone_name) or (None, None) if no active milestone
    """
    active_milestones = []

    for ms in milestones:
        if ms.get("archived"):
            continue

        end_date = parse_backlog_date(ms.get("releaseDueDate"))
        if not end_date:
            continue

        if end_date >= today:
            active_milestones.append((end_date, ms.get("name", "Unknown")))

    if not active_milestones:
        return None, None

    # Sort by end_date and return earliest
    active_milestones.sort(key=lambda x: x[0])
    return active_milestones[0]


def validate_master_data(users: list, milestones: list = None) -> list[str]:
    """Validate master.yaml against Backlog API data.

    Checks for:
    - Members in Backlog not in master.yaml
    - Members in master.yaml not in Backlog
    - Sprint/milestone date mismatches

    Args:
        users: List of User objects from Backlog API
        milestones: List of milestone/version dicts from Backlog API (optional)

    Returns:
        List of warning messages
    """
    warnings = []
    skill_dir = Path(__file__).parent.parent.parent
    yaml_path = skill_dir / "brsekit" / "master.yaml"

    if not yaml_path.exists():
        warnings.append("Warning: master.yaml not found - cannot validate")
        return warnings

    try:
        with open(yaml_path, "r", encoding="utf-8") as f:
            master_data = yaml.safe_load(f)
    except Exception as e:
        warnings.append(f"Warning: Cannot read master.yaml - {e}")
        return warnings

    # Validate members
    team_data = master_data.get("team", {})
    master_members = {m.get("name") for m in team_data.get("members", [])}
    backlog_members = {u.name for u in users}

    # Members in Backlog but not in master.yaml
    new_members = backlog_members - master_members
    if new_members:
        warnings.append(f"New members in Backlog (add to master.yaml): {', '.join(new_members)}")

    # Members in master.yaml but not in Backlog
    removed_members = master_members - backlog_members
    if removed_members:
        warnings.append(f"Members in master.yaml not found in Backlog: {', '.join(removed_members)}")

    return warnings


def get_output_path(project_name: str) -> Path:
    """Generate output path with timestamp.

    Args:
        project_name: Project name for filename

    Returns:
        Path to output file
    """
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    safe_name = project_name.replace(" ", "-").replace("/", "-")
    output_dir = Path("./project-status")
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir / f"{timestamp}_{safe_name}-status.md"


def main():
    """Run status check."""
    parser = argparse.ArgumentParser(description="Check project status")
    parser.add_argument(
        "--threshold",
        type=int,
        default=5,
        help="Overloaded threshold (default: 5)"
    )
    parser.add_argument(
        "--hours-per-day",
        type=float,
        default=None,
        help="Working hours per day (default: from master.yaml, typically 6h = 75%% of 8h)"
    )
    parser.add_argument(
        "--sprint-end",
        type=str,
        default=None,
        help="Sprint end date (YYYY-MM-DD) for overall capacity calculation"
    )
    parser.add_argument(
        "--lang",
        type=str,
        default=None,
        choices=SUPPORTED_LANGS,
        help="Report language: en (English), vi (Vietnamese), ja (Japanese). Default: from master.yaml"
    )
    args = parser.parse_args()

    # Load config from .env file
    load_dotenv_file()
    space_url, api_key, project_id = load_env()

    # Load calendar config from master.yaml (holidays, working days)
    calendar = CalendarConfig.from_master_yaml()
    print(f"Calendar loaded: {len(calendar.holidays)} holidays, working days: {sorted(calendar.working_days)}")

    # Load sprint info from master.yaml (will be auto-synced from API)
    sprint_info = get_sprint_info()
    if sprint_info:
        print(f"Sprint: {sprint_info.get('sprint_name')}")

    # Determine report language: CLI > master.yaml > default
    if args.lang:
        report_lang = args.lang
    else:
        report_lang = get_lang_from_master_yaml()
    print(f"Report language: {report_lang}")

    try:
        # Initialize API client
        client = BacklogClient(space_url, api_key)

        # Fetch data
        print(f"Fetching data for project {project_id}...")
        project = client.get_project(project_id)
        statuses = client.get_project_statuses(project_id)
        users = client.get_project_users(project_id)
        issues = client.list_issues(project.id)
        milestones = client.get_milestones(project_id)

        print(f"Found {len(issues)} issues, {len(users)} members, {len(milestones)} milestones")

        today = date.today()

        # Auto-sync sprint from Backlog API milestone to master.yaml
        if milestones:
            api_end, api_name = get_active_milestone_end_date(milestones, today)
            if api_end and api_name:
                synced, sync_msg = sync_sprint_from_api(api_name, api_end)
                if synced:
                    print(f"[SYNC] {sync_msg}")
                    # Reload sprint_info after sync
                    sprint_info = get_sprint_info()

        # Validate master.yaml against Backlog data
        validation_warnings = validate_master_data(users)
        for warning in validation_warnings:
            print(f"⚠️  {warning}")

        # Analyze with calendar support
        analyzer = StatusAnalyzer(
            [{"id": s.id, "name": s.name} for s in statuses],
            closed_status_names=["Closed"],
            calendar=calendar
        )

        # Convert Issue objects to dicts for analyzer
        issue_dicts = []
        for issue in issues:
            issue_dict = {
                "id": issue.id,
                "issueKey": issue.key_id,
                "summary": issue.summary,
                "status": {"id": issue.status_id},
                "assignee": {"id": issue.assignee_id} if issue.assignee_id else None,
                "startDate": issue.start_date,
                "dueDate": issue.due_date,
                "estimatedHours": issue.estimated_hours,
                "actualHours": issue.actual_hours,
            }
            issue_dicts.append(issue_dict)

        user_dicts = [{"id": u.id, "name": u.name} for u in users]

        # Generate report - default capacity: CLI > master.yaml > default 6h
        default_hours_per_day = args.hours_per_day or calendar.default_hours_per_day
        # Load per-member capacities from master.yaml
        member_capacities = get_all_member_capacities()
        if member_capacities:
            capacity_info = ", ".join(f"{n}: {c}h" for n, c in member_capacities.items())
            print(f"Member capacities: {capacity_info}")
        print(f"Default capacity: {default_hours_per_day}h/day (daily_standup: {calendar.daily_standup})")

        # Sprint end: CLI arg override > master.yaml (synced from API)
        sprint_end = None
        sprint_source = None
        if args.sprint_end:
            try:
                sprint_end = date.fromisoformat(args.sprint_end)
                sprint_source = "CLI override"
            except ValueError:
                print(f"Warning: Invalid sprint-end date format: {args.sprint_end}")

        # Use master.yaml as single source of truth (already synced from API above)
        if not sprint_end and sprint_info.get("end_date"):
            sprint_end = sprint_info["end_date"]
            sprint_source = "master.yaml"

        if sprint_end:
            print(f"Sprint end: {sprint_end} (source: {sprint_source})")

        report = analyzer.generate_report(
            issue_dicts,
            user_dicts,
            today,
            project_name=project.name,
            capacity=default_hours_per_day,  # Default capacity for risk calculation
            hours_per_day=default_hours_per_day,
            sprint_end=sprint_end,
            lang=report_lang,
            member_capacities=member_capacities  # Per-member capacities
        )

        # Save to file
        output_path = get_output_path(project.name)
        output_path.write_text(report, encoding="utf-8")
        print(f"\nReport saved to: {output_path}")

        # Show summary
        summary = analyzer.get_summary(issue_dicts)
        late_tasks = analyzer.get_late_tasks(issue_dicts, today)
        at_risk_tasks = analyzer.get_at_risk_tasks(issue_dicts, today, default_hours_per_day)
        overloaded = analyzer.get_overloaded_members(
            issue_dicts, user_dicts, threshold=args.threshold
        )

        print(f"\nSummary:")
        print(f"  Total issues: {len(issues)}")
        if summary.get("hours_progress_percent") is not None:
            print(f"  Hours progress: {summary['hours_progress_percent']:.1f}%")
        print(f"  Late tasks: {len(late_tasks)}")
        print(f"  At-risk tasks: {len(at_risk_tasks)}")
        if at_risk_tasks:
            for task in at_risk_tasks[:3]:  # Show top 3
                v = task["risk"]["required_velocity"]
                d = task["risk"]["days_remaining"]
                print(f"    - {task['issueKey']}: {v:.1f}h/day needed, {d} days left")
        if overloaded:
            print(f"  Overloaded members (>{args.threshold} issues):")
            for member in overloaded:
                print(f"    - {member['name']}: {member['open_count']} issues")

        # BrSE Insights - Member Capacity
        member_capacity = analyzer.analyze_member_capacity(
            issue_dicts, user_dicts, today, default_hours_per_day, sprint_end, member_capacities
        )
        if member_capacity:
            print(f"\nBrSE Insights (Default: {default_hours_per_day}h/day):")
            for mc in member_capacity:
                status_map = {
                    "MemberStatus.SURPLUS": "[+] Surplus",
                    "MemberStatus.ON_TRACK": "[=] On Track",
                    "MemberStatus.AT_RISK": "[!] At Risk",
                    "MemberStatus.OVERLOADED": "[X] Overload"
                }
                status = status_map.get(str(mc["status"]), str(mc["status"]))
                gap_str = f"+{mc['gap']:.0f}h" if mc["gap"] >= 0 else f"{mc['gap']:.0f}h"
                print(f"  - {mc['name']}: {status} | {mc['task_count']} tasks | "
                      f"{mc['total_remaining_hours']:.0f}h left | {mc['working_days']}d avail | gap: {gap_str}")

    except BacklogAPIError as e:
        print(f"API Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
