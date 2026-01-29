"""Tests for template_loader module."""

import pytest
import sys
from pathlib import Path

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from template_loader import load_template, render_template, get_available_templates, TEMPLATES_DIR


class TestLoadTemplate:
    """Tests for load_template function."""

    def test_load_task_template(self):
        """Load task template successfully."""
        template = load_template("task")
        assert template is not None
        # New format: separated VI/JA sections with ーーー separator
        assert "### Mô tả" in template
        assert "### 説明" in template
        assert "ーーー" in template
        assert "{description_vn}" in template

    def test_load_bug_internal_template(self):
        """Load bug-internal template successfully."""
        template = load_template("bug_internal")
        assert template is not None
        # New format: VI section has "### Phân loại", JA section has "### 分類"
        assert "### Phân loại" in template
        assert "### 分類" in template
        assert "ーーー" in template

    def test_load_risk_template(self):
        """Load risk template successfully."""
        template = load_template("risk")
        assert template is not None
        # New format: VI section has "### Đánh giá", JA section has "### 評価"
        assert "### Đánh giá" in template
        assert "### 評価" in template
        assert "ーーー" in template

    def test_load_nonexistent_template(self):
        """Return None for nonexistent template type."""
        template = load_template("nonexistent")
        assert template is None

    def test_feature_uses_task_template(self):
        """Feature type uses task template (alias)."""
        feature_template = load_template("feature")
        task_template = load_template("task")
        assert feature_template == task_template


class TestRenderTemplate:
    """Tests for render_template function."""

    def test_render_task_with_values(self):
        """Render task template with provided values."""
        rendered = render_template(
            "task",
            description_vn="VN Description",
            description_ja="JA Description",
            notes_vn="VN Notes",
            notes_ja="JA Notes",
        )
        assert "VN Description" in rendered
        assert "JA Description" in rendered
        assert "VN Notes" in rendered

    def test_render_keeps_unmatched_placeholders(self):
        """Unmatched placeholders remain in output."""
        rendered = render_template("task", description_vn="Test")
        # criterion_1_vn not provided, should remain as placeholder
        assert "{criterion_1_vn}" in rendered

    def test_render_fallback_for_unknown_type(self):
        """Use fallback render for unknown template type."""
        rendered = render_template("unknown_type", summary="Test Summary")
        assert "UNKNOWN_TYPE" in rendered
        assert "Test Summary" in rendered


class TestGetAvailableTemplates:
    """Tests for get_available_templates function."""

    def test_returns_list(self):
        """Returns a list of template types."""
        templates = get_available_templates()
        assert isinstance(templates, list)
        assert len(templates) > 0

    def test_contains_expected_types(self):
        """Contains expected template types."""
        templates = get_available_templates()
        assert "task" in templates
        assert "bug_internal" in templates
        assert "risk" in templates
        assert "feedback" in templates


class TestTemplatesDirectory:
    """Tests for templates directory structure."""

    def test_templates_dir_exists(self):
        """Templates directory exists."""
        assert TEMPLATES_DIR.exists()
        assert TEMPLATES_DIR.is_dir()

    def test_all_template_files_exist(self):
        """All expected template files exist."""
        expected_files = [
            "task.md",
            "subtask.md",
            "bug-internal.md",
            "bug-uat.md",
            "bug-prod.md",
            "risk.md",
            "issue.md",
            "feedback.md",
        ]
        for filename in expected_files:
            assert (TEMPLATES_DIR / filename).exists(), f"Missing: {filename}"


class TestBilingualSeparation:
    """Tests for bilingual section separation."""

    def test_task_has_separate_vi_ja_sections(self):
        """Task template has separate VI and JA sections."""
        template = load_template("task")
        vi_section, ja_section = template.split("ーーー")
        # VI section should have Vietnamese headers
        assert "### Mô tả" in vi_section
        assert "### Tiêu chí hoàn thành" in vi_section
        assert "### Ghi chú" in vi_section
        # JA section should have Japanese headers
        assert "### 説明" in ja_section
        assert "### 完了基準" in ja_section
        assert "### 備考" in ja_section

    def test_bug_internal_has_separate_vi_ja_sections(self):
        """Bug internal template has separate VI and JA sections."""
        template = load_template("bug_internal")
        vi_section, ja_section = template.split("ーーー")
        # VI section
        assert "### Hiện tượng" in vi_section
        assert "### Các bước tái hiện" in vi_section
        # JA section
        assert "### 現象" in ja_section
        assert "### 再現手順" in ja_section

    def test_no_inline_bilingual_headers(self):
        """Templates should not have inline bilingual headers like 'Mô tả (説明)'."""
        for template_type in ["task", "subtask", "bug_internal", "bug_uat", "bug_prod", "risk", "issue", "feedback"]:
            template = load_template(template_type)
            # Should not contain inline bilingual pattern
            assert "(説明)" not in template
            assert "(完了基準)" not in template
            assert "(備考)" not in template
