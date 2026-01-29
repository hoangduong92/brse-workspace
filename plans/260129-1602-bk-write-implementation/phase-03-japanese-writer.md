---
phase: 3
title: "Japanese Writer Module"
status: pending
effort: 2h
---

# Phase 3: Japanese Writer Core Module

## Context Links

- Tests: `.claude/skills/bk-write/tests/test_japanese_writer.py`
- Keigo helper: `.claude/skills/bk-write/scripts/keigo_helper.py`
- Pattern ref: `.claude/skills/bk-task/scripts/task_parser.py` (dataclass patterns)
- Template pattern: `.claude/skills/bk-task/scripts/template_loader.py`

## Overview

Core document generation module. Uses keigo_helper and JSON templates to produce consistent Japanese business documents.

## Key Insights

- Load templates from JSON files (easy customization)
- Use keigo_helper for greeting/closing generation
- Template placeholders: `{recipient}`, `{subject}`, `{content}`, etc.
- Output as markdown for easy preview/copy

## Requirements

### Functional
- `DocumentType` enum: EMAIL_CLIENT, EMAIL_INTERNAL, REPORT_ISSUE, DESIGN_DOC
- Load templates from `../templates/*.json`
- Generate document with keigo-appropriate phrases
- Replace placeholders with actual values

### Non-functional
- Templates loaded lazily (on first use)
- Fallback if template file missing
- All tests from Phase 1 pass

## Files to Create

```
.claude/skills/bk-write/scripts/
└── japanese_writer.py
```

## Architecture

```
User Input → JapaneseWriter.generate()
                    │
                    ├── Load template from JSON
                    │
                    ├── Get greeting from KeigoHelper
                    │
                    ├── Replace placeholders
                    │
                    └── Get closing from KeigoHelper
                              │
                              ▼
                        Output (Markdown)
```

## Implementation Steps

### 1. Implement japanese_writer.py (90 min)

**File:** `scripts/japanese_writer.py`

```python
"""Japanese business document writer.

Generates consistent Japanese business documents using templates
and keigo helper for appropriate formality levels.
"""

import json
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Optional

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


# Template directory
TEMPLATES_DIR = Path(__file__).parent.parent / "templates"


@dataclass
class DocumentContext:
    """Context for document generation."""
    doc_type: DocumentType
    level: KeigoLevel
    recipient: str = ""
    subject: str = ""
    content_points: list[str] = field(default_factory=list)
    # Issue report specific
    issue_title: str = ""
    environment: str = ""
    steps: list[str] = field(default_factory=list)
    expected_behavior: str = ""
    actual_behavior: str = ""
    # Design doc specific
    feature_name: str = ""
    overview: str = ""
    specifications: list[str] = field(default_factory=list)
    tech_stack: list[str] = field(default_factory=list)
    schedule: str = ""


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
            # Return default template
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

    def generate(
        self,
        doc_type: DocumentType,
        level: KeigoLevel,
        **kwargs
    ) -> str:
        """Generate document from template.

        Args:
            doc_type: Type of document to generate
            level: Keigo formality level
            **kwargs: Document-specific parameters

        Returns:
            Generated document as markdown string
        """
        template = self._load_template(doc_type)
        lines = []

        # Format recipient if provided
        recipient = kwargs.get("recipient", "")
        if recipient:
            recipient = self.keigo.format_recipient(recipient, level)
            lines.append(f"{recipient}\n")

        # Process each section
        for section in template.get("sections", []):
            section_content = self._render_section(section, level, kwargs)
            if section_content:
                lines.append(section_content)

        return "\n".join(lines)

    def _render_section(
        self,
        section: dict,
        level: KeigoLevel,
        context: dict
    ) -> str:
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
                if label:
                    return f"**{label}:** {value}\n"
                return f"{value}\n"
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
            # Nested section with subsections
            subsections = section.get("subsections", [])
            header = f"## {label}\n" if label else ""
            content = "\n".join(
                self._render_section(sub, level, context)
                for sub in subsections
            )
            return f"{header}{content}"

        return ""


def generate_document(
    doc_type: str,
    level: str = "polite",
    **kwargs
) -> str:
    """Convenience function to generate document.

    Args:
        doc_type: Document type string (email-client, email-internal, etc.)
        level: Keigo level string (casual, polite, honorific)
        **kwargs: Document-specific parameters

    Returns:
        Generated document as markdown string
    """
    writer = JapaneseWriter()
    return writer.generate(
        doc_type=DocumentType.from_string(doc_type),
        level=KeigoLevel.from_string(level),
        **kwargs
    )
```

### 2. Run Tests (15 min)

```bash
cd ".claude/skills/bk-write" && "../.venv/Scripts/python.exe" -m pytest tests/test_japanese_writer.py -v
```

Note: Tests may fail until templates are created in Phase 4.

### 3. Add Fallback Templates (15 min)

If tests fail due to missing templates, the `_get_default_template()` method provides fallback. However, full tests pass after Phase 4 adds JSON templates.

## Todo List

- [ ] Implement `DocumentType` enum
- [ ] Implement `DocumentContext` dataclass
- [ ] Implement `JapaneseWriter._load_template()`
- [ ] Implement `JapaneseWriter._get_default_template()`
- [ ] Implement `JapaneseWriter.generate()`
- [ ] Implement `JapaneseWriter._render_section()`
- [ ] Implement `generate_document()` convenience function
- [ ] Run tests - verify core functionality works

## Success Criteria

- `JapaneseWriter.generate()` produces valid markdown
- Greeting/closing match keigo level
- Template placeholders replaced correctly
- Tests pass (with fallback templates)

## Risk Assessment

| Risk | Mitigation |
|------|------------|
| Template not found | Fallback to default template |
| Invalid section type | Return empty string, log warning |

## Security Considerations

- No user input executed as code
- Template files read-only
- JSON parsing with standard library (safe)

## Next Phase

Phase 4: Create JSON templates for all document types.
