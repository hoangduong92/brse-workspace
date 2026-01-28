"""Backlog API client for bk-status skill."""

import time
import logging
import requests
from typing import Optional

# Support both relative and absolute imports
try:
    from .models import Issue, User, Status, Project
except ImportError:
    from models import Issue, User, Status, Project

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

    def __init__(self, space_url: str, api_key: str):
        self.space_url = space_url.rstrip("/")
        self.api_key = api_key
        self.base_url = f"https://{self.space_url}/api/v2"
        self.session = requests.Session()
        self.last_request_time = 0.0

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
                    method, url, params=params, timeout=30, **kwargs
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
