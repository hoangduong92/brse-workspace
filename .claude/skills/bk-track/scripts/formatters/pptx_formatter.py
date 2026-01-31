"""PPTX formatter for bk-track - generates PowerPoint reports."""
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import Optional, List, Tuple

from models import ReportData, TaskStatus, MemberLoad


class PptxFormatter:
    """Format reports as PPTX slides."""

    MAX_TASKS_PER_SLIDE = 8

    def __init__(self, template_dir: Optional[Path] = None):
        """Initialize PPTX formatter.

        Args:
            template_dir: Directory containing slide templates
        """
        self.template_dir = template_dir or Path(__file__).parent.parent.parent / "templates" / "slides"
        self.pptx_skill = Path(__file__).parent.parent.parent.parent / "document-skills" / "pptx"

    def generate(self, data: ReportData, output_path: str) -> str:
        """Generate PPTX report.

        Args:
            data: ReportData object
            output_path: Output file path

        Returns:
            Path to generated file

        Raises:
            FileNotFoundError: If html2pptx.js script not found
            subprocess.CalledProcessError: If PPTX conversion fails
        """
        # 1. Render HTML templates with data
        slides = self._render_slides(data)

        # 2. Write HTML files to temp directory
        temp_dir = self._write_html_files(slides)

        try:
            # 3. Convert to PPTX using html2pptx.js
            self._convert_to_pptx(temp_dir, output_path)
        finally:
            # Cleanup temp directory
            if temp_dir.exists():
                shutil.rmtree(temp_dir)

        return output_path

    def _render_slides(self, data: ReportData) -> List[Tuple[str, str]]:
        """Render HTML slides from templates.

        Args:
            data: ReportData object

        Returns:
            List of (slide_name, rendered_html) tuples
        """
        slides = []

        # 1. Title slide
        slides.append(("title", self._render_template("title.html", {
            "project_name": data.project_name,
            "date_range": data.date_range
        })))

        # 2. Summary slide
        health_score = int(data.health.health_score) if data.health else 0
        slides.append(("summary", self._render_template("summary.html", {
            "completed_count": len(data.completed_tasks) if data.completed_tasks else 0,
            "in_progress_count": len(data.in_progress_tasks) if data.in_progress_tasks else 0,
            "at_risk_count": len(data.at_risk_tasks) if data.at_risk_tasks else 0,
            "late_count": len(data.late_tasks) if data.late_tasks else 0,
            "health_score": health_score
        })))

        # 3. Completed tasks slide
        if data.completed_tasks:
            task_items, overflow = self._format_task_list(data.completed_tasks)
            slides.append(("accomplishments", self._render_template("accomplishments.html", {
                "task_items": task_items,
                "overflow_note": overflow
            })))

        # 4. In progress tasks slide
        if data.in_progress_tasks:
            task_items, overflow = self._format_task_list(data.in_progress_tasks, show_assignee=True)
            slides.append(("in_progress", self._render_template("in_progress.html", {
                "task_items": task_items,
                "overflow_note": overflow
            })))

        # 5. Risks/late tasks slide
        at_risk = data.at_risk_tasks if data.at_risk_tasks else []
        late = data.late_tasks if data.late_tasks else []
        risk_tasks = at_risk + late
        if risk_tasks:
            task_items, overflow = self._format_task_list(risk_tasks, show_assignee=True)
            slides.append(("risks", self._render_template("risks.html", {
                "task_items": task_items,
                "overflow_note": overflow
            })))

        # 6. Next week tasks slide
        if data.next_week_tasks:
            task_items, overflow = self._format_task_list(data.next_week_tasks, show_assignee=True)
            slides.append(("next_steps", self._render_template("next_steps.html", {
                "task_items": task_items,
                "overflow_note": overflow
            })))

        # 7. Team workload slide
        if data.member_loads:
            member_rows = self._format_member_rows(data.member_loads)
            slides.append(("team_workload", self._render_template("team_workload.html", {
                "member_rows": member_rows
            })))

        return slides

    def _render_template(self, template_name: str, context: dict) -> str:
        """Simple template rendering with {{var}} substitution.

        Args:
            template_name: Template file name
            context: Template context variables

        Returns:
            Rendered HTML string
        """
        template_path = self.template_dir / template_name
        if not template_path.exists():
            return f"<div>Template {template_name} not found at {template_path}</div>"

        template = template_path.read_text(encoding="utf-8")

        # Simple substitution for {{var}}
        for key, value in context.items():
            placeholder = "{{" + key + "}}"
            template = template.replace(placeholder, str(value))

        return template

    def _format_task_list(self, tasks: List[TaskStatus], show_assignee: bool = False) -> Tuple[str, str]:
        """Format task list with overflow handling.

        Args:
            tasks: List of TaskStatus objects
            show_assignee: Whether to show assignee name

        Returns:
            Tuple of (task_items_html, overflow_note_html)
        """
        display_tasks = tasks[:self.MAX_TASKS_PER_SLIDE]
        overflow_count = len(tasks) - self.MAX_TASKS_PER_SLIDE

        items = []
        for task in display_tasks:
            issue_key = getattr(task, 'issue_key', 'N/A')
            summary = getattr(task, 'summary', 'No summary')

            item = f'<span class="task-key">[{issue_key}]</span> {summary}'

            if show_assignee:
                assignee = getattr(task, 'assignee', None)
                if assignee:
                    item += f' <span class="task-assignee">@{assignee}</span>'

            items.append(f"<li>{item}</li>")

        task_items_html = "\n            ".join(items)

        overflow_note_html = ""
        if overflow_count > 0:
            overflow_note_html = f'<div class="overflow-note">...and {overflow_count} more tasks</div>'

        return task_items_html, overflow_note_html

    def _format_member_rows(self, member_loads: List[MemberLoad]) -> str:
        """Format team member workload table rows.

        Args:
            member_loads: List of MemberLoad objects

        Returns:
            HTML table rows
        """
        rows = []
        for member in member_loads:
            name = getattr(member, 'name', 'Unknown')
            assigned = getattr(member, 'total_tasks', 0)
            completed = getattr(member, 'completed', 0)
            overdue = getattr(member, 'overdue', 0)

            # Calculate load percentage
            load_pct = int((assigned / max(assigned, 1)) * 100) if assigned > 0 else 0

            # Apply load level styling
            load_class = "load-normal"
            if load_pct >= 90:
                load_class = "load-high"
            elif load_pct >= 70:
                load_class = "load-medium"

            rows.append(
                f'<tr>'
                f'<td>{name}</td>'
                f'<td>{assigned}</td>'
                f'<td>{completed}</td>'
                f'<td>{overdue}</td>'
                f'<td class="{load_class}">{load_pct}%</td>'
                f'</tr>'
            )

        return "\n                ".join(rows)

    def _write_html_files(self, slides: List[Tuple[str, str]]) -> Path:
        """Write rendered HTML slides to temporary directory.

        Args:
            slides: List of (slide_name, html_content) tuples

        Returns:
            Path to temporary directory
        """
        temp_dir = Path(tempfile.mkdtemp(prefix="pptx_"))

        for i, (name, html) in enumerate(slides):
            slide_file = temp_dir / f"{i:02d}_{name}.html"
            slide_file.write_text(html, encoding="utf-8")

        return temp_dir

    def _convert_to_pptx(self, html_dir: Path, output_path: str):
        """Convert HTML slides to PPTX using html2pptx.js.

        Args:
            html_dir: Directory containing HTML slide files
            output_path: Output PPTX file path

        Raises:
            FileNotFoundError: If html2pptx.js not found
            subprocess.CalledProcessError: If conversion fails
        """
        script_path = self.pptx_skill / "scripts" / "html2pptx.js"
        if not script_path.exists():
            raise FileNotFoundError(
                f"html2pptx.js not found at {script_path}. "
                f"Ensure document-skills/pptx skill is installed."
            )

        # Call html2pptx.js via Node.js
        subprocess.run(
            [
                "node",
                str(script_path),
                "--input", str(html_dir),
                "--output", output_path
            ],
            check=True,
            capture_output=True,
            text=True
        )
