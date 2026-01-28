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
    args = parser.parse_args()

    # Load config
    space_url, api_key, project_id = load_env()

    try:
        # Initialize API client
        client = BacklogClient(space_url, api_key)

        # Fetch data
        print(f"Fetching data for project {project_id}...")
        project = client.get_project(project_id)
        statuses = client.get_project_statuses(project_id)
        users = client.get_project_users(project_id)
        issues = client.list_issues(project.id)

        print(f"Found {len(issues)} issues, {len(users)} members")

        # Analyze
        analyzer = StatusAnalyzer(
            [{"id": s.id, "name": s.name} for s in statuses],
            closed_status_names=["Closed"]
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
                "dueDate": issue.due_date,
            }
            issue_dicts.append(issue_dict)

        user_dicts = [{"id": u.id, "name": u.name} for u in users]

        # Generate report
        today = date.today()
        report = analyzer.generate_report(
            issue_dicts,
            user_dicts,
            today,
            project_name=project.name
        )

        # Save to file
        output_path = get_output_path(project.name)
        output_path.write_text(report, encoding="utf-8")
        print(f"\nReport saved to: {output_path}")

        # Show summary
        late_tasks = analyzer.get_late_tasks(issue_dicts, today)
        overloaded = analyzer.get_overloaded_members(
            issue_dicts, user_dicts, threshold=args.threshold
        )

        print(f"\nSummary:")
        print(f"  Total issues: {len(issues)}")
        print(f"  Late tasks: {len(late_tasks)}")
        if overloaded:
            print(f"  Overloaded members (>{args.threshold} issues):")
            for member in overloaded:
                print(f"    - {member['name']}: {member['open_count']} issues")

    except BacklogAPIError as e:
        print(f"API Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
