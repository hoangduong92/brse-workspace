"""Fetch ticket from Nulab Backlog and output as JSON."""

import os
import sys
import json
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
from nulab_client import BacklogAPI, BacklogAPIError

# Load environment variables
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)


def fetch_ticket(ticket_id: str) -> dict:
    """Fetch ticket and return as dictionary.

    Args:
        ticket_id: Ticket ID (e.g., 'HB21373-123')

    Returns:
        Dictionary with ticket data
    """
    space_url = os.getenv("NULAB_SPACE_URL")
    api_key = os.getenv("NULAB_API_KEY")

    if not space_url or not api_key:
        return {"error": "Missing NULAB_SPACE_URL or NULAB_API_KEY in .env"}

    try:
        api = BacklogAPI(space_url=space_url, api_key=api_key)
        issue = api.get_issue(ticket_id)

        return {
            "success": True,
            "id": issue.id,
            "key_id": issue.key_id,
            "summary": issue.summary,
            "description": issue.description or "",
            "issue_type_id": issue.issue_type_id,
            "priority_id": issue.priority_id,
            "status_id": issue.status_id,
            "attachments_count": len(issue.attachments),
            "attachments": [
                {"id": a.id, "name": a.name, "size": a.size}
                for a in issue.attachments
            ]
        }
    except BacklogAPIError as e:
        return {"success": False, "error": str(e)}
    except Exception as e:
        return {"success": False, "error": str(e)}


def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Usage: fetch_ticket.py <ticket_id>"}))
        sys.exit(1)

    ticket_id = sys.argv[1]
    result = fetch_ticket(ticket_id)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
