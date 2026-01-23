"""Create subtask in Nulab Backlog."""
# -*- coding: utf-8 -*-

import os
import sys
import json
import argparse
from pathlib import Path

# Fix Windows console encoding for Unicode (Vietnamese/Japanese)
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
from nulab_client import BacklogAPI, BacklogAPIError

# Load environment variables
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)


def create_subtask(
    parent_id: int,
    summary: str,
    issue_type_id: int,
    priority_id: int
) -> dict:
    """Create subtask under parent issue.

    Args:
        parent_id: Parent issue ID
        summary: Subtask summary
        issue_type_id: Issue type ID
        priority_id: Priority ID

    Returns:
        Dictionary with created subtask data
    """
    space_url = os.getenv("NULAB_SPACE_URL")
    api_key = os.getenv("NULAB_API_KEY")
    project_id = os.getenv("NULAB_PROJECT_ID")

    if not all([space_url, api_key, project_id]):
        return {"error": "Missing environment variables"}

    try:
        api = BacklogAPI(space_url=space_url, api_key=api_key)
        project = api.get_project(project_id)

        subtask = api.create_subtask(
            project_id=project.id,
            parent_id=parent_id,
            summary=summary,
            issueTypeId=issue_type_id,
            priorityId=priority_id
        )

        return {
            "success": True,
            "id": subtask.id,
            "key_id": subtask.key_id,
            "summary": subtask.summary
        }
    except BacklogAPIError as e:
        return {"success": False, "error": str(e)}
    except Exception as e:
        return {"success": False, "error": str(e)}


def main():
    parser = argparse.ArgumentParser(description="Create subtask in Nulab Backlog")
    parser.add_argument("--parent-id", type=int, required=True, help="Parent issue ID")
    parser.add_argument("--summary", required=True, help="Subtask summary")
    parser.add_argument("--issue-type-id", type=int, required=True, help="Issue type ID")
    parser.add_argument("--priority-id", type=int, required=True, help="Priority ID")

    args = parser.parse_args()

    result = create_subtask(
        parent_id=args.parent_id,
        summary=args.summary,
        issue_type_id=args.issue_type_id,
        priority_id=args.priority_id
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
