"""Backlog API client with rate limiting and retry.

Provides BacklogClient class for Nulab Backlog API v2 integration.
Features:
- Rate limiting (1 req/sec)
- Retry with exponential backoff
- SSL proxy support
- Pagination handling
"""

import os
import time
import logging
import requests
import urllib3
from typing import Optional

from .models import Issue, User, Status, Project

# Suppress SSL warnings when verification is disabled
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger(__name__)


class BacklogAPIError(Exception):
    """Custom exception for Backlog API errors."""
    def __init__(self, message: str, status_code: int = 0):
        super().__init__(message)
        self.status_code = status_code


class BacklogClient:
    """Client for Nulab Backlog API v2."""

    MIN_REQUEST_INTERVAL = 1.0
    MAX_RETRIES = 3
    RETRY_DELAY = 2.0

    def __init__(self, space_url: str, api_key: str, verify_ssl: bool = True):
        self.space_url = space_url.rstrip("/")
        self.api_key = api_key
        self.base_url = f"https://{self.space_url}/api/v2"
        self.session = requests.Session()
        self.last_request_time = 0.0

        # Auto-detect proxy and disable SSL verification if proxy is set
        self.verify_ssl = verify_ssl
        if os.environ.get("HTTPS_PROXY") or os.environ.get("HTTP_PROXY"):
            self.verify_ssl = False
            logger.info("Proxy detected, SSL verification disabled")

        if not api_key or len(api_key) < 10:
            raise ValueError("Invalid API key format")

    def _rate_limit_wait(self) -> None:
        elapsed = time.time() - self.last_request_time
        if elapsed < self.MIN_REQUEST_INTERVAL:
            time.sleep(self.MIN_REQUEST_INTERVAL - elapsed)
        self.last_request_time = time.time()

    def _request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        self._rate_limit_wait()
        url = f"{self.base_url}{endpoint}"
        params = kwargs.pop("params", {})
        params["apiKey"] = self.api_key

        for attempt in range(self.MAX_RETRIES):
            try:
                response = self.session.request(
                    method, url, params=params, timeout=30, verify=self.verify_ssl, **kwargs
                )

                if response.status_code == 429:
                    delay = self.RETRY_DELAY * (2 ** attempt)
                    logger.warning(f"Rate limited, waiting {delay}s")
                    time.sleep(delay)
                    continue

                if response.status_code >= 500 and attempt < self.MAX_RETRIES - 1:
                    delay = self.RETRY_DELAY * (2 ** attempt)
                    time.sleep(delay)
                    continue

                if response.status_code == 401:
                    raise BacklogAPIError("Invalid API key", 401)
                if response.status_code == 404:
                    raise BacklogAPIError("Resource not found", 404)

                response.raise_for_status()
                return response

            except requests.RequestException as e:
                if attempt < self.MAX_RETRIES - 1:
                    time.sleep(self.RETRY_DELAY * (2 ** attempt))
                else:
                    raise BacklogAPIError(f"Request failed: {e}")

        raise BacklogAPIError("Max retries exceeded")

    def get_project(self, project_id: str) -> Project:
        """Get project info by ID or key."""
        response = self._request("GET", f"/projects/{project_id}")
        return Project.from_dict(response.json())

    def get_project_statuses(self, project_id: str) -> list[Status]:
        """Get all status definitions for a project."""
        response = self._request("GET", f"/projects/{project_id}/statuses")
        return [Status.from_dict(s) for s in response.json()]

    def get_project_users(self, project_id: str) -> list[User]:
        """Get all users/members of a project."""
        response = self._request("GET", f"/projects/{project_id}/users")
        return [User.from_dict(u) for u in response.json()]

    def get_milestones(self, project_id: str) -> list[dict]:
        """Get all milestones/versions for a project.

        Args:
            project_id: Project ID or key

        Returns:
            List of milestone dicts with keys: id, name, startDate, releaseDueDate, archived
        """
        response = self._request("GET", f"/projects/{project_id}/versions")
        return response.json()

    def get_project_issue_types(self, project_id: str) -> list[dict]:
        """Get all issue types for a project.

        Args:
            project_id: Project ID or key

        Returns:
            List of issue type dicts with keys: id, projectId, name, color, displayOrder
        """
        response = self._request("GET", f"/projects/{project_id}/issueTypes")
        return response.json()

    def create_issue(self, **kwargs) -> dict:
        """Create a new issue.

        Args:
            projectId: Project ID (required)
            summary: Issue summary (required)
            issueTypeId: Issue type ID (required)
            priorityId: Priority ID (required)
            description: Issue description
            dueDate: Due date (yyyy-MM-dd)
            estimatedHours: Estimated hours
            assigneeId: Assignee user ID

        Returns:
            Created issue dict with issueKey, summary, etc.
        """
        response = self._request("POST", "/issues", data=kwargs)
        return response.json()

    def get_issue(self, issue_id_or_key: str) -> dict:
        """Get a single issue by ID or key.

        Args:
            issue_id_or_key: Issue ID or key (e.g., "BKT-9")

        Returns:
            Issue dict with all fields
        """
        response = self._request("GET", f"/issues/{issue_id_or_key}")
        return response.json()

    def update_issue(self, issue_id_or_key: str, **kwargs) -> dict:
        """Update an existing issue.

        Args:
            issue_id_or_key: Issue ID or key (e.g., "BKT-9")
            summary: Issue summary
            description: Issue description
            statusId: Status ID
            priorityId: Priority ID
            dueDate: Due date (yyyy-MM-dd)
            estimatedHours: Estimated hours
            assigneeId: Assignee user ID

        Returns:
            Updated issue dict
        """
        response = self._request("PATCH", f"/issues/{issue_id_or_key}", data=kwargs)
        return response.json()

    def list_issues(
        self,
        project_id: int,
        status_ids: Optional[list[int]] = None,
        assignee_ids: Optional[list[int]] = None,
        due_date_until: Optional[str] = None,
        due_date_since: Optional[str] = None,
        sort: str = "dueDate",
        order: str = "asc"
    ) -> list[Issue]:
        """List all issues for a project with pagination.

        Args:
            project_id: Numeric project ID
            status_ids: Filter by status IDs
            assignee_ids: Filter by assignee IDs
            due_date_until: Filter due date <= value (yyyy-MM-dd)
            due_date_since: Filter due date >= value (yyyy-MM-dd)
            sort: Sort field (dueDate, created, updated)
            order: Sort order (asc, desc)

        Returns:
            List of all issues matching filters
        """
        all_issues = []
        offset = 0

        while True:
            params = {
                "projectId[]": project_id,
                "sort": sort,
                "order": order,
                "count": 100,
                "offset": offset
            }

            if status_ids:
                params["statusId[]"] = status_ids
            if assignee_ids:
                params["assigneeId[]"] = assignee_ids
            if due_date_until:
                params["dueDateUntil"] = due_date_until
            if due_date_since:
                params["dueDateSince"] = due_date_since

            logger.info(f"Fetching issues offset={offset}")
            response = self._request("GET", "/issues", params=params)
            batch = [Issue.from_dict(i) for i in response.json()]

            all_issues.extend(batch)

            if len(batch) < 100:
                break
            offset += 100

        return all_issues

    def get_issue_comments(
        self,
        issue_id_or_key: str,
        min_id: Optional[int] = None,
        max_id: Optional[int] = None,
        count: int = 100,
        order: str = "desc"
    ) -> list[dict]:
        """Get comments for an issue.

        Args:
            issue_id_or_key: Issue ID or key
            min_id: Minimum comment ID
            max_id: Maximum comment ID
            count: Number of comments to fetch (max 100)
            order: Sort order (asc, desc)

        Returns:
            List of comment dicts with changeLog for field changes
        """
        params = {"count": count, "order": order}
        if min_id:
            params["minId"] = min_id
        if max_id:
            params["maxId"] = max_id

        response = self._request(
            "GET", f"/issues/{issue_id_or_key}/comments", params=params
        )
        return response.json()

    def get_project_activities(
        self,
        project_id: str,
        activity_type_ids: Optional[list[int]] = None,
        min_id: Optional[int] = None,
        max_id: Optional[int] = None,
        count: int = 100
    ) -> list[dict]:
        """Get recent activities for a project.

        Activity types related to issue updates:
        - 1: Issue created
        - 2: Issue updated
        - 3: Issue commented
        - 14: Issue multi-updated

        Args:
            project_id: Project ID or key
            activity_type_ids: Filter by activity types
            min_id: Minimum activity ID
            max_id: Maximum activity ID
            count: Number of activities to fetch (max 100)

        Returns:
            List of activity dicts with content including field changes
        """
        params = {"count": count}
        if activity_type_ids:
            params["activityTypeId[]"] = activity_type_ids
        if min_id:
            params["minId"] = min_id
        if max_id:
            params["maxId"] = max_id

        response = self._request(
            "GET", f"/projects/{project_id}/activities", params=params
        )
        return response.json()

    def get_all_project_activities(
        self,
        project_id: str,
        activity_type_ids: Optional[list[int]] = None,
        since_id: Optional[int] = None,
        limit: int = 500
    ) -> list[dict]:
        """Get all project activities with pagination.

        Args:
            project_id: Project ID or key
            activity_type_ids: Filter by activity types (2=issue updated)
            since_id: Only get activities with ID > since_id
            limit: Maximum total activities to fetch

        Returns:
            List of all activity dicts matching filters
        """
        all_activities = []
        max_id = None

        while len(all_activities) < limit:
            params = {"count": 100}
            if activity_type_ids:
                params["activityTypeId[]"] = activity_type_ids
            if max_id:
                params["maxId"] = max_id
            if since_id and not max_id:
                params["minId"] = since_id

            response = self._request(
                "GET", f"/projects/{project_id}/activities", params=params
            )
            batch = response.json()

            if not batch:
                break

            # Filter by since_id if provided
            if since_id:
                batch = [a for a in batch if a["id"] > since_id]

            all_activities.extend(batch)

            if len(batch) < 100:
                break

            # Get max_id for next page (oldest in current batch)
            max_id = min(a["id"] for a in batch) - 1

        return all_activities[:limit]
