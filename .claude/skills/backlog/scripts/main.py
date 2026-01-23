"""Main entry point for Backlog Automation Skill (DEPRECATED).

NOTE: This file is kept for backward compatibility.
The new workflow uses helper scripts directly:
- fetch_ticket.py
- create_ticket.py
- create_subtask.py
- copy_attachments.py
- add_comment.py

Translation is now performed in-conversation by Claude Code.
"""

import os
import sys
import argparse
import json
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
from nulab_client import BacklogAPI, BacklogAPIError
from language_detector import LanguageDetector

# Load environment variables from skill directory
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)


def fetch_and_show(ticket_id: str) -> None:
    """Fetch ticket and display info for Claude Code workflow.

    Args:
        ticket_id: Source ticket ID (e.g., "HB21373-123")
    """
    space_url = os.getenv("NULAB_SPACE_URL")
    api_key = os.getenv("NULAB_API_KEY")

    if not space_url or not api_key:
        print(json.dumps({"error": "Missing NULAB_SPACE_URL or NULAB_API_KEY"}))
        sys.exit(1)

    try:
        api = BacklogAPI(space_url=space_url, api_key=api_key)
        issue = api.get_issue(ticket_id)
        detector = LanguageDetector()

        # Detect source language
        source_lang = detector.detect(issue.summary)
        target_lang = detector.get_target_language(source_lang)

        result = {
            "success": True,
            "ticket": {
                "id": issue.id,
                "key_id": issue.key_id,
                "summary": issue.summary,
                "description": issue.description or "",
                "issue_type_id": issue.issue_type_id,
                "priority_id": issue.priority_id,
                "attachments_count": len(issue.attachments)
            },
            "language": {
                "source": source_lang.value,
                "target": target_lang.value
            }
        }

        print(json.dumps(result, ensure_ascii=False, indent=2))

    except BacklogAPIError as e:
        print(json.dumps({"success": False, "error": str(e)}))
        sys.exit(1)
    except Exception as e:
        print(json.dumps({"success": False, "error": str(e)}))
        sys.exit(1)


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Backlog Automation - Fetch ticket info for Claude Code workflow"
    )
    parser.add_argument(
        "ticket_id",
        help="Source ticket ID (e.g., HB21373-123)"
    )

    args = parser.parse_args()
    fetch_and_show(args.ticket_id)


if __name__ == "__main__":
    main()
