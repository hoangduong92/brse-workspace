"""Load and render bilingual templates for Backlog tasks.

Templates are stored in ../templates/ directory with placeholders
like {variable_name} that get replaced with actual values.
"""

from pathlib import Path
from typing import Optional


# Template directory relative to this script
TEMPLATES_DIR = Path(__file__).parent.parent / "templates"

# Map task type to template filename
TEMPLATE_MAP = {
    "task": "task.md",
    "feature": "task.md",  # alias
    "subtask": "subtask.md",
    "bug": "bug-internal.md",  # default bug type
    "bug_internal": "bug-internal.md",
    "bug_uat": "bug-uat.md",
    "bug_prod": "bug-prod.md",
    "risk": "risk.md",
    "issue": "issue.md",
    "question": "task.md",  # questions use task template
    "improvement": "task.md",  # improvements use task template
    "feedback": "feedback.md",
}


def load_template(template_type: str) -> Optional[str]:
    """Load template content from file.

    Args:
        template_type: Type of template (task, bug_internal, risk, etc.)

    Returns:
        Template content as string, or None if not found
    """
    filename = TEMPLATE_MAP.get(template_type.lower())
    if not filename:
        return None

    template_path = TEMPLATES_DIR / filename
    if not template_path.exists():
        return None

    return template_path.read_text(encoding="utf-8")


def render_template(template_type: str, **kwargs) -> str:
    """Render template with provided values.

    Args:
        template_type: Type of template to load
        **kwargs: Values to substitute into template placeholders

    Returns:
        Rendered template string
    """
    template = load_template(template_type)
    if not template:
        # Fallback: return simple format if template not found
        return _fallback_render(template_type, **kwargs)

    # Replace placeholders with values
    # Use safe replacement - keep placeholder if value not provided
    for key, value in kwargs.items():
        placeholder = "{" + key + "}"
        if value is not None:
            template = template.replace(placeholder, str(value))

    return template


def _fallback_render(template_type: str, **kwargs) -> str:
    """Fallback rendering when template file not found."""
    summary = kwargs.get("summary", "タスク")
    description = kwargs.get("description", "")

    lines = [
        f"## [{template_type.upper()}] {summary}",
        "",
        description if description else "(No description)",
    ]
    return "\n".join(lines)


def get_available_templates() -> list[str]:
    """Get list of available template types."""
    return list(TEMPLATE_MAP.keys())
