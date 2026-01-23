#!/usr/bin/env python3
"""Hook to prevent accidental ticket deletion on Backlog.

Exit codes:
- 0: Allow the command
- 2: Block the command (stderr message shown to Claude)
"""

import json
import sys
import re


def is_delete_command(command: str) -> tuple[bool, str]:
    """Check if the command attempts to delete a Backlog ticket."""
    command_lower = command.lower()

    delete_patterns = [
        # HTTP DELETE to issues endpoint (lowercase since we check command_lower)
        (r'curl.*-x\s*delete.*/issues', 'DELETE request to /issues'),
        (r'curl.*--request\s*delete.*/issues', 'DELETE request to /issues'),
        # Python requests
        (r'requests\.delete.*/issues', 'requests.delete to /issues'),
        (r'_request.*delete.*/issues', '_request DELETE to /issues'),
        # Function names
        (r'delete_issue', 'delete_issue function'),
        (r'delete_ticket', 'delete_ticket function'),
        # API with delete method
        (r'backlog.*delete', 'Backlog delete operation'),
        # Script with delete flag
        (r'\.py.*--delete|--delete.*\.py', 'Script with --delete flag'),
    ]

    for pattern, reason in delete_patterns:
        if re.search(pattern, command_lower):
            return True, reason

    return False, ''


def main():
    try:
        input_data = json.load(sys.stdin)

        tool_name = input_data.get('tool_name', '')
        if tool_name != 'Bash':
            sys.exit(0)

        tool_input = input_data.get('tool_input', {})
        command = tool_input.get('command', '')

        if not command:
            sys.exit(0)

        is_blocked, reason = is_delete_command(command)

        if is_blocked:
            # Write to stderr - this message is shown to Claude
            print(f"BLOCKED: Ticket deletion is not allowed.", file=sys.stderr)
            print(f"Reason: {reason}", file=sys.stderr)
            print(f"Please use Backlog web interface to delete tickets.", file=sys.stderr)
            sys.exit(2)

        sys.exit(0)

    except json.JSONDecodeError:
        sys.exit(0)
    except Exception:
        sys.exit(0)


if __name__ == '__main__':
    main()