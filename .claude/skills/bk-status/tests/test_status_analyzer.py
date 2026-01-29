"""TDD tests for bk-status analyzer.

Tests written first (TDD red phase) - will fail until StatusAnalyzer is implemented.
"""

import json
import pytest
from datetime import date
from pathlib import Path

# Import will fail until implemented - this is expected in TDD
from scripts.status_analyzer import StatusAnalyzer
from scripts.models import RiskLevel

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
        """Report should contain action items, workload table, summary."""
        issues = load_fixture("sample_issues.json")
        users = load_fixture("sample_users.json")
        statuses = load_fixture("sample_statuses.json")
        today = date(2026, 1, 28)

        analyzer = StatusAnalyzer(statuses, closed_status_names=["Closed"])
        report = analyzer.generate_report(issues, users, today)

        # Check structure - updated for new Action Items section
        assert "# Project Status Report" in report
        assert "Action Required" in report  # New executive summary section
        assert "## BrSE Insights" in report
        assert "## Summary" in report
        assert "| Issue |" in report  # Table header


class TestHoursProgress:
    """Tests for hours-based progress calculation."""

    def test_calculates_hours_based_progress(self):
        """Progress = sum(actual) / sum(estimated) * 100."""
        issues = load_fixture("sample_issues.json")
        statuses = load_fixture("sample_statuses.json")

        analyzer = StatusAnalyzer(statuses, closed_status_names=["Closed"])
        summary = analyzer.get_summary(issues)

        # Total estimated: 16 + 8 + 20 + 12 + 0 + 4 = 60
        # Total actual: 4 + 6 + 10 + 12 + 0 + 2 = 34
        # Progress = 34/60 * 100 = 56.67%
        assert summary["hours_progress_percent"] == pytest.approx(56.67, rel=0.1)
        assert summary["total_estimated_hours"] == 60.0
        assert summary["total_actual_hours"] == 34.0

    def test_returns_none_when_no_hours_data(self):
        """Returns None for hours progress if no issues have estimated hours."""
        statuses = load_fixture("sample_statuses.json")
        issues = [
            {"id": 1, "status": {"id": 1}, "estimatedHours": None, "actualHours": None},
            {"id": 2, "status": {"id": 2}}  # No hours fields
        ]

        analyzer = StatusAnalyzer(statuses, closed_status_names=["Closed"])
        summary = analyzer.get_summary(issues)

        assert summary["hours_progress_percent"] is None
        assert summary["total_estimated_hours"] is None


class TestRiskDetection:
    """Tests for task risk assessment."""

    def test_on_track_task(self):
        """Task with sufficient time is ON_TRACK."""
        statuses = load_fixture("sample_statuses.json")
        analyzer = StatusAnalyzer(statuses, closed_status_names=["Closed"])

        # 10h remaining, 5 days left, capacity 4h/day
        # required_velocity = 10/5 = 2h/day <= 4h/day
        issue = {
            "issueKey": "TEST-A",
            "estimatedHours": 20,
            "actualHours": 10,
            "dueDate": "2026-02-02",
            "status": {"id": 1}  # Open
        }
        today = date(2026, 1, 28)

        risk = analyzer.assess_task_risk(issue, today, capacity=4.0)
        assert risk["level"].value == "on_track"
        assert risk["required_velocity"] == 2.0
        assert risk["days_remaining"] == 5

    def test_at_risk_task(self):
        """Task requiring more than capacity is AT_RISK."""
        statuses = load_fixture("sample_statuses.json")
        analyzer = StatusAnalyzer(statuses, closed_status_names=["Closed"])

        # 20h remaining, 2 days left, capacity 4h/day
        # required_velocity = 20/2 = 10h/day > 4h/day
        issue = {
            "issueKey": "TEST-B",
            "estimatedHours": 30,
            "actualHours": 10,
            "dueDate": "2026-01-30",
            "status": {"id": 1}  # Open
        }
        today = date(2026, 1, 28)

        risk = analyzer.assess_task_risk(issue, today, capacity=4.0)
        assert risk["level"].value == "at_risk"
        assert risk["required_velocity"] == 10.0
        assert risk["days_remaining"] == 2

    def test_late_task(self):
        """Past due + not closed = LATE."""
        statuses = load_fixture("sample_statuses.json")
        analyzer = StatusAnalyzer(statuses, closed_status_names=["Closed"])

        issue = {
            "issueKey": "TEST-C",
            "dueDate": "2026-01-20",
            "status": {"id": 1}  # Open
        }
        today = date(2026, 1, 28)

        risk = analyzer.assess_task_risk(issue, today)
        assert risk["level"].value == "late"
        assert risk["days_overdue"] == 8

    def test_closed_task_no_risk(self):
        """Closed tasks have no risk."""
        statuses = load_fixture("sample_statuses.json")
        analyzer = StatusAnalyzer(statuses, closed_status_names=["Closed"])

        issue = {
            "issueKey": "TEST-D",
            "dueDate": "2026-01-15",  # Past due
            "status": {"id": 4}  # Closed
        }
        today = date(2026, 1, 28)

        risk = analyzer.assess_task_risk(issue, today)
        assert risk["level"] is None
        assert risk["reason"] == "closed"

    def test_no_due_date_no_risk(self):
        """Tasks without due date cannot be assessed."""
        statuses = load_fixture("sample_statuses.json")
        analyzer = StatusAnalyzer(statuses, closed_status_names=["Closed"])

        issue = {
            "issueKey": "TEST-E",
            "dueDate": None,
            "status": {"id": 1}
        }
        today = date(2026, 1, 28)

        risk = analyzer.assess_task_risk(issue, today)
        assert risk["level"] is None
        assert risk["reason"] == "no_due_date"


class TestGetAtRiskTasks:
    """Tests for get_at_risk_tasks method."""

    def test_returns_at_risk_tasks_only(self):
        """Should return only AT_RISK tasks, not LATE or ON_TRACK."""
        statuses = load_fixture("sample_statuses.json")
        analyzer = StatusAnalyzer(statuses, closed_status_names=["Closed"])

        issues = [
            # AT_RISK: 15h remaining, 2 days, capacity 4 -> need 7.5h/day
            {"issueKey": "RISK-1", "estimatedHours": 20, "actualHours": 5,
             "dueDate": "2026-01-30", "status": {"id": 1}},
            # ON_TRACK: 5h remaining, 5 days -> need 1h/day
            {"issueKey": "OK-1", "estimatedHours": 10, "actualHours": 5,
             "dueDate": "2026-02-02", "status": {"id": 1}},
            # LATE: past due
            {"issueKey": "LATE-1", "dueDate": "2026-01-20", "status": {"id": 1}},
        ]
        today = date(2026, 1, 28)

        at_risk = analyzer.get_at_risk_tasks(issues, today, capacity=4.0)

        assert len(at_risk) == 1
        assert at_risk[0]["issueKey"] == "RISK-1"

    def test_sorted_by_required_velocity(self):
        """At-risk tasks should be sorted by required velocity (most urgent first)."""
        statuses = load_fixture("sample_statuses.json")
        analyzer = StatusAnalyzer(statuses, closed_status_names=["Closed"])

        issues = [
            # Less urgent: 10h remaining, 2 days -> 5h/day
            {"issueKey": "RISK-A", "estimatedHours": 15, "actualHours": 5,
             "dueDate": "2026-01-30", "status": {"id": 1}},
            # More urgent: 16h remaining, 2 days -> 8h/day
            {"issueKey": "RISK-B", "estimatedHours": 20, "actualHours": 4,
             "dueDate": "2026-01-30", "status": {"id": 1}},
        ]
        today = date(2026, 1, 28)

        at_risk = analyzer.get_at_risk_tasks(issues, today, capacity=4.0)

        assert len(at_risk) == 2
        assert at_risk[0]["issueKey"] == "RISK-B"  # 8h/day first
        assert at_risk[1]["issueKey"] == "RISK-A"  # 5h/day second


# =============================================================================
# Brainstorm Test Cases (TC-S01 to TC-S18)
# Reference: plans/reports/brainstorm-260128-1658-brsekit-test-cases.md
# =============================================================================


class TestProgressCalculation:
    """Tests for progress calculation (TC-S01 to TC-S05).

    Brainstorm formula: actual_hours / estimate_hours
    """

    def test_tc_s01_normal_progress(self):
        """TC-S01: Normal progress = actual_hours / estimated_hours.

        Input: est=16h, actual=4h
        Expected: 25%
        """
        statuses = load_fixture("sample_statuses.json")
        analyzer = StatusAnalyzer(statuses, closed_status_names=["Closed"])

        issues = [
            {"id": 1, "status": {"id": 1}, "estimatedHours": 16.0, "actualHours": 4.0}
        ]
        summary = analyzer.get_summary(issues)

        # 4/16 = 25%
        assert summary["hours_progress_percent"] == pytest.approx(25.0, rel=0.1)

    def test_tc_s02_overtime_progress(self):
        """TC-S02: Overtime = actual > estimated (>100%).

        Input: est=8h, actual=12h
        Expected: 150% (over budget)
        """
        statuses = load_fixture("sample_statuses.json")
        analyzer = StatusAnalyzer(statuses, closed_status_names=["Closed"])

        issues = [
            {"id": 1, "status": {"id": 1}, "estimatedHours": 8.0, "actualHours": 12.0}
        ]
        summary = analyzer.get_summary(issues)

        # 12/8 = 150%
        assert summary["hours_progress_percent"] == pytest.approx(150.0, rel=0.1)

    def test_tc_s03_no_estimate_returns_none(self):
        """TC-S03: No estimate should return None (not crash).

        Input: est=null
        Expected: hours_progress_percent = None
        """
        statuses = load_fixture("sample_statuses.json")
        analyzer = StatusAnalyzer(statuses, closed_status_names=["Closed"])

        issues = [
            {"id": 1, "status": {"id": 1}, "estimatedHours": None, "actualHours": 5.0}
        ]
        summary = analyzer.get_summary(issues)

        assert summary["hours_progress_percent"] is None
        assert summary["total_estimated_hours"] is None

    def test_tc_s04_no_actual_zero_progress(self):
        """TC-S04: No actual hours = 0% progress.

        Input: est=16h, actual=0h
        Expected: 0%
        """
        statuses = load_fixture("sample_statuses.json")
        analyzer = StatusAnalyzer(statuses, closed_status_names=["Closed"])

        issues = [
            {"id": 1, "status": {"id": 1}, "estimatedHours": 16.0, "actualHours": 0.0}
        ]
        summary = analyzer.get_summary(issues)

        # 0/16 = 0%
        assert summary["hours_progress_percent"] == 0.0

    def test_tc_s05_closed_task_counts_as_done(self):
        """TC-S05: Closed task contributes to progress.

        Input: status=Closed
        Expected: Counts in closed_count (100% done for that task)
        """
        statuses = load_fixture("sample_statuses.json")
        analyzer = StatusAnalyzer(statuses, closed_status_names=["Closed"])

        issues = [
            {"id": 1, "status": {"id": 4}},  # Closed
            {"id": 2, "status": {"id": 1}}   # Open
        ]
        summary = analyzer.get_summary(issues)

        # 1 closed out of 2 = 50%
        assert summary["closed_count"] == 1
        assert summary["progress_percent"] == 50.0


class TestDeadlineRisk:
    """Tests for deadline risk detection (TC-S06 to TC-S10).

    Brainstorm formulas:
    - required_velocity = hours_remaining / days_remaining
    - ON_TRACK: required_velocity <= capacity
    - AT_RISK: required_velocity > capacity
    - LATE: due_date < today
    """

    def test_tc_s06_on_track_scenario(self):
        """TC-S06: On track when velocity <= capacity.

        Scenario: remain=12h, days=3, cap=6h/day
        Expected: ON_TRACK (need 4h/day, have 6h/day)
        """
        statuses = load_fixture("sample_statuses.json")
        analyzer = StatusAnalyzer(statuses, closed_status_names=["Closed"])

        issue = {
            "issueKey": "TC-S06",
            "estimatedHours": 20,
            "actualHours": 8,  # 12h remaining
            "dueDate": "2026-01-31",  # 3 days from Jan 28
            "status": {"id": 1}
        }
        today = date(2026, 1, 28)

        risk = analyzer.assess_task_risk(issue, today, capacity=6.0)

        assert risk["level"].value == "on_track"
        assert risk["required_velocity"] == 4.0  # 12/3
        assert risk["days_remaining"] == 3

    def test_tc_s07_at_risk_scenario(self):
        """TC-S07: At risk when velocity > capacity.

        Scenario: remain=12h, days=2, cap=6h/day
        Expected: AT_RISK (need 6h/day, equals capacity = still at risk)
        """
        statuses = load_fixture("sample_statuses.json")
        analyzer = StatusAnalyzer(statuses, closed_status_names=["Closed"])

        issue = {
            "issueKey": "TC-S07",
            "estimatedHours": 20,
            "actualHours": 8,  # 12h remaining
            "dueDate": "2026-01-29",  # 1 day from Jan 28
            "status": {"id": 1}
        }
        today = date(2026, 1, 28)

        risk = analyzer.assess_task_risk(issue, today, capacity=6.0)

        # 12h / 1 day = 12h/day > 6h/day capacity
        assert risk["level"].value == "at_risk"
        assert risk["required_velocity"] == 12.0

    def test_tc_s08_late_scenario(self):
        """TC-S08: Late when due_date < today.

        Scenario: Due yesterday
        Expected: LATE
        """
        statuses = load_fixture("sample_statuses.json")
        analyzer = StatusAnalyzer(statuses, closed_status_names=["Closed"])

        issue = {
            "issueKey": "TC-S08",
            "estimatedHours": 8,
            "actualHours": 4,
            "dueDate": "2026-01-27",  # Yesterday
            "status": {"id": 1}
        }
        today = date(2026, 1, 28)

        risk = analyzer.assess_task_risk(issue, today, capacity=6.0)

        assert risk["level"].value == "late"
        assert risk["days_overdue"] == 1

    def test_tc_s10_overdue_days_calculation(self):
        """TC-S10: Overdue = due < today, calculate days overdue.

        Scenario: Due 5 days ago
        Expected: LATE with 5 days overdue
        """
        statuses = load_fixture("sample_statuses.json")
        analyzer = StatusAnalyzer(statuses, closed_status_names=["Closed"])

        issue = {
            "issueKey": "TC-S10",
            "dueDate": "2026-01-23",  # 5 days ago
            "status": {"id": 1}
        }
        today = date(2026, 1, 28)

        risk = analyzer.assess_task_risk(issue, today)

        assert risk["level"].value == "late"
        assert risk["days_overdue"] == 5


class TestMemberWorkloadAdvanced:
    """Tests for member workload (TC-S11 to TC-S15).

    Note: Current implementation uses count-based workload.
    TC-S11, TC-S13, TC-S14 require hours-based workload (future).
    """

    def test_tc_s12_threshold_overloaded(self):
        """TC-S12: Member hits overload threshold.

        Scenario: 3 open issues, threshold=2
        Expected: Marked as overloaded
        """
        statuses = load_fixture("sample_statuses.json")
        analyzer = StatusAnalyzer(statuses, closed_status_names=["Closed"])

        users = [{"id": 101, "name": "Tanaka"}]
        issues = [
            {"id": 1, "assignee": {"id": 101}, "status": {"id": 1}},  # Open
            {"id": 2, "assignee": {"id": 101}, "status": {"id": 2}},  # In Progress
            {"id": 3, "assignee": {"id": 101}, "status": {"id": 1}},  # Open
        ]

        overloaded = analyzer.get_overloaded_members(issues, users, threshold=2)

        assert len(overloaded) == 1
        assert overloaded[0]["name"] == "Tanaka"
        assert overloaded[0]["open_count"] == 3

    def test_tc_s15_multiple_tasks_aggregate(self):
        """TC-S15: Multiple tasks with different deadlines aggregate correctly.

        Scenario: Member has 5 tasks with various deadlines
        Expected: All non-closed tasks counted
        """
        statuses = load_fixture("sample_statuses.json")
        analyzer = StatusAnalyzer(statuses, closed_status_names=["Closed"])

        users = [{"id": 101, "name": "Tanaka"}]
        issues = [
            {"id": 1, "assignee": {"id": 101}, "status": {"id": 1}, "dueDate": "2026-01-29"},
            {"id": 2, "assignee": {"id": 101}, "status": {"id": 1}, "dueDate": "2026-01-30"},
            {"id": 3, "assignee": {"id": 101}, "status": {"id": 2}, "dueDate": "2026-02-01"},
            {"id": 4, "assignee": {"id": 101}, "status": {"id": 4}, "dueDate": "2026-01-25"},  # Closed
            {"id": 5, "assignee": {"id": 101}, "status": {"id": 1}, "dueDate": "2026-02-05"},
        ]

        workload = analyzer.get_workload(issues, users)

        # 4 open tasks (1 closed excluded)
        assert workload[101]["open_count"] == 4


class TestMemberProgress:
    """Tests for member progress calculation."""

    def test_member_progress_by_hours(self):
        """Member progress calculated by hours worked vs estimated."""
        statuses = load_fixture("sample_statuses.json")
        analyzer = StatusAnalyzer(statuses, closed_status_names=["Closed"])

        users = [{"id": 101, "name": "Tanaka"}]
        issues = [
            {"id": 1, "assignee": {"id": 101}, "status": {"id": 1},
             "estimatedHours": 10, "actualHours": 5},
            {"id": 2, "assignee": {"id": 101}, "status": {"id": 4},
             "estimatedHours": 8, "actualHours": 8},  # Closed
        ]

        progress = analyzer.get_member_progress(issues, users)

        assert len(progress) == 1
        tanaka = progress[0]
        assert tanaka["name"] == "Tanaka"
        assert tanaka["total"] == 2
        assert tanaka["closed"] == 1
        assert tanaka["count_progress"] == 50.0  # 1/2 closed
        assert tanaka["estimated_hours"] == 18.0
        assert tanaka["actual_hours"] == 13.0
        # hours_progress = 13/18 * 100 = 72.2%
        assert tanaka["hours_progress"] == pytest.approx(72.2, rel=0.1)

    def test_member_progress_sorted_by_hours(self):
        """Members sorted by hours_progress ascending (needs attention first)."""
        statuses = load_fixture("sample_statuses.json")
        analyzer = StatusAnalyzer(statuses, closed_status_names=["Closed"])

        users = [
            {"id": 101, "name": "Tanaka"},
            {"id": 102, "name": "Nguyen"}
        ]
        issues = [
            # Tanaka: 80% hours progress
            {"id": 1, "assignee": {"id": 101}, "status": {"id": 1},
             "estimatedHours": 10, "actualHours": 8},
            # Nguyen: 30% hours progress (needs attention)
            {"id": 2, "assignee": {"id": 102}, "status": {"id": 1},
             "estimatedHours": 10, "actualHours": 3},
        ]

        progress = analyzer.get_member_progress(issues, users)

        # Nguyen first (30%), then Tanaka (80%)
        assert progress[0]["name"] == "Nguyen"
        assert progress[1]["name"] == "Tanaka"


class TestScheduleWarnings:
    """Tests for schedule warnings (weekend/holiday detection)."""

    def test_detects_due_date_on_weekend(self):
        """Due date on Saturday/Sunday should trigger warning."""
        from scripts.calendar_utils import CalendarConfig

        statuses = load_fixture("sample_statuses.json")
        calendar = CalendarConfig(working_days=[0, 1, 2, 3, 4])  # Mon-Fri
        analyzer = StatusAnalyzer(
            statuses, closed_status_names=["Closed"], calendar=calendar
        )

        issues = [
            # Due date on Saturday (Jan 31, 2026 is Saturday)
            {"issueKey": "SAT-1", "summary": "Task on Saturday",
             "dueDate": "2026-01-31", "status": {"id": 1}},
            # Due date on Sunday (Feb 1, 2026 is Sunday)
            {"issueKey": "SUN-1", "summary": "Task on Sunday",
             "dueDate": "2026-02-01", "status": {"id": 1}},
            # Due date on Monday (Feb 2, 2026 is Monday) - OK
            {"issueKey": "MON-1", "summary": "Task on Monday",
             "dueDate": "2026-02-02", "status": {"id": 1}},
        ]

        warnings = analyzer.get_schedule_warnings(issues)

        assert len(warnings) == 2
        warning_keys = [w["issue_key"] for w in warnings]
        assert "SAT-1" in warning_keys
        assert "SUN-1" in warning_keys
        assert "MON-1" not in warning_keys

    def test_detects_start_date_on_weekend(self):
        """Start date on weekend should trigger warning."""
        from scripts.calendar_utils import CalendarConfig

        statuses = load_fixture("sample_statuses.json")
        calendar = CalendarConfig(working_days=[0, 1, 2, 3, 4])  # Mon-Fri
        analyzer = StatusAnalyzer(
            statuses, closed_status_names=["Closed"], calendar=calendar
        )

        issues = [
            # Start date on Saturday
            {"issueKey": "START-SAT", "summary": "Starts on Saturday",
             "startDate": "2026-01-31", "dueDate": "2026-02-05", "status": {"id": 1}},
        ]

        warnings = analyzer.get_schedule_warnings(issues)

        assert len(warnings) == 1
        assert warnings[0]["issue_key"] == "START-SAT"
        assert warnings[0]["date_type"] == "startDate"
        assert "weekend" in warnings[0]["reason"]

    def test_detects_due_date_on_holiday(self):
        """Due date on holiday should trigger warning."""
        from scripts.calendar_utils import CalendarConfig

        holidays = [date(2026, 2, 11)]  # National Foundation Day (Japan)
        statuses = load_fixture("sample_statuses.json")
        calendar = CalendarConfig(working_days=[0, 1, 2, 3, 4], holidays=holidays)
        analyzer = StatusAnalyzer(
            statuses, closed_status_names=["Closed"], calendar=calendar
        )

        issues = [
            {"issueKey": "HOL-1", "summary": "Task on holiday",
             "dueDate": "2026-02-11", "status": {"id": 1}},
        ]

        warnings = analyzer.get_schedule_warnings(issues)

        assert len(warnings) == 1
        assert warnings[0]["reason"] == "holiday"

    def test_no_warnings_without_calendar(self):
        """Without calendar config, no warnings generated."""
        statuses = load_fixture("sample_statuses.json")
        analyzer = StatusAnalyzer(statuses, closed_status_names=["Closed"])

        issues = [
            {"issueKey": "SAT-1", "summary": "Task on Saturday",
             "dueDate": "2026-01-31", "status": {"id": 1}},
        ]

        warnings = analyzer.get_schedule_warnings(issues)

        assert len(warnings) == 0

    def test_both_start_and_due_on_weekend(self):
        """Task with both start and due on weekend should have 2 warnings."""
        from scripts.calendar_utils import CalendarConfig

        statuses = load_fixture("sample_statuses.json")
        calendar = CalendarConfig(working_days=[0, 1, 2, 3, 4])
        analyzer = StatusAnalyzer(
            statuses, closed_status_names=["Closed"], calendar=calendar
        )

        issues = [
            # Both dates on weekend
            {"issueKey": "BOTH-WE", "summary": "Both on weekend",
             "startDate": "2026-01-31", "dueDate": "2026-02-01", "status": {"id": 1}},
        ]

        warnings = analyzer.get_schedule_warnings(issues)

        assert len(warnings) == 2
        date_types = [w["date_type"] for w in warnings]
        assert "startDate" in date_types
        assert "dueDate" in date_types


class TestCapacityExceeded:
    """Tests for capacity exceeded detection and analysis."""

    def test_detects_unscheduled_tasks(self):
        """Tasks that can't fit in capacity should be marked unscheduled."""
        from scripts.calendar_utils import CalendarConfig

        statuses = load_fixture("sample_statuses.json")
        calendar = CalendarConfig(working_days=[0, 1, 2, 3, 4])
        analyzer = StatusAnalyzer(
            statuses, closed_status_names=["Closed"], calendar=calendar
        )

        users = [{"id": 101, "name": "Tanaka"}]
        # 3 tasks totaling 30h, but only 12h available (2 days × 6h/day)
        today = date(2026, 1, 28)  # Wednesday
        sprint_end = date(2026, 1, 29)  # Thursday (2 working days)

        member_capacity = analyzer.analyze_member_capacity(
            [
                {"issueKey": "T-1", "summary": "Task 1", "assignee": {"id": 101},
                 "status": {"id": 1}, "dueDate": "2026-01-29",
                 "estimatedHours": 10, "actualHours": 0},
                {"issueKey": "T-2", "summary": "Task 2", "assignee": {"id": 101},
                 "status": {"id": 1}, "dueDate": "2026-01-29",
                 "estimatedHours": 10, "actualHours": 0},
                {"issueKey": "T-3", "summary": "Task 3", "assignee": {"id": 101},
                 "status": {"id": 1}, "dueDate": "2026-01-29",
                 "estimatedHours": 10, "actualHours": 0},
            ],
            users, today, hours_per_day=6.0, sprint_end=sprint_end
        )

        _, analysis = analyzer.generate_gantt_schedule_with_analysis(
            member_capacity, today, hours_per_day=6.0, sprint_end=sprint_end
        )

        assert analysis is not None
        assert analysis["has_unscheduled"] is True
        assert len(analysis["unscheduled_tasks"]) >= 1  # At least 1 task unscheduled
        assert analysis["deficit"] > 0

    def test_no_unscheduled_when_capacity_sufficient(self):
        """All tasks scheduled when capacity is sufficient."""
        from scripts.calendar_utils import CalendarConfig

        statuses = load_fixture("sample_statuses.json")
        calendar = CalendarConfig(working_days=[0, 1, 2, 3, 4])
        analyzer = StatusAnalyzer(
            statuses, closed_status_names=["Closed"], calendar=calendar
        )

        users = [{"id": 101, "name": "Tanaka"}]
        today = date(2026, 1, 28)  # Wednesday
        sprint_end = date(2026, 2, 6)  # Friday (8 working days = 48h capacity)

        member_capacity = analyzer.analyze_member_capacity(
            [
                {"issueKey": "T-1", "summary": "Task 1", "assignee": {"id": 101},
                 "status": {"id": 1}, "dueDate": "2026-02-06",
                 "estimatedHours": 20, "actualHours": 0},
                {"issueKey": "T-2", "summary": "Task 2", "assignee": {"id": 101},
                 "status": {"id": 1}, "dueDate": "2026-02-06",
                 "estimatedHours": 20, "actualHours": 0},
            ],
            users, today, hours_per_day=6.0, sprint_end=sprint_end
        )

        _, analysis = analyzer.generate_gantt_schedule_with_analysis(
            member_capacity, today, hours_per_day=6.0, sprint_end=sprint_end
        )

        assert analysis is not None
        assert analysis["has_unscheduled"] is False
        assert len(analysis["unscheduled_tasks"]) == 0

    def test_report_includes_capacity_warning(self):
        """Report should include capacity warning section when exceeded."""
        from scripts.calendar_utils import CalendarConfig

        statuses = load_fixture("sample_statuses.json")
        calendar = CalendarConfig(working_days=[0, 1, 2, 3, 4])
        analyzer = StatusAnalyzer(
            statuses, closed_status_names=["Closed"], calendar=calendar
        )

        users = [{"id": 101, "name": "Tanaka"}]
        today = date(2026, 1, 28)
        sprint_end = date(2026, 1, 29)  # Only 2 days

        issues = [
            {"issueKey": "T-1", "summary": "Big task", "assignee": {"id": 101},
             "status": {"id": 1}, "dueDate": "2026-01-29",
             "estimatedHours": 50, "actualHours": 0},
        ]

        report = analyzer.generate_report(
            issues, users, today,
            project_name="Test",
            hours_per_day=6.0,
            sprint_end=sprint_end
        )

        assert "Capacity Exceeded" in report
        assert "Re-scheduling Required" in report
        assert "Please Specify Task Priority" in report

    def test_report_includes_schedule_warnings(self):
        """Report should include schedule warnings section."""
        from scripts.calendar_utils import CalendarConfig

        statuses = load_fixture("sample_statuses.json")
        calendar = CalendarConfig(working_days=[0, 1, 2, 3, 4])
        analyzer = StatusAnalyzer(
            statuses, closed_status_names=["Closed"], calendar=calendar
        )

        users = [{"id": 101, "name": "Tanaka"}]
        today = date(2026, 1, 28)

        issues = [
            {"issueKey": "SAT-1", "summary": "Task on Saturday",
             "assignee": {"id": 101}, "status": {"id": 1},
             "dueDate": "2026-01-31",  # Saturday
             "estimatedHours": 8, "actualHours": 0},
        ]

        report = analyzer.generate_report(
            issues, users, today,
            project_name="Test",
            hours_per_day=6.0
        )

        assert "Schedule Warnings" in report
        assert "non-working days" in report
        assert "SAT-1" in report
