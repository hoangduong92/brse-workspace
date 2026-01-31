"""Pytest fixtures for bk-track tests."""
import pytest
import sys
import os
from pathlib import Path
from datetime import date, datetime, timedelta
from unittest.mock import MagicMock

# Add parent directories to path
bk_track_root = Path(__file__).parent.parent
scripts_dir = bk_track_root / "scripts"
skills_dir = bk_track_root.parent.parent
common_dir = skills_dir / "common"

# Insert in order: scripts first, then common
sys.path.insert(0, str(scripts_dir))
sys.path.insert(0, str(common_dir))

# Set PYTHONPATH environment variable as well
os.environ["PYTHONPATH"] = f"{scripts_dir}{os.pathsep}{common_dir}"


@pytest.fixture
def sample_user():
    """Create a sample user for testing."""
    from backlog.models import User
    return User(
        id=1,
        user_id="user001",
        name="John Doe",
        role_type=1,
        email="john@example.com"
    )


@pytest.fixture
def sample_status():
    """Create a sample status for testing."""
    from backlog.models import Status
    return Status(
        id=1,
        name="In Progress",
        project_id=1,
        display_order=2
    )


@pytest.fixture
def sample_project():
    """Create a sample project for testing."""
    from backlog.models import Project
    return Project(
        id=1,
        project_key="TEST",
        name="Test Project"
    )


@pytest.fixture
def sample_issue(sample_project):
    """Create a sample issue for testing."""
    from backlog.models import Issue
    return Issue(
        id=1,
        project_id=sample_project.id,
        key_id="TEST-1",
        summary="Sample Task",
        description="A sample task for testing",
        issue_type_id=1,
        priority_id=3,
        status_id=2,
        assignee_id=1,
        start_date="2024-01-01",
        due_date="2024-01-15",
        estimated_hours=8.0,
        actual_hours=6.0,
        created="2024-01-01T00:00:00Z",
        updated="2024-01-05T00:00:00Z"
    )


@pytest.fixture
def sample_overdue_issue(sample_project):
    """Create a sample overdue issue for testing."""
    from backlog.models import Issue
    today = date.today()
    overdue_date = (today - timedelta(days=5)).isoformat()

    return Issue(
        id=2,
        project_id=sample_project.id,
        key_id="TEST-2",
        summary="Overdue Task",
        description="An overdue task for testing",
        issue_type_id=1,
        priority_id=2,
        status_id=2,
        assignee_id=1,
        start_date="2024-01-01",
        due_date=overdue_date,
        estimated_hours=10.0,
        actual_hours=2.0,
        created="2024-01-01T00:00:00Z",
        updated="2024-01-10T00:00:00Z"
    )


@pytest.fixture
def sample_closed_issue(sample_project):
    """Create a sample closed issue for testing."""
    from backlog.models import Issue
    return Issue(
        id=3,
        project_id=sample_project.id,
        key_id="TEST-3",
        summary="Completed Task",
        description="A completed task for testing",
        issue_type_id=1,
        priority_id=3,
        status_id=5,
        assignee_id=1,
        start_date="2024-01-01",
        due_date="2024-01-10",
        estimated_hours=5.0,
        actual_hours=5.0,
        created="2024-01-01T00:00:00Z",
        updated="2024-01-10T00:00:00Z"
    )


@pytest.fixture
def mock_backlog_client():
    """Create a mock Backlog client."""
    mock_client = MagicMock()
    mock_client.get_issues = MagicMock(return_value=[])
    mock_client.get_project = MagicMock(return_value={"id": 1, "projectKey": "TEST", "name": "Test Project"})
    return mock_client


@pytest.fixture
def sample_analysis_results():
    """Create sample analysis results with flat models."""
    from models import TaskStatus, MemberLoad, ProjectHealth

    return {
        "health": ProjectHealth(
            total_issues=10,
            completed=3,
            in_progress=5,
            late_count=2,
            at_risk_count=1,
            health_score=80.0
        ),
        "late_tasks": [
            TaskStatus(
                issue_key="TEST-2",
                summary="Overdue Task",
                status="In Progress",
                assignee="John Doe",
                due_date="2024-01-01",
                days_late=5,
                risk_level="high"
            )
        ],
        "at_risk_tasks": [
            TaskStatus(
                issue_key="TEST-1",
                summary="Sample Task",
                status="In Progress",
                assignee="John Doe",
                due_date="2024-01-15",
                days_late=0,
                risk_level="medium"
            )
        ],
        "in_progress_tasks": [
            TaskStatus(
                issue_key="TEST-1",
                summary="Sample Task",
                status="In Progress",
                assignee="John Doe",
                due_date="2024-01-15",
                days_late=0,
                risk_level="low"
            )
        ],
        "completed_tasks": [
            TaskStatus(
                issue_key="TEST-3",
                summary="Completed Task",
                status="Closed",
                assignee="John Doe",
                due_date="2024-01-10",
                days_late=0,
                risk_level="low"
            )
        ],
        "member_loads": [
            MemberLoad(
                name="John Doe",
                total_tasks=5,
                completed=2,
                in_progress=2,
                overdue=1
            )
        ]
    }
