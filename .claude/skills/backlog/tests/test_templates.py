"""Tests for template system."""

import pytest
import sys
from pathlib import Path

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from templates import TemplateManager, TemplateError
from models import TaskType, Issue, Template


class TestTemplateManager:
    """Test cases for TemplateManager."""

    def setup_method(self):
        """Set up test fixtures."""
        self.manager = TemplateManager()

    def test_load_templates(self):
        """Test that all templates are loaded."""
        assert TaskType.FEATURE_DEV in self.manager.templates
        assert TaskType.UPLOAD_SCENARIO in self.manager.templates
        assert TaskType.INVESTIGATE_ISSUE in self.manager.templates

    def test_feature_dev_template_has_subtasks(self):
        """Test feature dev template has subtasks."""
        template = self.manager.templates[TaskType.FEATURE_DEV]
        assert len(template.subtasks) == 4

    def test_upload_scenario_template_no_subtasks(self):
        """Test upload scenario template has no subtasks."""
        template = self.manager.templates[TaskType.UPLOAD_SCENARIO]
        assert len(template.subtasks) == 0

    def test_investigate_issue_template_no_subtasks(self):
        """Test investigate issue template has no subtasks."""
        template = self.manager.templates[TaskType.INVESTIGATE_ISSUE]
        assert len(template.subtasks) == 0

    def test_detect_feature_dev_english(self):
        """Test detection of feature dev from English keywords."""
        issue = Issue(
            id=1, project_id=1, key_id="TEST-1",
            summary="Implement new feature for user authentication",
            description="Add OAuth2 support",
            issue_type_id=1, priority_id=3, status_id=1
        )
        assert self.manager.detect_task_type(issue) == TaskType.FEATURE_DEV

    def test_detect_feature_dev_japanese(self):
        """Test detection of feature dev from Japanese keywords."""
        issue = Issue(
            id=1, project_id=1, key_id="TEST-1",
            summary="新機能を実装する",
            description="認証機能の追加",
            issue_type_id=1, priority_id=3, status_id=1
        )
        assert self.manager.detect_task_type(issue) == TaskType.FEATURE_DEV

    def test_detect_upload_scenario(self):
        """Test detection of upload scenario."""
        issue = Issue(
            id=1, project_id=1, key_id="TEST-1",
            summary="Upload test scenario for login flow",
            description="Test cases for authentication",
            issue_type_id=1, priority_id=3, status_id=1
        )
        assert self.manager.detect_task_type(issue) == TaskType.UPLOAD_SCENARIO

    def test_detect_investigate_issue(self):
        """Test detection of investigate issue."""
        issue = Issue(
            id=1, project_id=1, key_id="TEST-1",
            summary="Investigate login bug",
            description="Users cannot login after password reset",
            issue_type_id=1, priority_id=3, status_id=1
        )
        assert self.manager.detect_task_type(issue) == TaskType.INVESTIGATE_ISSUE

    def test_manual_type_override(self):
        """Test manual type override takes precedence."""
        issue = Issue(
            id=1, project_id=1, key_id="TEST-1",
            summary="Investigate login bug",  # Would be INVESTIGATE_ISSUE
            description="",
            issue_type_id=1, priority_id=3, status_id=1
        )
        # Manual override should take precedence
        result = self.manager.detect_task_type(issue, TaskType.FEATURE_DEV)
        assert result == TaskType.FEATURE_DEV

    def test_apply_template(self):
        """Test template variable substitution."""
        template = self.manager.templates[TaskType.FEATURE_DEV]
        context = {
            "project_id": "HB21373",
            "source_ticket_id": "HB21373-123",
            "original_summary": "New feature",
            "translated_summary": "Tính năng mới",
            "original_description": "Description",
            "translated_description": "Mô tả"
        }

        result = self.manager.apply_template(template, context)

        assert "summary" in result
        assert "description" in result
        assert "[KH-HB21373]" in result["summary"]
        assert "Tính năng mới" in result["summary"]

    def test_generate_subtasks(self):
        """Test subtask generation from template."""
        template = self.manager.templates[TaskType.FEATURE_DEV]
        context = {
            "translated_summary": "Test feature"
        }

        subtasks = self.manager.generate_subtasks(template, parent_id=100, context=context)

        assert len(subtasks) == 4
        assert subtasks[0]["parentIssueId"] == 100
        assert "[Analysis]" in subtasks[0]["summary"]
        assert "[Implementation]" in subtasks[1]["summary"]
        assert "[Testing]" in subtasks[2]["summary"]
        assert "[Code Review]" in subtasks[3]["summary"]

    def test_default_task_type(self):
        """Test default task type when no pattern matches."""
        issue = Issue(
            id=1, project_id=1, key_id="TEST-1",
            summary="Random unrelated text",
            description="No keywords here",
            issue_type_id=1, priority_id=3, status_id=1
        )
        # Should default to FEATURE_DEV
        assert self.manager.detect_task_type(issue) == TaskType.FEATURE_DEV
