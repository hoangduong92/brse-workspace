"""Unit tests for bk-status BacklogClient."""

import pytest
from unittest.mock import MagicMock, patch
import time

from scripts.backlog_client import BacklogClient, BacklogAPIError


class TestBacklogClientInit:
    """Tests for BacklogClient initialization."""

    def test_init_success(self):
        """Client initializes with valid params."""
        client = BacklogClient("test.backlog.com", "valid-api-key-123")
        assert client.space_url == "test.backlog.com"
        assert client.api_key == "valid-api-key-123"
        assert client.base_url == "https://test.backlog.com/api/v2"

    def test_init_strips_trailing_slash(self):
        """Client strips trailing slash from space_url."""
        client = BacklogClient("test.backlog.com/", "valid-api-key-123")
        assert client.space_url == "test.backlog.com"

    def test_init_invalid_api_key_empty(self):
        """Client raises ValueError for empty API key."""
        with pytest.raises(ValueError, match="Invalid API key"):
            BacklogClient("test.backlog.com", "")

    def test_init_invalid_api_key_short(self):
        """Client raises ValueError for too short API key."""
        with pytest.raises(ValueError, match="Invalid API key"):
            BacklogClient("test.backlog.com", "short")


class TestBacklogClientRateLimiting:
    """Tests for rate limiting behavior."""

    def test_rate_limit_wait_enforced(self):
        """Rate limiter waits between requests."""
        client = BacklogClient("test.backlog.com", "valid-api-key-123")
        client.last_request_time = time.time()

        start = time.time()
        client._rate_limit_wait()
        elapsed = time.time() - start

        # Should wait approximately 1 second
        assert elapsed >= 0.9  # Allow small margin


class TestBacklogClientAPIMethods:
    """Tests for API methods with mocked responses."""

    @patch('scripts.backlog_client.BacklogClient._request')
    def test_get_project(self, mock_request):
        """get_project returns Project object."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "id": 12345,
            "projectKey": "TEST",
            "name": "Test Project"
        }
        mock_request.return_value = mock_response

        client = BacklogClient("test.backlog.com", "valid-api-key-123")
        project = client.get_project("TEST")

        assert project.id == 12345
        assert project.project_key == "TEST"
        assert project.name == "Test Project"

    @patch('scripts.backlog_client.BacklogClient._request')
    def test_get_project_statuses(self, mock_request):
        """get_project_statuses returns list of Status objects."""
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {"id": 1, "name": "Open"},
            {"id": 2, "name": "In Progress"},
            {"id": 4, "name": "Closed"}
        ]
        mock_request.return_value = mock_response

        client = BacklogClient("test.backlog.com", "valid-api-key-123")
        statuses = client.get_project_statuses("TEST")

        assert len(statuses) == 3
        assert statuses[0].name == "Open"
        assert statuses[2].name == "Closed"

    @patch('scripts.backlog_client.BacklogClient._request')
    def test_get_project_users(self, mock_request):
        """get_project_users returns list of User objects."""
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {"id": 101, "name": "Tanaka"},
            {"id": 102, "name": "Nguyen"}
        ]
        mock_request.return_value = mock_response

        client = BacklogClient("test.backlog.com", "valid-api-key-123")
        users = client.get_project_users("TEST")

        assert len(users) == 2
        assert users[0].name == "Tanaka"
        assert users[1].name == "Nguyen"

    @patch('scripts.backlog_client.BacklogClient._request')
    def test_list_issues_single_page(self, mock_request):
        """list_issues returns all issues from single page."""
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {
                "id": 1001,
                "projectId": 12345,
                "issueKey": "TEST-1",
                "summary": "Issue 1",
                "issueType": {"id": 1},
                "priority": {"id": 2},
                "status": {"id": 1},
                "dueDate": "2026-01-28"
            }
        ]
        mock_request.return_value = mock_response

        client = BacklogClient("test.backlog.com", "valid-api-key-123")
        issues = client.list_issues(12345)

        assert len(issues) == 1
        assert issues[0].key_id == "TEST-1"
        assert issues[0].due_date == "2026-01-28"

    @patch('scripts.backlog_client.BacklogClient._request')
    def test_list_issues_pagination(self, mock_request):
        """list_issues handles pagination correctly."""
        # First call returns 100 issues, second call returns 50
        page1 = [
            {
                "id": i,
                "projectId": 12345,
                "issueKey": f"TEST-{i}",
                "summary": f"Issue {i}",
                "issueType": {"id": 1},
                "priority": {"id": 2},
                "status": {"id": 1}
            }
            for i in range(100)
        ]
        page2 = [
            {
                "id": i,
                "projectId": 12345,
                "issueKey": f"TEST-{i}",
                "summary": f"Issue {i}",
                "issueType": {"id": 1},
                "priority": {"id": 2},
                "status": {"id": 1}
            }
            for i in range(100, 150)
        ]

        mock_response1 = MagicMock()
        mock_response1.json.return_value = page1
        mock_response2 = MagicMock()
        mock_response2.json.return_value = page2

        mock_request.side_effect = [mock_response1, mock_response2]

        client = BacklogClient("test.backlog.com", "valid-api-key-123")
        issues = client.list_issues(12345)

        assert len(issues) == 150
        assert mock_request.call_count == 2
