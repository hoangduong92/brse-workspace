"""Generate project-context.yaml from wizard data."""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional


def generate_config(wizard_data: Dict[str, Any], methodology: Optional[str] = None) -> Dict[str, Any]:
    """Generate config dictionary from wizard data.

    Args:
        wizard_data: Data collected from SetupWizard
        methodology: Override methodology template

    Returns:
        Complete configuration dictionary
    """
    methodology = methodology or wizard_data.get("methodology", "waterfall")

    # Load methodology template
    template = load_methodology_template(methodology)

    # Build config structure
    config = {
        "project": {
            "name": wizard_data.get("project_name", ""),
            "backlog_key": wizard_data.get("backlog_key", ""),
            "type": wizard_data.get("project_type", "project-based"),
            "methodology": methodology
        },
        "customer": {
            "name": wizard_data.get("customer_name", ""),
            "industry": wizard_data.get("industry", ""),
            "timezone": wizard_data.get("timezone", "JST"),
            "communication_style": wizard_data.get("communication_style", "formal")
        },
        "focus_areas": {
            "primary": wizard_data.get("primary_focus", []),
            "secondary": wizard_data.get("secondary_focus", [])
        },
        "warning_triggers": template.get("warning_triggers", {
            "high": ["scope change", "追加要件", "budget", "delay"],
            "medium": ["clarification", "確認"]
        }),
        "pm_checklist": template.get("pm_checklist", {
            "weekly": [],
            "meeting": []
        }),
        "vault": {
            "enabled": wizard_data.get("vault_enabled", False),
            "sources": wizard_data.get("vault_sources", []),
            "sync_schedule": wizard_data.get("sync_schedule", "manual")
        }
    }

    return config


def load_methodology_template(methodology: str) -> Dict[str, Any]:
    """Load methodology template file.

    Args:
        methodology: One of 'waterfall', 'agile', 'hybrid'

    Returns:
        Template dictionary
    """
    template_dir = Path(__file__).parent.parent / "templates"
    template_file = template_dir / f"{methodology}.yaml"

    if not template_file.exists():
        return {}

    with open(template_file, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def save_config(config: Dict[str, Any], output_path: Path) -> str:
    """Save config to YAML file.

    Args:
        config: Configuration dictionary
        output_path: Output file path

    Returns:
        Path to saved file
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        yaml.dump(
            config,
            f,
            default_flow_style=False,
            allow_unicode=True,
            sort_keys=False
        )

    return str(output_path)


def format_config_yaml(config: Dict[str, Any]) -> str:
    """Format config as YAML string.

    Args:
        config: Configuration dictionary

    Returns:
        YAML formatted string
    """
    return yaml.dump(
        config,
        default_flow_style=False,
        allow_unicode=True,
        sort_keys=False
    )
