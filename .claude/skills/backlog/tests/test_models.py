"""Tests for data models."""

import pytest
import sys
from pathlib import Path

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from models import Issue, Attachment, Project, Comment, Template, Language, TaskType


class TestIssue:
    """Test cases for Issue model."""

    def test_from_dict_basic(self):
        """Test Issue creation from dictionary."""
        data = {
            "id": 123,
            "projectId": 456,
            "issueKey": "TEST-123",
            "summary": "Test issue",
            "description": "Test description",
            "issueType": {"id": 1},
            "priority": {"id": 3},
            "status": {"id": 1},
            "attachments": []
        }

        issue = Issue.from_dict(data)

        assert issue.id == 123
        assert issue.project_id == 456
        assert issue.key_id == "TEST-123"
        assert issue.summary == "Test issue"
        assert issue.description == "Test description"
        assert issue.issue_type_id == 1
        assert issue.priority_id == 3

    def test_from_dict_with_assignee(self):
        """Test Issue with assignee."""
        data = {
            "id": 123,
            "projectId": 456,
            "issueKey": "TEST-123",
            "summary": "Test",
            "description": "",
            "issueType": {"id": 1},
            "priority": {"id": 3},
            "status": {"id": 1},
            "assignee": {"id": 789}
        }

        issue = Issue.from_dict(data)
        assert issue.assignee_id == 789

    def test_from_dict_with_attachments(self):
        """Test Issue with attachments."""
        data = {
            "id": 123,
            "projectId": 456,
            "issueKey": "TEST-123",
            "summary": "Test",
            "description": "",
            "issueType": {"id": 1},
            "priority": {"id": 3},
            "status": {"id": 1},
            "attachments": [
                {"id": 1, "name": "file.txt", "size": 100, "created": "2024-01-01"}
            ]
        }

        issue = Issue.from_dict(data)
        assert len(issue.attachments) == 1
        assert issue.attachments[0].name == "file.txt"


class TestAttachment:
    """Test cases for Attachment model."""

    def test_from_dict(self):
        """Test Attachment creation from dictionary."""
        data = {
            "id": 1,
            "name": "screenshot.png",
            "size": 1024,
            "created": "2024-01-01T00:00:00Z"
        }

        attachment = Attachment.from_dict(data)

        assert attachment.id == 1
        assert attachment.name == "screenshot.png"
        assert attachment.size == 1024


class TestProject:
    """Test cases for Project model."""

    def test_from_dict(self):
        """Test Project creation from dictionary."""
        data = {
            "id": 100,
            "projectKey": "TEST",
            "name": "Test Project"
        }

        project = Project.from_dict(data)

        assert project.id == 100
        assert project.project_key == "TEST"
        assert project.name == "Test Project"


class TestTemplate:
    """Test cases for Template model."""

    def test_from_dict_basic(self):
        """Test Template creation from dictionary."""
        data = {
            "name": "Test Template",
            "summary_template": "Test: {summary}",
            "description_template": "{description}",
            "subtasks": [],
            "default_priority": "normal"
        }

        template = Template.from_dict(data)

        assert template.name == "Test Template"
        assert template.summary_template == "Test: {summary}"
        assert len(template.subtasks) == 0
        assert template.default_priority == "normal"

    def test_from_dict_with_subtasks(self):
        """Test Template with subtasks."""
        data = {
            "name": "Dev Template",
            "summary_template": "{summary}",
            "description_template": "{description}",
            "subtasks": [
                {
                    "subject_template": "[Analysis] {summary}",
                    "estimated_hours": 2.0,
                    "assignee_key": "analysis"
                }
            ],
            "assignee_mapping": {"analysis": 123}
        }

        template = Template.from_dict(data)

        assert len(template.subtasks) == 1
        assert template.subtasks[0].subject_template == "[Analysis] {summary}"
        assert template.subtasks[0].estimated_hours == 2.0
        assert template.assignee_mapping["analysis"] == 123


class TestEnums:
    """Test cases for enum types."""

    def test_language_values(self):
        """Test Language enum values."""
        assert Language.JAPANESE.value == "ja"
        assert Language.VIETNAMESE.value == "vi"

    def test_task_type_values(self):
        """Test TaskType enum values."""
        assert TaskType.FEATURE_DEV.value == "feature-dev"
        assert TaskType.UPLOAD_SCENARIO.value == "upload-scenario"
        assert TaskType.INVESTIGATE_ISSUE.value == "investigate-issue"
