"""Tests for prompt_builder module."""
import pytest
from pathlib import Path
from prompt_builder import PromptBuilder


class TestPromptBuilderInitialization:
    """Test PromptBuilder initialization."""

    def test_init_without_template_dir(self):
        """Test initialization without template directory."""
        builder = PromptBuilder()

        assert builder.template_dir is None

    def test_init_with_template_dir(self, tmp_path):
        """Test initialization with template directory."""
        template_dir = tmp_path / "templates"
        builder = PromptBuilder(template_dir=template_dir)

        assert builder.template_dir == template_dir
        assert template_dir.exists()

    def test_init_creates_template_dir_if_not_exists(self, tmp_path):
        """Test that template directory is created if not exists."""
        template_dir = tmp_path / "new_templates"
        builder = PromptBuilder(template_dir=template_dir)

        assert template_dir.exists()


class TestPromptBuilderTemplates:
    """Test template management."""

    def test_templates_dict_contains_expected_keys(self):
        """Test that TEMPLATES contains all expected keys."""
        builder = PromptBuilder()

        expected_keys = ["analyze", "test", "story", "gap", "viewpoint"]
        for key in expected_keys:
            assert key in builder.TEMPLATES

    def test_all_templates_are_strings(self):
        """Test that all templates are non-empty strings."""
        builder = PromptBuilder()

        for key, template in builder.TEMPLATES.items():
            assert isinstance(template, str)
            assert len(template) > 0

    def test_templates_contain_placeholders(self):
        """Test that templates contain necessary placeholders."""
        builder = PromptBuilder()

        for key, template in builder.TEMPLATES.items():
            assert "{input_text}" in template
            assert "{context_section}" in template


class TestPromptBuilderLoadTemplate:
    """Test template loading."""

    def test_load_builtin_template(self):
        """Test loading built-in template."""
        builder = PromptBuilder()
        template = builder.load_template("analyze")

        assert isinstance(template, str)
        assert len(template) > 0

    def test_load_all_builtin_templates(self):
        """Test loading all built-in templates."""
        builder = PromptBuilder()

        for key in ["analyze", "test", "story", "gap", "viewpoint"]:
            template = builder.load_template(key)
            assert isinstance(template, str)

    def test_load_template_raises_for_invalid_name(self):
        """Test that invalid template name raises error."""
        builder = PromptBuilder()

        with pytest.raises(ValueError):
            builder.load_template("invalid_template")

    def test_load_custom_template(self, tmp_path):
        """Test loading custom template from file."""
        template_dir = tmp_path / "templates"
        builder = PromptBuilder(template_dir=template_dir)

        # Create custom template
        custom_template = "Custom: {input_text}\n{context_section}"
        template_file = template_dir / "custom.txt"
        template_file.write_text(custom_template, encoding="utf-8")

        # Load it
        loaded = builder.load_template("custom")
        assert loaded == custom_template

    def test_custom_template_takes_precedence(self, tmp_path):
        """Test that custom template takes precedence over built-in."""
        template_dir = tmp_path / "templates"
        builder = PromptBuilder(template_dir=template_dir)

        # Create custom "analyze" template
        custom_template = "CUSTOM ANALYZE: {input_text}\n{context_section}"
        template_file = template_dir / "analyze.txt"
        template_file.write_text(custom_template, encoding="utf-8")

        # Load it - should get custom version
        loaded = builder.load_template("analyze")
        assert loaded == custom_template


class TestPromptBuilderBuild:
    """Test prompt building."""

    def test_build_basic_prompt(self):
        """Test building a basic prompt."""
        builder = PromptBuilder()
        input_text = "ユーザー認証機能の要件定義"
        prompt = builder.build("analyze", input_text)

        assert isinstance(prompt, str)
        assert input_text in prompt
        assert len(prompt) > 0

    def test_build_all_task_types(self):
        """Test building prompts for all task types."""
        builder = PromptBuilder()
        input_text = "Test requirements"

        for task_type in ["analyze", "test", "story", "gap", "viewpoint"]:
            prompt = builder.build(task_type, input_text)
            assert isinstance(prompt, str)
            assert input_text in prompt

    def test_build_with_context(self):
        """Test building prompt with context."""
        builder = PromptBuilder()
        input_text = "ユーザー認証機能"
        context = {
            "keywords": ["認証", "ユーザー"],
            "related_items": [],
            "context_summary": "Test summary"
        }

        prompt = builder.build("analyze", input_text, context=context)

        assert isinstance(prompt, str)
        assert input_text in prompt
        assert "認証" in prompt

    def test_build_with_empty_context(self):
        """Test building prompt with empty context."""
        builder = PromptBuilder()
        input_text = "Test requirements"
        context = {}

        prompt = builder.build("analyze", input_text, context=context)

        assert isinstance(prompt, str)
        assert input_text in prompt

    def test_build_without_context(self):
        """Test building prompt without context."""
        builder = PromptBuilder()
        input_text = "Test requirements"

        prompt = builder.build("analyze", input_text)

        assert isinstance(prompt, str)
        assert input_text in prompt


class TestPromptBuilderContextSection:
    """Test context section building."""

    def test_build_context_section_empty_context(self):
        """Test building context section from empty context."""
        builder = PromptBuilder()
        context_section = builder._build_context_section({})

        assert context_section == ""

    def test_build_context_section_keywords_only(self):
        """Test context section with keywords only."""
        builder = PromptBuilder()
        context = {
            "keywords": ["認証", "ユーザー", "セキュリティ"]
        }

        context_section = builder._build_context_section(context)

        assert "関連キーワード" in context_section
        assert "認証" in context_section

    def test_build_context_section_limits_keywords_to_10(self):
        """Test that only 10 keywords max are shown."""
        builder = PromptBuilder()
        context = {
            "keywords": [f"key{i}" for i in range(20)]
        }

        context_section = builder._build_context_section(context)

        # Count occurrences of 'key' - should not include all 20
        key_count = sum(1 for i in range(20) if f"key{i}" in context_section)
        assert key_count <= 10

    def test_build_context_section_related_items(self):
        """Test context section with related items."""
        builder = PromptBuilder()
        context = {
            "related_items": [
                {
                    "title": "Item 1",
                    "source": "source-1",
                    "score": 0.95
                }
            ]
        }

        context_section = builder._build_context_section(context)

        assert "関連する過去の情報" in context_section
        assert "Item 1" in context_section

    def test_build_context_section_limits_items_to_5(self):
        """Test that only 5 items max are shown."""
        builder = PromptBuilder()
        context = {
            "related_items": [
                {
                    "title": f"Item {i}",
                    "source": f"source-{i}",
                    "score": 0.9
                }
                for i in range(10)
            ]
        }

        context_section = builder._build_context_section(context)

        # Count items shown (should be <= 5)
        item_lines = [l for l in context_section.split("\n") if "Item" in l]
        assert len(item_lines) <= 5

    def test_build_context_section_summary(self):
        """Test context section with summary."""
        builder = PromptBuilder()
        context = {
            "context_summary": "Found 3 related items"
        }

        context_section = builder._build_context_section(context)

        assert "コンテキスト要約" in context_section
        assert "Found 3 related items" in context_section

    def test_build_context_section_all_parts(self):
        """Test context section with all components."""
        builder = PromptBuilder()
        context = {
            "keywords": ["key1", "key2"],
            "related_items": [
                {"title": "Item 1", "source": "src1", "score": 0.95}
            ],
            "context_summary": "Summary text"
        }

        context_section = builder._build_context_section(context)

        assert "関連キーワード" in context_section
        assert "関連する過去の情報" in context_section
        assert "コンテキスト要約" in context_section


class TestPromptBuilderSaveTemplate:
    """Test saving custom templates."""

    def test_save_template(self, tmp_path):
        """Test saving a custom template."""
        template_dir = tmp_path / "templates"
        builder = PromptBuilder(template_dir=template_dir)

        content = "Custom template content with {input_text}"
        result = builder.save_template("custom", content)

        assert result.exists()
        assert result.name == "custom.txt"
        assert result.read_text(encoding="utf-8") == content

    def test_save_template_without_dir_raises_error(self):
        """Test that save_template raises error without template_dir."""
        builder = PromptBuilder()

        with pytest.raises(ValueError):
            builder.save_template("custom", "content")

    def test_save_template_overwrites_existing(self, tmp_path):
        """Test that save_template overwrites existing template."""
        template_dir = tmp_path / "templates"
        builder = PromptBuilder(template_dir=template_dir)

        content1 = "First content"
        content2 = "Second content"

        builder.save_template("test", content1)
        builder.save_template("test", content2)

        template_file = template_dir / "test.txt"
        assert template_file.read_text(encoding="utf-8") == content2


class TestPromptBuilderListTemplates:
    """Test listing templates."""

    def test_list_templates_builtin(self):
        """Test listing built-in templates."""
        builder = PromptBuilder()
        templates = builder.list_templates()

        assert isinstance(templates, dict)
        assert "analyze" in templates
        assert templates["analyze"] == "built-in"

    def test_list_templates_custom(self, tmp_path):
        """Test listing custom templates."""
        template_dir = tmp_path / "templates"
        builder = PromptBuilder(template_dir=template_dir)

        # Add custom template
        template_file = template_dir / "my_template.txt"
        template_file.write_text("content", encoding="utf-8")

        templates = builder.list_templates()

        assert "my_template" in templates
        assert templates["my_template"] == "custom"

    def test_list_templates_includes_both_types(self, tmp_path):
        """Test that list includes both built-in and custom."""
        template_dir = tmp_path / "templates"
        builder = PromptBuilder(template_dir=template_dir)

        # Add custom template
        template_file = template_dir / "custom.txt"
        template_file.write_text("content", encoding="utf-8")

        templates = builder.list_templates()

        # Should have built-in templates
        builtin = [v for v in templates.values() if v == "built-in"]
        assert len(builtin) >= 5

        # Should have custom template
        custom = [v for v in templates.values() if v == "custom"]
        assert len(custom) >= 1


class TestPromptBuilderEdgeCases:
    """Test edge cases."""

    def test_build_with_none_context(self):
        """Test building with None context."""
        builder = PromptBuilder()
        input_text = "Test"

        prompt = builder.build("analyze", input_text, context=None)

        assert isinstance(prompt, str)
        assert input_text in prompt

    def test_build_with_long_input(self):
        """Test building with very long input."""
        builder = PromptBuilder()
        long_input = "X" * 10000

        prompt = builder.build("analyze", long_input)

        assert isinstance(prompt, str)
        assert long_input in prompt

    def test_build_with_special_characters(self):
        """Test building with special characters."""
        builder = PromptBuilder()
        input_text = "特殊文字: <>{}[]()&*%$#@!"

        prompt = builder.build("analyze", input_text)

        assert isinstance(prompt, str)
        assert input_text in prompt

    def test_context_section_with_missing_fields(self):
        """Test context section with missing fields."""
        builder = PromptBuilder()
        context = {
            "keywords": ["key1"],
            # Missing related_items and context_summary
        }

        context_section = builder._build_context_section(context)

        assert isinstance(context_section, str)
