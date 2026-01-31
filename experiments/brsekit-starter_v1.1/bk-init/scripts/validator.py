"""Validation utilities for Backlog API and config."""

import os
import sys
from typing import Dict, Tuple

# Add common module to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../common"))

try:
    from backlog.client import BacklogClient, BacklogAPIError
except ImportError:
    BacklogClient = None
    BacklogAPIError = Exception


def validate_backlog_connection(space_url: str, api_key: str, project_key: str) -> Tuple[bool, str]:
    """Validate Backlog API connection and project access.

    Args:
        space_url: Backlog space URL (e.g., your-space.backlog.jp)
        api_key: Backlog API key
        project_key: Project key to validate (e.g., PROJ)

    Returns:
        Tuple of (success: bool, message: str)
    """
    if not BacklogClient:
        return False, "BacklogClient not available. Check common/backlog installation."

    try:
        client = BacklogClient(space_url, api_key)
        project = client.get_project(project_key)

        return True, f"[OK] Connected to project: {project.name} ({project.key})"

    except BacklogAPIError as e:
        if e.status_code == 401:
            return False, "[FAIL] Invalid API key"
        elif e.status_code == 404:
            return False, f"[FAIL] Project '{project_key}' not found"
        else:
            return False, f"[FAIL] API error: {e}"
    except Exception as e:
        return False, f"[FAIL] Connection failed: {e}"


def validate_config(config: Dict) -> Tuple[bool, str]:
    """Validate generated config structure.

    Args:
        config: Configuration dictionary

    Returns:
        Tuple of (valid: bool, message: str)
    """
    required_keys = {
        "project": ["name", "backlog_key", "type", "methodology"],
        "customer": ["name", "industry", "timezone", "communication_style"],
        "focus_areas": ["primary"],
        "vault": ["enabled"]
    }

    for section, keys in required_keys.items():
        if section not in config:
            return False, f"[FAIL] Missing section: {section}"

        for key in keys:
            if key not in config[section]:
                return False, f"[FAIL] Missing key: {section}.{key}"

    # Validate types
    if not isinstance(config["focus_areas"]["primary"], list):
        return False, "[FAIL] focus_areas.primary must be a list"

    if not isinstance(config["vault"]["enabled"], bool):
        return False, "[FAIL] vault.enabled must be boolean"

    return True, "[OK] Config structure valid"


def validate_env_vars() -> Tuple[bool, str]:
    """Check required environment variables.

    Returns:
        Tuple of (valid: bool, message: str)
    """
    required = ["BACKLOG_SPACE_URL", "BACKLOG_API_KEY"]
    missing = [var for var in required if not os.getenv(var)]

    if missing:
        return False, f"[FAIL] Missing environment variables: {', '.join(missing)}"

    return True, "[OK] Environment variables set"
