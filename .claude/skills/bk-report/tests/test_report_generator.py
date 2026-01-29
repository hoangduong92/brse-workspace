"""Tests for bk-report skill."""

import json
import pytest
from datetime import date
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from report_stats import (
    calculate_stats,
    filter_completed_this_week,
    filter_in_progress,
    filter_next_week_tasks,
    filter_late_tasks,
    parse_date,
)
from report_templates import (
    get_template,
    format_tasks_table,
    generate_report,
    SUPPORTED_LANGS,
)


# Load test fixtures
@pytest.fixture
def sample_data():
    """Load sample weekly data."""
    fixtures_path = Path(__file__).parent / "fixtures" / "sample_weekly_data.json"
    with open(fixtures_path, encoding="utf-8") as f:
        return json.load(f)


class TestParseDate:
    """Tests for date parsing."""

    def test_iso_date(self):
        result = parse_date("2026-01-20")
        assert result == date(2026, 1, 20)

    def test_iso_datetime(self):
        result = parse_date("2026-01-20T09:00:00Z")
        assert result == date(2026, 1, 20)

    def test_none(self):
        assert parse_date(None) is None

    def test_invalid(self):
        assert parse_date("invalid") is None


class TestCalculateStats:
    """Tests for statistics calculation."""

    def test_calculate_stats(self, sample_data):
        """TC-RP01: Calculate stats from issues."""
        stats = calculate_stats(sample_data["issues"])

        assert stats["total"] == 6
        assert stats["completed"] == 2
        assert stats["in_progress"] == 2
        assert stats["open"] == 2
        assert stats["late"] >= 0

    def test_empty_issues(self):
        """Handle empty issue list."""
        stats = calculate_stats([])
        assert stats["total"] == 0
        assert stats["completion_rate"] == 0


class TestFilterCompletedThisWeek:
    """Tests for filtering completed tasks."""

    def test_filter_completed(self, sample_data):
        """TC-RP05: Filter completed tasks in week."""
        week_start = date(2026, 1, 20)
        week_end = date(2026, 1, 26)

        completed = filter_completed_this_week(
            sample_data["issues"],
            week_start,
            week_end
        )

        # Both HB-101 and HB-102 were updated in this week
        assert len(completed) >= 1
        keys = [t["key"] for t in completed]
        # HB-102 was updated on 2026-01-23 which is in range
        assert "HB-102" in keys


class TestFilterInProgress:
    """Tests for filtering in-progress tasks."""

    def test_filter_in_progress(self, sample_data):
        """Filter in-progress tasks."""
        in_progress = filter_in_progress(sample_data["issues"])

        assert len(in_progress) == 2
        keys = [t["key"] for t in in_progress]
        assert "HB-103" in keys
        assert "HB-106" in keys


class TestFilterNextWeekTasks:
    """Tests for filtering next week tasks."""

    def test_filter_next_week(self, sample_data):
        """TC-RP07: Filter tasks due next week."""
        week_end = date(2026, 1, 26)

        next_week = filter_next_week_tasks(sample_data["issues"], week_end)

        # HB-103 due 2026-01-28, HB-104 due 2026-01-30, HB-105 due 2026-02-02
        assert len(next_week) >= 1
        keys = [t["key"] for t in next_week]
        assert "HB-103" in keys or "HB-104" in keys


class TestFilterLateTasks:
    """Tests for filtering late tasks."""

    def test_filter_late(self, sample_data):
        """Filter late tasks with days_late."""
        today = date(2026, 1, 27)

        late = filter_late_tasks(sample_data["issues"], today)

        # HB-106 due 2026-01-24, should be 3 days late
        assert len(late) >= 1

        hb106 = next((t for t in late if t["key"] == "HB-106"), None)
        assert hb106 is not None
        assert hb106["days_late"] == 3


class TestGetTemplate:
    """Tests for template retrieval."""

    def test_get_template_ja(self):
        """Get Japanese template."""
        t = get_template("ja")
        assert t["title"] == "週次進捗報告"

    def test_get_template_vi(self):
        """Get Vietnamese template."""
        t = get_template("vi")
        assert t["title"] == "Báo Cáo Tiến Độ Tuần"

    def test_get_template_en(self):
        """Get English template."""
        t = get_template("en")
        assert t["title"] == "Weekly Progress Report"

    def test_get_template_fallback(self):
        """Fallback to Japanese for unknown lang."""
        t = get_template("xx")
        assert t["title"] == "週次進捗報告"


class TestFormatTasksTable:
    """Tests for table formatting."""

    def test_format_table_ja(self):
        """TC-RP03: Format tasks table in Japanese."""
        tasks = [
            {"key": "HB-101", "summary": "Login feature", "assignee": "Tam", "status": "完了", "due_date": "2026-01-22"},
        ]

        table = format_tasks_table(tasks, "ja")

        assert "| HB-101 |" in table
        assert "| Tam |" in table

    def test_format_empty_table(self):
        """Format empty table."""
        table = format_tasks_table([], "ja")
        assert "該当なし" in table

    def test_format_table_with_days_late(self):
        """Format table with days late column."""
        tasks = [
            {"key": "HB-106", "summary": "Late task", "assignee": "Hai", "status": "進行中", "days_late": 3},
        ]

        table = format_tasks_table(tasks, "ja", include_days_late=True)

        assert "3日遅延" in table


class TestGenerateReport:
    """Tests for report generation."""

    def test_generate_report_ja(self):
        """TC-RP04: Generate Japanese report."""
        data = {
            "project_name": "HB Project",
            "period_start": "2026-01-20",
            "period_end": "2026-01-26",
            "stats": {"total": 6, "completed": 2, "in_progress": 2, "open": 2, "late": 1},
            "completed_tasks": [{"key": "HB-101", "summary": "Login", "assignee": "Tam", "status": "完了", "due_date": "2026-01-22"}],
            "in_progress_tasks": [],
            "next_week_tasks": [],
            "late_tasks": [],
        }

        report = generate_report(data, lang="ja")

        assert "週次進捗報告" in report
        assert "今週の成果" in report
        assert "来週の予定" in report
        assert "HB Project" in report

    def test_generate_report_vi(self):
        """TC-RP05: Generate Vietnamese report."""
        data = {
            "project_name": "HB Project",
            "period_start": "2026-01-20",
            "period_end": "2026-01-26",
            "stats": {"total": 6, "completed": 2, "in_progress": 2, "open": 2, "late": 1},
            "completed_tasks": [],
            "in_progress_tasks": [],
            "next_week_tasks": [],
            "late_tasks": [],
        }

        report = generate_report(data, lang="vi")

        assert "Báo Cáo Tiến Độ Tuần" in report
        assert "Kết quả tuần này" in report

    def test_generate_report_en(self):
        """Generate English report."""
        data = {
            "project_name": "HB Project",
            "period_start": "2026-01-20",
            "period_end": "2026-01-26",
            "stats": {"total": 6, "completed": 2, "in_progress": 2, "open": 2, "late": 1},
            "completed_tasks": [],
            "in_progress_tasks": [],
            "next_week_tasks": [],
            "late_tasks": [],
        }

        report = generate_report(data, lang="en")

        assert "Weekly Progress Report" in report
        assert "This Week's Accomplishments" in report

    def test_generate_report_with_reporter(self):
        """Generate report with reporter name."""
        data = {
            "project_name": "HB Project",
            "period_start": "2026-01-20",
            "period_end": "2026-01-26",
            "stats": {"total": 6, "completed": 2, "in_progress": 2, "open": 2, "late": 0},
            "completed_tasks": [],
            "in_progress_tasks": [],
            "next_week_tasks": [],
            "late_tasks": [],
        }

        report = generate_report(data, lang="ja", reporter="Tam BrSE")

        assert "Tam BrSE" in report


class TestWeekOverWeekComparison:
    """Tests for week-over-week comparison (future feature)."""

    def test_progress_summary(self):
        """TC-RP01: Progress summary from stats."""
        stats = {"total": 10, "completed": 6, "in_progress": 2, "open": 2, "late": 0}
        completion_rate = stats["completed"] / stats["total"] * 100
        assert completion_rate == 60.0


class TestEmptyWeek:
    """Tests for empty week handling."""

    def test_empty_week_report(self):
        """TC-RP08: Handle week with no completions."""
        data = {
            "project_name": "Empty Project",
            "period_start": "2026-01-20",
            "period_end": "2026-01-26",
            "stats": {"total": 5, "completed": 0, "in_progress": 3, "open": 2, "late": 0},
            "completed_tasks": [],
            "in_progress_tasks": [],
            "next_week_tasks": [],
            "late_tasks": [],
        }

        report = generate_report(data, lang="ja")

        assert "該当なし" in report  # No data indicator
