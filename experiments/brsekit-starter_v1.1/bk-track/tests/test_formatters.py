"""Tests for formatters module."""
import pytest
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch, PropertyMock

# Add scripts directory to path as a package
scripts_dir = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(scripts_dir.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "common"))

from scripts.formatters.markdown import MarkdownFormatter
from scripts.formatters.pptx_formatter import PptxFormatter
from scripts.models import TaskStatus, ProjectHealth, MemberLoad, ReportData, RiskLevel


class TestMarkdownFormatterInit:
    """Test MarkdownFormatter initialization."""

    def test_init_default(self):
        """Test MarkdownFormatter initialization."""
        formatter = MarkdownFormatter()
        assert formatter is not None


class TestMarkdownFormatterFormatStatus:
    """Test format_status method."""

    def test_format_status_complete_analysis(self, sample_analysis_results):
        """Test formatting complete status analysis."""
        formatter = MarkdownFormatter()

        output = formatter.format_status(sample_analysis_results)

        assert "Project Status Report" in output
        assert "Health Overview" in output
        assert "80.0%" in output  # Health score value present
        assert "Late Tasks" in output or len(sample_analysis_results["late_tasks"]) == 0
        assert "Team Workload" in output

    def test_format_status_no_data(self):
        """Test formatting with no analysis data."""
        formatter = MarkdownFormatter()
        output = formatter.format_status({})
        assert "No analysis data available" in output

    def test_format_status_no_health(self):
        """Test formatting without health data."""
        formatter = MarkdownFormatter()
        output = formatter.format_status({"other_key": "value"})
        assert "No analysis data available" in output

    def test_format_status_empty_lists(self):
        """Test formatting with empty task lists."""
        formatter = MarkdownFormatter()

        analysis = {
            "health": ProjectHealth(
                total_issues=10,
                completed=5,
                in_progress=5,
                late_count=0,
                at_risk_count=0,
                health_score=90.0
            ),
            "late_tasks": [],
            "at_risk_tasks": [],
            "member_loads": []
        }

        output = formatter.format_status(analysis)

        assert "Project Status Report" in output
        assert "90.0%" in output  # Health score value present
        assert "## Late Tasks" not in output  # No Late Tasks section
        assert "## At Risk\n" not in output  # No At Risk section (but "At Risk:" stats is ok)
        assert "Team Workload" not in output

    def test_format_status_contains_headers(self):
        """Test that output contains proper markdown headers."""
        formatter = MarkdownFormatter()

        analysis = {
            "health": ProjectHealth(
                total_issues=1,
                completed=0,
                in_progress=1,
                late_count=0,
                at_risk_count=0,
                health_score=100.0
            ),
            "late_tasks": [],
            "at_risk_tasks": [],
            "member_loads": []
        }

        output = formatter.format_status(analysis)

        assert "# Project Status Report" in output
        assert "## Health Overview" in output


class TestMarkdownFormatterHealthBadge:
    """Test format_health_badge method."""

    def test_format_health_badge_excellent(self):
        """Test health badge for excellent score."""
        formatter = MarkdownFormatter()

        health = ProjectHealth(
            total_issues=10,
            completed=10,
            in_progress=0,
            late_count=0,
            at_risk_count=0,
            health_score=95.0
        )

        badge = formatter.format_health_badge(health)

        assert "95.0%" in badge or "95%" in badge
        # Should contain green indicator
        assert "🟢" in badge

    def test_format_health_badge_medium(self):
        """Test health badge for medium score."""
        formatter = MarkdownFormatter()

        health = ProjectHealth(
            total_issues=10,
            completed=6,
            in_progress=3,
            late_count=1,
            at_risk_count=0,
            health_score=65.0
        )

        badge = formatter.format_health_badge(health)

        assert "65.0%" in badge or "65%" in badge
        # Should contain yellow indicator
        assert "🟡" in badge

    def test_format_health_badge_poor(self):
        """Test health badge for poor score."""
        formatter = MarkdownFormatter()

        health = ProjectHealth(
            total_issues=10,
            completed=1,
            in_progress=2,
            late_count=7,
            at_risk_count=2,
            health_score=30.0
        )

        badge = formatter.format_health_badge(health)

        assert "30.0%" in badge or "30%" in badge
        # Should contain red indicator
        assert "🔴" in badge

    def test_format_health_badge_boundary_80(self):
        """Test health badge at 80% boundary."""
        formatter = MarkdownFormatter()

        health = ProjectHealth(
            total_issues=10,
            completed=8,
            in_progress=2,
            late_count=0,
            at_risk_count=0,
            health_score=80.0
        )

        badge = formatter.format_health_badge(health)

        assert "80.0%" in badge or "80%" in badge
        assert "🟢" in badge

    def test_format_health_badge_boundary_50(self):
        """Test health badge at 50% boundary."""
        formatter = MarkdownFormatter()

        health = ProjectHealth(
            total_issues=10,
            completed=5,
            in_progress=4,
            late_count=1,
            at_risk_count=0,
            health_score=50.0
        )

        badge = formatter.format_health_badge(health)

        assert "50.0%" in badge or "50%" in badge
        assert "🟡" in badge


class TestPptxFormatterInit:
    """Test PptxFormatter initialization."""

    def test_init_default(self):
        """Test PptxFormatter initialization with defaults."""
        formatter = PptxFormatter()
        assert formatter.template_dir is not None
        assert formatter.pptx_skill is not None

    def test_init_custom_template_dir(self):
        """Test PptxFormatter with custom template directory."""
        custom_dir = Path("/custom/templates")
        formatter = PptxFormatter(template_dir=custom_dir)
        assert formatter.template_dir == custom_dir

    def test_max_tasks_constant(self):
        """Test MAX_TASKS_PER_SLIDE constant."""
        assert PptxFormatter.MAX_TASKS_PER_SLIDE == 8


class TestPptxFormatterFormatTaskList:
    """Test _format_task_list method."""

    def test_format_task_list_within_limit(self):
        """Test formatting task list within slide limit."""
        formatter = PptxFormatter()

        tasks = [
            TaskStatus(
                issue_key=f"TEST-{i}",
                summary=f"Task {i}",
                status="In Progress",
                assignee=None,
                days_late=0,
                risk_level="low"
            )
            for i in range(5)
        ]

        html, overflow = formatter._format_task_list(tasks)

        assert len(tasks) <= formatter.MAX_TASKS_PER_SLIDE
        assert overflow == ""
        assert "TEST-0" in html
        assert "Task 0" in html

    def test_format_task_list_exceeds_limit(self):
        """Test formatting task list exceeding slide limit."""
        formatter = PptxFormatter()

        tasks = [
            TaskStatus(
                issue_key=f"TEST-{i}",
                summary=f"Task {i}",
                status="In Progress",
                assignee=None,
                days_late=0,
                risk_level="low"
            )
            for i in range(15)
        ]

        html, overflow = formatter._format_task_list(tasks)

        # Should only display first MAX_TASKS_PER_SLIDE
        assert "TEST-0" in html
        assert "TEST-7" in html
        assert "TEST-8" not in html
        # Should show overflow note
        assert "7 more tasks" in overflow

    def test_format_task_list_with_assignee(self):
        """Test formatting task list showing assignees."""
        formatter = PptxFormatter()

        tasks = [
            TaskStatus(
                issue_key="TEST-1",
                summary="Assigned Task",
                status="In Progress",
                assignee="John Doe",
                days_late=0,
                risk_level="low"
            )
        ]

        html, overflow = formatter._format_task_list(tasks, show_assignee=True)

        assert "TEST-1" in html
        assert "Assigned Task" in html
        assert "John Doe" in html or "@John Doe" in html

    def test_format_task_list_no_assignee(self):
        """Test formatting task list without assignee display."""
        formatter = PptxFormatter()

        tasks = [
            TaskStatus(
                issue_key="TEST-1",
                summary="Task",
                status="In Progress",
                assignee=None,
                days_late=0,
                risk_level="low"
            )
        ]

        html, overflow = formatter._format_task_list(tasks, show_assignee=True)

        assert "TEST-1" in html
        assert "Task" in html

    def test_format_task_list_empty(self):
        """Test formatting empty task list."""
        formatter = PptxFormatter()

        html, overflow = formatter._format_task_list([])

        assert html == ""
        assert overflow == ""


class TestPptxFormatterFormatMemberRows:
    """Test _format_member_rows method."""

    def test_format_member_rows_single(self):
        """Test formatting single member."""
        formatter = PptxFormatter()

        members = [
            MemberLoad(
                name="John Doe",
                total_tasks=5,
                completed=3,
                in_progress=2,
                overdue=0
            )
        ]

        html = formatter._format_member_rows(members)

        assert "John Doe" in html
        assert "5" in html
        assert "3" in html
        assert "<tr>" in html

    def test_format_member_rows_multiple(self):
        """Test formatting multiple members."""
        formatter = PptxFormatter()

        members = [
            MemberLoad(
                name=f"User{i}",
                total_tasks=5 + i,
                completed=3 + i,
                in_progress=2,
                overdue=i
            )
            for i in range(3)
        ]

        html = formatter._format_member_rows(members)

        assert "User0" in html
        assert "User1" in html
        assert "User2" in html
        assert html.count("<tr>") == 3

    def test_format_member_rows_load_levels(self):
        """Test member load level styling."""
        formatter = PptxFormatter()

        members = [
            MemberLoad(
                name="Light",
                total_tasks=2,
                completed=1,
                in_progress=1,
                overdue=0
            ),
            MemberLoad(
                name="Medium",
                total_tasks=5,
                completed=3,
                in_progress=1,
                overdue=1
            ),
            MemberLoad(
                name="Heavy",
                total_tasks=10,
                completed=2,
                in_progress=6,
                overdue=2
            )
        ]

        html = formatter._format_member_rows(members)

        # Should contain load level classes or names
        assert "Light" in html
        assert "Medium" in html
        assert "Heavy" in html

    def test_format_member_rows_empty(self):
        """Test formatting empty member list."""
        formatter = PptxFormatter()

        html = formatter._format_member_rows([])

        assert html == ""


class TestPptxFormatterRenderTemplate:
    """Test _render_template method."""

    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.read_text")
    def test_render_template_success(self, mock_read, mock_exists):
        """Test successful template rendering."""
        mock_exists.return_value = True
        mock_read.return_value = "<h1>{{title}}</h1><p>{{content}}</p>"

        formatter = PptxFormatter()
        html = formatter._render_template("test.html", {"title": "Test", "content": "Content"})

        assert "<h1>Test</h1>" in html
        assert "<p>Content</p>" in html

    @patch("pathlib.Path.exists")
    def test_render_template_not_found(self, mock_exists):
        """Test template not found."""
        mock_exists.return_value = False

        formatter = PptxFormatter()
        html = formatter._render_template("missing.html", {})

        assert "not found" in html or "Template" in html

    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.read_text")
    def test_render_template_multiple_vars(self, mock_read, mock_exists):
        """Test template with multiple variables."""
        mock_exists.return_value = True
        mock_read.return_value = "{{a}} - {{b}} - {{c}}"

        formatter = PptxFormatter()
        html = formatter._render_template("test.html", {"a": "1", "b": "2", "c": "3"})

        assert "1 - 2 - 3" in html

    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.read_text")
    def test_render_template_empty_context(self, mock_read, mock_exists):
        """Test template rendering with empty context."""
        mock_exists.return_value = True
        mock_read.return_value = "<div>Static content</div>"

        formatter = PptxFormatter()
        html = formatter._render_template("test.html", {})

        assert "<div>Static content</div>" in html


class TestPptxFormatterWriteHtmlFiles:
    """Test _write_html_files method."""

    def test_write_html_files(self):
        """Test writing HTML files to temp directory."""
        formatter = PptxFormatter()

        slides = [
            ("title", "<h1>Title</h1>"),
            ("summary", "<h2>Summary</h2>"),
            ("tasks", "<ul><li>Task 1</li></ul>")
        ]

        temp_dir = formatter._write_html_files(slides)

        assert temp_dir.exists()
        # Check that files were created
        files = list(temp_dir.glob("*.html"))
        assert len(files) == 3

        # Cleanup
        import shutil
        shutil.rmtree(temp_dir)

    def test_write_html_files_content(self):
        """Test that HTML content is written correctly."""
        formatter = PptxFormatter()

        slides = [("test", "<div>Test Content</div>")]

        temp_dir = formatter._write_html_files(slides)

        # Read first file
        files = sorted(temp_dir.glob("*.html"))
        assert len(files) > 0
        content = files[0].read_text(encoding="utf-8")
        assert "Test Content" in content

        # Cleanup
        import shutil
        shutil.rmtree(temp_dir)


class TestPptxFormatterRenderSlides:
    """Test _render_slides method."""

    @patch.object(PptxFormatter, "_render_template")
    def test_render_slides_basic(self, mock_render):
        """Test rendering slides with basic report data."""
        mock_render.return_value = "<slide>Test</slide>"

        formatter = PptxFormatter()

        health = ProjectHealth(
            total_issues=10,
            completed=5,
            in_progress=3,
            late_count=2,
            health_score=80.0
        )

        report = ReportData(
            project_name="TEST",
            date_range="2024-01-01 ~ 2024-01-07",
            health=health,
            completed_tasks=[],
            in_progress_tasks=[],
            late_tasks=[],
            member_loads=[]
        )

        slides = formatter._render_slides(report)

        # Should have at least title and summary
        assert len(slides) >= 2
        # First slide should be title
        assert slides[0][0] == "title"

    @patch.object(PptxFormatter, "_render_template")
    def test_render_slides_with_tasks(self, mock_render):
        """Test rendering slides with tasks."""
        mock_render.return_value = "<slide>Test</slide>"

        formatter = PptxFormatter()

        health = ProjectHealth(
            total_issues=5,
            completed=2,
            in_progress=2,
            late_count=1,
            health_score=80.0
        )

        tasks = [
            TaskStatus(
                issue_key="TEST-1",
                summary="Task 1",
                status="Closed",
                assignee="John Doe",
                days_late=0,
                risk_level="low"
            )
        ]

        report = ReportData(
            project_name="TEST",
            date_range="2024-01-01 ~ 2024-01-07",
            health=health,
            completed_tasks=tasks,
            in_progress_tasks=tasks,
            late_tasks=[],
            member_loads=[]
        )

        slides = formatter._render_slides(report)

        # Should have multiple slides
        assert len(slides) > 2
