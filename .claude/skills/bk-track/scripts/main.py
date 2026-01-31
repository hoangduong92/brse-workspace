#!/usr/bin/env python3
"""bk-track CLI - Project tracking for BrseKit."""
import argparse
import os
import sys
import io
from datetime import date, datetime
from pathlib import Path
import yaml

# Fix Windows encoding for Unicode output
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# Add scripts to path for relative imports
sys.path.insert(0, os.path.dirname(__file__))

# Add common and lib to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../common"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../lib"))

from status_analyzer import StatusAnalyzer
from formatters.markdown import MarkdownFormatter
from formatters.pptx_formatter import PptxFormatter
from calendar_utils import CalendarConfig, get_sprint_info, get_all_member_capacities, sync_sprint_from_api
from translations import get_lang_from_master_yaml, SUPPORTED_LANGS

# Import ReportGenerator for 'report' command only
try:
    # bk-track specific report generator (for weekly reports)
    from report_generator_weekly import ReportGenerator
except ImportError:
    # Fallback - will handle in cmd_report
    ReportGenerator = None

try:
    from backlog.client import BacklogClient
except ImportError:
    BacklogClient = None

# Import vault for time log tracking
try:
    from vault import TimeLogStore
except ImportError:
    TimeLogStore = None

# Import backlog sync for time logs (from bk-recall)
try:
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../bk-recall/scripts/sources"))
    from backlog_sync import BacklogSync
except ImportError:
    BacklogSync = None


def load_brsekit_env():
    """Load env vars from shared brsekit .env file."""
    env_path = os.path.join(os.path.dirname(__file__), "../../brsekit/.env")
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ.setdefault(key.strip(), value.strip())


def parse_backlog_date(date_str: str):
    """Parse Backlog API date string to date object."""
    if not date_str:
        return None
    try:
        if "T" in date_str:
            return datetime.fromisoformat(date_str.replace("Z", "+00:00")).date()
        return date.fromisoformat(date_str)
    except (ValueError, TypeError):
        return None


def get_active_milestone_end_date(milestones, today):
    """Find active milestone and return its end date."""
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
    active_milestones.sort(key=lambda x: x[0])
    return active_milestones[0]


def get_output_path(project_name: str) -> Path:
    """Generate output path with timestamp."""
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    safe_name = project_name.replace(" ", "-").replace("/", "-")
    output_dir = Path(__file__).parent.parent / "project-status"
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir / f"{timestamp}_{safe_name}-status.md"


def cmd_status(args):
    """Handle status command - full bk-status implementation."""
    # Import skill_utils for multi-project support
    try:
        from skill_utils import setup_project_env, validate_project_exists
    except ImportError:
        setup_project_env = None
        validate_project_exists = None

    # Get project from args (positional or flag)
    project = getattr(args, "project", None) or getattr(args, "project_flag", None)

    # Multi-project mode: load env from project directory
    if project and setup_project_env:
        if validate_project_exists and not validate_project_exists(project):
            # Check if it's actually a valid Backlog project key (not in projects/)
            # Fall back to global env if project dir doesn't exist
            load_brsekit_env()
            space_url = os.getenv("NULAB_SPACE_URL")
            api_key = os.getenv("NULAB_API_KEY")
            project_id = project
        else:
            pm, env_loader = setup_project_env(project)
            space_url = env_loader.get("NULAB_SPACE_URL", project) or env_loader.get("BACKLOG_SPACE_URL", project)
            api_key = env_loader.get("NULAB_API_KEY", project) or env_loader.get("BACKLOG_API_KEY", project)
            project_id = env_loader.get("NULAB_PROJECT_ID", project) or project
    else:
        # Fallback: load from brsekit env
        load_brsekit_env()
        space_url = os.getenv("NULAB_SPACE_URL")
        api_key = os.getenv("NULAB_API_KEY")
        project_id = os.getenv("NULAB_PROJECT_ID") or project

    if not space_url or not api_key or not project_id:
        print("Error: Missing Backlog environment variables")
        print("\nFor multi-project setup, run:")
        print(f"  /bk-init {project or 'PROJECT'}")
        print("\nOr set in .claude/skills/brsekit/.env:")
        print("  NULAB_SPACE_URL=yourspace.backlog.com")
        print("  NULAB_API_KEY=your-api-key")
        print("  NULAB_PROJECT_ID=PROJECTKEY")
        return

    if not BacklogClient:
        print("Error: BacklogClient not available. Install backlog package.")
        return

    # Load calendar config
    calendar = CalendarConfig.from_master_yaml()
    print(f"Calendar loaded: {len(calendar.holidays)} holidays, working days: {sorted(calendar.working_days)}")

    # Load sprint info
    sprint_info = get_sprint_info()
    if sprint_info:
        print(f"Sprint: {sprint_info.get('sprint_name')}")

    # Determine report language
    report_lang = args.lang if args.lang else get_lang_from_master_yaml()
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

        # Sync time logs from Backlog activities to vault (if not --no-sync)
        time_log_data = None
        if not args.no_sync and BacklogSync:
            try:
                syncer = BacklogSync(space_url, api_key)
                sync_result = syncer.sync_time_logs_only(project_id, limit=500)
                if sync_result.get("time_logs_synced", 0) > 0:
                    print(f"Synced {sync_result['time_logs_synced']} time log entries to vault")
            except Exception as e:
                print(f"Warning: Time log sync failed: {e}")

        # Read time logs from vault for report (use project-scoped vault)
        if TimeLogStore:
            try:
                time_log_store = TimeLogStore(project=project) if project else TimeLogStore()
                # Get sprint start date if available
                sprint_start = sprint_info.get("start_date") if sprint_info else None
                time_log_data = time_log_store.get_daily_summary(
                    project_id,
                    sprint_start or date.today().replace(day=1),  # Default: start of month
                    date.today()
                )
                if time_log_data:
                    total_entries = sum(len(days) for days in time_log_data.values())
                    print(f"Loaded {total_entries} time log days from vault")
            except Exception as e:
                print(f"Warning: Failed to read time logs from vault: {e}")

        today = date.today()

        # Auto-sync sprint from Backlog API milestone
        if milestones:
            api_end, api_name = get_active_milestone_end_date(milestones, today)
            if api_end and api_name:
                synced, sync_msg = sync_sprint_from_api(api_name, api_end)
                if synced:
                    print(f"[SYNC] {sync_msg}")
                    sprint_info = get_sprint_info()

        # Analyze with calendar support
        analyzer = StatusAnalyzer(
            [{"id": s.id, "name": s.name} for s in statuses],
            closed_status_names=["Closed"],
            calendar=calendar
        )

        # Build user id->name mapping
        user_map = {u.id: u.name for u in users}
        user_dicts = [{"id": u.id, "name": u.name} for u in users]

        # Convert Issue objects to dicts
        issue_dicts = []
        for issue in issues:
            assignee_dict = None
            if issue.assignee_id:
                assignee_dict = {
                    "id": issue.assignee_id,
                    "name": user_map.get(issue.assignee_id, "Unknown")
                }
            issue_dict = {
                "id": issue.id,
                "issueKey": issue.key_id,
                "summary": issue.summary,
                "status": {"id": issue.status_id},
                "assignee": assignee_dict,
                "startDate": issue.start_date,
                "dueDate": issue.due_date,
                "estimatedHours": issue.estimated_hours,
                "actualHours": issue.actual_hours,
            }
            issue_dicts.append(issue_dict)

        # Load capacities
        default_hours_per_day = args.hours_per_day or calendar.default_hours_per_day
        member_capacities = get_all_member_capacities()
        if member_capacities:
            capacity_info = ", ".join(f"{n}: {c}h" for n, c in member_capacities.items())
            print(f"Member capacities: {capacity_info}")
        print(f"Default capacity: {default_hours_per_day}h/day (daily_standup: {calendar.daily_standup})")

        # Sprint end: CLI arg > master.yaml
        sprint_end = None
        if args.sprint_end:
            try:
                sprint_end = date.fromisoformat(args.sprint_end)
            except ValueError:
                print(f"Warning: Invalid sprint-end date format: {args.sprint_end}")

        if not sprint_end and sprint_info.get("end_date"):
            sprint_end = sprint_info["end_date"]

        if sprint_end:
            print(f"Sprint end: {sprint_end}")

        # Get sprint_start for extended Gantt view
        sprint_start = sprint_info.get("start_date") if sprint_info else None

        # Generate report with extended Gantt support
        report = analyzer.generate_report(
            issue_dicts,
            user_dicts,
            today,
            project_name=project.name,
            capacity=default_hours_per_day,
            hours_per_day=default_hours_per_day,
            sprint_end=sprint_end,
            lang=report_lang,
            member_capacities=member_capacities,
            sprint_start=sprint_start,
            time_log_data=time_log_data
        )

        # Save to file
        output_path = get_output_path(project.name)
        output_path.write_text(report, encoding="utf-8")
        print(f"\nReport saved to: {output_path}")

        # Show summary
        summary = analyzer.get_summary(issue_dicts)
        late_tasks = analyzer.get_late_tasks(issue_dicts, today)
        at_risk_tasks = analyzer.get_at_risk_tasks(issue_dicts, today, default_hours_per_day)

        print(f"\nSummary:")
        print(f"  Total issues: {len(issues)}")
        if summary.get("hours_progress_percent") is not None:
            print(f"  Hours progress: {summary['hours_progress_percent']:.1f}%")
        print(f"  Late tasks: {len(late_tasks)}")
        print(f"  At-risk tasks: {len(at_risk_tasks)}")

        # BrSE Insights
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

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return


def cmd_report(args):
    """Handle report command."""
    generator = ReportGenerator(period_days=args.period)
    data = generator.generate(args.project)

    if not data:
        print("Error: Failed to generate report. Check Backlog configuration.")
        return

    if args.format == "pptx":
        # PPTX format
        if not args.output:
            print("Error: --output is required for PPTX format")
            return

        try:
            formatter = PptxFormatter()
            output_path = formatter.generate(data, args.output)
            print(f"PPTX report saved to: {output_path}")
        except FileNotFoundError as e:
            print(f"Error: {e}")
        except Exception as e:
            print(f"Error generating PPTX: {e}")
        return

    # Markdown format
    output = generator.format_markdown(data)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"Report saved to: {args.output}")
    else:
        print(output)


def cmd_summary(args):
    """Handle summary command."""
    generator = ReportGenerator()
    data = generator.generate(args.project)

    if not data:
        print("Error: Failed to generate summary.")
        return

    summary = generator.format_summary(data)
    print(summary)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="bk-track - Project tracking for BrseKit",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  bk-track status HB21373           Status for project HB21373
  bk-track status --project ABC     Alternative syntax
  bk-track report HB21373 -f pptx   Weekly report in PPTX
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # status command
    status_parser = subparsers.add_parser("status", help="Project status report (same as bk-status)")
    status_parser.add_argument("project", nargs="?", help="Project name (e.g., HB21373)")
    status_parser.add_argument("--project", "-p", dest="project_flag",
                                help="Project name (alternative to positional)")
    status_parser.add_argument("--threshold", "-t", type=int, default=5,
                                help="Overloaded threshold (default: 5)")
    status_parser.add_argument("--hours-per-day", type=float, default=None,
                                help="Working hours per day (default: from master.yaml)")
    status_parser.add_argument("--sprint-end", type=str, default=None,
                                help="Sprint end date (YYYY-MM-DD)")
    status_parser.add_argument("--lang", "-l", default=None,
                                choices=SUPPORTED_LANGS,
                                help="Report language: en, vi, ja (default: from master.yaml)")
    status_parser.add_argument("--no-sync", action="store_true",
                                help="Skip syncing time logs from Backlog activities")
    status_parser.set_defaults(func=cmd_status)

    # report command
    report_parser = subparsers.add_parser("report", help="Weekly report")
    report_parser.add_argument("--period", type=int, default=7,
                                help="Report period in days")
    report_parser.add_argument("--format", "-f", choices=["md", "pptx"],
                                default="md", help="Output format")
    report_parser.add_argument("--output", "-o", help="Output file path")
    report_parser.set_defaults(func=cmd_report)

    # summary command
    summary_parser = subparsers.add_parser("summary", help="Quick summary")
    summary_parser.set_defaults(func=cmd_summary)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Pass project to subcommand if set
    if hasattr(args, "func"):
        args.func(args)


if __name__ == "__main__":
    main()
