"""Nulab Backlog API client with rate limiting and error handling."""

import time
import logging
import requests
from typing import Optional

try:
    from .models import Issue, Project, Comment, Attachment
except ImportError:
    from models import Issue, Project, Comment, Attachment

logger = logging.getLogger(__name__)


class BacklogAPIError(Exception):
    """Custom exception for Backlog API errors."""
    def __init__(self, message: str, status_code: int = 0):
        super().__init__(message)
        self.status_code = status_code


class BacklogAPI:
    """Client for Nulab Backlog API v2."""

    MIN_REQUEST_INTERVAL = 1.0  # 1 second between requests
    MAX_RETRIES = 3
    RETRY_DELAY = 2.0  # Base delay for exponential backoff

    def __init__(self, space_url: str, api_key: str):
        """Initialize Backlog API client.

        Args:
            space_url: Backlog space URL (e.g., 'hblab.backlogtool.com')
            api_key: API key for authentication
        """
        self.space_url = space_url.rstrip("/")
        self.api_key = api_key
        self.base_url = f"https://{self.space_url}/api/v2"
        self.session = requests.Session()
        self.last_request_time = 0.0

        # Validate API key on init
        if not api_key or len(api_key) < 10:
            raise ValueError("Invalid API key format")

    def _rate_limit_wait(self) -> None:
        """Wait if needed to respect rate limits."""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.MIN_REQUEST_INTERVAL:
            time.sleep(self.MIN_REQUEST_INTERVAL - elapsed)
        self.last_request_time = time.time()

    def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[dict] = None,
        files: Optional[dict] = None,
        **kwargs
    ) -> requests.Response:
        """Make API request with rate limiting and error handling.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            data: Request body data
            files: Files for multipart upload
            **kwargs: Additional request arguments

        Returns:
            Response object

        Raises:
            BacklogAPIError: On API errors
        """
        self._rate_limit_wait()

        url = f"{self.base_url}{endpoint}"
        params = kwargs.pop("params", {})
        params["apiKey"] = self.api_key

        logger.debug(f"{method} {endpoint}")

        for attempt in range(self.MAX_RETRIES):
            try:
                response = self.session.request(
                    method=method,
                    url=url,
                    params=params,
                    data=data,
                    files=files,
                    timeout=30,
                    **kwargs
                )

                # Handle rate limiting (429)
                if response.status_code == 429:
                    delay = self.RETRY_DELAY * (2 ** attempt)
                    logger.warning(f"Rate limited, waiting {delay}s")
                    time.sleep(delay)
                    continue

                # Handle server errors with retry
                if response.status_code >= 500 and attempt < self.MAX_RETRIES - 1:
                    delay = self.RETRY_DELAY * (2 ** attempt)
                    logger.warning(f"Server error {response.status_code}, retrying in {delay}s")
                    time.sleep(delay)
                    continue

                # Handle client errors
                if response.status_code == 401:
                    raise BacklogAPIError("Invalid API key", response.status_code)
                if response.status_code == 404:
                    raise BacklogAPIError("Resource not found", response.status_code)
                if response.status_code == 400:
                    error_msg = response.json().get("errors", [{}])[0].get("message", "Bad request")
                    raise BacklogAPIError(f"Bad request: {error_msg}", response.status_code)

                response.raise_for_status()
                return response

            except requests.RequestException as e:
                if attempt < self.MAX_RETRIES - 1:
                    delay = self.RETRY_DELAY * (2 ** attempt)
                    logger.warning(f"Request failed: {e}, retrying in {delay}s")
                    time.sleep(delay)
                else:
                    raise BacklogAPIError(f"Request failed after {self.MAX_RETRIES} attempts: {e}")

        raise BacklogAPIError("Max retries exceeded")

    def get_issue(self, issue_id: str) -> Issue:
        """Fetch issue by ID.

        Args:
            issue_id: Issue ID (e.g., 'HB21373-123')

        Returns:
            Issue object
        """
        logger.info(f"Fetching issue {issue_id}")
        response = self._request("GET", f"/issues/{issue_id}")
        return Issue.from_dict(response.json())

    def create_issue(self, project_id: int, **kwargs) -> Issue:
        """Create new issue.

        Args:
            project_id: Project ID
            **kwargs: Issue fields (summary, description, issueTypeId, priorityId, etc.)

        Returns:
            Created Issue object
        """
        data = {"projectId": project_id, **kwargs}
        logger.info(f"Creating issue in project {project_id}")
        response = self._request("POST", "/issues", data=data)
        return Issue.from_dict(response.json())

    def create_subtask(self, project_id: int, parent_id: int, **kwargs) -> Issue:
        """Create subtask under parent issue.

        Args:
            project_id: Project ID
            parent_id: Parent issue ID
            **kwargs: Issue fields

        Returns:
            Created subtask Issue object
        """
        kwargs["parentIssueId"] = parent_id
        return self.create_issue(project_id, **kwargs)

    def add_comment(self, issue_id: str, content: str) -> Comment:
        """Add comment to issue.

        Args:
            issue_id: Issue ID
            content: Comment content

        Returns:
            Created Comment object
        """
        logger.info(f"Adding comment to {issue_id}")
        response = self._request("POST", f"/issues/{issue_id}/comments", data={"content": content})
        return Comment.from_dict(response.json())

    def get_project(self, project_id: str) -> Project:
        """Fetch project by ID.

        Args:
            project_id: Project ID or key

        Returns:
            Project object
        """
        logger.info(f"Fetching project {project_id}")
        response = self._request("GET", f"/projects/{project_id}")
        return Project.from_dict(response.json())

    def get_attachments(self, issue_id: str) -> list[Attachment]:
        """Get list of attachments for an issue.

        Args:
            issue_id: Issue ID

        Returns:
            List of Attachment objects
        """
        logger.info(f"Fetching attachments for {issue_id}")
        response = self._request("GET", f"/issues/{issue_id}/attachments")
        return [Attachment.from_dict(a) for a in response.json()]

    def download_attachment(self, issue_id: str, attachment_id: int) -> bytes:
        """Download attachment content.

        Args:
            issue_id: Issue ID
            attachment_id: Attachment ID

        Returns:
            Attachment file content as bytes
        """
        logger.info(f"Downloading attachment {attachment_id}")
        url = f"{self.base_url}/issues/{issue_id}/attachments/{attachment_id}"
        response = requests.get(url, params={"apiKey": self.api_key}, timeout=60)
        response.raise_for_status()
        return response.content

    def add_attachment(self, issue_id: str, file_data: bytes, filename: str) -> Attachment:
        """Upload attachment to issue.

        Note: Backlog requires uploading to /space/attachment first, then linking to issue.
        This simplified version uploads directly if supported.

        Args:
            issue_id: Issue ID
            file_data: File content as bytes
            filename: Original filename

        Returns:
            Created Attachment object
        """
        logger.info(f"Uploading attachment {filename} to {issue_id}")

        # First, upload to space
        files = {"file": (filename, file_data)}
        response = self._request("POST", "/space/attachment", files=files)
        attachment_data = response.json()

        # Then link to issue by updating with attachmentId
        if isinstance(attachment_data, dict) and "id" in attachment_data:
            attachment_id = attachment_data["id"]
            # Update issue with attachment
            self._request(
                "PATCH",
                f"/issues/{issue_id}",
                data={"attachmentId[]": attachment_id}
            )

        return Attachment.from_dict(attachment_data if isinstance(attachment_data, dict) else attachment_data[0])

    def copy_attachments(self, source_issue_id: str, dest_issue_id: str) -> list[Attachment]:
        """Copy all attachments from source to destination issue.

        Args:
            source_issue_id: Source issue ID
            dest_issue_id: Destination issue ID

        Returns:
            List of copied Attachment objects
        """
        attachments = self.get_attachments(source_issue_id)
        copied = []

        for attachment in attachments:
            try:
                file_data = self.download_attachment(source_issue_id, attachment.id)
                new_attachment = self.add_attachment(dest_issue_id, file_data, attachment.name)
                copied.append(new_attachment)
                logger.info(f"Copied attachment: {attachment.name}")
            except Exception as e:
                logger.error(f"Failed to copy attachment {attachment.name}: {e}")

        return copied
