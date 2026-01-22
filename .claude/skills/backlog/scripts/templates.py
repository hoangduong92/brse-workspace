"""Template system for task types with dynamic variable substitution."""

import json
import re
import logging
from pathlib import Path
from typing import Optional

try:
    from .models import TaskType, Template, Issue
except ImportError:
    from models import TaskType, Template, Issue

logger = logging.getLogger(__name__)


class TemplateError(Exception):
    """Custom exception for template errors."""
    pass


class TemplateManager:
    """Manager for loading and applying task templates."""

    TEMPLATE_DIR = Path(__file__).parent.parent / "templates"

    # Task type detection patterns (JA/VI keywords)
    TASK_TYPE_PATTERNS = {
        TaskType.FEATURE_DEV: [
            r'feature|dev|implement|add new|create|build|enhance',
            r'機能|開発|実装|新規|追加|作成',
            r'tính năng|phát triển|triển khai|thêm mới|tạo'
        ],
        TaskType.UPLOAD_SCENARIO: [
            r'scenario|upload|test case|test scenario',
            r'シナリオ|アップロード|テストケース',
            r'kịch bản|tải lên|trường hợp kiểm thử'
        ],
        TaskType.INVESTIGATE_ISSUE: [
            r'investigate|bug|fix|issue|error|debug|problem',
            r'調査|バグ|修正|不具合|エラー|問題',
            r'điều tra|lỗi|sửa|vấn đề|khắc phục'
        ]
    }

    # Priority mapping (string to Backlog ID)
    PRIORITY_MAP = {
        "urgent": 2,
        "high": 2,
        "normal": 3,
        "low": 4
    }

    def __init__(self):
        """Initialize template manager and load all templates."""
        self.templates = self._load_templates()

    def _load_templates(self) -> dict[TaskType, Template]:
        """Load all templates from JSON files.

        Returns:
            Dictionary mapping TaskType to Template

        Raises:
            TemplateError: If template files are missing or invalid
        """
        templates = {}

        for task_type in TaskType:
            path = self.TEMPLATE_DIR / f"{task_type.value}.json"

            if not path.exists():
                logger.warning(f"Template not found: {path}")
                continue

            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self._validate_template(data)
                    templates[task_type] = Template.from_dict(data)
                    logger.debug(f"Loaded template: {task_type.value}")
            except json.JSONDecodeError as e:
                raise TemplateError(f"Invalid JSON in {path}: {e}")
            except KeyError as e:
                raise TemplateError(f"Missing required field in {path}: {e}")

        return templates

    def _validate_template(self, data: dict) -> None:
        """Validate template data structure.

        Args:
            data: Template data dictionary

        Raises:
            TemplateError: If validation fails
        """
        required_fields = ["name", "summary_template", "description_template"]

        for field in required_fields:
            if field not in data:
                raise TemplateError(f"Missing required field: {field}")

        # Validate subtasks structure if present
        for i, subtask in enumerate(data.get("subtasks", [])):
            if "subject_template" not in subtask:
                raise TemplateError(f"Subtask {i} missing 'subject_template'")

    def detect_task_type(
        self,
        issue: Issue,
        manual_type: Optional[TaskType] = None
    ) -> TaskType:
        """Detect task type from issue content or use manual override.

        Args:
            issue: Source issue
            manual_type: Optional manual override

        Returns:
            Detected or specified TaskType
        """
        # Manual override takes precedence
        if manual_type:
            logger.info(f"Using manual task type: {manual_type.value}")
            return manual_type

        # Combine summary and description for pattern matching
        text = f"{issue.summary} {issue.description}".lower()

        # Check patterns for each task type
        for task_type, patterns in self.TASK_TYPE_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    logger.info(f"Detected task type: {task_type.value}")
                    return task_type

        # Default to feature development
        logger.info("No pattern matched, defaulting to feature-dev")
        return TaskType.FEATURE_DEV

    def apply_template(self, template: Template, context: dict) -> dict:
        """Apply template with variable substitution.

        Args:
            template: Template to apply
            context: Variable context dictionary

        Returns:
            Dictionary with filled summary, description, and metadata
        """
        # Perform variable substitution
        summary = self._substitute(template.summary_template, context)
        description = self._substitute(template.description_template, context)

        return {
            "summary": summary,
            "description": description,
            "priorityId": self.PRIORITY_MAP.get(template.default_priority, 3),
            "assigneeId": template.default_assignee
        }

    def _substitute(self, template_str: str, context: dict) -> str:
        """Substitute variables in template string.

        Args:
            template_str: Template string with {variable} placeholders
            context: Variable values

        Returns:
            String with substituted values
        """
        try:
            return template_str.format(**context)
        except KeyError as e:
            logger.warning(f"Missing template variable: {e}")
            # Return template with missing variables replaced with empty
            result = template_str
            for key in re.findall(r'\{(\w+)\}', template_str):
                if key not in context:
                    result = result.replace(f"{{{key}}}", "")
            return result

    def generate_subtasks(
        self,
        template: Template,
        parent_id: int,
        context: dict
    ) -> list[dict]:
        """Generate subtask data from template.

        Args:
            template: Template with subtasks
            parent_id: Parent issue ID
            context: Variable context

        Returns:
            List of subtask data dictionaries
        """
        subtasks = []

        for subtask_template in template.subtasks:
            subject = self._substitute(subtask_template.subject_template, context)

            # Determine assignee: mapping > default > None
            assignee_id = subtask_template.default_assignee
            if subtask_template.assignee_key and template.assignee_mapping:
                assignee_id = template.assignee_mapping.get(
                    subtask_template.assignee_key,
                    assignee_id
                )

            subtask_data = {
                "parentIssueId": parent_id,
                "summary": subject,
            }

            if subtask_template.estimated_hours > 0:
                subtask_data["estimatedHours"] = subtask_template.estimated_hours

            if assignee_id:
                subtask_data["assigneeId"] = assignee_id

            subtasks.append(subtask_data)

        return subtasks

    def get_template(self, task_type: TaskType) -> Optional[Template]:
        """Get template by task type.

        Args:
            task_type: Task type enum

        Returns:
            Template or None if not found
        """
        return self.templates.get(task_type)
