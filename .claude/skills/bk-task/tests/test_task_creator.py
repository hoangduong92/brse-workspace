"""Tests for task_creator.py - TDD approach."""

import pytest
from unittest.mock import Mock, patch
from datetime import date
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from task_parser import ParsedTask, TaskType, Priority, DeadlineType
from task_creator import (
    TaskCreator,
    map_task_type_to_backlog,
    map_priority_to_backlog,
    format_task_for_api,
)


@pytest.fixture
def sample_task():
    """Create sample ParsedTask for testing."""
    return ParsedTask(
        summary="ログイン機能を実装",
        task_type=TaskType.FEATURE,
        priority=Priority.NORMAL,
        deadline_type=DeadlineType.TOMORROW,
        deadline_date=date(2026, 1, 30),
        estimated_hours=8.0,
        assignee_hint="田中",
        description="ログイン機能の実装詳細",
        warnings=[],
        source_type="comment"
    )


@pytest.fixture
def mock_client():
    """Create mock BacklogClient."""
    client = Mock()

    # Project mock - name is a special attribute for Mock, set separately
    project_mock = Mock(id=123, project_key="BKT")
    project_mock.name = "Test Project"
    client.get_project.return_value = project_mock

    # User mocks - name must be set separately due to Mock's special handling
    user1 = Mock(id=1, user_id="tanaka")
    user1.name = "田中"
    user2 = Mock(id=2, user_id="yamada")
    user2.name = "山田"
    client.get_project_users.return_value = [user1, user2]

    return client


class TestMapTaskTypeToBacklog:
    """Test task type mapping to Backlog issue types."""

    def test_bug_maps_to_bug(self):
        """BUG -> Bug issue type."""
        result = map_task_type_to_backlog(TaskType.BUG)
        assert result == "Bug"

    def test_feature_maps_to_task(self):
        """FEATURE -> Task issue type."""
        result = map_task_type_to_backlog(TaskType.FEATURE)
        assert result == "Task"

    def test_question_maps_to_task(self):
        """QUESTION -> Task issue type."""
        result = map_task_type_to_backlog(TaskType.QUESTION)
        assert result == "Task"

    def test_improvement_maps_to_task(self):
        """IMPROVEMENT -> Task issue type."""
        result = map_task_type_to_backlog(TaskType.IMPROVEMENT)
        assert result == "Task"


class TestMapPriorityToBacklog:
    """Test priority mapping to Backlog priority IDs."""

    def test_high_priority(self):
        """HIGH -> priority ID 2 (High)."""
        result = map_priority_to_backlog(Priority.HIGH)
        assert result == 2

    def test_normal_priority(self):
        """NORMAL -> priority ID 3 (Normal)."""
        result = map_priority_to_backlog(Priority.NORMAL)
        assert result == 3

    def test_low_priority(self):
        """LOW -> priority ID 4 (Low)."""
        result = map_priority_to_backlog(Priority.LOW)
        assert result == 4


class TestFormatTaskForAPI:
    """Test formatting task for Backlog API."""

    def test_format_basic_task(self, sample_task):
        """Format task with all fields."""
        result = format_task_for_api(
            sample_task,
            project_id=123,
            issue_type_id=1,
            assignee_id=1
        )

        assert result["projectId"] == 123
        assert result["summary"] == "ログイン機能を実装"
        assert result["issueTypeId"] == 1
        assert result["priorityId"] == 3  # Normal
        assert result["assigneeId"] == 1
        assert result["dueDate"] == "2026-01-30"
        assert result["estimatedHours"] == 8.0
        assert "ログイン機能の実装詳細" in result["description"]

    def test_format_task_without_assignee(self, sample_task):
        """Format task without assignee."""
        sample_task.assignee_hint = None
        result = format_task_for_api(
            sample_task,
            project_id=123,
            issue_type_id=1,
            assignee_id=None
        )

        assert "assigneeId" not in result

    def test_format_task_without_due_date(self, sample_task):
        """Format task without due date."""
        sample_task.deadline_date = None
        result = format_task_for_api(
            sample_task,
            project_id=123,
            issue_type_id=1,
            assignee_id=None
        )

        assert "dueDate" not in result

    def test_format_task_without_estimate(self, sample_task):
        """Format task without estimated hours."""
        sample_task.estimated_hours = None
        result = format_task_for_api(
            sample_task,
            project_id=123,
            issue_type_id=1,
            assignee_id=None
        )

        assert "estimatedHours" not in result


class TestTaskCreator:
    """Test TaskCreator class."""

    def test_resolve_assignee_exact_match(self, mock_client):
        """Resolve assignee with exact name match."""
        creator = TaskCreator(mock_client, "BKT")
        result = creator.resolve_assignee("田中")

        assert result == 1

    def test_resolve_assignee_not_found(self, mock_client):
        """Return None for unknown assignee."""
        creator = TaskCreator(mock_client, "BKT")
        result = creator.resolve_assignee("佐藤")

        assert result is None

    def test_resolve_assignee_none_input(self, mock_client):
        """Return None for None input."""
        creator = TaskCreator(mock_client, "BKT")
        result = creator.resolve_assignee(None)

        assert result is None

    def test_get_issue_type_id_bug(self, mock_client):
        """Get issue type ID for Bug."""
        type1 = Mock(id=1)
        type1.name = "Task"
        type2 = Mock(id=2)
        type2.name = "Bug"
        mock_client.get_project_issue_types = Mock(return_value=[type1, type2])
        creator = TaskCreator(mock_client, "BKT")
        result = creator.get_issue_type_id("Bug")

        assert result == 2

    def test_get_issue_type_id_default(self, mock_client):
        """Default to first issue type if not found."""
        type1 = Mock(id=1)
        type1.name = "Task"
        mock_client.get_project_issue_types = Mock(return_value=[type1])
        creator = TaskCreator(mock_client, "BKT")
        result = creator.get_issue_type_id("Unknown")

        assert result == 1

    @patch("task_creator.TaskCreator.create_issue")
    def test_create_task(self, mock_create, mock_client, sample_task):
        """Create task on Backlog."""
        type1 = Mock(id=1)
        type1.name = "Task"
        mock_client.get_project_issue_types = Mock(return_value=[type1])
        mock_create.return_value = {"id": 999, "issueKey": "BKT-123"}

        creator = TaskCreator(mock_client, "BKT")
        result = creator.create_task(sample_task)

        mock_create.assert_called_once()
        assert result["issueKey"] == "BKT-123"


class TestDryRunMode:
    """Test dry run mode for previewing without creating."""

    def test_dry_run_returns_preview(self, mock_client, sample_task):
        """Dry run returns preview data without API call."""
        type1 = Mock(id=1)
        type1.name = "Task"
        mock_client.get_project_issue_types = Mock(return_value=[type1])

        creator = TaskCreator(mock_client, "BKT")
        result = creator.preview_task(sample_task)

        assert result["summary"] == "ログイン機能を実装"
        assert result["projectId"] == 123
        assert "issueKey" not in result  # Not created yet


class TestMultipleTasksCreation:
    """Test creating multiple tasks."""

    def test_create_multiple_tasks(self, mock_client):
        """Create multiple tasks from list."""
        type1 = Mock(id=1)
        type1.name = "Task"
        mock_client.get_project_issue_types = Mock(return_value=[type1])

        tasks = [
            ParsedTask(summary="Task 1", task_type=TaskType.FEATURE),
            ParsedTask(summary="Task 2", task_type=TaskType.BUG),
        ]

        creator = TaskCreator(mock_client, "BKT")
        with patch.object(creator, "create_issue") as mock_create:
            mock_create.side_effect = [
                {"id": 1, "issueKey": "BKT-1"},
                {"id": 2, "issueKey": "BKT-2"},
            ]
            results = creator.create_multiple_tasks(tasks)

        assert len(results) == 2
        assert results[0]["issueKey"] == "BKT-1"
        assert results[1]["issueKey"] == "BKT-2"
