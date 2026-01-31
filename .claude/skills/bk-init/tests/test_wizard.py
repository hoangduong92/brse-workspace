"""Tests for SetupWizard class."""

import sys
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

import pytest
from unittest.mock import patch, MagicMock
from wizard import SetupWizard


@pytest.fixture
def wizard():
    """Create a fresh wizard instance for each test."""
    return SetupWizard()


@pytest.fixture
def sample_wizard_data():
    """Sample data collected from a completed wizard run."""
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


class TestSetupWizardInit:
    """Test SetupWizard initialization."""

    def test_wizard_initializes_with_empty_data(self, wizard):
        """Test that wizard starts with empty data dictionary."""
        assert wizard.data == {}

    def test_wizard_has_run_method(self, wizard):
        """Test that wizard has run method."""
        assert hasattr(wizard, 'run')
        assert callable(wizard.run)


class TestSetupWizardPrompts:
    """Test wizard prompt methods."""

    def test_prompt_accepts_valid_input(self, wizard):
        """Test that _prompt returns non-empty user input."""
        with patch('builtins.input', return_value='Valid Input'):
            result = wizard._prompt("Test prompt")
            assert result == 'Valid Input'

    def test_prompt_strips_whitespace(self, wizard):
        """Test that _prompt strips leading/trailing whitespace."""
        with patch('builtins.input', return_value='  Input with spaces  '):
            result = wizard._prompt("Test prompt")
            assert result == 'Input with spaces'

    def test_prompt_rejects_empty_input(self, wizard):
        """Test that _prompt retries on empty input."""
        with patch('builtins.input', side_effect=['', '', 'Valid']):
            result = wizard._prompt("Test prompt")
            assert result == 'Valid'

    def test_choice_returns_selected_option(self, wizard):
        """Test that _choice returns the selected option."""
        options = ["option1", "option2", "option3"]
        with patch('builtins.input', return_value='2'):
            result = wizard._choice(options)
            assert result == "option2"

    def test_choice_validates_index_bounds(self, wizard):
        """Test that _choice validates index bounds."""
        options = ["option1", "option2"]
        with patch('builtins.input', side_effect=['5', '0', '2']):
            result = wizard._choice(options)
            assert result == "option2"

    def test_choice_handles_invalid_input(self, wizard):
        """Test that _choice handles non-numeric input."""
        options = ["option1", "option2"]
        with patch('builtins.input', side_effect=['abc', '1']):
            result = wizard._choice(options)
            assert result == "option1"

    def test_multi_choice_returns_selected_options(self, wizard):
        """Test that _multi_choice returns list of selected options."""
        options = ["opt1", "opt2", "opt3", "opt4"]
        with patch('builtins.input', return_value='1,3,4'):
            result = wizard._multi_choice(options, "Select")
            assert result == ["opt1", "opt3", "opt4"]

    def test_multi_choice_allows_empty_when_permitted(self, wizard):
        """Test that _multi_choice allows empty input when allow_empty=True."""
        options = ["opt1", "opt2"]
        with patch('builtins.input', return_value=''):
            result = wizard._multi_choice(options, "Select", allow_empty=True)
            assert result == []

    def test_multi_choice_rejects_empty_by_default(self, wizard):
        """Test that _multi_choice rejects empty input by default."""
        options = ["opt1", "opt2"]
        with patch('builtins.input', side_effect=['', '1']):
            result = wizard._multi_choice(options, "Select")
            assert result == ["opt1"]

    def test_multi_choice_filters_invalid_indices(self, wizard):
        """Test that _multi_choice filters out-of-bounds indices."""
        options = ["opt1", "opt2"]
        with patch('builtins.input', return_value='1,5,2'):
            result = wizard._multi_choice(options, "Select")
            assert result == ["opt1", "opt2"]

    def test_multi_choice_handles_malformed_input(self, wizard):
        """Test that _multi_choice handles malformed comma-separated input."""
        options = ["opt1", "opt2", "opt3"]
        with patch('builtins.input', side_effect=['abc,def', '1,2']):
            result = wizard._multi_choice(options, "Select")
            assert result == ["opt1", "opt2"]


class TestSetupWizardStep1:
    """Test wizard Step 1: Project information."""

    def test_step1_collects_project_name_and_key(self, wizard):
        """Test that step 1 collects project name and Backlog key."""
        inputs = ['My Project', 'PROJ']
        with patch('builtins.input', side_effect=inputs):
            wizard._step1_project_info()
            assert wizard.data["project_name"] == "My Project"
            assert wizard.data["backlog_key"] == "PROJ"

    def test_step1_strips_whitespace_from_inputs(self, wizard):
        """Test that step 1 strips whitespace."""
        inputs = ['  Spaced Project  ', '  KEY  ']
        with patch('builtins.input', side_effect=inputs):
            wizard._step1_project_info()
            assert wizard.data["project_name"] == "Spaced Project"
            assert wizard.data["backlog_key"] == "KEY"

    def test_step1_requires_non_empty_inputs(self, wizard):
        """Test that step 1 rejects empty inputs."""
        inputs = ['', 'Project', '', 'KEY']
        with patch('builtins.input', side_effect=inputs):
            wizard._step1_project_info()
            assert wizard.data["project_name"] == "Project"
            assert wizard.data["backlog_key"] == "KEY"


class TestSetupWizardStep2:
    """Test wizard Step 2: Project type and methodology."""

    def test_step2_sets_project_type(self, wizard):
        """Test that step 2 sets project type."""
        with patch('builtins.input', side_effect=['1', '1']):
            wizard._step2_project_type()
            assert wizard.data["project_type"] == "project-based"

    def test_step2_sets_methodology(self, wizard):
        """Test that step 2 sets methodology."""
        with patch('builtins.input', side_effect=['2', '2']):
            wizard._step2_project_type()
            assert wizard.data["methodology"] == "agile"

    def test_step2_validates_project_type_choices(self, wizard):
        """Test that step 2 validates project type choices."""
        with patch('builtins.input', side_effect=['4', '3', '3']):
            wizard._step2_project_type()
            assert wizard.data["project_type"] == "hybrid"

    def test_step2_supports_all_methodologies(self, wizard):
        """Test that step 2 supports waterfall, agile, and hybrid."""
        methodologies = ["waterfall", "agile", "hybrid"]
        for idx, expected in enumerate(methodologies, 1):
            wizard.data = {}
            with patch('builtins.input', side_effect=['1', str(idx)]):
                wizard._step2_project_type()
                assert wizard.data["methodology"] == expected


class TestSetupWizardStep3:
    """Test wizard Step 3: Customer profile."""

    def test_step3_collects_customer_info(self, wizard):
        """Test that step 3 collects customer information."""
        inputs = ['ACME Corp', 'Technology', '1', '1']
        with patch('builtins.input', side_effect=inputs):
            wizard._step3_customer_info()
            assert wizard.data["customer_name"] == "ACME Corp"
            assert wizard.data["industry"] == "Technology"
            assert wizard.data["timezone"] == "JST"
            assert wizard.data["communication_style"] == "formal"

    def test_step3_supports_all_timezones(self, wizard):
        """Test that step 3 supports all timezone options."""
        timezones = ["JST", "PST", "EST", "UTC"]
        for idx, expected in enumerate(timezones, 1):
            wizard.data = {}
            inputs = ['Customer', 'Finance', str(idx), '1']
            with patch('builtins.input', side_effect=inputs):
                wizard._step3_customer_info()
                assert wizard.data["timezone"] == expected

    def test_step3_supports_all_communication_styles(self, wizard):
        """Test that step 3 supports all communication styles."""
        styles = ["formal", "casual", "collaborative"]
        for idx, expected in enumerate(styles, 1):
            wizard.data = {}
            inputs = ['Customer', 'Finance', '1', str(idx)]
            with patch('builtins.input', side_effect=inputs):
                wizard._step3_customer_info()
                assert wizard.data["communication_style"] == expected

    def test_step3_validates_timezone_choice(self, wizard):
        """Test that step 3 validates timezone choice."""
        inputs = ['ACME', 'Tech', '5', '1', '1']
        with patch('builtins.input', side_effect=inputs):
            wizard._step3_customer_info()
            assert wizard.data["timezone"] == "JST"


class TestSetupWizardStep4:
    """Test wizard Step 4: Focus areas."""

    def test_step4_collects_primary_focus(self, wizard):
        """Test that step 4 collects primary focus areas."""
        inputs = ['1,2', '']
        with patch('builtins.input', side_effect=inputs):
            wizard._step4_focus_areas()
            assert "change_request_tracking" in wizard.data["primary_focus"]
            assert "budget_monitoring" in wizard.data["primary_focus"]

    def test_step4_collects_secondary_focus(self, wizard):
        """Test that step 4 collects secondary focus areas."""
        inputs = ['1', '3,5']
        with patch('builtins.input', side_effect=inputs):
            wizard._step4_focus_areas()
            assert "sprint_goal_alignment" in wizard.data["secondary_focus"]
            assert "documentation_quality" in wizard.data["secondary_focus"]

    def test_step4_allows_empty_secondary_focus(self, wizard):
        """Test that step 4 allows empty secondary focus."""
        inputs = ['1,2', '']
        with patch('builtins.input', side_effect=inputs):
            wizard._step4_focus_areas()
            assert wizard.data["secondary_focus"] == []

    def test_step4_primary_focus_required(self, wizard):
        """Test that step 4 requires primary focus."""
        inputs = ['', '1', '2']
        with patch('builtins.input', side_effect=inputs):
            wizard._step4_focus_areas()
            assert len(wizard.data["primary_focus"]) > 0

    def test_step4_filters_invalid_focus_indices(self, wizard):
        """Test that step 4 filters invalid focus indices."""
        inputs = ['1,10,2', '']
        with patch('builtins.input', side_effect=inputs):
            wizard._step4_focus_areas()
            assert len(wizard.data["primary_focus"]) == 2


class TestSetupWizardStep5:
    """Test wizard Step 5: Vault configuration."""

    def test_step5_vault_disabled(self, wizard):
        """Test that step 5 disables vault when user selects no."""
        inputs = ['2']
        with patch('builtins.input', side_effect=inputs):
            wizard._step5_vault_config()
            assert wizard.data["vault_enabled"] is False
            assert wizard.data["vault_sources"] == []
            assert wizard.data["sync_schedule"] == "manual"

    def test_step5_vault_enabled_with_sources(self, wizard):
        """Test that step 5 enables vault with sources."""
        inputs = ['1', '1,2', '1']
        with patch('builtins.input', side_effect=inputs):
            wizard._step5_vault_config()
            assert wizard.data["vault_enabled"] is True
            assert "email" in wizard.data["vault_sources"]
            assert "backlog" in wizard.data["vault_sources"]
            assert wizard.data["sync_schedule"] == "daily"

    def test_step5_supports_all_sync_schedules(self, wizard):
        """Test that step 5 supports daily, weekly, manual schedules."""
        schedules = ["daily", "weekly", "manual"]
        for idx, expected in enumerate(schedules, 1):
            wizard.data = {}
            inputs = ['1', '1', str(idx)]
            with patch('builtins.input', side_effect=inputs):
                wizard._step5_vault_config()
                assert wizard.data["sync_schedule"] == expected

    def test_step5_vault_sources_single_selection(self, wizard):
        """Test that step 5 allows single vault source selection."""
        inputs = ['1', '1', '2']
        with patch('builtins.input', side_effect=inputs):
            wizard._step5_vault_config()
            assert wizard.data["vault_sources"] == ["email"]

    def test_step5_vault_sources_both_selections(self, wizard):
        """Test that step 5 allows both vault sources."""
        inputs = ['1', '1,2', '3']
        with patch('builtins.input', side_effect=inputs):
            wizard._step5_vault_config()
            assert len(wizard.data["vault_sources"]) == 2


class TestSetupWizardFullFlow:
    """Test complete wizard workflow."""

    def test_run_completes_all_steps(self, wizard, sample_wizard_data):
        """Test that wizard.run() completes all steps and returns data."""
        # Create input values for all prompts
        inputs = [
            'Test Project',          # Step 1: project_name
            'TEST',                  # Step 1: backlog_key
            '1',                     # Step 2: project_type
            '1',                     # Step 2: methodology
            'Test Customer',         # Step 3: customer_name
            'Finance',               # Step 3: industry
            '1',                     # Step 3: timezone
            '1',                     # Step 3: communication_style
            '1,2',                   # Step 4: primary_focus
            '3',                     # Step 4: secondary_focus
            '1',                     # Step 5: vault_enabled
            '1,2',                   # Step 5: vault_sources
            '1',                     # Step 5: sync_schedule
        ]

        with patch('builtins.input', side_effect=inputs):
            result = wizard.run()

        assert isinstance(result, dict)
        assert result["project_name"] == "Test Project"
        assert result["backlog_key"] == "TEST"
        assert result["project_type"] == "project-based"
        assert result["methodology"] == "waterfall"
        assert result["customer_name"] == "Test Customer"
        assert result["industry"] == "Finance"
        assert result["timezone"] == "JST"
        assert result["communication_style"] == "formal"
        assert "change_request_tracking" in result["primary_focus"]
        assert "budget_monitoring" in result["primary_focus"]
        assert "sprint_goal_alignment" in result["secondary_focus"]
        assert result["vault_enabled"] is True
        assert len(result["vault_sources"]) == 2
        assert result["sync_schedule"] == "daily"

    def test_run_keyboard_interrupt_raises(self, wizard):
        """Test that keyboard interrupt during run raises KeyboardInterrupt."""
        with patch('builtins.input', side_effect=KeyboardInterrupt):
            with pytest.raises(KeyboardInterrupt):
                wizard.run()

    def test_wizard_handles_various_inputs(self, wizard):
        """Test wizard with various valid input combinations."""
        inputs = [
            'Labor Tracking',        # project_name
            'LBR',                   # backlog_key
            '2',                     # project_type (labor-based)
            '2',                     # methodology (agile)
            'BigCorp Inc',           # customer_name
            'Healthcare',            # industry
            '2',                     # timezone (PST)
            '3',                     # communication_style (collaborative)
            '2,4',                   # primary_focus
            '',                      # secondary_focus (empty)
            '2',                     # vault_enabled (no)
        ]

        with patch('builtins.input', side_effect=inputs):
            result = wizard.run()

        assert result["project_type"] == "labor-based"
        assert result["methodology"] == "agile"
        assert result["timezone"] == "PST"
        assert result["vault_enabled"] is False
