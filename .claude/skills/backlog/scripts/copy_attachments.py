"""Copy attachments between issues in Nulab Backlog."""

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


def copy_attachments(source_issue_id: str, dest_issue_id: str) -> dict:
    """Copy all attachments from source to destination issue.

    Args:
        source_issue_id: Source issue ID (e.g., 'HB21373-123')
        dest_issue_id: Destination issue ID

    Returns:
        Dictionary with copy results
    """
    space_url = os.getenv("NULAB_SPACE_URL")
    api_key = os.getenv("NULAB_API_KEY")

    if not space_url or not api_key:
        return {"error": "Missing NULAB_SPACE_URL or NULAB_API_KEY in .env"}

    try:
        api = BacklogAPI(space_url=space_url, api_key=api_key)
        copied = api.copy_attachments(source_issue_id, dest_issue_id)

        return {
            "success": True,
            "copied_count": len(copied),
            "attachments": [
                {"name": a.name, "id": a.id}
                for a in copied
            ]
        }
    except BacklogAPIError as e:
        return {"success": False, "error": str(e)}
    except Exception as e:
        return {"success": False, "error": str(e)}


def main():
    parser = argparse.ArgumentParser(description="Copy attachments between issues")
    parser.add_argument("--source", required=True, help="Source issue ID")
    parser.add_argument("--dest", required=True, help="Destination issue ID")

    args = parser.parse_args()

    result = copy_attachments(args.source, args.dest)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
