"""Unit tests for bk-status models."""

import pytest
from scripts.models import User, Status, Project, Issue, RiskLevel


class TestUser:
    """Tests for User model."""

    def test_from_dict_full(self):
        """User.from_dict with all fields."""
        data = {
            "id": 101,
            "userId": "tanaka",
            "name": "Tanaka Taro",
            "roleType": 2,
            "mailAddress": "tanaka@example.com"
        }
        user = User.from_dict(data)
        assert user.id == 101
        assert user.user_id == "tanaka"
        assert user.name == "Tanaka Taro"
        assert user.role_type == 2
        assert user.email == "tanaka@example.com"

    def test_from_dict_minimal(self):
        """User.from_dict with minimal fields."""
        data = {"id": 1, "name": "Test User"}
        user = User.from_dict(data)
        assert user.id == 1
        assert user.name == "Test User"
        assert user.user_id == ""
        assert user.role_type == 1
        assert user.email == ""


class TestStatus:
    """Tests for Status model."""

    def test_from_dict_full(self):
        """Status.from_dict with all fields."""
        data = {
            "id": 1,
            "name": "Open",
            "projectId": 12345,
            "displayOrder": 1
        }
        status = Status.from_dict(data)
        assert status.id == 1
        assert status.name == "Open"
        assert status.project_id == 12345
        assert status.display_order == 1

    def test_from_dict_minimal(self):
        """Status.from_dict with minimal fields."""
        data = {"id": 4, "name": "Closed"}
        status = Status.from_dict(data)
        assert status.id == 4
        assert status.name == "Closed"
        assert status.project_id == 0
        assert status.display_order == 0


class TestProject:
    """Tests for Project model."""

    def test_from_dict(self):
        """Project.from_dict parses correctly."""
        data = {
            "id": 12345,
            "projectKey": "TEST",
            "name": "Test Project"
        }
        project = Project.from_dict(data)
        assert project.id == 12345
        assert project.project_key == "TEST"
        assert project.name == "Test Project"


class TestIssue:
    """Tests for Issue model."""

    def test_from_dict_full(self):
        """Issue.from_dict with all fields including dueDate."""
        data = {
            "id": 1001,
            "projectId": 12345,
            "issueKey": "TEST-1",
            "summary": "Test issue",
            "description": "Test description",
            "issueType": {"id": 1},
            "priority": {"id": 2},
            "status": {"id": 1},
            "assignee": {"id": 101},
            "dueDate": "2026-01-28",
            "created": "2026-01-10T10:00:00Z",
            "updated": "2026-01-15T10:00:00Z"
        }
        issue = Issue.from_dict(data)
        assert issue.id == 1001
        assert issue.project_id == 12345
        assert issue.key_id == "TEST-1"
        assert issue.summary == "Test issue"
        assert issue.description == "Test description"
        assert issue.issue_type_id == 1
        assert issue.priority_id == 2
        assert issue.status_id == 1
        assert issue.assignee_id == 101
        assert issue.due_date == "2026-01-28"
        assert issue.created == "2026-01-10T10:00:00Z"
        assert issue.updated == "2026-01-15T10:00:00Z"

    def test_from_dict_no_assignee(self):
        """Issue.from_dict with null assignee."""
        data = {
            "id": 1002,
            "projectId": 12345,
            "issueKey": "TEST-2",
            "summary": "Unassigned issue",
            "issueType": {"id": 1},
            "priority": {"id": 3},
            "status": {"id": 2},
            "assignee": None,
            "dueDate": None
        }
        issue = Issue.from_dict(data)
        assert issue.assignee_id is None
        assert issue.due_date is None

    def test_from_dict_no_due_date(self):
        """Issue.from_dict without dueDate field."""
        data = {
            "id": 1003,
            "projectId": 12345,
            "issueKey": "TEST-3",
            "summary": "No due date",
            "issueType": {"id": 1},
            "priority": {"id": 4},
            "status": {"id": 1},
            "assignee": {"id": 102}
        }
        issue = Issue.from_dict(data)
        assert issue.due_date is None
        assert issue.assignee_id == 102

    def test_from_dict_with_hours(self):
        """Issue.from_dict parses estimatedHours and actualHours."""
        data = {
            "id": 1004,
            "projectId": 12345,
            "issueKey": "TEST-4",
            "summary": "Issue with hours",
            "issueType": {"id": 1},
            "priority": {"id": 2},
            "status": {"id": 1},
            "estimatedHours": 16.0,
            "actualHours": 4.5
        }
        issue = Issue.from_dict(data)
        assert issue.estimated_hours == 16.0
        assert issue.actual_hours == 4.5

    def test_from_dict_null_hours(self):
        """Issue.from_dict handles null hours."""
        data = {
            "id": 1005,
            "projectId": 12345,
            "issueKey": "TEST-5",
            "summary": "Null hours",
            "issueType": {"id": 1},
            "priority": {"id": 2},
            "status": {"id": 1},
            "estimatedHours": None,
            "actualHours": None
        }
        issue = Issue.from_dict(data)
        assert issue.estimated_hours is None
        assert issue.actual_hours is None

    def test_from_dict_missing_hours(self):
        """Issue.from_dict handles missing hours fields."""
        data = {
            "id": 1006,
            "projectId": 12345,
            "issueKey": "TEST-6",
            "summary": "No hours fields",
            "issueType": {"id": 1},
            "priority": {"id": 2},
            "status": {"id": 1}
        }
        issue = Issue.from_dict(data)
        assert issue.estimated_hours is None
        assert issue.actual_hours is None


class TestRiskLevel:
    """Tests for RiskLevel enum."""

    def test_risk_level_values(self):
        """RiskLevel has correct values."""
        assert RiskLevel.ON_TRACK.value == "on_track"
        assert RiskLevel.AT_RISK.value == "at_risk"
        assert RiskLevel.LATE.value == "late"
