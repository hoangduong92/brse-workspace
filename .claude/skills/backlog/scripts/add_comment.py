"""Add comment to issue in Nulab Backlog."""

import os
import sys
import json
import argparse
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
from nulab_client import BacklogAPI, BacklogAPIError

# Load environment variables
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)


def add_comment(issue_id: str, content: str) -> dict:
    """Add comment to issue.

    Args:
        issue_id: Issue ID (e.g., 'HB21373-123')
        content: Comment content

    Returns:
        Dictionary with result
    """
    space_url = os.getenv("NULAB_SPACE_URL")
    api_key = os.getenv("NULAB_API_KEY")

    if not space_url or not api_key:
        return {"error": "Missing NULAB_SPACE_URL or NULAB_API_KEY in .env"}

    try:
        api = BacklogAPI(space_url=space_url, api_key=api_key)
        comment = api.add_comment(issue_id, content)

        return {
            "success": True,
            "comment_id": comment.id
        }
    except BacklogAPIError as e:
        return {"success": False, "error": str(e)}
    except Exception as e:
        return {"success": False, "error": str(e)}


def main():
    parser = argparse.ArgumentParser(description="Add comment to issue")
    parser.add_argument("--issue-id", required=True, help="Issue ID")
    parser.add_argument("--content", required=True, help="Comment content")

    args = parser.parse_args()

    result = add_comment(args.issue_id, args.content)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
