"""Tests for bk-track data models."""
import pytest
import sys
from pathlib import Path
from datetime import date

# Add scripts directory to path as a package
scripts_dir = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(scripts_dir.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "common"))

from scripts.models import TaskStatus, MemberLoad, ProjectHealth, ReportData
from backlog.models import RiskLevel


class TestTaskStatus:
    """Test TaskStatus model."""

    def test_task_status_creation(self):
        """Test creating a TaskStatus."""
        task = TaskStatus(
            issue_key="TEST-1",
            summary="Sample Task",
            status="In Progress",
            assignee="John Doe",
            due_date="2024-01-15",
            days_late=0,
            risk_level="low"
        )

        assert task.issue_key == "TEST-1"
        assert task.summary == "Sample Task"
        assert task.status == "In Progress"
        assert task.assignee == "John Doe"
        assert task.due_date == "2024-01-15"
        assert task.days_late == 0
        assert task.risk_level == "low"

    def test_task_status_with_overdue(self):
        """Test TaskStatus with overdue days."""
        task = TaskStatus(
            issue_key="TEST-2",
            summary="Overdue Task",
            status="In Progress",
            assignee="Jane Doe",
            due_date="2024-01-01",
            days_late=5,
            risk_level="high"
        )

        assert task.days_late == 5
        assert task.risk_level == "high"

    def test_task_status_at_risk(self):
        """Test TaskStatus at risk level."""
        task = TaskStatus(
            issue_key="TEST-3",
            summary="At Risk Task",
            status="In Progress",
            assignee="Bob Smith",
            due_date="2024-01-10",
            days_late=2,
            risk_level="medium"
        )

        assert task.risk_level == "medium"
        assert task.days_late == 2

    def test_task_status_default_values(self):
        """Test TaskStatus default values."""
        task = TaskStatus(
            issue_key="TEST-4",
            summary="New Task",
            status="New"
        )

        assert task.assignee is None
        assert task.due_date is None
        assert task.days_late == 0
        assert task.risk_level == "low"


class TestMemberLoad:
    """Test MemberLoad model."""

    def test_member_load_creation(self):
        """Test creating a MemberLoad."""
        load = MemberLoad(
            name="John Doe",
            total_tasks=5,
            completed=3,
            in_progress=1,
            overdue=1
        )

        assert load.name == "John Doe"
        assert load.total_tasks == 5
        assert load.completed == 3
        assert load.in_progress == 1
        assert load.overdue == 1

    def test_member_load_high_load(self):
        """Test MemberLoad with high workload."""
        load = MemberLoad(
            name="Jane Doe",
            total_tasks=10,
            completed=2,
            in_progress=5,
            overdue=3
        )

        assert load.total_tasks == 10
        assert load.overdue == 3

    def test_member_load_zero_assigned(self):
        """Test MemberLoad with no assigned tasks."""
        load = MemberLoad(
            name="Bob Smith",
            total_tasks=0,
            completed=0,
            in_progress=0,
            overdue=0
        )

        assert load.total_tasks == 0
        assert load.completed == 0


class TestProjectHealth:
    """Test ProjectHealth model."""

    def test_project_health_creation(self):
        """Test creating a ProjectHealth."""
        health = ProjectHealth(
            total_issues=10,
            completed=5,
            in_progress=3,
            late_count=2,
            at_risk_count=1,
            health_score=85.0
        )

        assert health.total_issues == 10
        assert health.completed == 5
        assert health.in_progress == 3
        assert health.late_count == 2
        assert health.at_risk_count == 1
        assert health.health_score == 85.0

    def test_project_health_excellent(self):
        """Test ProjectHealth with excellent score."""
        health = ProjectHealth(
            total_issues=20,
            completed=18,
            in_progress=2,
            late_count=0,
            at_risk_count=0,
            health_score=95.0
        )

        assert health.health_score == 95.0
        assert health.late_count == 0

    def test_project_health_poor(self):
        """Test ProjectHealth with poor score."""
        health = ProjectHealth(
            total_issues=10,
            completed=1,
            in_progress=2,
            late_count=7,
            at_risk_count=2,
            health_score=25.0
        )

        assert health.health_score == 25.0
        assert health.late_count == 7

    def test_project_health_default_score(self):
        """Test ProjectHealth default score."""
        health = ProjectHealth(
            total_issues=10,
            completed=5,
            in_progress=5,
            late_count=0
        )

        assert health.health_score == 0.0
        assert health.at_risk_count == 0

    def test_project_health_zero_tasks(self):
        """Test ProjectHealth with no tasks."""
        health = ProjectHealth(
            total_issues=0,
            completed=0,
            in_progress=0,
            late_count=0,
            at_risk_count=0,
            health_score=0.0
        )

        assert health.total_issues == 0


class TestReportData:
    """Test ReportData model."""

    def test_report_data_creation(self):
        """Test creating a ReportData."""
        health = ProjectHealth(
            total_issues=10,
            completed=5,
            in_progress=3,
            late_count=2,
            at_risk_count=1,
            health_score=80.0
        )

        completed = [
            TaskStatus(
                issue_key="TEST-1",
                summary="Closed Task",
                status="Closed",
                assignee="John Doe",
                days_late=0,
                risk_level="low"
            )
        ]
        in_progress = [
            TaskStatus(
                issue_key="TEST-2",
                summary="In Progress Task",
                status="In Progress",
                assignee="Jane Doe",
                days_late=0,
                risk_level="medium"
            )
        ]
        members = [
            MemberLoad(name="John Doe", total_tasks=5, completed=3, in_progress=1, overdue=1)
        ]

        report = ReportData(
            project_name="TEST",
            date_range="2024-01-01 ~ 2024-01-07",
            health=health,
            completed_tasks=completed,
            in_progress_tasks=in_progress,
            at_risk_tasks=[],
            late_tasks=[],
            next_week_tasks=[],
            member_loads=members
        )

        assert report.project_name == "TEST"
        assert report.date_range == "2024-01-01 ~ 2024-01-07"
        assert len(report.completed_tasks) == 1
        assert len(report.in_progress_tasks) == 1
        assert len(report.member_loads) == 1
        assert report.health.health_score == 80.0

    def test_report_data_empty_tasks(self):
        """Test ReportData with empty task lists."""
        health = ProjectHealth(
            total_issues=0,
            completed=0,
            in_progress=0,
            late_count=0
        )

        report = ReportData(
            project_name="EMPTY",
            date_range="2024-01-01 ~ 2024-01-07",
            health=health,
            completed_tasks=[],
            in_progress_tasks=[],
            late_tasks=[],
            member_loads=[]
        )

        assert len(report.completed_tasks) == 0
        assert len(report.in_progress_tasks) == 0
        assert len(report.member_loads) == 0

    def test_report_data_with_metrics(self):
        """Test ReportData with optional metrics."""
        health = ProjectHealth(
            total_issues=15,
            completed=10,
            in_progress=3,
            late_count=2,
            health_score=75.5
        )

        metrics = {
            "completion_rate": 66.7,
            "velocity": 5.2
        }

        report = ReportData(
            project_name="TEST",
            date_range="2024-01-01 ~ 2024-01-07",
            health=health,
            completed_tasks=[],
            in_progress_tasks=[],
            late_tasks=[],
            member_loads=[],
            metrics=metrics
        )

        assert report.health.total_issues == 15
        assert report.health.health_score == 75.5
        assert report.metrics["completion_rate"] == 66.7


class TestRiskLevelEnum:
    """Test RiskLevel enum."""

    def test_risk_level_values(self):
        """Test RiskLevel enum values."""
        assert RiskLevel.ON_TRACK.value == "on_track"
        assert RiskLevel.AT_RISK.value == "at_risk"
        assert RiskLevel.LATE.value == "late"

    def test_risk_level_comparison(self):
        """Test RiskLevel comparison."""
        assert RiskLevel.ON_TRACK != RiskLevel.AT_RISK
        assert RiskLevel.LATE != RiskLevel.ON_TRACK
        assert RiskLevel.AT_RISK == RiskLevel.AT_RISK

    def test_risk_level_in_condition(self):
        """Test RiskLevel in conditional statements."""
        risk = RiskLevel.LATE

        if risk == RiskLevel.LATE:
            is_late = True
        else:
            is_late = False

        assert is_late is True
