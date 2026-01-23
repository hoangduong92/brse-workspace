"""Create ticket in Nulab Backlog."""
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


def create_ticket(
    summary: str,
    description: str,
    issue_type_id: int,
    priority_id: int
) -> dict:
    """Create ticket and return result.

    Args:
        summary: Ticket summary
        description: Ticket description
        issue_type_id: Issue type ID
        priority_id: Priority ID

    Returns:
        Dictionary with created ticket data
    """
    space_url = os.getenv("NULAB_SPACE_URL")
    api_key = os.getenv("NULAB_API_KEY")
    project_id = os.getenv("NULAB_PROJECT_ID")

    if not all([space_url, api_key, project_id]):
        return {"error": "Missing environment variables"}

    try:
        api = BacklogAPI(space_url=space_url, api_key=api_key)
        project = api.get_project(project_id)

        issue = api.create_issue(
            project_id=project.id,
            summary=summary,
            description=description,
            issueTypeId=issue_type_id,
            priorityId=priority_id
        )

        return {
            "success": True,
            "id": issue.id,
            "key_id": issue.key_id,
            "summary": issue.summary,
            "url": f"https://{space_url}/view/{issue.key_id}"
        }
    except BacklogAPIError as e:
        return {"success": False, "error": str(e)}
    except Exception as e:
        return {"success": False, "error": str(e)}


def main():
    parser = argparse.ArgumentParser(description="Create ticket in Nulab Backlog")
    parser.add_argument("--summary", required=True, help="Ticket summary")
    parser.add_argument("--description", required=True, help="Ticket description")
    parser.add_argument("--issue-type-id", type=int, required=True, help="Issue type ID")
    parser.add_argument("--priority-id", type=int, required=True, help="Priority ID")

    args = parser.parse_args()

    result = create_ticket(
        summary=args.summary,
        description=args.description,
        issue_type_id=args.issue_type_id,
        priority_id=args.priority_id
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
