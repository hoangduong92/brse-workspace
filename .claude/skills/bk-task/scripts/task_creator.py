"""Task creator for Backlog API integration.

Creates tasks on Backlog from parsed task data.
"""

from typing import Optional, Dict, Any, List
from datetime import date

from task_parser import ParsedTask, TaskType, Priority


def map_task_type_to_backlog(task_type: TaskType) -> str:
    """Map TaskType enum to Backlog issue type name.

    Args:
        task_type: TaskType enum value

    Returns:
        Backlog issue type name (Bug or Task)
    """
    if task_type == TaskType.BUG:
        return "Bug"
    return "Task"


def map_priority_to_backlog(priority: Priority) -> int:
    """Map Priority enum to Backlog priority ID.

    Backlog priority IDs:
        2 = High
        3 = Normal
        4 = Low

    Args:
        priority: Priority enum value

    Returns:
        Backlog priority ID
    """
    priority_map = {
        Priority.HIGH: 2,
        Priority.NORMAL: 3,
        Priority.LOW: 4,
    }
    return priority_map.get(priority, 3)


def format_task_for_api(
    task: ParsedTask,
    project_id: int,
    issue_type_id: int,
    assignee_id: Optional[int] = None
) -> Dict[str, Any]:
    """Format ParsedTask for Backlog API.

    Args:
        task: ParsedTask instance
        project_id: Backlog project ID
        issue_type_id: Backlog issue type ID
        assignee_id: Optional assignee user ID

    Returns:
        Dictionary formatted for Backlog API
    """
    result = {
        "projectId": project_id,
        "summary": task.summary,
        "issueTypeId": issue_type_id,
        "priorityId": map_priority_to_backlog(task.priority),
    }

    if assignee_id is not None:
        result["assigneeId"] = assignee_id

    if task.deadline_date is not None:
        result["dueDate"] = task.deadline_date.strftime("%Y-%m-%d")

    if task.estimated_hours is not None:
        result["estimatedHours"] = task.estimated_hours

    if task.description:
        result["description"] = task.description

    return result


class TaskCreator:
    """Creates tasks on Backlog from parsed task data."""

    def __init__(self, client, project_key: str):
        """Initialize TaskCreator.

        Args:
            client: BacklogClient instance
            project_key: Backlog project key (e.g., "BKT")
        """
        self.client = client
        self.project_key = project_key
        self._project = None
        self._users = None
        self._issue_types = None

    @property
    def project(self):
        """Get project info (cached)."""
        if self._project is None:
            self._project = self.client.get_project(self.project_key)
        return self._project

    @property
    def users(self):
        """Get project users (cached)."""
        if self._users is None:
            self._users = self.client.get_project_users(self.project_key)
        return self._users

    @property
    def issue_types(self):
        """Get project issue types (cached)."""
        if self._issue_types is None:
            self._issue_types = self.client.get_project_issue_types(self.project_key)
        return self._issue_types

    def resolve_assignee(self, assignee_hint: Optional[str]) -> Optional[int]:
        """Resolve assignee hint to user ID.

        Args:
            assignee_hint: Name hint (e.g., "田中")

        Returns:
            User ID if found, None otherwise
        """
        if assignee_hint is None:
            return None

        for user in self.users:
            if user.name == assignee_hint:
                return user.id

        return None

    def get_issue_type_id(self, type_name: str) -> int:
        """Get issue type ID by name.

        Args:
            type_name: Issue type name (e.g., "Bug", "Task")

        Returns:
            Issue type ID (defaults to first type if not found)
        """
        for issue_type in self.issue_types:
            # Handle both dict and object formats
            name = issue_type.get("name") if isinstance(issue_type, dict) else issue_type.name
            type_id = issue_type.get("id") if isinstance(issue_type, dict) else issue_type.id
            if name == type_name:
                return type_id

        # Default to first issue type
        first = self.issue_types[0]
        return first.get("id") if isinstance(first, dict) else first.id

    def create_issue(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create issue on Backlog API.

        Args:
            params: Issue parameters formatted for API

        Returns:
            Created issue data from API
        """
        return self.client.create_issue(**params)

    def create_task(self, task: ParsedTask) -> Dict[str, Any]:
        """Create task on Backlog.

        Args:
            task: ParsedTask instance

        Returns:
            Created issue data
        """
        # Resolve type and assignee
        type_name = map_task_type_to_backlog(task.task_type)
        issue_type_id = self.get_issue_type_id(type_name)
        assignee_id = self.resolve_assignee(task.assignee_hint)

        # Format for API
        params = format_task_for_api(
            task,
            project_id=self.project.id,
            issue_type_id=issue_type_id,
            assignee_id=assignee_id
        )

        return self.create_issue(params)

    def preview_task(self, task: ParsedTask) -> Dict[str, Any]:
        """Preview task without creating (dry run).

        Args:
            task: ParsedTask instance

        Returns:
            Task data that would be sent to API
        """
        type_name = map_task_type_to_backlog(task.task_type)
        issue_type_id = self.get_issue_type_id(type_name)
        assignee_id = self.resolve_assignee(task.assignee_hint)

        return format_task_for_api(
            task,
            project_id=self.project.id,
            issue_type_id=issue_type_id,
            assignee_id=assignee_id
        )

    def create_multiple_tasks(self, tasks: List[ParsedTask]) -> List[Dict[str, Any]]:
        """Create multiple tasks on Backlog.

        Args:
            tasks: List of ParsedTask instances

        Returns:
            List of created issue data
        """
        results = []
        for task in tasks:
            result = self.create_task(task)
            results.append(result)
        return results
