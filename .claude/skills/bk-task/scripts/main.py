"""Entry point for bk-task skill.

Parse unstructured Japanese input into structured Backlog tasks.
Supports customer emails, chat messages, meeting minutes.
"""

import os
import sys
import argparse
import json
from pathlib import Path

# Fix Windows console encoding for Japanese characters
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Add parent dir to path for relative imports
sys.path.insert(0, str(Path(__file__).parent))

from task_parser import TaskParser, ParsedTask, parse_multiple_tasks
from task_creator import TaskCreator


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
    skill_env = skills_dir / "bk-task" / ".env"
    if skill_env.exists():
        with open(skill_env, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, _, value = line.partition("=")
                    os.environ[key.strip()] = value.strip()  # Override


def load_env() -> tuple:
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


def format_task_preview(task: ParsedTask, index: int = None) -> str:
    """Format task for human-readable preview.

    Args:
        task: ParsedTask instance
        index: Optional task number for multiple tasks

    Returns:
        Formatted string
    """
    lines = []

    if index is not None:
        lines.append(f"\n--- Task {index + 1} ---")

    lines.append(f"  Summary: {task.summary}")
    lines.append(f"  Type: {task.task_type.value}")
    lines.append(f"  Priority: {task.priority.value}")

    if task.deadline_date:
        lines.append(f"  Due Date: {task.deadline_date.strftime('%Y-%m-%d')} ({task.deadline_type.value})")
    elif task.deadline_type:
        lines.append(f"  Deadline: {task.deadline_type.value}")

    if task.estimated_hours:
        lines.append(f"  Estimated: {task.estimated_hours}h")

    if task.assignee_hint:
        lines.append(f"  Assignee: {task.assignee_hint}")

    if task.description:
        desc_preview = task.description[:100] + "..." if len(task.description) > 100 else task.description
        lines.append(f"  Description: {desc_preview}")

    if task.warnings:
        lines.append(f"  ⚠️ Warnings: {', '.join(task.warnings)}")

    return "\n".join(lines)


def output_json(tasks: list, created_results: list = None):
    """Output tasks as JSON for programmatic use.

    Args:
        tasks: List of ParsedTask instances
        created_results: Optional list of created issue results
    """
    output = []
    for i, task in enumerate(tasks):
        task_data = {
            "summary": task.summary,
            "task_type": task.task_type.value,
            "priority": task.priority.value,
            "deadline_type": task.deadline_type.value if task.deadline_type else None,
            "deadline_date": task.deadline_date.strftime("%Y-%m-%d") if task.deadline_date else None,
            "estimated_hours": task.estimated_hours,
            "assignee_hint": task.assignee_hint,
            "description": task.description,
            "warnings": task.warnings,
            "source_type": task.source_type,
        }
        if created_results and i < len(created_results):
            task_data["created"] = created_results[i]
        output.append(task_data)

    print(json.dumps(output, ensure_ascii=False, indent=2))


def main():
    """Run task parsing and optional creation."""
    parser = argparse.ArgumentParser(
        description="Parse unstructured Japanese input into Backlog tasks"
    )
    parser.add_argument(
        "input",
        nargs="?",
        help="Input text (or use --file, or pipe via stdin)"
    )
    parser.add_argument(
        "--file",
        "-f",
        type=str,
        help="Read input from file"
    )
    parser.add_argument(
        "--project",
        "-p",
        type=str,
        help="Backlog project key (overrides NULAB_PROJECT_ID)"
    )
    parser.add_argument(
        "--source-type",
        "-s",
        type=str,
        choices=["comment", "email", "chat", "minutes"],
        default="comment",
        help="Source type for context-aware parsing (default: comment)"
    )
    parser.add_argument(
        "--dry-run",
        "-d",
        action="store_true",
        help="Parse only, don't create tasks (preview mode)"
    )
    parser.add_argument(
        "--yes",
        "-y",
        action="store_true",
        help="Auto-confirm task creation (skip prompt)"
    )
    parser.add_argument(
        "--json",
        "-j",
        action="store_true",
        help="Output as JSON (for programmatic use)"
    )
    args = parser.parse_args()

    # Load .env
    load_dotenv_file()

    # Get input text
    input_text = None
    if args.input:
        input_text = args.input
    elif args.file:
        input_path = Path(args.file)
        if not input_path.exists():
            print(f"Error: File not found: {args.file}")
            sys.exit(1)
        input_text = input_path.read_text(encoding="utf-8")
    elif not sys.stdin.isatty():
        input_text = sys.stdin.read()

    if not input_text or not input_text.strip():
        print("Error: No input provided")
        print("\nUsage:")
        print("  bk-task '明日までにログイン画面を田中さんが作成'")
        print("  bk-task --file input.txt")
        print("  echo 'タスク内容' | bk-task")
        sys.exit(1)

    # Parse input - use parse_multiple_tasks for bullet lists, single parse for simple input
    tasks = parse_multiple_tasks(input_text, source_type=args.source_type)

    # If parse_multiple_tasks returns empty, try single task parse
    if not tasks:
        task_parser = TaskParser()
        single_task = task_parser.parse(input_text, source_type=args.source_type)
        if single_task and single_task.summary:
            tasks = [single_task]

    if not tasks:
        print("No tasks could be parsed from input.")
        sys.exit(0)

    # Preview mode (dry run)
    if args.dry_run:
        if args.json:
            output_json(tasks)
        else:
            print(f"Parsed {len(tasks)} task(s):\n")
            for i, task in enumerate(tasks):
                print(format_task_preview(task, i if len(tasks) > 1 else None))
        sys.exit(0)

    # Create mode - need environment variables
    space_url, api_key, project_id = load_env()
    project_key = args.project or project_id

    # Show preview
    if not args.json:
        print(f"Parsed {len(tasks)} task(s) for project {project_key}:\n")
        for i, task in enumerate(tasks):
            print(format_task_preview(task, i if len(tasks) > 1 else None))
        print()

    # Confirm creation
    if not args.yes and not args.json:
        try:
            response = input(f"Create {len(tasks)} task(s) on Backlog? [y/N]: ")
            if response.lower() not in ("y", "yes"):
                print("Cancelled.")
                sys.exit(0)
        except (EOFError, KeyboardInterrupt):
            print("\nCancelled.")
            sys.exit(0)

    # Import BacklogClient dynamically (only needed for create mode)
    try:
        # Use common/backlog client
        common_path = Path(__file__).parent.parent.parent / "common"
        sys.path.insert(0, str(common_path))
        from backlog.client import BacklogClient
    except ImportError:
        print("Error: BacklogClient not found. Install common module.")
        sys.exit(1)

    # Create tasks
    try:
        client = BacklogClient(space_url, api_key)
        creator = TaskCreator(client, project_key)

        if not args.json:
            print(f"\nCreating tasks...")

        results = creator.create_multiple_tasks(tasks)

        if args.json:
            output_json(tasks, results)
        else:
            print(f"\nCreated {len(results)} task(s):")
            for result in results:
                issue_key = result.get("issueKey", "Unknown")
                summary = result.get("summary", "")[:50]
                print(f"  ✓ {issue_key}: {summary}")

    except Exception as e:
        print(f"Error creating tasks: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
