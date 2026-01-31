"""Tests for config_generator module."""

import sys
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

import pytest
import yaml
from unittest.mock import patch, mock_open, MagicMock
from config_generator import (
    generate_config,
    load_methodology_template,
    save_config,
    format_config_yaml
)


@pytest.fixture
def sample_wizard_data():
    """Sample data from SetupWizard."""
    return {
        "project_name": "Test Project",
        "backlog_key": "TEST",
        "project_type": "project-based",
        "methodology": "waterfall",
        "customer_name": "Test Customer",
        "industry": "Finance",
        "timezone": "JST",
        "communication_style": "formal",
        "primary_focus": ["change_request_tracking", "budget_monitoring"],
        "secondary_focus": ["documentation_quality"],
        "vault_enabled": True,
        "vault_sources": ["email", "backlog"],
        "sync_schedule": "daily"
    }


@pytest.fixture
def agile_wizard_data():
    """Sample agile project data."""
    return {
        "project_name": "Agile Project",
        "backlog_key": "AGI",
        "project_type": "labor-based",
        "methodology": "agile",
        "customer_name": "Tech Corp",
        "industry": "Technology",
        "timezone": "PST",
        "communication_style": "casual",
        "primary_focus": ["sprint_goal_alignment", "quality_metrics"],
        "secondary_focus": ["budget_monitoring"],
        "vault_enabled": False,
        "vault_sources": [],
        "sync_schedule": "manual"
    }


@pytest.fixture
def hybrid_wizard_data():
    """Sample hybrid project data."""
    return {
        "project_name": "Hybrid Project",
        "backlog_key": "HYB",
        "project_type": "hybrid",
        "methodology": "hybrid",
        "customer_name": "Hybrid Corp",
        "industry": "Healthcare",
        "timezone": "EST",
        "communication_style": "collaborative",
        "primary_focus": ["change_request_tracking", "sprint_goal_alignment"],
        "secondary_focus": [],
        "vault_enabled": True,
        "vault_sources": ["backlog"],
        "sync_schedule": "weekly"
    }


class TestGenerateConfig:
    """Test generate_config function."""

    def test_generate_config_with_waterfall_data(self, sample_wizard_data):
        """Test config generation from waterfall wizard data."""
        config = generate_config(sample_wizard_data)

        assert config["project"]["name"] == "Test Project"
        assert config["project"]["backlog_key"] == "TEST"
        assert config["project"]["type"] == "project-based"
        assert config["project"]["methodology"] == "waterfall"

        assert config["customer"]["name"] == "Test Customer"
        assert config["customer"]["industry"] == "Finance"
        assert config["customer"]["timezone"] == "JST"
        assert config["customer"]["communication_style"] == "formal"

        assert "change_request_tracking" in config["focus_areas"]["primary"]
        assert "budget_monitoring" in config["focus_areas"]["primary"]
        assert "documentation_quality" in config["focus_areas"]["secondary"]

        assert config["vault"]["enabled"] is True
        assert "email" in config["vault"]["sources"]
        assert "backlog" in config["vault"]["sources"]
        assert config["vault"]["sync_schedule"] == "daily"

    def test_generate_config_with_agile_data(self, agile_wizard_data):
        """Test config generation from agile wizard data."""
        config = generate_config(agile_wizard_data)

        assert config["project"]["methodology"] == "agile"
        assert config["customer"]["timezone"] == "PST"
        assert config["vault"]["enabled"] is False
        assert config["vault"]["sync_schedule"] == "manual"

    def test_generate_config_with_hybrid_data(self, hybrid_wizard_data):
        """Test config generation from hybrid wizard data."""
        config = generate_config(hybrid_wizard_data)

        assert config["project"]["methodology"] == "hybrid"
        assert config["customer"]["timezone"] == "EST"
        assert config["vault"]["enabled"] is True
        assert config["vault"]["sync_schedule"] == "weekly"

    def test_generate_config_with_empty_secondary_focus(self, sample_wizard_data):
        """Test config generation with empty secondary focus."""
        sample_wizard_data["secondary_focus"] = []
        config = generate_config(sample_wizard_data)

        assert config["focus_areas"]["secondary"] == []

    def test_generate_config_with_override_methodology(self, sample_wizard_data):
        """Test config generation with overridden methodology."""
        config = generate_config(sample_wizard_data, methodology="agile")

        assert config["project"]["methodology"] == "agile"

    def test_generate_config_has_required_sections(self, sample_wizard_data):
        """Test that generated config has all required sections."""
        config = generate_config(sample_wizard_data)

        assert "project" in config
        assert "customer" in config
        assert "focus_areas" in config
        assert "vault" in config
        assert "warning_triggers" in config
        assert "pm_checklist" in config

    def test_generate_config_has_default_values(self, sample_wizard_data):
        """Test that generated config uses defaults for missing wizard data."""
        minimal_data = {
            "project_name": "Project",
            "backlog_key": "PROJ"
        }
        config = generate_config(minimal_data)

        assert config["project"]["type"] == "project-based"
        assert config["project"]["methodology"] == "waterfall"
        assert config["customer"]["timezone"] == "JST"
        assert config["customer"]["communication_style"] == "formal"
        assert config["vault"]["enabled"] is False

    def test_generate_config_warning_triggers(self, sample_wizard_data):
        """Test that warning triggers are included in config."""
        config = generate_config(sample_wizard_data)

        assert "warning_triggers" in config
        assert "high" in config["warning_triggers"]
        assert "medium" in config["warning_triggers"]
        assert isinstance(config["warning_triggers"]["high"], list)

    def test_generate_config_pm_checklist(self, sample_wizard_data):
        """Test that PM checklist is included in config."""
        config = generate_config(sample_wizard_data)

        assert "pm_checklist" in config
        assert "weekly" in config["pm_checklist"]
        assert "meeting" in config["pm_checklist"]


class TestLoadMethodologyTemplate:
    """Test load_methodology_template function."""

    def test_load_waterfall_template(self):
        """Test loading waterfall methodology template."""
        template = load_methodology_template("waterfall")
        assert isinstance(template, dict)

    def test_load_agile_template(self):
        """Test loading agile methodology template."""
        template = load_methodology_template("agile")
        assert isinstance(template, dict)

    def test_load_hybrid_template(self):
        """Test loading hybrid methodology template."""
        template = load_methodology_template("hybrid")
        assert isinstance(template, dict)

    def test_load_nonexistent_template(self):
        """Test loading non-existent methodology template."""
        template = load_methodology_template("nonexistent")
        assert template == {}

    def test_waterfall_template_has_content(self):
        """Test that waterfall template has expected content."""
        template = load_methodology_template("waterfall")
        if template:  # Only check if template file exists
            assert isinstance(template, dict)

    def test_template_returns_dict(self):
        """Test that load_methodology_template always returns dict."""
        for methodology in ["waterfall", "agile", "hybrid", "invalid"]:
            result = load_methodology_template(methodology)
            assert isinstance(result, dict)


class TestSaveConfig:
    """Test save_config function."""

    def test_save_config_creates_file(self, sample_wizard_data, tmp_path):
        """Test that save_config creates a file."""
        config = {
            "project": {"name": "Test", "backlog_key": "TEST", "type": "project-based", "methodology": "waterfall"},
            "customer": {"name": "Customer", "industry": "Tech", "timezone": "JST", "communication_style": "formal"},
            "focus_areas": {"primary": ["change_request_tracking"]},
            "vault": {"enabled": False}
        }
        output_path = tmp_path / "test_config.yaml"

        result = save_config(config, output_path)

        assert Path(result).exists()
        assert str(output_path) == result

    def test_save_config_creates_parent_directories(self, tmp_path):
        """Test that save_config creates parent directories."""
        config = {
            "project": {"name": "Test", "backlog_key": "TEST", "type": "project-based", "methodology": "waterfall"},
            "customer": {"name": "Customer", "industry": "Tech", "timezone": "JST", "communication_style": "formal"},
            "focus_areas": {"primary": ["change_request_tracking"]},
            "vault": {"enabled": False}
        }
        nested_path = tmp_path / "nested" / "deep" / "config.yaml"

        result = save_config(config, nested_path)

        assert Path(result).exists()
        assert nested_path.parent.exists()

    def test_save_config_writes_valid_yaml(self, tmp_path):
        """Test that saved file is valid YAML."""
        config = {
            "project": {"name": "Test", "backlog_key": "TEST", "type": "project-based", "methodology": "waterfall"},
            "customer": {"name": "Customer", "industry": "Tech", "timezone": "JST", "communication_style": "formal"},
            "focus_areas": {"primary": ["change_request_tracking"]},
            "vault": {"enabled": False}
        }
        output_path = tmp_path / "config.yaml"

        save_config(config, output_path)

        with open(output_path, "r", encoding="utf-8") as f:
            loaded = yaml.safe_load(f)

        assert loaded["project"]["name"] == "Test"
        assert loaded["vault"]["enabled"] is False

    def test_save_config_preserves_structure(self, tmp_path):
        """Test that save_config preserves config structure."""
        config = {
            "project": {"name": "Test", "backlog_key": "TEST", "type": "project-based", "methodology": "waterfall"},
            "customer": {"name": "Customer", "industry": "Tech", "timezone": "JST", "communication_style": "formal"},
            "focus_areas": {"primary": ["change_request_tracking"]},
            "vault": {"enabled": False, "sources": ["email", "backlog"]}
        }
        output_path = tmp_path / "config.yaml"

        save_config(config, output_path)

        with open(output_path, "r", encoding="utf-8") as f:
            loaded = yaml.safe_load(f)

        assert loaded == config

    def test_save_config_overwrites_existing_file(self, tmp_path):
        """Test that save_config overwrites existing file."""
        old_config = {"data": "old"}
        new_config = {
            "project": {"name": "Test", "backlog_key": "TEST", "type": "project-based", "methodology": "waterfall"},
            "customer": {"name": "Customer", "industry": "Tech", "timezone": "JST", "communication_style": "formal"},
            "focus_areas": {"primary": ["change_request_tracking"]},
            "vault": {"enabled": False}
        }
        output_path = tmp_path / "config.yaml"

        # Write old config
        with open(output_path, "w") as f:
            yaml.dump(old_config, f)

        # Save new config
        save_config(new_config, output_path)

        with open(output_path, "r") as f:
            loaded = yaml.safe_load(f)

        assert "project" in loaded
        assert "data" not in loaded

    def test_save_config_handles_unicode(self, tmp_path):
        """Test that save_config handles Unicode characters."""
        config = {
            "project": {"name": "プロジェクト", "backlog_key": "TEST", "type": "project-based", "methodology": "waterfall"},
            "customer": {"name": "顧客", "industry": "技術", "timezone": "JST", "communication_style": "formal"},
            "focus_areas": {"primary": ["change_request_tracking"]},
            "vault": {"enabled": False}
        }
        output_path = tmp_path / "config.yaml"

        save_config(config, output_path)

        with open(output_path, "r", encoding="utf-8") as f:
            content = f.read()

        assert "プロジェクト" in content
        assert "顧客" in content


class TestFormatConfigYaml:
    """Test format_config_yaml function."""

    def test_format_returns_string(self):
        """Test that format_config_yaml returns a string."""
        config = {
            "project": {"name": "Test", "backlog_key": "TEST", "type": "project-based", "methodology": "waterfall"},
            "customer": {"name": "Customer", "industry": "Tech", "timezone": "JST", "communication_style": "formal"},
            "focus_areas": {"primary": ["change_request_tracking"]},
            "vault": {"enabled": False}
        }
        result = format_config_yaml(config)
        assert isinstance(result, str)

    def test_format_is_valid_yaml(self):
        """Test that formatted output is valid YAML."""
        config = {
            "project": {"name": "Test", "backlog_key": "TEST", "type": "project-based", "methodology": "waterfall"},
            "customer": {"name": "Customer", "industry": "Tech", "timezone": "JST", "communication_style": "formal"},
            "focus_areas": {"primary": ["change_request_tracking"]},
            "vault": {"enabled": False}
        }
        result = format_config_yaml(config)
        parsed = yaml.safe_load(result)

        assert parsed == config

    def test_format_includes_all_keys(self):
        """Test that formatted YAML includes all config keys."""
        config = {
            "project": {"name": "Test", "backlog_key": "TEST", "type": "project-based", "methodology": "waterfall"},
            "customer": {"name": "Customer", "industry": "Tech", "timezone": "JST", "communication_style": "formal"},
            "focus_areas": {"primary": ["change_request_tracking"], "secondary": []},
            "vault": {"enabled": True, "sources": ["email"], "sync_schedule": "daily"}
        }
        result = format_config_yaml(config)

        assert "project:" in result
        assert "customer:" in result
        assert "focus_areas:" in result
        assert "vault:" in result

    def test_format_handles_empty_collections(self):
        """Test that format_config_yaml handles empty lists and dicts."""
        config = {
            "project": {"name": "Test", "backlog_key": "TEST", "type": "project-based", "methodology": "waterfall"},
            "customer": {"name": "Customer", "industry": "Tech", "timezone": "JST", "communication_style": "formal"},
            "focus_areas": {"primary": [], "secondary": []},
            "vault": {"enabled": False, "sources": []}
        }
        result = format_config_yaml(config)
        parsed = yaml.safe_load(result)

        assert parsed["focus_areas"]["primary"] == []
        assert parsed["vault"]["sources"] == []

    def test_format_handles_unicode(self):
        """Test that format_config_yaml handles Unicode."""
        config = {
            "project": {"name": "プロジェクト", "backlog_key": "TEST", "type": "project-based", "methodology": "waterfall"},
            "customer": {"name": "顧客", "industry": "技術", "timezone": "JST", "communication_style": "formal"},
            "focus_areas": {"primary": ["change_request_tracking"]},
            "vault": {"enabled": False}
        }
        result = format_config_yaml(config)

        assert "プロジェクト" in result
        assert "顧客" in result

    def test_format_output_is_readable(self):
        """Test that formatted output is human-readable."""
        config = {
            "project": {"name": "Test", "backlog_key": "TEST", "type": "project-based", "methodology": "waterfall"},
            "customer": {"name": "Customer", "industry": "Tech", "timezone": "JST", "communication_style": "formal"},
            "focus_areas": {"primary": ["change_request_tracking"]},
            "vault": {"enabled": False}
        }
        result = format_config_yaml(config)

        # Check for readable formatting (indentation, newlines)
        assert "\n" in result
        assert "project:" in result
        assert "  name:" in result  # Indented


class TestConfigIntegration:
    """Integration tests for config generation and saving."""

    def test_full_workflow_waterfall(self, sample_wizard_data, tmp_path):
        """Test full workflow: generate → save → load → validate."""
        config = generate_config(sample_wizard_data)
        output_path = tmp_path / "project-context.yaml"

        # Save config
        save_config(config, output_path)

        # Load and verify
        with open(output_path, "r", encoding="utf-8") as f:
            loaded = yaml.safe_load(f)

        assert loaded["project"]["name"] == sample_wizard_data["project_name"]
        assert loaded["project"]["backlog_key"] == sample_wizard_data["backlog_key"]
        assert loaded["customer"]["name"] == sample_wizard_data["customer_name"]

    def test_full_workflow_agile(self, agile_wizard_data, tmp_path):
        """Test full workflow with agile data."""
        config = generate_config(agile_wizard_data)
        output_path = tmp_path / "agile-context.yaml"

        save_config(config, output_path)

        with open(output_path, "r", encoding="utf-8") as f:
            loaded = yaml.safe_load(f)

        assert loaded["project"]["methodology"] == "agile"
        assert loaded["vault"]["enabled"] is False

    def test_format_and_parse_roundtrip(self, sample_wizard_data):
        """Test that format → parse roundtrip preserves data."""
        config = generate_config(sample_wizard_data)
        formatted = format_config_yaml(config)
        parsed = yaml.safe_load(formatted)

        assert parsed == config
