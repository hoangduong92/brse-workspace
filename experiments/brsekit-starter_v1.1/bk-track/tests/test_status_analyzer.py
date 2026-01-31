"""Tests for status_analyzer module."""
import pytest
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch, call
from datetime import date, timedelta

# Add scripts directory to path as a package
scripts_dir = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(scripts_dir.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "common"))

from scripts.status_analyzer import StatusAnalyzer
from scripts.models import TaskStatus, RiskLevel


class TestStatusAnalyzerInit:
    """Test StatusAnalyzer initialization."""

    def test_init_with_statuses(self):
        """Test StatusAnalyzer initialization with status list."""
        statuses = [
            {"id": 1, "name": "To Do"},
            {"id": 2, "name": "In Progress"},
            {"id": 3, "name": "Closed"}
        ]
        analyzer = StatusAnalyzer(statuses=statuses)
        assert analyzer.statuses == {1: "To Do", 2: "In Progress", 3: "Closed"}
        assert analyzer.closed_status_ids == {3}  # "Closed" by default

    def test_init_with_custom_closed_statuses(self):
        """Test StatusAnalyzer with custom closed status names."""
        statuses = [
            {"id": 1, "name": "To Do"},
            {"id": 2, "name": "Done"},
            {"id": 3, "name": "完了"}  # Japanese "Completed"
        ]
        closed_names = ["Done", "完了"]
        analyzer = StatusAnalyzer(statuses=statuses, closed_status_names=closed_names)
        assert analyzer.closed_status_ids == {2, 3}

    def test_init_default_closed_status(self):
        """Test StatusAnalyzer defaults to 'Closed' as only closed status."""
        statuses = [
            {"id": 1, "name": "Open"},
            {"id": 2, "name": "Closed"}
        ]
        analyzer = StatusAnalyzer(statuses=statuses)
        assert analyzer.closed_status_names == ["Closed"]
        assert 2 in analyzer.closed_status_ids


class TestStatusAnalyzerHelperMethods:
    """Test StatusAnalyzer helper methods."""

    def test_parse_date_iso_format(self):
        """Test _parse_date with ISO format."""
        statuses = [{"id": 1, "name": "Closed"}]
        analyzer = StatusAnalyzer(statuses=statuses)
        test_date = date(2024, 1, 15)
        parsed = analyzer._parse_date(test_date.isoformat())
        assert parsed == test_date

    def test_parse_date_iso_datetime(self):
        """Test _parse_date with ISO datetime format."""
        statuses = [{"id": 1, "name": "Closed"}]
        analyzer = StatusAnalyzer(statuses=statuses)
        test_date = date(2024, 1, 15)
        parsed = analyzer._parse_date(f"{test_date.isoformat()}T10:00:00Z")
        assert parsed == test_date

    def test_parse_date_invalid(self):
        """Test _parse_date with invalid format returns None."""
        statuses = [{"id": 1, "name": "Closed"}]
        analyzer = StatusAnalyzer(statuses=statuses)
        parsed = analyzer._parse_date("invalid-date")
        assert parsed is None

    def test_parse_date_none(self):
        """Test _parse_date with None returns None."""
        statuses = [{"id": 1, "name": "Closed"}]
        analyzer = StatusAnalyzer(statuses=statuses)
        parsed = analyzer._parse_date(None)
        assert parsed is None

    def test_is_closed(self):
        """Test _is_closed status check."""
        statuses = [
            {"id": 1, "name": "Open"},
            {"id": 2, "name": "Closed"}
        ]
        analyzer = StatusAnalyzer(statuses=statuses)
        assert analyzer._is_closed(2) is True
        assert analyzer._is_closed(1) is False

    def test_get_status_id_from_dict(self):
        """Test _get_status_id extraction."""
        statuses = [{"id": 1, "name": "Open"}]
        analyzer = StatusAnalyzer(statuses=statuses)
        issue = {"status": {"id": 1, "name": "Open"}}
        status_id = analyzer._get_status_id(issue)
        assert status_id == 1

    def test_get_assignee_id_from_dict(self):
        """Test _get_assignee_id extraction."""
        statuses = [{"id": 1, "name": "Open"}]
        analyzer = StatusAnalyzer(statuses=statuses)
        issue = {"assignee": {"id": 42, "name": "John"}}
        assignee_id = analyzer._get_assignee_id(issue)
        assert assignee_id == 42


class TestStatusAnalyzerPublicMethods:
    """Test StatusAnalyzer public API methods."""

    def test_get_late_tasks(self):
        """Test get_late_tasks returns list."""
        statuses = [
            {"id": 1, "name": "In Progress"},
            {"id": 2, "name": "Closed"}
        ]
        analyzer = StatusAnalyzer(statuses=statuses)
        today = date.today()

        issues = [
            {
                "status": {"id": 1},
                "dueDate": (today - timedelta(days=5)).isoformat()
            },
            {
                "status": {"id": 2},  # Closed, should not appear
                "dueDate": (today - timedelta(days=5)).isoformat()
            }
        ]

        late_tasks = analyzer.get_late_tasks(issues, today)
        assert isinstance(late_tasks, list)
        assert len(late_tasks) == 1

    def test_get_summary_empty(self):
        """Test get_summary with empty issues."""
        statuses = [{"id": 1, "name": "Open"}]
        analyzer = StatusAnalyzer(statuses=statuses)

        summary = analyzer.get_summary([])
        assert summary["total"] == 0
        assert summary["closed_count"] == 0
        assert summary["progress_percent"] == 0

    def test_get_summary_with_issues(self):
        """Test get_summary calculates progress."""
        statuses = [
            {"id": 1, "name": "Open"},
            {"id": 2, "name": "Closed"}
        ]
        analyzer = StatusAnalyzer(statuses=statuses)

        issues = [
            {"status": {"id": 1}},
            {"status": {"id": 1}},
            {"status": {"id": 2}},  # Closed
        ]

        summary = analyzer.get_summary(issues)
        assert summary["total"] == 3
        assert summary["closed_count"] == 1
        # 1/3 closed = 33.33%
        assert 33 <= summary["progress_percent"] <= 34

    def test_get_workload(self):
        """Test get_workload calculation."""
        statuses = [
            {"id": 1, "name": "Open"},
            {"id": 2, "name": "Closed"}
        ]
        analyzer = StatusAnalyzer(statuses=statuses)

        issues = [
            {"status": {"id": 1}, "assignee": {"id": 1, "name": "John"}},
            {"status": {"id": 1}, "assignee": {"id": 1, "name": "John"}},
            {"status": {"id": 1}, "assignee": {"id": 2, "name": "Jane"}},
        ]
        users = [
            {"id": 1, "name": "John"},
            {"id": 2, "name": "Jane"}
        ]

        workload = analyzer.get_workload(issues, users)
        assert isinstance(workload, dict)

    def test_count_working_days_weekend_skip(self):
        """Test _count_working_days skips weekends."""
        statuses = [{"id": 1, "name": "Open"}]
        analyzer = StatusAnalyzer(statuses=statuses)

        # Create a 4-day range that includes a Saturday and Sunday
        friday = date(2024, 1, 12)  # Friday
        monday = date(2024, 1, 15)  # Monday
        # Range: Fri, Sat, Sun, Mon = 2 working days (Fri, Mon)
        working_days = analyzer._count_working_days(friday, monday)
        assert working_days == 2
