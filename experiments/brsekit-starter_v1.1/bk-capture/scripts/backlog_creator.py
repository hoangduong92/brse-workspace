"""Backlog task creator for bk-capture."""
import sys
import os
from pathlib import Path
from typing import Optional

# Add common to path
_skills_root = Path(__file__).parent.parent.parent
_common_dir = _skills_root / "common"
sys.path.insert(0, str(_common_dir))

from backlog.client import BacklogClient, BacklogAPIError


class BacklogCreator:
    """Create tasks on Backlog from captured items."""

    def __init__(self):
        """Initialize with BacklogClient from environment."""
        self.client = self._init_client()
        self.project_id = os.getenv("BACKLOG_PROJECT_ID")

        if not self.project_id:
            raise ValueError("BACKLOG_PROJECT_ID not set in environment")

    def _init_client(self) -> BacklogClient:
        """Initialize Backlog client from environment variables."""
        space_url = os.getenv("BACKLOG_SPACE_URL")
        api_key = os.getenv("BACKLOG_API_KEY")

        if not space_url or not api_key:
            raise ValueError("BACKLOG_SPACE_URL and BACKLOG_API_KEY must be set")

        return BacklogClient(space_url=space_url, api_key=api_key)

    def create_task(self, task: dict) -> dict:
        """Create single task on Backlog.

        Args:
            task: {title, description, priority, deadline, assignee}

        Returns:
            Created issue data with issueKey, id, etc.
        """
        # Map priority to Backlog priority ID (2=High, 3=Medium, 4=Low)
        priority_map = {"high": 2, "medium": 3, "low": 4}
        priority_id = priority_map.get(task.get("priority", "medium"), 3)

        # Get default issue type (usually first one)
        issue_types = self.client.get_project_issue_types(self.project_id)
        if not issue_types:
            raise BacklogAPIError("No issue types found for project")
        issue_type_id = issue_types[0]["id"]

        # Get assignee ID if specified
        assignee_id = None
        if task.get("assignee"):
            assignee_id = self._find_user_id(task["assignee"])

        # Create issue payload
        payload = {
            "projectId": self.project_id,
            "summary": task["title"],
            "description": task.get("description", ""),
            "issueTypeId": issue_type_id,
            "priorityId": priority_id
        }

        if task.get("deadline"):
            payload["dueDate"] = task["deadline"]

        if assignee_id:
            payload["assigneeId"] = assignee_id

        try:
            return self.client.create_issue(**payload)
        except BacklogAPIError as e:
            raise BacklogAPIError(f"Failed to create task: {e}")

    def create_batch(self, tasks: list[dict]) -> list[dict]:
        """Create multiple tasks with confirmation.

        Args:
            tasks: List of task dicts

        Returns:
            List of created issue data
        """
        if not tasks:
            return []

        # Show preview and confirm
        if not self.confirm_creation(tasks):
            print("Cancelled by user.")
            return []

        # Create tasks one by one
        created = []
        for i, task in enumerate(tasks, 1):
            print(f"Creating task {i}/{len(tasks)}: {task['title'][:50]}...")
            try:
                issue = self.create_task(task)
                created.append(issue)
                print(f"  ✓ Created: {issue['issueKey']}")
            except BacklogAPIError as e:
                print(f"  ✗ Failed: {e}")

        return created

    def confirm_creation(self, tasks: list[dict]) -> bool:
        """Show preview and get user confirmation.

        Args:
            tasks: List of tasks to create

        Returns:
            True if user confirms, False otherwise
        """
        print("\n" + "=" * 60)
        print(f"Preview: {len(tasks)} tasks to create on Backlog")
        print("=" * 60 + "\n")

        for i, task in enumerate(tasks, 1):
            print(f"{i}. {task['title']}")
            print(f"   Priority: {task.get('priority', 'medium')}")
            if task.get("deadline"):
                print(f"   Deadline: {task['deadline']}")
            if task.get("assignee"):
                print(f"   Assignee: {task['assignee']}")
            print()

        print("=" * 60)
        response = input("Create these tasks on Backlog? [y/N]: ").strip().lower()
        return response in ["y", "yes"]

    def _find_user_id(self, username: str) -> Optional[int]:
        """Find user ID by username or name.

        Args:
            username: Username or display name

        Returns:
            User ID if found, None otherwise
        """
        try:
            users = self.client.get_project_users(self.project_id)
            for user in users:
                if user.user_id == username or user.name == username:
                    return user.id
        except BacklogAPIError:
            pass

        return None
