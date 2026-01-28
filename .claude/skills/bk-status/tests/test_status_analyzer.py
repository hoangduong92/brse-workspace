"""TDD tests for bk-status analyzer.

Tests written first (TDD red phase) - will fail until StatusAnalyzer is implemented.
"""

import json
import pytest
from datetime import date
from pathlib import Path

# Import will fail until implemented - this is expected in TDD
from scripts.status_analyzer import StatusAnalyzer

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def load_fixture(name: str) -> list:
    """Load JSON fixture file."""
    with open(FIXTURES_DIR / name) as f:
        return json.load(f)


class TestLateTasks:
    """Tests for late task detection."""

    def test_identifies_late_tasks_correctly(self):
        """Late = dueDate < today AND status not closed."""
        issues = load_fixture("sample_issues.json")
        statuses = load_fixture("sample_statuses.json")
        today = date(2026, 1, 28)

        analyzer = StatusAnalyzer(statuses, closed_status_names=["Closed"])
        late_tasks = analyzer.get_late_tasks(issues, today)

        # TEST-1: Due 2026-01-20, status Open
        # TEST-2: Due 2026-01-25, status In Progress
        # TEST-6: Due 2026-01-22, status Open (unassigned)
        assert len(late_tasks) == 3
        late_keys = [t["issueKey"] for t in late_tasks]
        assert "TEST-1" in late_keys
        assert "TEST-2" in late_keys
        assert "TEST-6" in late_keys

    def test_excludes_closed_tasks(self):
        """Closed tasks should not appear as late."""
        issues = load_fixture("sample_issues.json")
        statuses = load_fixture("sample_statuses.json")
        today = date(2026, 1, 28)

        analyzer = StatusAnalyzer(statuses, closed_status_names=["Closed"])
        late_tasks = analyzer.get_late_tasks(issues, today)

        late_keys = [t["issueKey"] for t in late_tasks]
        assert "TEST-4" not in late_keys  # Closed, even though past due

    def test_excludes_no_due_date(self):
        """Tasks without due date should not be flagged as late."""
        issues = load_fixture("sample_issues.json")
        statuses = load_fixture("sample_statuses.json")
        today = date(2026, 1, 28)

        analyzer = StatusAnalyzer(statuses, closed_status_names=["Closed"])
        late_tasks = analyzer.get_late_tasks(issues, today)

        late_keys = [t["issueKey"] for t in late_tasks]
        assert "TEST-5" not in late_keys  # No due date

    def test_calculates_days_overdue(self):
        """Each late task should have days_overdue calculated."""
        issues = load_fixture("sample_issues.json")
        statuses = load_fixture("sample_statuses.json")
        today = date(2026, 1, 28)

        analyzer = StatusAnalyzer(statuses, closed_status_names=["Closed"])
        late_tasks = analyzer.get_late_tasks(issues, today)

        test1 = next(t for t in late_tasks if t["issueKey"] == "TEST-1")
        assert test1["days_overdue"] == 8  # Due 01-20, today 01-28


class TestWorkload:
    """Tests for workload calculation."""

    def test_counts_open_issues_per_assignee(self):
        """Workload = count of non-closed issues per user."""
        issues = load_fixture("sample_issues.json")
        users = load_fixture("sample_users.json")
        statuses = load_fixture("sample_statuses.json")

        analyzer = StatusAnalyzer(statuses, closed_status_names=["Closed"])
        workload = analyzer.get_workload(issues, users)

        # Tanaka: TEST-1 (Open), TEST-3 (In Progress) = 2 (TEST-4 is Closed)
        # Nguyen: TEST-2 (In Progress), TEST-5 (Open) = 2
        # Suzuki: 0
        assert workload[101]["open_count"] == 2
        assert workload[102]["open_count"] == 2
        assert workload[103]["open_count"] == 0

    def test_identifies_overloaded_members(self):
        """Overloaded = open_count > threshold."""
        issues = load_fixture("sample_issues.json")
        users = load_fixture("sample_users.json")
        statuses = load_fixture("sample_statuses.json")

        analyzer = StatusAnalyzer(statuses, closed_status_names=["Closed"])
        overloaded = analyzer.get_overloaded_members(issues, users, threshold=1)

        # Both Tanaka and Nguyen have 2 issues, threshold=1
        assert len(overloaded) == 2

    def test_handles_unassigned_issues(self):
        """Unassigned issues should be tracked separately."""
        issues = load_fixture("sample_issues.json")
        users = load_fixture("sample_users.json")
        statuses = load_fixture("sample_statuses.json")

        analyzer = StatusAnalyzer(statuses, closed_status_names=["Closed"])
        workload = analyzer.get_workload(issues, users)

        # TEST-6 is unassigned - should appear in "unassigned" bucket
        assert workload.get("unassigned", {}).get("open_count", 0) == 1


class TestProjectSummary:
    """Tests for project summary generation."""

    def test_counts_by_status(self):
        """Summary should show count per status."""
        issues = load_fixture("sample_issues.json")
        statuses = load_fixture("sample_statuses.json")

        analyzer = StatusAnalyzer(statuses, closed_status_names=["Closed"])
        summary = analyzer.get_summary(issues)

        # Open: TEST-1, TEST-5, TEST-6 = 3
        # In Progress: TEST-2, TEST-3 = 2
        # Closed: TEST-4 = 1
        assert summary["by_status"]["Open"] == 3
        assert summary["by_status"]["In Progress"] == 2
        assert summary["by_status"]["Closed"] == 1

    def test_calculates_progress_percentage(self):
        """Progress = closed / total * 100."""
        issues = load_fixture("sample_issues.json")
        statuses = load_fixture("sample_statuses.json")

        analyzer = StatusAnalyzer(statuses, closed_status_names=["Closed"])
        summary = analyzer.get_summary(issues)

        # 1 closed out of 6 = 16.67%
        assert summary["progress_percent"] == pytest.approx(16.67, rel=0.1)

    def test_handles_empty_project(self):
        """Should not crash on empty issue list."""
        statuses = load_fixture("sample_statuses.json")

        analyzer = StatusAnalyzer(statuses, closed_status_names=["Closed"])
        summary = analyzer.get_summary([])

        assert summary["total"] == 0
        assert summary["progress_percent"] == 0


class TestMarkdownReport:
    """Tests for Markdown report generation."""

    def test_generates_markdown_with_tables(self):
        """Report should contain late tasks table, workload table, summary."""
        issues = load_fixture("sample_issues.json")
        users = load_fixture("sample_users.json")
        statuses = load_fixture("sample_statuses.json")
        today = date(2026, 1, 28)

        analyzer = StatusAnalyzer(statuses, closed_status_names=["Closed"])
        report = analyzer.generate_report(issues, users, today)

        # Check structure
        assert "# Project Status Report" in report
        assert "## Late Tasks" in report
        assert "## Workload" in report
        assert "## Summary" in report
        assert "| Issue |" in report  # Table header
