"""Japanese business document writer.

Generates consistent Japanese business documents using templates
and keigo helper for appropriate formality levels.
"""

import json
from enum import Enum
from pathlib import Path
from typing import Any

from keigo_helper import KeigoHelper, KeigoLevel


class DocumentType(Enum):
    """Supported document types."""
    EMAIL_CLIENT = "email-client"
    EMAIL_INTERNAL = "email-internal"
    REPORT_ISSUE = "report-issue"
    DESIGN_DOC = "design-doc"

    @classmethod
    def from_string(cls, value: str) -> "DocumentType":
        """Parse string to DocumentType."""
        value = value.lower().strip()
        for doc_type in cls:
            if doc_type.value == value:
                return doc_type
        raise ValueError(f"Unknown document type: {value}")


TEMPLATES_DIR = Path(__file__).parent.parent / "templates"


class JapaneseWriter:
    """Generate Japanese business documents from templates."""

    def __init__(self):
        self.keigo = KeigoHelper()
        self._templates: dict[str, dict] = {}

    def _load_template(self, doc_type: DocumentType) -> dict:
        """Load template from JSON file."""
        if doc_type.value in self._templates:
            return self._templates[doc_type.value]

        template_path = TEMPLATES_DIR / f"{doc_type.value}-ja.json"
        if not template_path.exists():
            return self._get_default_template(doc_type)

        with open(template_path, encoding="utf-8") as f:
            template = json.load(f)

        self._templates[doc_type.value] = template
        return template

    def _get_default_template(self, doc_type: DocumentType) -> dict:
        """Get default template when file not found."""
        return {
            "sections": [
                {"key": "greeting", "type": "greeting"},
                {"key": "subject", "label": "件名", "type": "text"},
                {"key": "content", "label": "内容", "type": "text"},
                {"key": "closing", "type": "closing"},
            ]
        }

    def generate(self, doc_type: DocumentType, level: KeigoLevel, **kwargs: Any) -> str:
        """Generate document from template."""
        template = self._load_template(doc_type)
        lines = []

        recipient = kwargs.get("recipient", "")
        if recipient:
            recipient = self.keigo.format_recipient(recipient, level)
            lines.append(f"{recipient}\n")

        for section in template.get("sections", []):
            section_content = self._render_section(section, level, kwargs)
            if section_content:
                lines.append(section_content)

        return "\n".join(lines)

    def _render_section(self, section: dict, level: KeigoLevel, context: dict) -> str:
        """Render a single section from template."""
        section_type = section.get("type", "text")
        key = section.get("key", "")
        label = section.get("label", "")

        if section_type == "greeting":
            return self.keigo.get_greeting(level)

        if section_type == "closing":
            return f"\n{self.keigo.get_closing(level)}"

        if section_type == "header":
            value = context.get(key, "")
            if value:
                return f"## {label}: {value}\n" if label else f"## {value}\n"
            return ""

        if section_type == "text":
            value = context.get(key, "")
            if value:
                return f"**{label}:** {value}\n" if label else f"{value}\n"
            return ""

        if section_type == "list":
            items = context.get(key, [])
            if items:
                header = f"### {label}\n" if label else ""
                bullets = "\n".join(f"- {item}" for item in items)
                return f"{header}{bullets}\n"
            return ""

        if section_type == "numbered_list":
            items = context.get(key, [])
            if items:
                header = f"### {label}\n" if label else ""
                numbered = "\n".join(f"{i+1}. {item}" for i, item in enumerate(items))
                return f"{header}{numbered}\n"
            return ""

        if section_type == "section":
            subsections = section.get("subsections", [])
            header = f"## {label}\n" if label else ""
            content = "\n".join(
                self._render_section(sub, level, context) for sub in subsections
            )
            return f"{header}{content}"

        return ""


def generate_document(doc_type: str, level: str = "polite", **kwargs: Any) -> str:
    """Convenience function to generate document."""
    writer = JapaneseWriter()
    return writer.generate(
        doc_type=DocumentType.from_string(doc_type),
        level=KeigoLevel.from_string(level),
        **kwargs
    )
